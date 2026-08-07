<template>
  <v-container class="narrow-container">
    <BaseDialog
      v-model="state.captureOpen"
      :title="$t('receipts.add-receipt')"
      :icon="$globals.icons.receipt"
      can-submit
      :submit-text="$t('receipts.create-from-image')"
      :submit-disabled="!selectedCaptureImage"
      :loading="state.creatingFromImage"
      @submit="createReceiptFromImage"
      @cancel="closeCapture"
    >
      <v-card-text>
        <div class="capture-panel">
          <div
            v-if="capturePreviewUrl"
            class="capture-preview-wrap"
          >
            <img
              :src="capturePreviewUrl"
              :alt="$t('receipts.receipt-image')"
              class="capture-preview"
            >
          </div>
          <div
            v-else
            class="capture-placeholder"
          >
            <v-icon size="64">
              {{ $globals.icons.fileImage }}
            </v-icon>
          </div>

          <v-file-input
            v-model="state.captureImage"
            accept="image/*"
            capture="environment"
            :label="$t('receipts.receipt-image')"
            :prepend-icon="$globals.icons.upload"
            density="comfortable"
          />
        </div>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton
          text
          @click="openManualCreate"
        >
          {{ $t("receipts.manual-entry") }}
        </BaseButton>
      </template>
    </BaseDialog>

    <BaseDialog
      v-model="state.editorOpen"
      :title="state.editingId ? draft.merchantName || $t('receipts.edit-receipt') : $t('receipts.add-receipt')"
      :icon="$globals.icons.receipt"
      can-submit
      :submit-text="state.editingId ? $t('general.save') : $t('general.create')"
      :submit-disabled="!draft.merchantName.trim()"
      :loading="state.saving"
      @submit="saveReceipt"
      @cancel="closeEditor"
    >
      <v-card-text>
        <v-form class="receipt-form">
          <div
            v-if="state.editingId"
            class="receipt-upload"
          >
            <img
              v-if="draft.imageUrl"
              :src="draft.imageUrl"
              :alt="draft.merchantName"
              class="receipt-image-preview"
            >
            <div
              v-else
              class="receipt-image-placeholder"
            >
              <v-icon size="48">
                {{ $globals.icons.fileImage }}
              </v-icon>
            </div>
            <div class="receipt-upload-controls">
              <v-file-input
                v-model="state.selectedImage"
                accept="image/*"
                :label="$t('receipts.receipt-image')"
                :prepend-icon="$globals.icons.upload"
                density="comfortable"
                hide-details
              />
              <BaseButton
                color="primary"
                :loading="state.uploading"
                :disabled="!selectedReceiptImage"
                @click="uploadReceiptImage"
              >
                <template #icon>
                  {{ $globals.icons.upload }}
                </template>
                {{ $t("receipts.upload-and-ocr") }}
              </BaseButton>
            </div>
          </div>

          <div class="form-grid">
            <v-text-field
              v-model="draft.merchantName"
              autofocus
              :label="$t('receipts.merchant')"
              :prepend-inner-icon="$globals.icons.store"
            />
            <v-text-field
              v-model="draft.purchasedAt"
              type="datetime-local"
              :label="$t('receipts.purchased-at')"
              :prepend-inner-icon="$globals.icons.calendar"
            />
          </div>

          <div class="totals-grid">
            <v-text-field
              v-model="draft.subtotal"
              type="number"
              min="0"
              step="0.01"
              :label="$t('receipts.subtotal')"
            />
            <v-text-field
              v-model="draft.tax"
              type="number"
              min="0"
              step="0.01"
              :label="$t('receipts.tax')"
            />
            <v-text-field
              v-model="draft.total"
              type="number"
              min="0"
              step="0.01"
              :label="$t('receipts.total')"
              :prepend-inner-icon="$globals.icons.currencyUsd"
            />
          </div>

          <div class="form-grid">
            <v-text-field
              v-model="draft.currency"
              :label="$t('receipts.currency')"
            />
            <v-text-field
              v-model="draft.status"
              :label="$t('receipts.status')"
              :prepend-inner-icon="$globals.icons.clipboardCheck"
            />
          </div>

          <v-text-field
            v-model="draft.imageUrl"
            :label="$t('receipts.image-url')"
            :prepend-inner-icon="$globals.icons.fileImage"
          />
          <div class="form-grid">
            <v-text-field
              v-model="draft.ocrStatus"
              readonly
              :label="$t('receipts.ocr-status')"
              :prepend-inner-icon="$globals.icons.textBoxCheckOutline"
            />
            <v-text-field
              v-model="draft.ocrEngine"
              readonly
              :label="$t('receipts.ocr-engine')"
              :prepend-inner-icon="$globals.icons.textBoxCheckOutline"
            />
          </div>
          <v-textarea
            v-model="draft.ocrText"
            rows="3"
            auto-grow
            :label="$t('receipts.ocr-output')"
            :prepend-inner-icon="$globals.icons.text"
          />
          <v-textarea
            v-model="draft.parserOutput"
            rows="3"
            auto-grow
            readonly
            :label="$t('receipts.parser-output')"
            :prepend-inner-icon="$globals.icons.text"
          />
          <v-textarea
            v-model="draft.parserWarnings"
            rows="2"
            auto-grow
            readonly
            :label="$t('receipts.parser-warnings')"
            :prepend-inner-icon="$globals.icons.alertCircle"
          />
          <v-textarea
            v-model="draft.notes"
            rows="2"
            auto-grow
            :label="$t('receipts.notes')"
            :prepend-inner-icon="$globals.icons.text"
          />
        </v-form>

        <div class="line-items">
          <div class="line-items-header">
            <strong>{{ $t("receipts.items") }}</strong>
            <BaseButton @click="addLineItem">
              <template #icon>
                {{ $globals.icons.plus }}
              </template>
              {{ $t("receipts.add-line") }}
            </BaseButton>
          </div>

          <div
            v-for="(item, index) in draft.items"
            :key="index"
            class="line-item"
          >
            <div class="line-item-main">
              <v-text-field
                v-model="item.name"
                density="compact"
                :label="$t('receipts.item-name')"
              />
              <v-text-field
                v-model="item.totalPrice"
                density="compact"
                type="number"
                min="0"
                step="0.01"
                :label="$t('receipts.total')"
              />
              <BaseButton
                icon
                delete
                @click="removeLineItem(index)"
              />
            </div>
            <div class="line-item-details">
              <v-text-field
                v-model.number="item.quantity"
                density="compact"
                type="number"
                :label="$t('receipts.quantity')"
              />
              <v-text-field
                v-model="item.unitText"
                density="compact"
                :label="$t('receipts.unit')"
              />
              <v-text-field
                v-model="item.unitPrice"
                density="compact"
                type="number"
                min="0"
                step="0.01"
                :label="$t('receipts.unit-price')"
              />
              <v-text-field
                v-model="item.discount"
                density="compact"
                type="number"
                min="0"
                step="0.01"
                :label="$t('receipts.discount')"
              />
              <v-text-field
                v-model="item.productCode"
                density="compact"
                :label="$t('receipts.product-code')"
              />
              <v-text-field
                v-model="item.category"
                density="compact"
                :label="$t('receipts.category')"
              />
            </div>
            <v-text-field
              v-model="item.rawText"
              density="compact"
              :label="$t('receipts.raw-text')"
            />
          </div>
        </div>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton
          v-if="state.editingId"
          delete
          @click="openDeleteForEditing"
        />
      </template>
    </BaseDialog>

    <BaseDialog
      v-model="state.deleteOpen"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="deleteReceipt"
    >
      <v-card-text>
        {{ $t("receipts.delete-confirmation") }}
      </v-card-text>
    </BaseDialog>

    <BasePageTitle divider>
      <template #header>
        <v-icon size="96">
          {{ $globals.icons.receipt }}
        </v-icon>
      </template>
      <template #title>
        {{ $t("receipts.receipts") }}
      </template>
    </BasePageTitle>

    <div class="toolbar">
      <v-text-field
        v-model="state.search"
        hide-details
        density="comfortable"
        :label="$t('search.search')"
        :prepend-inner-icon="$globals.icons.search"
      />
      <BaseButton create @click="openCreate">
        {{ $t("receipts.add-receipt") }}
      </BaseButton>
    </div>

    <v-progress-linear
      v-if="state.loading"
      indeterminate
      color="primary"
      class="mb-4"
    />

    <v-alert
      v-if="!state.loading && !filteredReceipts.length"
      type="info"
      variant="tonal"
    >
      {{ $t("receipts.no-receipts") }}
    </v-alert>

    <section class="receipt-grid">
      <v-card
        v-for="receipt in filteredReceipts"
        :key="receipt.id"
        class="receipt-card"
        @click="openEdit(receipt)"
      >
        <v-card-title class="receipt-card-title">
          {{ receipt.merchantName }}
        </v-card-title>
        <v-card-subtitle>
          {{ formatDate(receipt.receiptDate || receipt.purchasedAt) }}
        </v-card-subtitle>
        <v-card-text>
          <div class="receipt-total">
            {{ formatMoney(receipt.total, receipt.currency) }}
          </div>
          <div class="receipt-chips">
            <v-chip size="small" color="primary" variant="tonal">
              {{ receipt.items.length }} {{ $t("receipts.items") }}
            </v-chip>
            <v-chip size="small" color="info" variant="tonal">
              {{ receipt.status }}
            </v-chip>
          </div>
          <p v-if="receipt.notes || receipt.rawText" class="receipt-summary">
            {{ receipt.notes || receipt.rawText }}
          </p>
          <img
            v-if="receipt.imageUrl"
            :src="receipt.imageUrl"
            :alt="receipt.merchantName"
            class="receipt-card-image"
          >
        </v-card-text>
      </v-card>
    </section>
  </v-container>
</template>

<script setup lang="ts">
import type { ReceiptCreate, ReceiptLineItemCreate, ReceiptOut } from "~/lib/api/types/household";
import { alert } from "~/composables/use-toast";
import { useUserApi } from "~/composables/api";

type ReceiptDraft = Omit<ReceiptCreate, "items"> & { items: ReceiptLineItemCreate[] };

const api = useUserApi();
const i18n = useI18n();

useSeoMeta({
  title: i18n.t("receipts.receipts"),
});

const state = reactive({
  loading: false,
  saving: false,
  uploading: false,
  creatingFromImage: false,
  captureOpen: false,
  editorOpen: false,
  deleteOpen: false,
  editingId: "",
  deleteTargetId: "",
  search: "",
  captureImage: null as File | File[] | null,
  selectedImage: null as File | File[] | null,
});

const receipts = ref<ReceiptOut[]>([]);
const draft = reactive<ReceiptDraft>(emptyDraft());
const selectedCaptureImage = computed(() => {
  const image = state.captureImage;
  return Array.isArray(image) ? image[0] : image;
});
const selectedReceiptImage = computed(() => {
  const image = state.selectedImage;
  return Array.isArray(image) ? image[0] : image;
});
const capturePreviewUrl = ref("");

watch(selectedCaptureImage, (image) => {
  if (capturePreviewUrl.value) {
    URL.revokeObjectURL(capturePreviewUrl.value);
    capturePreviewUrl.value = "";
  }

  if (image) {
    capturePreviewUrl.value = URL.createObjectURL(image);
  }
});

const filteredReceipts = computed(() => {
  const query = state.search.trim().toLowerCase();
  return receipts.value
    .filter((receipt) => {
      if (!query) return true;

      return [
        receipt.merchantName,
        receipt.status,
        receipt.currency,
        receipt.notes,
        receipt.rawText,
        receipt.ocrText,
        receipt.parserOutput,
        ...receipt.items.map(item => [item.name, item.rawText, item.productCode, item.category].join(" ")),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(query);
    })
    .sort((a, b) => (b.purchasedAt || "").localeCompare(a.purchasedAt || ""));
});

onMounted(refresh);

function emptyLineItem(): ReceiptLineItemCreate {
  return {
    rawText: "",
    name: "",
    quantity: null,
    unitText: "",
    unitPrice: null,
    totalPrice: "",
    discount: null,
    productCode: "",
    category: "",
    confidence: null,
    notes: "",
  };
}

function emptyDraft(): ReceiptDraft {
  return {
    merchantName: "",
    purchasedAt: new Date().toISOString().slice(0, 16),
    receiptDate: null,
    subtotal: null,
    tax: null,
    total: null,
    currency: "USD",
    status: "manual",
    imageUrl: "",
    imageFilename: "",
    rawText: "",
    ocrText: "",
    ocrStatus: "",
    ocrEngine: "",
    parserName: "",
    parserVersion: "",
    parserOutput: "",
    parserWarnings: "",
    notes: "",
    items: [emptyLineItem()],
  };
}

function setDraft(data: ReceiptDraft) {
  Object.assign(draft, emptyDraft(), data);
  draft.items = data.items.length ? data.items : [emptyLineItem()];
}

async function refresh() {
  state.loading = true;
  const { data } = await api.receipts.getAll(1, -1);
  receipts.value = data?.items || [];
  state.loading = false;
}

function openCreate() {
  state.captureImage = null;
  state.captureOpen = true;
}

function openManualCreate() {
  closeCapture();
  state.editingId = "";
  setDraft(emptyDraft());
  state.editorOpen = true;
}

function closeCapture() {
  state.captureOpen = false;
  state.captureImage = null;
  if (capturePreviewUrl.value) {
    URL.revokeObjectURL(capturePreviewUrl.value);
    capturePreviewUrl.value = "";
  }
}

function openEdit(receipt: ReceiptOut) {
  state.editingId = receipt.id;
  setDraft({
    merchantName: receipt.merchantName,
    purchasedAt: receipt.purchasedAt ? receipt.purchasedAt.slice(0, 16) : null,
    receiptDate: receipt.receiptDate || null,
    subtotal: receipt.subtotal || null,
    tax: receipt.tax || null,
    total: receipt.total || null,
    currency: receipt.currency || "USD",
    status: receipt.status || "manual",
    imageUrl: receipt.imageUrl || "",
    imageFilename: receipt.imageFilename || "",
    rawText: receipt.rawText || "",
    ocrText: receipt.ocrText || "",
    ocrStatus: receipt.ocrStatus || "",
    ocrEngine: receipt.ocrEngine || "",
    parserName: receipt.parserName || "",
    parserVersion: receipt.parserVersion || "",
    parserOutput: receipt.parserOutput || "",
    parserWarnings: receipt.parserWarnings || "",
    notes: receipt.notes || "",
    items: receipt.items.map(item => ({
      rawText: item.rawText || "",
      name: item.name,
      quantity: item.quantity ?? null,
      unitText: item.unitText || "",
      unitPrice: item.unitPrice || null,
      totalPrice: item.totalPrice,
      discount: item.discount || null,
      productCode: item.productCode || "",
      category: item.category || "",
      confidence: item.confidence ?? null,
      notes: item.notes || "",
    })),
  });
  state.selectedImage = null;
  state.editorOpen = true;
}

function closeEditor() {
  state.editorOpen = false;
  state.selectedImage = null;
}

function addLineItem() {
  draft.items.push(emptyLineItem());
}

function removeLineItem(index: number) {
  draft.items.splice(index, 1);
  if (!draft.items.length) {
    draft.items.push(emptyLineItem());
  }
}

function payload(): ReceiptCreate {
  return {
    merchantName: draft.merchantName.trim(),
    purchasedAt: draft.purchasedAt ? localDateTimeToIso(draft.purchasedAt) : null,
    receiptDate: draft.receiptDate || null,
    subtotal: moneyOrNull(draft.subtotal),
    tax: moneyOrNull(draft.tax),
    total: moneyOrNull(draft.total),
    currency: draft.currency?.trim().toUpperCase() || "USD",
    status: draft.status?.trim().toLowerCase() || "manual",
    imageUrl: clean(draft.imageUrl),
    imageFilename: clean(draft.imageFilename),
    rawText: clean(draft.rawText),
    ocrText: clean(draft.ocrText),
    ocrStatus: clean(draft.ocrStatus),
    ocrEngine: clean(draft.ocrEngine),
    parserName: clean(draft.parserName),
    parserVersion: clean(draft.parserVersion),
    parserOutput: clean(draft.parserOutput),
    parserWarnings: clean(draft.parserWarnings),
    notes: clean(draft.notes),
    items: draft.items
      .filter(item => item.name.trim() && String(item.totalPrice || "").trim())
      .map(item => ({
        rawText: clean(item.rawText),
        name: item.name.trim(),
        quantity: item.quantity || null,
        unitText: clean(item.unitText),
        unitPrice: moneyOrNull(item.unitPrice),
        totalPrice: moneyOrNull(item.totalPrice) || "0",
        discount: moneyOrNull(item.discount),
        productCode: clean(item.productCode),
        category: clean(item.category),
        confidence: item.confidence ?? null,
        notes: clean(item.notes),
      })),
  };
}

async function saveReceipt() {
  const requestPayload = payload();
  if (!requestPayload.merchantName) return;

  state.saving = true;
  const request = state.editingId
    ? await api.receipts.updateOne(state.editingId, requestPayload)
    : await api.receipts.createOne(requestPayload);
  state.saving = false;

  if (request.error) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  alert.success(i18n.t(state.editingId ? "receipts.receipt-updated" : "receipts.receipt-created"));
  state.editorOpen = false;
  await refresh();
}

async function createReceiptFromImage() {
  const image = selectedCaptureImage.value;
  if (!image) return;

  state.creatingFromImage = true;
  const created = await api.receipts.createOne({
    merchantName: i18n.t("receipts.receipt-upload"),
    purchasedAt: new Date().toISOString(),
    currency: "USD",
    status: "image_upload",
    items: [],
  });

  if (created.error || !created.data) {
    state.creatingFromImage = false;
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  const uploaded = await api.receipts.uploadImage(created.data.id, image);
  state.creatingFromImage = false;

  if (uploaded.error || !uploaded.data) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  closeCapture();
  await refresh();
  openEdit(uploaded.data);
  alert.success(i18n.t("receipts.receipt-image-uploaded"));
}

async function uploadReceiptImage() {
  const image = selectedReceiptImage.value;
  if (!state.editingId || !image) return;

  state.uploading = true;
  const { data, error } = await api.receipts.uploadImage(state.editingId, image);
  state.uploading = false;

  if (error || !data) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  openEdit(data);
  alert.success(i18n.t("receipts.receipt-image-uploaded"));
  await refresh();
}

function openDeleteForEditing() {
  if (!state.editingId) return;
  state.deleteTargetId = state.editingId;
  state.deleteOpen = true;
}

async function deleteReceipt() {
  if (!state.deleteTargetId) return;
  const { error } = await api.receipts.deleteOne(state.deleteTargetId);
  if (error) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  alert.success(i18n.t("receipts.receipt-deleted"));
  state.deleteTargetId = "";
  state.editorOpen = false;
  state.deleteOpen = false;
  await refresh();
}

function localDateTimeToIso(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toISOString();
}

function clean(value: string | null | undefined) {
  const trimmed = value?.trim();
  return trimmed || null;
}

function moneyOrNull(value: string | number | null | undefined) {
  const normalized = String(value ?? "").trim();
  return normalized || null;
}

function formatMoney(value: string | number | null | undefined, currency = "USD") {
  if (value === null || value === undefined || value === "") return "";
  const amount = Number(value);
  if (Number.isNaN(amount)) return `${currency} ${value}`;

  try {
    return new Intl.NumberFormat(undefined, { style: "currency", currency }).format(amount);
  }
  catch {
    return `${currency} ${value}`;
  }
}

function formatDate(value: string | null | undefined) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleDateString(undefined, {
    month: "2-digit",
    day: "2-digit",
    year: "numeric",
  });
}
</script>

<style scoped>
.toolbar {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.receipt-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.capture-panel {
  display: grid;
  gap: 16px;
}

.capture-placeholder,
.capture-preview-wrap {
  display: grid;
  min-height: 260px;
  place-items: center;
  overflow: hidden;
  border-radius: 8px;
  background: rgba(var(--v-theme-on-surface), 0.08);
  color: rgba(var(--v-theme-on-surface), 0.54);
}

.capture-preview {
  width: 100%;
  max-height: 420px;
  object-fit: contain;
}

.receipt-card {
  cursor: pointer;
}

.receipt-card-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.receipt-total {
  margin-bottom: 10px;
  font-size: 1.6rem;
  font-weight: 700;
}

.receipt-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.receipt-summary {
  display: -webkit-box;
  margin: 12px 0 0;
  overflow: hidden;
  color: rgba(var(--v-theme-on-surface), 0.72);
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
}

.receipt-card-image {
  width: 100%;
  max-height: 180px;
  margin-top: 12px;
  object-fit: cover;
  border-radius: 8px;
}

.receipt-form,
.line-items {
  display: grid;
  gap: 12px;
}

.receipt-upload {
  display: grid;
  grid-template-columns: 160px minmax(0, 1fr);
  gap: 16px;
  align-items: center;
}

.receipt-image-preview,
.receipt-image-placeholder {
  width: 160px;
  aspect-ratio: 3 / 4;
  border-radius: 8px;
}

.receipt-image-preview {
  object-fit: cover;
}

.receipt-image-placeholder {
  display: grid;
  place-items: center;
  background: rgba(var(--v-theme-on-surface), 0.08);
  color: rgba(var(--v-theme-on-surface), 0.54);
}

.receipt-upload-controls {
  display: grid;
  gap: 10px;
}

.line-items {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.line-items-header,
.line-item-main,
.line-item-details,
.form-grid,
.totals-grid {
  display: grid;
  gap: 12px;
}

.line-items-header {
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
}

.line-item {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
}

.line-item-main {
  grid-template-columns: minmax(0, 1fr) minmax(110px, 150px) auto;
}

.line-item-details {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.form-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.totals-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

@media (max-width: 700px) {
  .toolbar,
  .receipt-upload,
  .line-items-header,
  .line-item-main,
  .line-item-details,
  .form-grid,
  .totals-grid {
    grid-template-columns: 1fr;
  }
}
</style>
