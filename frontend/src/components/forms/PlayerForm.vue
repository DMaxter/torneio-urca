<template>
  <fieldset class="player-fieldset">
    <div class="fieldset-header">
      <legend>Jogador {{ index + 1 }}</legend>
      <P-Button
        severity="secondary"
        size="small"
        text
        class="delete-btn"
        @click="$emit('remove')"
      >
        <span class="material-symbols-outlined">delete</span>
      </P-Button>
    </div>

    <P-FloatLabel class="field" variant="on">
      <P-InputText :id="`${playerId}Name`" v-model="formData.name" />
      <label :for="`${playerId}Name`">Nome</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-DatePicker :id="`${playerId}BirthDate`" v-model="formData.birth_date" fluid />
      <label :for="`${playerId}BirthDate`">Data de Nascimento</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText :id="`${playerId}FiscalNumber`" v-model="formData.fiscal_number" />
      <label :for="`${playerId}FiscalNumber`">NIF</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText :id="`${playerId}Address`" v-model="formData.address" />
      <label :for="`${playerId}Address`">Morada</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText :id="`${playerId}PlaceOfBirth`" v-model="formData.place_of_birth" />
      <label :for="`${playerId}PlaceOfBirth`">Local de Nascimento</label>
    </P-FloatLabel>

    <FileUpload
      :modelValue="localFiles.citizenCard"
      @update:modelValue="localFiles.citizenCard = $event"
      :id="`${playerId}CitizenCard`"
      label="Cartão de Cidadão (PDF)"
      required
    />
    <FileUpload
      :modelValue="localFiles.proofOfResidency"
      @update:modelValue="localFiles.proofOfResidency = $event"
      :id="`${playerId}ProofResidency`"
      label="Comprovativo de Residência (PDF)"
      required
    />

    <div class="field">
      <P-Checkbox v-model="formData.is_federated" :binary="true" :inputId="`federated${playerId}`" />
      <label :for="`federated${playerId}`"> É federado?</label>
    </div>
    <div v-if="formData.is_federated">
      <P-FloatLabel class="field" variant="on">
        <P-InputText :id="`${playerId}FederationTeam`" v-model="formData.federation_team" />
        <label :for="`${playerId}FederationTeam`">Equipa Federada</label>
      </P-FloatLabel>
      <div class="field">
        <P-Checkbox v-model="formData.federation_exams_up_to_date" :binary="true" :inputId="`exams${playerId}`" />
        <label :for="`exams${playerId}`"> Exames em dia?</label>
      </div>
    </div>

    <div v-if="checkUnderAge()" class="field authorization-required">
      <P-Tag severity="warn" :value="`Menor de ${TOURNAMENT.MIN_AGE} anos - é necessário autorização`" />
      <FileUpload
        :modelValue="localFiles.authorization"
        @update:modelValue="localFiles.authorization = $event"
        :id="`${playerId}Authorization`"
        label="Autorização do Encarregado de Educação (PDF)"
        required
      />
    </div>
  </fieldset>
</template>

<script setup lang="ts">
import { reactive, watchEffect } from "vue";
import { isUnderAge } from "@/utils";
import { TOURNAMENT } from "@/constants";
import FileUpload from "./FileUpload.vue";

interface PlayerFormData {
  name: string;
  birth_date: Date | null;
  address: string;
  place_of_birth: string;
  fiscal_number: string;
  is_federated: boolean;
  federation_team: string;
  federation_exams_up_to_date: boolean;
}

interface PlayerFiles {
  citizenCard?: File | null;
  proofOfResidency?: File | null;
  authorization?: File | null;
}

const props = defineProps<{
  index: number;
  modelValue?: PlayerFormData;
  files?: PlayerFiles;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: PlayerFormData): void;
  (e: "update:files", value: PlayerFiles): void;
  (e: "remove"): void;
}>();

const playerId = `player${props.index}`;

const formData = reactive<PlayerFormData>({
  name: "",
  birth_date: null,
  address: "",
  place_of_birth: "",
  fiscal_number: "",
  is_federated: false,
  federation_team: "",
  federation_exams_up_to_date: false
});

const localFiles = reactive<PlayerFiles>({
  citizenCard: null,
  proofOfResidency: null,
  authorization: null
});

if (props.modelValue) {
  Object.assign(formData, props.modelValue);
}

if (props.files) {
  localFiles.citizenCard = props.files.citizenCard ?? null;
  localFiles.proofOfResidency = props.files.proofOfResidency ?? null;
  localFiles.authorization = props.files.authorization ?? null;
}

watchEffect(() => {
  emit("update:modelValue", { ...formData });
});

watchEffect(() => {
  emit("update:files", {
    citizenCard: localFiles.citizenCard,
    proofOfResidency: localFiles.proofOfResidency,
    authorization: localFiles.authorization
  });
});

function checkUnderAge(): boolean {
  return isUnderAge(formData.birth_date, TOURNAMENT.MIN_AGE);
}
</script>

<style lang="scss" scoped>
fieldset {
  border: 1px solid var(--border-default);
  padding: 10px;
  margin-top: 15px;
  border-radius: 4px;
  position: relative;
}

.player-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;

  legend {
    font-weight: bold;
    padding: 0 10px;
    margin: 0;
  }
}

.field {
  margin-top: 15px;
  display: block;
}

.authorization-required {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
  background-color: var(--p-surface-ground);
  border: 1px solid var(--p-warn);
}

.player-fieldset {
  border: 1px solid var(--border-default);
  padding: 15px;
  margin-top: 15px;
  border-radius: 4px;
  position: relative;
}

.fieldset-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: absolute;
  top: -12px;
  left: 20px;
  right: 20px;
}

legend {
  font-weight: bold;
  padding: 0 10px;
  margin: 0;
  background: white;
}

.delete-btn {
  padding: 4px;
  background: white !important;
  border-radius: 50%;
}

.field {
  margin-top: 15px;
  display: block;
}

.authorization-required {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
  background-color: var(--p-surface-ground);
  border: 1px solid var(--p-warn);
}
</style>
