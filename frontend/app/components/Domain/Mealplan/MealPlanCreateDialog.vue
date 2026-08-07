<template>
  <BaseDialog
    v-model="dialog"
    :title="newMeal.existing ? $t('meal-plan.update-this-meal-plan') : $t('meal-plan.create-a-new-meal-plan')"
    :submit-text="newMeal.existing ? $t('general.update') : $t('general.create')"
    color="primary"
    :icon="$globals.icons.foods"
    :submit-disabled="isCreateDisabled"
    can-submit
    @submit="submit"
    @close="resetDialog"
  >
    <v-card-text class="pb-2">
      <v-date-picker
        v-model="newMeal.date"
        class="mx-auto"
        hide-header
        show-adjacent-months
        color="primary"
        :first-day-of-week="firstDayOfWeek"
        :local="$i18n.locale"
      />
      <v-card-text class="pb-0">
        <v-select
          v-model="newMeal.entryType"
          :return-object="false"
          :items="planTypeOptions"
          :label="$t('recipe.entry-type')"
          item-title="text"
          item-value="value"
        />
        <v-autocomplete
          v-if="!newMeal.note"
          v-model="newMeal.recipeId"
          v-model:search="search.query.value"
          :label="$t('meal-plan.meal-recipe')"
          :items="search.data.value"
          :custom-filter="normalizeFilter"
          :loading="search.loading.value"
          cache-items
          item-title="name"
          item-value="id"
          :return-object="false"
          :rules="[requiredRule]"
        />
        <template v-else>
          <v-text-field v-model="newMeal.title" :rules="[requiredRule]" :label="$t('meal-plan.meal-title')" />
          <v-textarea v-model="newMeal.text" rows="2" :label="$t('meal-plan.meal-note')" />
        </template>
      </v-card-text>
      <v-card-actions class="py-0 px-4">
        <v-switch v-model="newMeal.note" class="mt-n3 mb-n4" :label="$t('meal-plan.note-only')" />
      </v-card-actions>
    </v-card-text>
  </BaseDialog>
</template>

<script setup lang="ts">
import { format } from "date-fns";
import { useUserApi } from "~/composables/api";
import { useRecipeSearch } from "~/composables/recipes/use-recipe-search";

const dialog = defineModel<boolean>({
  default: false,
});

const props = withDefaults(defineProps<{
  actions: ReturnType<typeof useMealplans>["actions"];
  meal?: Partial<Meal>;
}>(), {
  meal: () => ({}),
});

const api = useUserApi();
const { household } = useHouseholdSelf();
const { newMeal: baseMeal, resetDialog } = useMealplanDialog();

const newMeal = ref({ ...baseMeal.value, ...props.meal });

watch(props.meal, () => {
  newMeal.value = { ...baseMeal.value, ...props.meal };
});

watch(newMeal, () => {
  if (newMeal.value.note) {
    newMeal.value.recipeId = undefined;
  }
});

function submit() {
  if (newMeal.value.existing) {
    props.actions.updateOne({ ...newMeal.value, date: newMealDateString.value });
  }
  else {
    props.actions.createOne({ ...newMeal.value, date: newMealDateString.value });
  }
  resetDialog();
}

const requiredRule = (value: any) => !!value || "Required.";

const firstDayOfWeek = computed(() => {
  return household.value?.preferences?.firstDayOfWeek || 0;
});

const newMealDateString = computed(() => {
  return format(newMeal.value.date, "yyyy-MM-dd");
});

const isCreateDisabled = computed(() => {
  if (newMeal.value.note) {
    return !newMeal.value.title.trim();
  }
  return !newMeal.value.recipeId;
});

const search = useRecipeSearch(api);
const planTypeOptions = usePlanTypeOptions();

onMounted(async () => {
  await search.trigger();
});
</script>
