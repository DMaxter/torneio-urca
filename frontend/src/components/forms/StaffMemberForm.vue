<template>
  <fieldset>
    <legend>{{ legend }}</legend>
    <PersonFields v-model="personData" :id="id" />
    <FileUpload
      v-model="citizenCardFile"
      @fileError="handleFileError"
      :id="`${id}CitizenCard`"
      label="Cartão de Cidadão (PDF)"
    />
    <FileUpload
      v-model="proofOfResidencyFile"
      @fileError="handleFileError"
      :id="`${id}ProofResidency`"
      label="Comprovativo de Residência (PDF)"
    />
  </fieldset>
</template>

<script setup lang="ts">
import { reactive, watch, ref } from "vue";
import { useToast } from "primevue/usetoast";

interface StaffMemberData {
  name: string;
  birth_date: Date | null;
  address: string;
  place_of_birth: string;
  fiscal_number: string;
}

interface StaffMemberFiles {
  citizenCard?: File | null;
  proofOfResidency?: File | null;
}

const props = defineProps<{
  id: string;
  legend: string;
  modelValue?: StaffMemberData;
  files?: StaffMemberFiles;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: StaffMemberData): void;
  (e: "update:files", value: StaffMemberFiles): void;
}>();

const personData = reactive<StaffMemberData>({
  name: "",
  birth_date: null,
  address: "",
  place_of_birth: "",
  fiscal_number: ""
});

const citizenCardFile = ref<File | null>(null);
const proofOfResidencyFile = ref<File | null>(null);
const toast = useToast();

function handleFileError(message: string) {
  toast.add({ severity: "error", summary: "Erro", detail: message, life: 5000 });
}

if (props.modelValue) {
  Object.assign(personData, props.modelValue);
}

if (props.files) {
  citizenCardFile.value = props.files.citizenCard || null;
  proofOfResidencyFile.value = props.files.proofOfResidency || null;
}

watch(
  personData,
  (newValue) => {
    emit("update:modelValue", { ...newValue });
  },
  { deep: true }
);

watch(
  [citizenCardFile, proofOfResidencyFile],
  () => {
    const files: StaffMemberFiles = {
      citizenCard: citizenCardFile.value,
      proofOfResidency: proofOfResidencyFile.value
    };
    emit("update:files", files);
  },
  { deep: true }
);
</script>

<style lang="scss" scoped>
fieldset {
  border: 1px solid var(--border-default);
  padding: 10px;
  margin-top: 15px;
  border-radius: 4px;

  legend {
    font-weight: bold;
    padding: 0 10px;
  }
}
</style>
