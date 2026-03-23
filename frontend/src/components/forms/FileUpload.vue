<template>
  <div class="field">
    <label>{{ label }} {{ required ? '*' : '' }}</label>
    <div class="file-input-wrapper">
      <P-Button size="small" @click="triggerFileInput">
        <span class="material-symbols-outlined">upload</span>
        Selecionar
      </P-Button>
      <span class="file-name">{{ fileName }}</span>
      <input
        type="file"
        :id="id"
        :accept="accept"
        @change="onFileChange"
        style="display: none"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue?: File | null;
    id: string;
    label: string;
    accept?: string;
    required?: boolean;
  }>(),
  {
    accept: ".pdf",
    required: false
  }
);

const emit = defineEmits<{
  (e: "update:modelValue", value: File | null): void;
}>();

function triggerFileInput() {
  const input = document.getElementById(props.id) as HTMLInputElement;
  if (input) {
    input.click();
  }
}

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    emit("update:modelValue", target.files[0]);
  }
}

const fileName = computed(() => {
  return props.modelValue?.name || "Nenhum ficheiro selecionado";
});

import { computed } from "vue";
</script>

<style lang="scss" scoped>
.field {
  margin-top: 15px;
  display: block;
}

.file-input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 5px;

  .file-name {
    flex: 1;
    font-size: 0.9rem;
    color: var(--p-text-muted-color);
  }
}
</style>
