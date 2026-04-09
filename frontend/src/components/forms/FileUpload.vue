<template>
  <div class="field">
    <label>{{ label }} {{ required ? '*' : '' }}</label>
    <div class="file-input-wrapper">
      <P-Button size="small" @click="triggerFileInput">
        <span class="material-symbols-outlined">upload</span>
        Selecionar
      </P-Button>
      <span class="file-name">{{ fileName }}</span>
      <span class="file-size-limit">(máx. 5MB)</span>
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
import { computed } from "vue";

const MAX_FILE_SIZE = 5 * 1024 * 1024;

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
  (e: "fileError", message: string): void;
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
    const file = target.files[0];
    if (file.size > MAX_FILE_SIZE) {
      emit("fileError", `O ficheiro "${file.name}" excede o limite de 5MB`);
      target.value = "";
      return;
    }
    emit("update:modelValue", file);
  }
}

const fileName = computed(() => {
  return props.modelValue?.name || "Nenhum ficheiro selecionado";
});
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
  flex-wrap: wrap;

  .file-name {
    flex: 1;
    font-size: 0.9rem;
    color: var(--p-text-muted-color);
    word-break: break-all;
  }

  .file-size-limit {
    font-size: 0.75rem;
    color: var(--p-text-muted-color);
    font-style: italic;
  }
}
</style>
