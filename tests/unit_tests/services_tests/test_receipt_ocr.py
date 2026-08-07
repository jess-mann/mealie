
from PIL import Image

from mealie.services.receipts import ocr


def test_extract_receipt_text_returns_subprocess_not_configured(tmp_path, monkeypatch):
    source = tmp_path / "receipt.jpg"
    Image.new("RGB", (20, 20), color="white").save(source)

    def fake_run_paddleocr_process(image_path):
        return ocr.ReceiptOcrResult(
            text=None,
            status="not_configured",
            engine=None,
            warnings=["PaddleOCR is not installed: missing paddleocr"],
        )

    monkeypatch.setattr(ocr, "_run_paddleocr_process", fake_run_paddleocr_process)

    result = ocr.extract_receipt_text(source)

    assert result.status == "not_configured"
    assert result.engine is None
    assert "PaddleOCR is not installed" in result.warnings[0]


def test_extract_receipt_text_uses_paddleocr_subprocess_with_preprocessed_image(tmp_path, monkeypatch):
    source = tmp_path / "receipt.jpg"
    Image.new("RGB", (20, 20), color="white").save(source)

    calls = []

    def fake_run_paddleocr_process(image_path):
        calls.append(image_path)
        return ocr.ReceiptOcrResult(
            text="MARKET\nTOTAL 4.57",
            status="completed",
            engine="paddleocr",
            warnings=[],
        )

    monkeypatch.setattr(ocr, "_run_paddleocr_process", fake_run_paddleocr_process)

    result = ocr.extract_receipt_text(source)

    assert result.status == "completed"
    assert result.engine == "paddleocr"
    assert result.text == "MARKET\nTOTAL 4.57"
    assert calls[0].name == f"receipt-ocr-{ocr.PADDLEOCR_MAX_IMAGE_DIMENSION}.jpg"


def test_prepare_image_for_paddleocr_downsizes_large_phone_photo(tmp_path):
    source = tmp_path / "receipt.jpg"
    Image.new("RGB", (4032, 3024), color="white").save(source)

    prepared_path, warnings = ocr._prepare_image_for_paddleocr(source, tmp_path)

    assert warnings == []
    assert prepared_path.name == f"receipt-ocr-{ocr.PADDLEOCR_MAX_IMAGE_DIMENSION}.jpg"
    with Image.open(prepared_path) as image:
        assert max(image.size) == ocr.PADDLEOCR_MAX_IMAGE_DIMENSION


def test_extract_receipt_text_retries_smaller_image_after_paddle_sigkill(tmp_path, monkeypatch):
    source = tmp_path / "receipt.jpg"
    Image.new("RGB", (4032, 3024), color="white").save(source)

    calls = []

    def fake_run_paddleocr_process(image_path):
        calls.append(image_path)
        if len(calls) == 1:
            return ocr.ReceiptOcrResult(
                text=None,
                status="failed",
                engine="paddleocr",
                warnings=["PaddleOCR exited with status -9."],
            )

        return ocr.ReceiptOcrResult(
            text="TRADER JOE'S",
            status="completed",
            engine="paddleocr",
            warnings=[],
        )

    monkeypatch.setattr(ocr, "_run_paddleocr_process", fake_run_paddleocr_process)

    result = ocr.extract_receipt_text(source)

    assert result.status == "completed"
    assert [call.name for call in calls] == [
        f"receipt-ocr-{ocr.PADDLEOCR_MAX_IMAGE_DIMENSION}.jpg",
        "receipt-ocr-800.jpg",
    ]
    assert any("retrying smaller" in warning for warning in result.warnings)
