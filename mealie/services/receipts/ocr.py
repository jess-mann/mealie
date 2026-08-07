from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps, UnidentifiedImageError

from mealie.core.config import get_app_dirs

try:
    from pillow_heif import register_heif_opener
except ImportError:
    register_heif_opener = None
else:
    register_heif_opener()


@dataclass
class ReceiptOcrResult:
    text: str | None
    status: str
    engine: str | None
    warnings: list[str]


PADDLEOCR_TIMEOUT_SECONDS = 180
PADDLEOCR_MAX_IMAGE_DIMENSION = 1100
PADDLEOCR_RETRY_IMAGE_DIMENSIONS = (800, 550)
PADDLEOCR_SIGKILL_STATUS = -9
_PADDLEOCR_LOCK = threading.Lock()

PADDLEOCR_SCRIPT = r"""
import importlib
import importlib.util
import json
import os
import sys
import traceback


def extract_text_lines(result):
    lines = []
    for page in result or []:
        for item in page or []:
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue
            text_result = item[1]
            if not isinstance(text_result, (list, tuple)) or not text_result:
                continue
            text = text_result[0]
            if isinstance(text, str) and text.strip():
                lines.append(text.strip())
    return lines


image_path = sys.argv[1]
output_path = sys.argv[2]

try:
    package_spec = importlib.util.find_spec("paddleocr")
    if package_spec is None or not package_spec.submodule_search_locations:
        raise ImportError("No module named 'paddleocr'")

    package_dir = package_spec.submodule_search_locations[0]
    sys.path.append(package_dir)

    tools_spec = importlib.util.spec_from_file_location(
        "tools",
        os.path.join(package_dir, "tools", "__init__.py"),
    )
    tools = importlib.util.module_from_spec(tools_spec)
    tools_spec.loader.exec_module(tools)
    sys.modules["tools"] = tools

    importlib.import_module("ppocr", "paddleocr")
    importlib.import_module("ppstructure", "paddleocr")
    for module_name in (
        "tools.infer.utility",
        "tools.infer.predict_rec",
        "tools.infer.predict_det",
        "tools.infer.predict_cls",
        "tools.infer.predict_system",
        "ppstructure.utility",
        "ppstructure.predict_system",
        "ppstructure.recovery.recovery_to_doc",
        "ppstructure.recovery.recovery_to_markdown",
    ):
        __import__(module_name, fromlist=["*"])

    paddleocr_spec = importlib.util.spec_from_file_location(
        "paddleocr_direct",
        os.path.join(package_dir, "paddleocr.py"),
    )
    paddleocr = importlib.util.module_from_spec(paddleocr_spec)
    paddleocr_spec.loader.exec_module(paddleocr)
    PaddleOCR = paddleocr.PaddleOCR
except ImportError as error:
    payload = {
        "text": None,
        "status": "not_configured",
        "engine": None,
        "warnings": [f"PaddleOCR is not installed: {error}"],
    }
else:
    try:
        ocr = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)
        result = ocr.ocr(image_path, cls=False)
        text = "\n".join(extract_text_lines(result)).strip()
        payload = {
            "text": text or None,
            "status": "completed" if text else "empty",
            "engine": "paddleocr",
            "warnings": [] if text else ["OCR completed, but no text was detected."],
        }
    except Exception as error:
        payload = {
            "text": None,
            "status": "failed",
            "engine": "paddleocr",
            "warnings": [str(error) or "PaddleOCR failed without an error message.", traceback.format_exc()],
        }

with open(output_path, "w", encoding="utf-8") as output_file:
    json.dump(payload, output_file)
"""


def _prepare_image_for_paddleocr(
    image_path: Path,
    work_dir: Path,
    max_dimension: int = PADDLEOCR_MAX_IMAGE_DIMENSION,
) -> tuple[Path, list[str]]:
    warnings: list[str] = []
    prepared_path = work_dir.joinpath(f"receipt-ocr-{max_dimension}.jpg")

    try:
        with Image.open(image_path) as image:
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")

            width, height = image.size
            longest_side = max(width, height)
            if longest_side > max_dimension:
                scale = max_dimension / longest_side
                next_size = (round(width * scale), round(height * scale))
                image = image.resize(next_size, Image.Resampling.LANCZOS)

            image.save(prepared_path, format="JPEG", quality=92, optimize=True)
    except (OSError, UnidentifiedImageError) as error:
        warnings.append(f"Could not preprocess receipt image; OCR used the original upload. {error}")
        return image_path, warnings

    return prepared_path, warnings


def _extract_text_lines(result: Any) -> list[str]:
    lines: list[str] = []

    for page in result or []:
        for item in page or []:
            if not isinstance(item, list | tuple) or len(item) < 2:
                continue

            text_result = item[1]
            if not isinstance(text_result, list | tuple) or not text_result:
                continue

            text = text_result[0]
            if isinstance(text, str) and text.strip():
                lines.append(text.strip())

    return lines


def _paddleocr_cache_dir() -> Path:
    cache_dir = get_app_dirs().DATA_DIR.joinpath(".paddleocr")
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _run_paddleocr_process(image_path: Path) -> ReceiptOcrResult:
    cache_dir = _paddleocr_cache_dir()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir).joinpath("paddleocr-output.json")
        env = os.environ.copy()
        env["HOME"] = str(get_app_dirs().DATA_DIR)
        env["PADDLEOCR_HOME"] = str(cache_dir)
        env["PADDLE_OCR_BASE_DIR"] = str(cache_dir)
        env.setdefault("OMP_NUM_THREADS", "1")

        try:
            with _PADDLEOCR_LOCK:
                completed = subprocess.run(
                    [sys.executable, "-c", PADDLEOCR_SCRIPT, str(image_path), str(output_path)],
                    capture_output=True,
                    check=False,
                    env=env,
                    text=True,
                    timeout=PADDLEOCR_TIMEOUT_SECONDS,
                )
        except subprocess.TimeoutExpired:
            return ReceiptOcrResult(
                text=None,
                status="failed",
                engine="paddleocr",
                warnings=[f"PaddleOCR timed out after {PADDLEOCR_TIMEOUT_SECONDS} seconds."],
            )

        if output_path.exists():
            try:
                payload = json.loads(output_path.read_text(encoding="utf-8"))
                return ReceiptOcrResult(
                    text=payload.get("text"),
                    status=payload.get("status") or "failed",
                    engine=payload.get("engine"),
                    warnings=payload.get("warnings") or [],
                )
            except (OSError, json.JSONDecodeError) as error:
                return ReceiptOcrResult(
                    text=None,
                    status="failed",
                    engine="paddleocr",
                    warnings=[f"PaddleOCR returned invalid output: {error}"],
                )

        output = "\n".join(
            part.strip()
            for part in (completed.stderr, completed.stdout)
            if part and part.strip()
        )
        if completed.returncode != 0:
            return ReceiptOcrResult(
                text=None,
                status="failed",
                engine="paddleocr",
                warnings=[output or f"PaddleOCR exited with status {completed.returncode}."],
            )

        return ReceiptOcrResult(
            text=None,
            status="failed",
            engine="paddleocr",
            warnings=["PaddleOCR completed without producing output."],
        )


def extract_receipt_text(image_path: Path) -> ReceiptOcrResult:
    warnings: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for max_dimension in (PADDLEOCR_MAX_IMAGE_DIMENSION, *PADDLEOCR_RETRY_IMAGE_DIMENSIONS):
            ocr_input, prepare_warnings = _prepare_image_for_paddleocr(image_path, Path(temp_dir), max_dimension)
            warnings.extend(prepare_warnings)
            result = _run_paddleocr_process(ocr_input)
            if result.status != "failed" or not _was_paddleocr_sigkilled(result):
                break
            warnings.append(
                f"PaddleOCR was killed while processing a {max_dimension}px image; retrying smaller."
            )

    return ReceiptOcrResult(
        text=result.text,
        status=result.status,
        engine=result.engine,
        warnings=[*warnings, *result.warnings],
    )


def _was_paddleocr_sigkilled(result: ReceiptOcrResult) -> bool:
    return any(f"status {PADDLEOCR_SIGKILL_STATUS}" in warning for warning in result.warnings)
