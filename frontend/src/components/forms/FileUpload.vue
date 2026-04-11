<template>
  <div class="block mt-[15px]">
    <label>{{ label }} {{ required ? '*' : '' }}</label>
    <div class="flex items-center gap-[10px] mt-[5px] flex-wrap">
      <P-Button size="small" @click="triggerFileInput">
        <span class="material-symbols-outlined">upload</span>
        Selecionar
      </P-Button>
      <span class="flex-1 text-[0.9rem] text-stone-500 break-all">{{ fileName }}</span>
      <span class="text-[0.75rem] text-stone-500 italic">(máx. 5MB)</span>
      <input
        type="file"
        :id="id"
        :accept="accept"
        @change="onFileChange"
        class="hidden"
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

