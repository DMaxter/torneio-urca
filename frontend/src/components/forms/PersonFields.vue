<template>
  <P-FloatLabel class="field" variant="on">
    <P-InputText :id="`${id}Name`" v-model="data.name" fluid />
    <label :for="`${id}Name`">Nome</label>
  </P-FloatLabel>
  <P-FloatLabel class="field" variant="on">
    <P-DatePicker :id="`${id}BirthDate`" v-model="data.birth_date" fluid />
    <label :for="`${id}BirthDate`">Data de Nascimento</label>
  </P-FloatLabel>
  <P-FloatLabel class="field" variant="on">
    <P-InputText :id="`${id}FiscalNumber`" v-model="data.fiscal_number" fluid />
    <label :for="`${id}FiscalNumber`">NIF</label>
  </P-FloatLabel>
  <P-FloatLabel class="field" variant="on">
    <P-InputText :id="`${id}Address`" v-model="data.address" fluid />
    <label :for="`${id}Address`">Morada</label>
  </P-FloatLabel>
  <P-FloatLabel class="field" variant="on">
    <P-InputText :id="`${id}PlaceOfBirth`" v-model="data.place_of_birth" fluid />
    <label :for="`${id}PlaceOfBirth`">Local de Nascimento</label>
  </P-FloatLabel>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";

interface PersonData {
  name: string;
  birth_date: Date | null;
  address: string;
  place_of_birth: string;
  fiscal_number: string;
}

const props = defineProps<{
  modelValue?: PersonData;
  id: string;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: PersonData): void;
}>();

const data = reactive<PersonData>({
  name: "",
  birth_date: null,
  address: "",
  place_of_birth: "",
  fiscal_number: ""
});

if (props.modelValue) {
  Object.assign(data, props.modelValue);
}

watch(
  data,
  (newValue) => {
    emit("update:modelValue", { ...newValue });
  },
  { deep: true, immediate: true }
);
</script>

<style lang="scss" scoped>
.field {
  margin-top: 15px;
  display: block;
}
</style>
