<template>
  <div class="team-registration">
    <div class="registration-header">
      <h1>Registar Equipa</h1>
      <p>Complete todos os passos para registar a sua equipa no torneio</p>
    </div>

    <div class="form-card">
      <P-Steps :model="steps" :activeStep="currentStep" />

      <div class="form-container">
        <!-- Step 1: Team Info -->
        <div v-show="currentStep === 0" class="step-content">
          <h2>Informações da Equipa</h2>
          <P-FloatLabel class="field" variant="on">
            <P-InputText id="teamName" v-model="teamData.name" fluid />
            <label for="teamName">Nome da Equipa</label>
          </P-FloatLabel>
          <P-FloatLabel class="field" variant="on">
            <P-Select
              id="tournament"
              v-model="teamData.tournament"
              :options="tournamentStore.tournaments"
              optionLabel="name"
              optionValue="id"
              fluid
            />
            <label for="tournament">Torneio</label>
          </P-FloatLabel>
        </div>

        <!-- Step 2: Responsible Info -->
        <div v-show="currentStep === 1" class="step-content">
          <h2>Responsável da Equipa</h2>
          <P-FloatLabel class="field" variant="on">
            <P-InputText id="responsibleName" v-model="teamData.responsible_name" fluid />
            <label for="responsibleName">Nome</label>
          </P-FloatLabel>
          <P-FloatLabel class="field" variant="on">
            <P-InputText id="responsibleEmail" v-model="teamData.responsible_email" type="email" fluid />
            <label for="responsibleEmail">Email</label>
          </P-FloatLabel>
          <P-FloatLabel class="field" variant="on">
            <P-InputText id="responsiblePhone" v-model="teamData.responsible_phone" fluid />
            <label for="responsiblePhone">Telemóvel</label>
          </P-FloatLabel>
        </div>

        <!-- Step 3: Players -->
        <div v-show="currentStep === 2" class="step-content">
          <div class="step-header">
            <h2>Jogadores ({{ TOURNAMENT.MIN_PLAYERS }} a {{ TOURNAMENT.MAX_PLAYERS }})</h2>
          </div>

          <div v-for="player in playerForms" :key="player.id" class="player-fieldset">
            <PlayerForm
              :index="playerForms.indexOf(player)"
              v-model="player.data"
              :files="player.files"
              @update:files="player.files = $event"
              @remove="removePlayer(player.id)"
            />
          </div>
          <P-Button 
            size="small"
            severity="secondary"
            @click="addPlayer" 
            :disabled="playerForms.length >= TOURNAMENT.MAX_PLAYERS" 
            class="add-player-btn"
          >
            <span class="material-symbols-outlined">add</span>
            Adicionar Jogador
          </P-Button>
        </div>

        <!-- Step 4: Staff Info -->
        <div v-show="currentStep === 3" class="step-content">
          <h2>Equipa Técnica (Opcional)</h2>
          <p class="optional-note">Todos os campos são opcionais</p>

          <div class="staff-grid">
            <StaffMemberForm
              id="coach"
              legend="Treinador Principal"
              v-model="staffForms.main_coach.data"
              :files="staffForms.main_coach.files"
            />
            <StaffMemberForm
              id="physio"
              legend="Fisioterapeuta"
              v-model="staffForms.physiotherapist.data"
              :files="staffForms.physiotherapist.files"
            />
            <StaffMemberForm
              id="deputy1"
              legend="Primeiro Delegado"
              v-model="staffForms.first_deputy.data"
              :files="staffForms.first_deputy.files"
            />
            <StaffMemberForm
              id="deputy2"
              legend="Segundo Delegado"
              v-model="staffForms.second_deputy.data"
              :files="staffForms.second_deputy.files"
            />
          </div>
        </div>

        <!-- Navigation -->
        <div class="navigation">
          <P-Button 
            v-if="currentStep > 0" 
            severity="secondary"
            @click="prevStep" 
          >
            <span class="material-symbols-outlined">arrow_back</span>
            Anterior
          </P-Button>
          <div class="spacer"></div>
          <P-Button 
            v-if="currentStep < steps.length - 1" 
            @click="nextStep" 
            :disabled="!canProceed"
          >
            Próximo
            <span class="material-symbols-outlined">arrow_forward</span>
          </P-Button>
          <P-Button 
            v-if="currentStep === steps.length - 1" 
            severity="success"
            @click="submit" 
            :loading="submitting" 
          >
            <span class="material-symbols-outlined">check</span>
            Submeter
          </P-Button>
        </div>
      </div>
    </div>

    <P-Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useTournamentStore } from "@stores/tournaments";
import { http } from "@router/backend/api";
import { TOURNAMENT } from "@/constants";
import { isUnderAge } from "@/utils";
import { useRegistrationDeadline } from "@composables/useRegistrationDeadline";
import PlayerForm from "@components/forms/PlayerForm.vue";
import StaffMemberForm from "@components/forms/StaffMemberForm.vue";

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

interface PlayerFormEntry {
  id: string;
  data: PlayerFormData;
  files: PlayerFiles;
}

interface StaffFormEntry {
  data: StaffMemberData;
  files: StaffMemberFiles;
}

const currentStep = ref(0);
const submitting = ref(false);

const steps = [
  { label: "Equipa" },
  { label: "Responsável" },
  { label: "Jogadores" },
  { label: "Staff" }
];

const teamData = reactive({
  name: "",
  tournament: "",
  responsible_name: "",
  responsible_email: "",
  responsible_phone: ""
});

const staffForms = reactive<{
  main_coach: StaffFormEntry;
  physiotherapist: StaffFormEntry;
  first_deputy: StaffFormEntry;
  second_deputy: StaffFormEntry;
}>({
  main_coach: { data: createEmptyStaffMember(), files: {} },
  physiotherapist: { data: createEmptyStaffMember(), files: {} },
  first_deputy: { data: createEmptyStaffMember(), files: {} },
  second_deputy: { data: createEmptyStaffMember(), files: {} }
});

const playerForms = reactive<PlayerFormEntry[]>([]);

const tournamentStore = useTournamentStore();

const canProceed = computed(() => {
  if (currentStep.value === 0) {
    return !!teamData.name && !!teamData.tournament;
  }
  if (currentStep.value === 1) {
    return !!teamData.responsible_name && !!teamData.responsible_email && !!teamData.responsible_phone;
  }
  if (currentStep.value === 2) {
    return playerForms.length >= TOURNAMENT.MIN_PLAYERS;
  }
  return true;
});

function createEmptyStaffMember(): StaffMemberData {
  return {
    name: "",
    birth_date: null,
    address: "",
    place_of_birth: "",
    fiscal_number: ""
  };
}

function createEmptyPlayer(): PlayerFormData {
  return {
    name: "",
    birth_date: null,
    address: "",
    place_of_birth: "",
    fiscal_number: "",
    is_federated: false,
    federation_team: "",
    federation_exams_up_to_date: false
  };
}

function createEmptyPlayerFiles(): PlayerFiles {
  return {
    citizenCard: null,
    proofOfResidency: null,
    authorization: null
  };
}

onMounted(async () => {
  if (!isRegistrationOpen.value) {
    router.push("/");
    return;
  }
  await tournamentStore.getTournaments();
});

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substring(2);
}

function addPlayer() {
  if (playerForms.length < TOURNAMENT.MAX_PLAYERS) {
    playerForms.push({
      id: generateId(),
      data: createEmptyPlayer(),
      files: createEmptyPlayerFiles()
    });
  }
}

function removePlayer(id: string) {
  const index = playerForms.findIndex(p => p.id === id);
  if (index !== -1) {
    playerForms.splice(index, 1);
  }
}

function nextStep() {
  if (currentStep.value === 0 && (!teamData.name || !teamData.tournament)) {
    toast.add({ severity: "error", summary: "Erro", detail: "Preencha o nome da equipa e selecione o torneio", life: 3000 });
    return;
  }
  if (currentStep.value === 1 && (!teamData.responsible_name || !teamData.responsible_email || !teamData.responsible_phone)) {
    toast.add({ severity: "error", summary: "Erro", detail: "Preencha todos os campos do responsável", life: 3000 });
    return;
  }
  if (currentStep.value === 2 && playerForms.length < TOURNAMENT.MIN_PLAYERS) {
    toast.add({ severity: "error", summary: "Erro", detail: `É necessário um mínimo de ${TOURNAMENT.MIN_PLAYERS} jogadores`, life: 3000 });
    return;
  }
  if (currentStep.value < steps.length - 1) {
    currentStep.value++;
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

async function submit() {
  if (playerForms.length < TOURNAMENT.MIN_PLAYERS) {
    toast.add({ severity: "error", summary: "Erro", detail: `É necessário um mínimo de ${TOURNAMENT.MIN_PLAYERS} jogadores`, life: 3000 });
    return;
  }

  for (let i = 0; i < playerForms.length; i++) {
    if (!playerForms[i].files.citizenCard) {
      toast.add({ severity: "error", summary: "Erro", detail: `Jogador ${i + 1}: Cartão de Cidadão é obrigatório`, life: 3000 });
      return;
    }
    if (!playerForms[i].files.proofOfResidency) {
      toast.add({ severity: "error", summary: "Erro", detail: `Jogador ${i + 1}: Comprovativo de Residência é obrigatório`, life: 3000 });
      return;
    }
    if (isUnderAge(playerForms[i].data.birth_date, TOURNAMENT.MIN_AGE) && !playerForms[i].files.authorization) {
      toast.add({ severity: "error", summary: "Erro", detail: `Jogador ${i + 1}: Autorização é obrigatória (menor de ${TOURNAMENT.MIN_AGE} anos)`, life: 3000 });
      return;
    }
  }

  submitting.value = true;

  try {
    const formData = new FormData();

    formData.append("tournament", teamData.tournament);
    formData.append("name", teamData.name);
    formData.append("responsible_name", teamData.responsible_name);
    formData.append("responsible_email", teamData.responsible_email);
    formData.append("responsible_phone", teamData.responsible_phone);

    if (staffForms.main_coach.data.name) {
      appendStaffData(formData, "main_coach", staffForms.main_coach.data);
    }

    if (staffForms.physiotherapist.data.name) {
      appendStaffData(formData, "physiotherapist", staffForms.physiotherapist.data);
    }

    if (staffForms.first_deputy.data.name) {
      appendStaffData(formData, "first_deputy", staffForms.first_deputy.data);
    }

    if (staffForms.second_deputy.data.name) {
      appendStaffData(formData, "second_deputy", staffForms.second_deputy.data);
    }

    const playersJson = playerForms.map(p => ({
      name: p.data.name,
      birth_date: p.data.birth_date?.toISOString() || "",
      address: p.data.address,
      place_of_birth: p.data.place_of_birth,
      fiscal_number: p.data.fiscal_number,
      is_federated: p.data.is_federated,
      federation_team: p.data.federation_team,
      federation_exams_up_to_date: p.data.federation_exams_up_to_date
    }));
    formData.append("players_json", JSON.stringify(playersJson));

    for (let i = 0; i < playerForms.length; i++) {
      if (playerForms[i].files.citizenCard) {
        formData.append("files", playerForms[i].files.citizenCard!, `player_${i}_citizen_card`);
      }
      if (playerForms[i].files.proofOfResidency) {
        formData.append("files", playerForms[i].files.proofOfResidency!, `player_${i}_proof_of_residency`);
      }
      if (playerForms[i].files.authorization) {
        formData.append("files", playerForms[i].files.authorization!, `player_${i}_authorization`);
      }
    }

    appendStaffFile(formData, "main_coach", staffForms.main_coach.files);
    appendStaffFile(formData, "physiotherapist", staffForms.physiotherapist.files);
    appendStaffFile(formData, "first_deputy", staffForms.first_deputy.files);
    appendStaffFile(formData, "second_deputy", staffForms.second_deputy.files);

    const response = await http.post("/teams/register", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });

    if (response.status === 201) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Equipa registada com sucesso", life: 3000 });
      setTimeout(() => {
        router.push("/");
      }, 1500);
    }
  } catch (error: any) {
    console.error(error);
  } finally {
    submitting.value = false;
  }
}

function appendStaffData(formData: FormData, prefix: string, data: StaffMemberData) {
  formData.append(`${prefix}_name`, data.name);
  formData.append(`${prefix}_birth_date`, data.birth_date?.toISOString() || "");
  formData.append(`${prefix}_address`, data.address);
  formData.append(`${prefix}_place_of_birth`, data.place_of_birth);
  formData.append(`${prefix}_fiscal_number`, data.fiscal_number);
}

function appendStaffFile(formData: FormData, prefix: string, files: StaffMemberFiles) {
  if (files.citizenCard) {
    formData.append("files", files.citizenCard, `${prefix}_citizen_card`);
  }
  if (files.proofOfResidency) {
    formData.append("files", files.proofOfResidency, `${prefix}_proof_of_residency`);
  }
}
</script>

<style scoped>
.team-registration {
  padding: 1rem;
  max-width: 900px;
  margin: 0 auto;
  background: var(--bg-surface);
}

.registration-header {
  margin-bottom: 1rem;
}

.registration-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-dark);
  margin: 0 0 0.25rem 0;
}

.registration-header p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
}

.form-card {
  background: white;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 1rem;
}

.form-container {
  margin-top: 1rem;
}

.step-content h2 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-dark);
  margin: 0 0 0.75rem 0;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
}

.step-header h2 {
  margin: 0;
  flex: 1;
}

.optional-note {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin: -0.5rem 0 0.75rem 0;
}

.field {
  margin-top: 0.75rem;
}

.field :deep(.p-inputtext),
.field :deep(.p-select) {
  width: 100%;
}

.staff-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.player-fieldset {
  position: relative;
  margin-bottom: 0.75rem;
}

.add-player-btn {
  width: 100%;
  margin-top: 0.5rem;
}

.navigation {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-light);
}

.navigation :deep(.p-button) {
  font-size: 0.8125rem;
  padding: 0.5rem 0.75rem;
}

.spacer {
  flex: 1;
}

/* Large phones */
@media (min-width: 480px) {
  .team-registration {
    padding: 1.25rem;
  }
  
  .form-card {
    padding: 1.25rem;
  }
}

/* Tablets */
@media (min-width: 768px) {
  .team-registration {
    padding: 1.5rem;
  }

  .registration-header {
    margin-bottom: 1.5rem;
  }

  .registration-header h1 {
    font-size: 1.5rem;
  }

  .form-card {
    padding: 1.5rem;
  }

  .form-container {
    margin-top: 1.5rem;
  }

  .step-content h2 {
    font-size: 1.125rem;
    margin-bottom: 1rem;
  }

  .step-header {
    margin-bottom: 1rem;
  }

  .optional-note {
    font-size: 0.875rem;
    margin: -0.5rem 0 1rem 0;
  }

  .field {
    margin-top: 1rem;
  }

  .staff-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .player-fieldset {
    margin-bottom: 1rem;
  }

  .navigation {
    margin-top: 1.5rem;
    gap: 0.75rem;
  }

  .navigation :deep(.p-button) {
    font-size: 0.875rem;
    padding: 0.625rem 1rem;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .team-registration {
    padding: 2rem;
  }

  .form-card {
    padding: 2rem;
    border-radius: 16px;
  }
}
</style>
