<template>
  <SpinTransition>
    <v-empty-state color="success" :icon="$globals.icons.checkboxMarkedCircle">
      <div class="d-flex ga-2 flex-column">
        <p>{{ $t("recipe.parser.ingredient-parser-description") }}</p>
        <p>{{ $t("recipe.parser.ingredient-parser-final-review-description") }}</p>
      </div>
    </v-empty-state>
  </SpinTransition>
  <v-checkbox
    v-model="dontShowAgain"
    hide-details
    density="compact"
    :label="$t('recipe.parser.dont-show-again')"
  />
</template>

<script setup lang="ts">
const dontShowAgain = defineModel<boolean>({ default: true });
</script>
