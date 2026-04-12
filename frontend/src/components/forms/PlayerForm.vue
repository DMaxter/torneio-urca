<template>
  <fieldset class="player-fieldset">
    <div v-if="showLegend || showDelete" class="fieldset-header">
      <legend v-if="showLegend">{{ `Jogador ${(index ?? 0) + 1}` }}</legend>
      <legend v-else class="sr-only">Jogador</legend>
      <P-Button v-if="showDelete" class="delete-btn" @click="$emit('remove')">
        <span class="material-symbols-outlined">delete</span>
      </P-Button>
    </div>

    <P-FloatLabel v-if="showTeam" class="field" variant="on">
      <P-Select :id="`${playerId}Team`" v-model="formData.team" :options="teamOptions" optionLabel="name" optionValue="id" fluid />
      <label :for="`${playerId}Team`">Equipa *</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText :id="`${playerId}Name`" v-model="formData.name" fluid />
      <label :for="`${playerId}Name`">Nome *</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-DatePicker :id="`${playerId}BirthDate`" v-model="formData.birth_date" fluid />
      <label :for="`${playerId}BirthDate`">Data de Nascimento *</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText :id="`${playerId}FiscalNumber`" v-model="formData.fiscal_number" fluid />
      <label :for="`${playerId}FiscalNumber`">NIF *</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText :id="`${playerId}Address`" v-model="formData.address" fluid />
      <label :for="`${playerId}Address`">Morada *</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText :id="`${playerId}PlaceOfBirth`" v-model="formData.place_of_birth" fluid />
      <label :for="`${playerId}PlaceOfBirth`">Local de Nascimento *</label>
    </P-FloatLabel>

    <FileUpload
      :modelValue="localFiles.citizenCard"
      @update:modelValue="localFiles.citizenCard = $event"
      @fileError="handleFileError"
      :id="`${playerId}CitizenCard`"
      label="Cartão de Cidadão (PDF)"
      required
    />
    <FileUpload
      :modelValue="localFiles.proofOfResidency"
      @update:modelValue="localFiles.proofOfResidency = $event"
      @fileError="handleFileError"
      :id="`${playerId}ProofResidency`"
      label="Comprovativo de Residência (PDF)"
      required
    />

    <div class="field">
      <P-Checkbox v-model="formData.is_goalkeeper" :binary="true" :inputId="`goalkeeper${playerId}`" />
      <label :for="`goalkeeper${playerId}`"> É guarda-redes?</label>
    </div>
    <div class="field">
      <P-Checkbox v-model="formData.is_federated" :binary="true" :inputId="`federated${playerId}`" />
      <label :for="`federated${playerId}`"> É federado?</label>
    </div>
    <div v-if="formData.is_federated" class="federated-section">
      <P-FloatLabel class="field" variant="on">
        <P-InputText :id="`${playerId}FederationTeam`" v-model="formData.federation_team" fluid />
        <label :for="`${playerId}FederationTeam`">Equipa Federada *</label>
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
        @fileError="handleFileError"
        :id="`${playerId}Authorization`"
        label="Autorização do Encarregado de Educação (PDF)"
        required
      />
    </div>
  </fieldset>
</template>

<script setup lang="ts">
import { reactive, watchEffect } from "vue";
import { useToast } from "primevue/usetoast";
import { isUnderAge } from "@/utils";
import { TOURNAMENT } from "@/constants";

interface PlayerFormData {
  team?: string;
  name: string;
  birth_date: Date | null;
  address: string;
  place_of_birth: string;
  fiscal_number: string;
  is_federated: boolean;
  federation_team: string;
  federation_exams_up_to_date: boolean;
  is_goalkeeper: boolean;
}

interface PlayerFiles {
  citizenCard?: File | null;
  proofOfResidency?: File | null;
  authorization?: File | null;
}

const props = defineProps<{
  index?: number;
  modelValue?: PlayerFormData;
  files?: PlayerFiles;
  showLegend?: boolean;
  showDelete?: boolean;
  showTeam?: boolean;
  teamOptions?: { name: string; id: string }[];
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: PlayerFormData): void;
  (e: "update:files", value: PlayerFiles): void;
  (e: "remove"): void;
}>();

const playerId = `player${props.index ?? 0}`;
const toast = useToast();

const showLegend = props.showLegend !== undefined ? props.showLegend : true;
const showDelete = props.showDelete !== undefined ? props.showDelete : true;
const showTeam = props.showTeam !== undefined ? props.showTeam : false;

const formData = reactive<PlayerFormData>({
  team: "",
  name: "",
  birth_date: null,
  address: "",
  place_of_birth: "",
  fiscal_number: "",
  is_federated: false,
  federation_team: "",
  federation_exams_up_to_date: false,
  is_goalkeeper: false
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

function handleFileError(message: string) {
  toast.add({ severity: "error", summary: "Erro", detail: message, life: 5000 });
}
</script>

<style lang="scss" scoped>
.player-form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .player-form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .player-form-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1280px) {
  .player-form-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.player-files-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

@media (min-width: 768px) {
  .player-files-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .player-files-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

fieldset {
  border: 1px solid var(--border-default);
  padding: 10px;
  margin-top: 15px;
  border-radius: 4px;
  position: relative;
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
  grid-column: 1 / -1;
}

.fieldset-header {
  display: flex !important;
  justify-content: space-between;
  align-items: center;
  position: absolute;
  top: -14px;
  left: 10px;
  right: 10px;
  padding: 0 5px;
}

legend {
  font-weight: bold;
  padding: 0 10px;
  margin: 0;
  background: var(--p-surface-50) !important;
  position: relative;
  z-index: 1;
}

.delete-btn {
  position: relative;
  z-index: 1;
  background: var(--p-surface-50) !important;
  color: #ea580c !important;
  border-radius: 50%;
  border: none !important;
  box-shadow: none !important;
}

.delete-btn .material-symbols-outlined {
  color: #ea580c !important;
}
</style>
