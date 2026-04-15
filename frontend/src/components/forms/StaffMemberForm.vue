<template>
  <fieldset :class="{ 'disabled': !enabled }">
    <legend>
      <label class="toggle-label">{{ legend }}</label>
      <P-ToggleSwitch v-model="enabled" />
    </legend>
    <div v-if="enabled">
      <PersonFields v-model="modelValue" :id="id" />
      <FileUpload
        :modelValue="files.citizenCard"
        @update:modelValue="files.citizenCard = $event"
        @fileError="handleFileError"
        :id="`${id}CitizenCard`"
        label="Cartão de Cidadão (PDF)"
      />
    </div>
  </fieldset>
</template>

<script setup lang="ts">
import { useToast } from "primevue/usetoast";

defineProps<{
  id: string;
  legend: string;
}>();

const [modelValue] = defineModel<Record<string, unknown>>();
const enabled = defineModel<boolean>("enabled", { default: false });
const files = defineModel<Record<string, unknown>>("files", { default: {} });

const toast = useToast();

function handleFileError(message: string) {
  toast.add({ severity: "error", summary: "Erro", detail: message, life: 5000 });
}
</script>

<style lang="scss" scoped>
fieldset {
  border: 1px solid var(--border-default);
  padding: 10px;
  margin-top: 15px;
  border-radius: 4px;
  transition: opacity 0.3s;

  &.disabled {
    opacity: 0.6;
  }

  legend {
    font-weight: bold;
    padding: 0 10px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    justify-content: space-between;
  }

  .toggle-label {
    font-weight: 600;
  }
}
</style>
