<template>
  <v-container class="narrow-container">
    <BaseDialog
      v-model="state.editorOpen"
      :title="state.editingId ? draft.name || $t('pantry.edit-item') : $t('pantry.add-item')"
      :icon="$globals.icons.fileCabinet"
      can-submit
      :submit-text="state.editingId ? $t('general.save') : $t('general.create')"
      :submit-disabled="!draft.name.trim()"
      :loading="state.saving"
      @submit="saveItem"
      @cancel="closeEditor"
    >
      <v-card-text>
        <img
          v-if="draft.productImageUrl"
          class="detail-image"
          :src="draft.productImageUrl"
          :alt="draft.name"
        >
        <v-form class="pantry-form">
          <v-text-field
            v-model="draft.name"
            autofocus
            :label="$t('pantry.item-name')"
            :prepend-inner-icon="$globals.icons.foods"
          />
          <v-text-field
            v-model="draft.barcode"
            :label="$t('pantry.barcode')"
            :prepend-inner-icon="$globals.icons.barcodeScan"
            inputmode="numeric"
          />
          <div class="form-grid">
            <v-text-field
              v-model.number="draft.quantity"
              type="number"
              :label="$t('pantry.quantity')"
            />
            <v-text-field
              v-model="draft.unitText"
              :label="$t('pantry.unit')"
            />
          </div>
          <div class="form-grid">
            <v-text-field
              v-model="draft.category"
              :label="$t('pantry.category')"
              :prepend-inner-icon="$globals.icons.categories"
            />
            <v-text-field
              v-model="draft.location"
              :label="$t('pantry.location')"
              :prepend-inner-icon="$globals.icons.home"
            />
          </div>
          <v-text-field
            v-model="draft.tags"
            :label="$t('pantry.tags')"
            :prepend-inner-icon="$globals.icons.tags"
          />
          <v-text-field
            v-model="draft.remaining"
            :label="$t('pantry.remaining')"
            :prepend-inner-icon="$globals.icons.timelineText"
          />
          <v-text-field
            v-model="draft.productImageUrl"
            :label="$t('pantry.product-image-url')"
            :prepend-inner-icon="$globals.icons.fileImage"
          />
          <v-text-field
            v-model="draft.manufacturer"
            :label="$t('pantry.manufacturer')"
            :prepend-inner-icon="$globals.icons.food"
          />
          <v-textarea
            v-model="draft.ingredients"
            rows="2"
            auto-grow
            :label="$t('pantry.ingredients')"
            :prepend-inner-icon="$globals.icons.formatListCheck"
          />
          <v-textarea
            v-model="draft.nutritionSummary"
            rows="2"
            auto-grow
            :label="$t('pantry.nutrition-facts')"
            :prepend-inner-icon="$globals.icons.clipboardCheck"
          />
          <div class="form-grid">
            <v-text-field
              v-model="draft.expirationDate"
              type="date"
              :label="$t('pantry.expiration-date')"
            />
            <v-text-field
              v-model="draft.openedDate"
              type="date"
              :label="$t('pantry.opened-date')"
            />
          </div>
          <v-switch
            v-model="draft.inStock"
            color="primary"
            hide-details
            :label="$t('pantry.in-stock')"
          />
          <v-textarea
            v-model="draft.notes"
            rows="3"
            auto-grow
            :label="$t('pantry.notes')"
            :prepend-inner-icon="$globals.icons.text"
          />
        </v-form>

        <div v-if="state.editingId" class="price-section">
          <div class="section-title">
            {{ $t("pantry.price-history") }}
          </div>
          <div class="price-form">
            <v-text-field
              v-model="priceDraft.price"
              type="number"
              min="0"
              step="0.01"
              :label="$t('pantry.price')"
              :prepend-inner-icon="$globals.icons.currencyUsd"
            />
            <v-text-field
              v-model="priceDraft.currency"
              :label="$t('pantry.currency')"
            />
            <v-text-field
              v-model="priceDraft.store"
              :label="$t('pantry.store')"
              :prepend-inner-icon="$globals.icons.store"
            />
            <v-text-field
              v-model.number="priceDraft.quantity"
              type="number"
              :label="$t('pantry.quantity')"
            />
            <v-text-field
              v-model="priceDraft.unitText"
              :label="$t('pantry.unit')"
            />
            <v-text-field
              v-model="priceDraft.purchasedAt"
              type="date"
              :label="$t('pantry.purchased-date')"
            />
          </div>
          <v-textarea
            v-model="priceDraft.note"
            rows="2"
            auto-grow
            :label="$t('pantry.price-note')"
            :prepend-inner-icon="$globals.icons.text"
          />
          <BaseButton
            :disabled="!priceDraft.price.trim() || state.priceLoading"
            @click="savePrice"
          >
            <template #icon>
              {{ $globals.icons.plus }}
            </template>
            {{ $t("pantry.add-price") }}
          </BaseButton>

          <v-alert
            v-if="!state.priceLoading && !priceItems.length"
            class="mt-3"
            type="info"
            variant="tonal"
          >
            {{ $t("pantry.no-prices") }}
          </v-alert>

          <div v-else class="history-list mt-3">
            <div
              v-for="entry in priceItems"
              :key="entry.id"
              class="history-entry"
            >
              <div class="history-entry-main">
                <strong>{{ formatPrice(entry) }}</strong>
                <span>{{ formatDateTime(entry.purchasedAt) }}</span>
              </div>
              <p v-if="priceMeta(entry)">
                {{ priceMeta(entry) }}
              </p>
              <p v-if="entry.note">
                {{ entry.note }}
              </p>
            </div>
          </div>
        </div>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton
          v-if="state.editingId"
          @click="openHistoryForEditing"
        >
          <template #icon>
            {{ $globals.icons.timelineText }}
          </template>
          {{ $t("pantry.history") }}
        </BaseButton>
        <BaseButton
          v-if="state.editingId"
          delete
          @click="openDeleteForEditing"
        />
      </template>
    </BaseDialog>

    <BaseDialog
      v-model="state.scannerOpen"
      :title="$t('pantry.scanner')"
      :icon="$globals.icons.barcodeScan"
      max-width="640"
      :loading="state.lookupLoading || state.scannerStarting"
      disable-submit-on-enter
      @cancel="closeScanner"
    >
      <v-card-text>
        <div class="scanner-panel">
          <video
            ref="scannerVideo"
            class="scanner-video"
            muted
            playsinline
          />
          <p class="scanner-help">
            {{ $t("pantry.scanner-instructions") }}
          </p>
          <v-alert
            v-if="state.scannerError"
            type="warning"
            variant="tonal"
            density="comfortable"
          >
            {{ state.scannerError }}
          </v-alert>
          <v-text-field
            v-model="state.manualBarcode"
            :label="$t('pantry.manual-barcode')"
            :prepend-inner-icon="$globals.icons.barcodeScan"
            inputmode="numeric"
            hide-details
            @keydown.enter.prevent="lookupBarcode(state.manualBarcode)"
          />
        </div>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton
          :disabled="!state.manualBarcode.trim() || state.lookupLoading"
          @click="lookupBarcode(state.manualBarcode)"
        >
          <template #icon>
            {{ $globals.icons.search }}
          </template>
          {{ $t("pantry.lookup-barcode") }}
        </BaseButton>
      </template>
    </BaseDialog>

    <BaseDialog
      v-model="state.historyOpen"
      :title="state.historyItemName || $t('pantry.history')"
      :icon="$globals.icons.timelineText"
      can-submit
      :submit-text="$t('pantry.log-update')"
      :submit-disabled="!historyDraft.remaining.trim()"
      :loading="state.historyLoading"
      @submit="saveHistory"
      @cancel="closeHistory"
    >
      <v-card-text>
        <div class="history-form">
          <v-text-field
            v-model="historyDraft.remaining"
            autofocus
            :label="$t('pantry.remaining')"
            :prepend-inner-icon="$globals.icons.timelineText"
          />
          <v-textarea
            v-model="historyDraft.note"
            rows="2"
            auto-grow
            :label="$t('pantry.history-note')"
            :prepend-inner-icon="$globals.icons.text"
          />
        </div>

        <v-divider class="my-4" />

        <v-alert
          v-if="!state.historyLoading && !historyItems.length"
          type="info"
          variant="tonal"
        >
          {{ $t("pantry.no-history") }}
        </v-alert>

        <div v-else class="history-list">
          <div
            v-for="entry in historyItems"
            :key="entry.id"
            class="history-entry"
          >
            <div class="history-entry-main">
              <strong>{{ entry.remaining }}</strong>
              <span>{{ formatDateTime(entry.checkedAt) }}</span>
            </div>
            <p v-if="entry.note">
              {{ entry.note }}
            </p>
          </div>
        </div>
      </v-card-text>
    </BaseDialog>

    <BaseDialog
      v-model="state.deleteOpen"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="deleteItem"
    >
      <v-card-text>
        {{ $t("pantry.delete-confirmation") }}
      </v-card-text>
    </BaseDialog>

    <BasePageTitle divider>
      <template #header>
        <v-icon size="96">
          {{ $globals.icons.fileCabinet }}
        </v-icon>
      </template>
      <template #title>
        {{ $t("pantry.pantry") }}
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
      <v-select
        v-model="state.stockFilter"
        hide-details
        density="comfortable"
        :items="stockFilterItems"
        item-title="title"
        item-value="value"
        :label="$t('pantry.stock')"
      />
      <BaseButton create @click="openCreate">
        {{ $t("pantry.add-item") }}
      </BaseButton>
      <BaseButton @click="openScanner">
        <template #icon>
          {{ $globals.icons.barcodeScan }}
        </template>
        {{ $t("pantry.scan-barcode") }}
      </BaseButton>
    </div>

    <v-progress-linear
      v-if="state.loading"
      indeterminate
      color="primary"
      class="mb-4"
    />

    <v-alert
      v-if="!state.loading && !filteredItems.length"
      type="info"
      variant="tonal"
    >
      {{ $t("pantry.no-items") }}
    </v-alert>

    <section class="pantry-grid">
      <v-hover
        v-for="item in filteredItems"
        :key="item.id"
        v-slot="{ isHovering, props: hoverProps }"
        :open-delay="50"
      >
        <v-card
          v-bind="hoverProps"
          class="pantry-card"
          :class="{ 'on-hover': isHovering }"
          :elevation="isHovering ? 12 : 2"
          @click="openEdit(item)"
        >
          <div class="pantry-card-image">
            <v-img
              v-if="item.productImageUrl"
              :src="item.productImageUrl"
              :alt="item.name"
              height="210"
              cover
            />
            <div v-else class="pantry-card-placeholder">
              <v-icon size="96">
                {{ $globals.icons.fileCabinet }}
              </v-icon>
            </div>

            <v-expand-transition>
              <div
                v-if="isHovering && cardDescription(item)"
                class="pantry-card-reveal"
              >
                <p>
                  {{ cardDescription(item) }}
                </p>
              </div>
            </v-expand-transition>
          </div>

          <v-card-title class="pantry-card-title">
            {{ item.name }}
          </v-card-title>

          <v-card-text class="pantry-card-body">
            <div class="pantry-card-chips">
              <v-chip
                v-if="item.expirationDate"
                size="small"
                :color="expirationColor(item.expirationDate)"
                variant="tonal"
              >
                {{ $t("pantry.expires") }} {{ formatDisplayDate(item.expirationDate) }}
              </v-chip>
              <v-chip
                v-if="item.inStock && item.remaining"
                size="small"
                color="info"
                variant="tonal"
              >
                {{ $t("pantry.remaining") }} {{ item.remaining }}
              </v-chip>
              <v-chip
                size="small"
                :color="item.inStock ? 'success' : 'grey'"
                variant="tonal"
              >
                {{ item.inStock ? $t("pantry.in-stock") : $t("pantry.out-of-stock") }}
              </v-chip>
            </div>

            <p v-if="cardSubhead(item)" class="pantry-card-meta">
              {{ cardSubhead(item) }}
            </p>
          </v-card-text>
        </v-card>
      </v-hover>
    </section>
  </v-container>
</template>

<script setup lang="ts">
import { BrowserMultiFormatReader, type IScannerControls } from "@zxing/browser";
import { BarcodeFormat, DecodeHintType } from "@zxing/library";
import type {
  PantryItemCreate,
  PantryItemHistoryCreate,
  PantryItemHistoryOut,
  PantryItemOut,
  PantryItemPriceHistoryOut,
} from "~/lib/api/types/household";
import { alert } from "~/composables/use-toast";
import { useUserApi } from "~/composables/api";

type StockFilter = "all" | "in" | "out";
type PantryDraft = PantryItemCreate;
type PantryHistoryDraft = PantryItemHistoryCreate;

interface PantryPriceDraft {
  price: string;
  currency: string;
  store: string;
  quantity: number | null;
  unitText: string;
  purchasedAt: string | null;
  note: string;
}

interface OpenFoodFactsProduct {
  brands?: string;
  categories?: string;
  categories_hierarchy?: string[];
  categories_tags?: string[];
  image_front_url?: string;
  image_url?: string;
  ingredients_text?: string;
  nutriments?: Record<string, number | string | undefined>;
  nutrition_data_per?: string;
  product_name?: string;
  quantity?: string;
  serving_size?: string;
}

interface OpenFoodFactsResponse {
  product?: OpenFoodFactsProduct;
  status?: number;
}

const api = useUserApi();
const i18n = useI18n();

useSeoMeta({
  title: i18n.t("pantry.pantry"),
});

const state = reactive({
  loading: false,
  saving: false,
  scannerOpen: false,
  scannerStarting: false,
  lookupLoading: false,
  editorOpen: false,
  historyOpen: false,
  historyLoading: false,
  priceLoading: false,
  deleteOpen: false,
  editingId: "",
  historyItemId: "",
  historyItemName: "",
  deleteTargetId: "",
  scannerError: "",
  manualBarcode: "",
  lastBarcode: "",
  search: "",
  stockFilter: "all" as StockFilter,
});

const items = ref<PantryItemOut[]>([]);
const historyItems = ref<PantryItemHistoryOut[]>([]);
const priceItems = ref<PantryItemPriceHistoryOut[]>([]);
const draft = reactive<PantryDraft>(emptyDraft());
const historyDraft = reactive<PantryHistoryDraft>(emptyHistoryDraft());
const priceDraft = reactive<PantryPriceDraft>(emptyPriceDraft());
const scannerVideo = ref<HTMLVideoElement | null>(null);
let codeReader: BrowserMultiFormatReader | null = null;
let scannerControls: IScannerControls | null = null;

const stockFilterItems = computed(() => [
  { title: i18n.t("pantry.in-stock"), value: "in" },
  { title: i18n.t("pantry.out-of-stock"), value: "out" },
  { title: i18n.t("pantry.all-items"), value: "all" },
]);

const filteredItems = computed(() => {
  const query = state.search.trim().toLowerCase();
  return items.value
    .filter((item) => {
      if (state.stockFilter === "in" && !item.inStock) return false;
      if (state.stockFilter === "out" && item.inStock) return false;
      if (!query) return true;

      return [
        item.name,
        item.barcode,
        item.category,
        item.location,
        item.tags,
        item.notes,
        item.manufacturer,
        item.ingredients,
        item.nutritionSummary,
        item.remaining,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(query);
    })
    .sort((a, b) => {
      const aDate = a.expirationDate || "9999-12-31";
      const bDate = b.expirationDate || "9999-12-31";
      return aDate.localeCompare(bDate) || a.name.localeCompare(b.name);
    });
});

onMounted(refresh);
onBeforeUnmount(stopScanner);

watch(() => state.scannerOpen, async (open) => {
  if (open) {
    await nextTick();
    await startScanner();
    return;
  }

  stopScanner();
});

function emptyDraft(): PantryDraft {
  return {
    name: "",
    barcode: "",
    quantity: null,
    unitText: "",
    category: "",
    location: "",
    tags: "",
    notes: "",
    productImageUrl: "",
    manufacturer: "",
    ingredients: "",
    nutritionSummary: "",
    remaining: "",
    expirationDate: null,
    openedDate: null,
    inStock: true,
  };
}

function setDraft(data: PantryDraft) {
  Object.assign(draft, emptyDraft(), data);
}

function emptyHistoryDraft(): PantryHistoryDraft {
  return {
    remaining: "",
    note: "",
    checkedAt: null,
  };
}

function setHistoryDraft(data: PantryHistoryDraft) {
  Object.assign(historyDraft, emptyHistoryDraft(), data);
}

function emptyPriceDraft(): PantryPriceDraft {
  return {
    price: "",
    currency: "USD",
    store: "",
    quantity: null,
    unitText: "",
    purchasedAt: new Date().toISOString().slice(0, 10),
    note: "",
  };
}

function setPriceDraft(data: Partial<PantryPriceDraft>) {
  Object.assign(priceDraft, emptyPriceDraft(), data);
}

async function refresh() {
  state.loading = true;
  const { data } = await api.pantry.items.getAll(1, -1);
  items.value = data?.items || [];
  state.loading = false;
}

function openCreate() {
  state.editingId = "";
  setDraft(emptyDraft());
  state.editorOpen = true;
}

async function openEdit(item: PantryItemOut) {
  state.editingId = item.id;
  setDraft({
    name: item.name,
    barcode: item.barcode || "",
    quantity: item.quantity ?? null,
    unitText: item.unitText || item.unit?.name || "",
    category: item.category || "",
    location: item.location || "",
    tags: item.tags || "",
    notes: item.notes || "",
    productImageUrl: item.productImageUrl || "",
    manufacturer: item.manufacturer || "",
    ingredients: item.ingredients || "",
    nutritionSummary: item.nutritionSummary || "",
    remaining: item.remaining || "",
    expirationDate: item.expirationDate || null,
    openedDate: item.openedDate || null,
    inStock: item.inStock,
  });
  state.editorOpen = true;
  setPriceDraft({ quantity: item.quantity ?? null, unitText: item.unitText || item.unit?.name || "" });
  await loadPrices(item.id);
}

function closeEditor() {
  state.editorOpen = false;
  priceItems.value = [];
  setPriceDraft(emptyPriceDraft());
}

function openScanner() {
  state.editingId = "";
  setDraft(emptyDraft());
  state.manualBarcode = "";
  state.lastBarcode = "";
  state.scannerError = "";
  state.scannerOpen = true;
}

function closeScanner() {
  state.scannerOpen = false;
}

async function startScanner() {
  if (!scannerVideo.value || state.scannerStarting) return;

  state.scannerStarting = true;
  state.scannerError = "";

  try {
    const hints = new Map();
    hints.set(DecodeHintType.POSSIBLE_FORMATS, [
      BarcodeFormat.UPC_A,
      BarcodeFormat.UPC_E,
      BarcodeFormat.EAN_13,
      BarcodeFormat.EAN_8,
    ]);

    codeReader = new BrowserMultiFormatReader(hints);
    scannerControls = await codeReader.decodeFromVideoDevice(undefined, scannerVideo.value, (result, _error, controls) => {
      if (!result) return;

      const barcode = normalizeBarcode(result.getText());
      if (!barcode || barcode === state.lastBarcode) return;

      state.lastBarcode = barcode;
      state.manualBarcode = barcode;
      controls.stop();
      scannerControls = null;
      void lookupBarcode(barcode);
    });
  }
  catch {
    state.scannerError = i18n.t("pantry.camera-unavailable");
  }
  finally {
    state.scannerStarting = false;
  }
}

function stopScanner() {
  scannerControls?.stop();
  scannerControls = null;
  codeReader = null;

  const stream = scannerVideo.value?.srcObject;
  if (stream instanceof MediaStream) {
    stream.getTracks().forEach(track => track.stop());
  }
}

async function lookupBarcode(rawBarcode: string) {
  const barcode = normalizeBarcode(rawBarcode);
  if (!barcode || state.lookupLoading) return;

  state.manualBarcode = barcode;
  state.lookupLoading = true;
  stopScanner();

  try {
    const response = await fetch(
      `https://world.openfoodfacts.org/api/v2/product/${barcode}.json?fields=product_name,brands,quantity,categories,categories_hierarchy,categories_tags,image_front_url,image_url,ingredients_text,nutriments,nutrition_data_per,serving_size`,
    );
    const product = (await response.json()) as OpenFoodFactsResponse;
    applyScannedProduct(barcode, product);
  }
  catch {
    prepareManualBarcodeItem(barcode);
    alert.error(i18n.t("pantry.product-lookup-failed"));
  }
  finally {
    state.lookupLoading = false;
    state.scannerOpen = false;
    state.editorOpen = true;
  }
}

function applyScannedProduct(barcode: string, response: OpenFoodFactsResponse) {
  const product = response.status === 1 ? response.product : null;

  if (!product) {
    prepareManualBarcodeItem(barcode);
    alert.info(i18n.t("pantry.barcode-not-found"));
    return;
  }

  const productName = clean(product.product_name);
  const brand = clean(product.brands?.split(",")[0]);
  const category = pantryCategory(product);
  const name = productName && brand ? `${brand} ${productName}` : productName || brand || barcode;

  setDraft({
    ...emptyDraft(),
    name,
    barcode,
    unitText: clean(product.quantity) || "",
    category,
    notes: brand && productName ? `${brand} product from Open Food Facts.` : "",
    productImageUrl: clean(product.image_front_url) || clean(product.image_url) || "",
    manufacturer: brand || "",
    ingredients: clean(product.ingredients_text) || "",
    nutritionSummary: nutritionSummary(product),
    remaining: "full",
  });
  alert.success(i18n.t("pantry.product-found"));
}

function prepareManualBarcodeItem(barcode: string) {
  setDraft({
    ...emptyDraft(),
    name: barcode,
    barcode,
  });
}

function pantryCategory(product: OpenFoodFactsProduct) {
  const hierarchy = product.categories_hierarchy || product.categories_tags;
  if (hierarchy?.length) {
    return hierarchy
      .filter(category => category.startsWith("en:"))
      .map(category => titleCase(category.replace(/^en:/, "").replace(/-/g, " ")))
      .join(" > ");
  }

  const tag = product.categories_tags?.find(category => category.startsWith("en:"));
  if (tag) {
    return titleCase(tag.replace(/^en:/, "").replace(/-/g, " "));
  }

  return clean(product.categories?.split(",")[0]) || "";
}

function normalizeBarcode(value: string | null | undefined) {
  return value?.replace(/\D/g, "") || "";
}

function titleCase(value: string) {
  return value.replace(/\b\w/g, letter => letter.toUpperCase());
}

function nutritionSummary(product: OpenFoodFactsProduct) {
  const nutriments = product.nutriments || {};
  const facts = [
    nutrientLine(nutriments, "energy-kcal", "Energy", "kcal"),
    nutrientLine(nutriments, "fat", "Fat", "g"),
    nutrientLine(nutriments, "saturated-fat", "Saturated Fat", "g"),
    nutrientLine(nutriments, "cholesterol", "Cholesterol", "g"),
    nutrientLine(nutriments, "carbohydrates", "Carbohydrates", "g"),
    nutrientLine(nutriments, "sugars", "Sugars", "g"),
    nutrientLine(nutriments, "proteins", "Protein", "g"),
    nutrientLine(nutriments, "salt", "Salt", "g"),
    nutrientLine(nutriments, "vitamin-a", "Vitamin A", "g"),
    nutrientLine(nutriments, "vitamin-d", "Vitamin D", "g"),
    nutrientLine(nutriments, "potassium", "Potassium", "g"),
    nutrientLine(nutriments, "calcium", "Calcium", "g"),
  ].filter(Boolean);

  const basis = product.nutrition_data_per ? `per ${product.nutrition_data_per}` : "";
  const serving = product.serving_size ? `Serving ${product.serving_size}` : "";
  return [basis, serving, facts.join(", ")].filter(Boolean).join(". ");
}

function nutrientLine(
  nutriments: Record<string, number | string | undefined>,
  key: string,
  label: string,
  fallbackUnit: string,
) {
  const rawValue = nutriments[`${key}_100g`] ?? nutriments[key];
  if (rawValue === undefined || rawValue === null || rawValue === "") return "";

  const value = typeof rawValue === "number" ? formatNumber(rawValue) : rawValue;
  const unit = nutriments[`${key}_unit`] || fallbackUnit;
  return `${label} ${value} ${unit}`;
}

function formatNumber(value: number) {
  if (Math.abs(value) >= 10) return String(Math.round(value));
  if (Math.abs(value) >= 1) return String(Math.round(value * 100) / 100);
  return String(Math.round(value * 1000000) / 1000000);
}

function payload(): PantryItemCreate {
  return {
    name: draft.name.trim(),
    barcode: clean(draft.barcode),
    quantity: draft.quantity || null,
    unitText: clean(draft.unitText),
    category: clean(draft.category),
    location: clean(draft.location),
    tags: clean(draft.tags),
    notes: clean(draft.notes),
    productImageUrl: clean(draft.productImageUrl),
    manufacturer: clean(draft.manufacturer),
    ingredients: clean(draft.ingredients),
    nutritionSummary: clean(draft.nutritionSummary),
    remaining: clean(draft.remaining),
    expirationDate: draft.expirationDate || null,
    openedDate: draft.openedDate || null,
    inStock: draft.inStock ?? true,
  };
}

async function saveItem() {
  if (!draft.name.trim()) return;

  state.saving = true;
  const request = state.editingId
    ? await api.pantry.items.updateOne(state.editingId, payload())
    : await api.pantry.items.createOne(payload());

  state.saving = false;

  if (request.error) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  alert.success(i18n.t(state.editingId ? "pantry.item-updated" : "pantry.item-created"));
  state.editorOpen = false;
  await refresh();
}

async function openHistory(item: PantryItemOut) {
  state.historyItemId = item.id;
  state.historyItemName = item.name;
  setHistoryDraft({ remaining: item.remaining || "", note: "", checkedAt: null });
  state.historyOpen = true;
  state.historyLoading = true;
  const { data, error } = await api.pantry.items.getHistory(item.id);
  state.historyLoading = false;

  if (error) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  historyItems.value = data || [];
}

function closeHistory() {
  state.historyOpen = false;
  state.historyItemId = "";
  state.historyItemName = "";
  historyItems.value = [];
  setHistoryDraft(emptyHistoryDraft());
}

async function saveHistory() {
  if (!state.historyItemId || !historyDraft.remaining.trim()) return;

  state.historyLoading = true;
  const { data, error } = await api.pantry.items.createHistory(state.historyItemId, {
    remaining: historyDraft.remaining.trim(),
    note: clean(historyDraft.note),
  });
  state.historyLoading = false;

  if (error || !data) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  historyItems.value = [data, ...historyItems.value];
  setHistoryDraft({ remaining: data.remaining, note: "", checkedAt: null });
  alert.success(i18n.t("pantry.history-updated"));
  await refresh();
}

async function loadPrices(itemId: string) {
  state.priceLoading = true;
  const { data, error } = await api.pantry.items.getPrices(itemId);
  state.priceLoading = false;

  if (error) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  priceItems.value = data || [];
}

async function savePrice() {
  if (!state.editingId || !priceDraft.price.trim()) return;

  state.priceLoading = true;
  const { data, error } = await api.pantry.items.createPrice(state.editingId, {
    price: priceDraft.price.trim(),
    currency: priceDraft.currency.trim().toUpperCase() || "USD",
    store: clean(priceDraft.store),
    quantity: priceDraft.quantity || null,
    unitText: clean(priceDraft.unitText),
    note: clean(priceDraft.note),
    purchasedAt: priceDraft.purchasedAt ? `${priceDraft.purchasedAt}T00:00:00` : null,
  });
  state.priceLoading = false;

  if (error || !data) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  priceItems.value = [data, ...priceItems.value];
  setPriceDraft({
    currency: data.currency || "USD",
    quantity: priceDraft.quantity,
    unitText: priceDraft.unitText,
  });
  alert.success(i18n.t("pantry.price-added"));
}

function openDeleteForEditing() {
  if (!state.editingId) return;
  state.deleteTargetId = state.editingId;
  state.deleteOpen = true;
}

async function openHistoryForEditing() {
  const item = items.value.find(item => item.id === state.editingId);
  if (!item) return;
  await openHistory(item);
}

async function deleteItem() {
  if (!state.deleteTargetId) return;
  const { error } = await api.pantry.items.deleteOne(state.deleteTargetId);
  if (error) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  alert.success(i18n.t("pantry.item-deleted"));
  state.deleteTargetId = "";
  state.editorOpen = false;
  await refresh();
}

function clean(value: string | null | undefined) {
  const trimmed = value?.trim();
  return trimmed || null;
}

function quantityLabel(item: PantryItemOut) {
  if (!item.quantity) return "";
  const unit = item.unitText || item.unit?.name;
  return unit ? `${item.quantity} ${unit}` : String(item.quantity);
}

function cardSubhead(item: PantryItemOut) {
  return [quantityLabel(item), item.category, item.location].filter(Boolean).join(" / ");
}

function cardDescription(item: PantryItemOut) {
  return item.notes || item.ingredients || item.nutritionSummary || item.manufacturer || "";
}

function formatDisplayDate(date: string) {
  const [year, month, day] = date.split("-");
  return month && day && year ? `${month}-${day}-${year}` : date;
}

function formatDateTime(value: string | null | undefined) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString(undefined, {
    month: "2-digit",
    day: "2-digit",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatPrice(entry: PantryItemPriceHistoryOut) {
  const amount = Number(entry.price);
  const currency = entry.currency || "USD";
  if (Number.isNaN(amount)) return `${currency} ${entry.price}`;

  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency,
    }).format(amount);
  }
  catch {
    return `${currency} ${entry.price}`;
  }
}

function priceMeta(entry: PantryItemPriceHistoryOut) {
  const quantity = entry.quantity
    ? entry.unitText
      ? `${entry.quantity} ${entry.unitText}`
      : String(entry.quantity)
    : "";

  return [entry.store, quantity].filter(Boolean).join(" / ");
}

function expirationColor(expirationDate: string) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const expires = new Date(`${expirationDate}T00:00:00`);
  const days = Math.ceil((expires.getTime() - today.getTime()) / 86400000);
  if (days < 0) return "error";
  if (days <= 7) return "warning";
  return "success";
}
</script>

<style scoped>
.toolbar {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(140px, 180px) auto auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.scanner-panel {
  display: grid;
  gap: 12px;
}

.scanner-video {
  width: 100%;
  aspect-ratio: 4 / 3;
  background: rgb(var(--v-theme-surface-variant));
  border-radius: 8px;
  object-fit: cover;
}

.scanner-help {
  margin: 0;
  color: rgba(var(--v-theme-on-surface), 0.72);
}

.pantry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 16px;
}

.pantry-card {
  cursor: pointer;
  overflow: hidden;
}

.pantry-card-image {
  position: relative;
  height: 210px;
  background: rgb(var(--v-theme-surface-variant));
}

.pantry-card-placeholder {
  display: grid;
  height: 100%;
  place-items: center;
  color: rgba(var(--v-theme-on-surface), 0.58);
}

.pantry-card-reveal {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  padding: 16px;
  background: rgba(var(--v-theme-secondary), 0.88);
  color: rgb(var(--v-theme-on-secondary));
}

.pantry-card-reveal p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 7;
  line-clamp: 7;
}

.pantry-card-title {
  display: -webkit-box;
  min-height: 70px;
  overflow: hidden;
  font-size: 1.05rem;
  line-height: 1.25;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.pantry-card-body {
  display: grid;
  gap: 8px;
}

.pantry-card-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.pantry-card-meta {
  display: -webkit-box;
  min-height: 40px;
  margin: 0;
  overflow: hidden;
  color: rgba(var(--v-theme-on-surface), 0.72);
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.detail-image {
  display: block;
  width: min(240px, 100%);
  max-height: 260px;
  margin: 0 auto 16px;
  border-radius: 8px;
  background: rgb(var(--v-theme-surface-variant));
  object-fit: contain;
}

.history-form,
.history-list {
  display: grid;
  gap: 10px;
}

.price-section {
  display: grid;
  gap: 12px;
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
}

.price-form {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.history-entry {
  border-left: 3px solid rgb(var(--v-theme-primary));
  padding: 4px 0 4px 12px;
}

.history-entry-main {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: space-between;
}

.history-entry-main span,
.history-entry p {
  color: rgba(var(--v-theme-on-surface), 0.72);
}

.history-entry p {
  margin: 4px 0 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 700px) {
  .toolbar,
  .form-grid,
  .price-form {
    grid-template-columns: 1fr;
  }
}
</style>
