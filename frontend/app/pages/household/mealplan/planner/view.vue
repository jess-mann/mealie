<template>
  <v-container class="mx-0 pa-0">
    <MealPlanCreateDialog v-model="editMealDialog" :actions="actions" :meal="newMeal" />
    <MealPlanLayout :mealplans="mealplans">
      <template #default="{ day }">
        <MealPlanDay :day="day.date" :actions="actions" :recipes="day.recipes">
          <SpinTransition>
            <v-card v-if="day.sections.length" variant="flat" class="pl-4 pr-2">
              <SpinTransition>
                <div v-for="section in day.sections" :key="section.title">
                  <div class="py-2 d-flex flex-column">
                    <div class="primary" style="width: 50px; height: 2.5px" />
                    <p class="text-overline my-0">
                      {{ section.title }}
                    </p>
                  </div>
                  <SpinTransition>
                    <RecipeCardMobile
                      v-for="mealplan in section.meals"
                      :key="mealplan.id"
                      :recipe-id="mealplan.recipe ? mealplan.recipe.id! : ''"
                      class="mb-2"
                      :rating="mealplan.recipe ? mealplan.recipe.rating! : 0"
                      :slug="mealplan.recipe ? mealplan.recipe.slug! : mealplan.title!"
                      :description="mealplan.recipe ? mealplan.recipe.description! : mealplan.text!"
                      :name="mealplan.recipe ? mealplan.recipe.name! : mealplan.title!"
                      :tags="mealplan.recipe ? mealplan.recipe.tags! : []"
                      :context-menu-leading-items="[
                        {
                          title: $t('meal-plan.remove-from-plan'),
                          icon: $globals.icons.calendarRemove,
                          color: undefined,
                          event: 'mealplanRemove',
                          isPublic: false,
                        },
                        {
                          title: $t('meal-plan.edit-meal-plan'),
                          icon: $globals.icons.calendarEdit,
                          color: undefined,
                          event: 'mealplanEdit',
                          isPublic: false,
                        },
                      ]"
                      @mealplan-remove="actions.deleteOne(mealplan.id)"
                      @mealplan-edit="editMeal(mealplan)"
                    >
                      <template v-if="!mealplan.recipe" #context-menu>
                        <MealPlanNoteMenu
                          @mealplan-remove="actions.deleteOne(mealplan.id)"
                          @mealplan-edit="editMeal(mealplan)"
                        />
                      </template>
                    </RecipeCardMobile>
                  </SpinTransition>
                </div>
              </SpinTransition>
            </v-card>
          </SpinTransition>
        </MealPlanDay>
      </template>
    </MealPlanLayout>
  </v-container>
</template>

<script setup lang="ts">
import MealPlanNoteMenu from "~/components/Domain/Mealplan/MealPlanNoteMenu.vue";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";
import type { MealsByDate } from "~/composables/use-group-mealplan";

defineProps<{
  mealplans: MealsByDate[];
  actions: ReturnType<typeof useMealplans>["actions"];
}>();

const { open: editMealDialog, newMeal, editMeal } = useMealplanDialog();
</script>
