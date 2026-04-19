<template>
  <div class="team-registration">
    <div class="registration-header">
      <h1>Registar Equipa</h1>
      <p>Complete todos os passos para registar a sua equipa no torneio</p>
    </div>

    <div class="form-card">
      <P-Steps :model="steps" :activeStep="currentStep" />

      <div v-if="submitting && registrationProgress.total > 0" class="registration-progress">
        <P-ProgressBar :value="Math.round((registrationProgress.current / registrationProgress.total) * 100)" :showValue="false" />
        <span class="progress-text">{{ registrationProgress.step }}</span>
      </div>

      <div class="form-container">
        <!-- Step 0: Instructions -->
        <div v-show="currentStep === 0" class="step-content">
          <h2>Instruções</h2>
          <ul class="list-disc list-inside space-y-2 mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4 text-stone-700">
            <li>O registo da equipa deve ser feito <strong>todo de uma só vez</strong>, se for necessário selecionar alterações, por favor contacte a organização.</li>
            <li>O registo requer um <strong>responsável de equipa</strong> que será o ponto de contacto entre a organização e a equipa.</li>
            <li>Caso haja problemas com a validação da informação dos jogadores, certifique-se de que a informação de contacto do responsável pela equipa está <strong>correcta</strong>, pois pode levar à <strong>não participação da equipa</strong>.</li>
            <li>As equipas têm um número mínimo de <strong>{{ TOURNAMENT.MIN_PLAYERS }} jogadores</strong> e um máximo de <strong>{{ TOURNAMENT.MAX_PLAYERS }} jogadores</strong>.</li>
            <li>É também possível selecionar o staff que fará parte da equipa e que corresponderão às pessoas que poderão estar em campo em dia de jogo: <strong>treinador</strong>, <strong>treinador adjunto</strong>, <strong>fisioterapeuta</strong> e <strong>2 delegados de jogo</strong>, no entanto estes são <strong>opcionais</strong> para este registo.</li>
            <li>Para cada jogador é obrigatório preencher: <strong>nome completo</strong>, <strong>data de nascimento</strong>, <strong>NIF</strong>, <strong>morada</strong>, <strong>local de nascimento</strong>, <strong>PDF com cartão de cidadão</strong> <span class="tooltip-wrapper"><button @click="citizenCardTooltipVisible = !citizenCardTooltipVisible" class="help-tooltip"><span class="material-symbols-outlined">help</span></button><span v-if="citizenCardTooltipVisible" class="tooltip-box">Pode digitalizar o cartão de cidadão com uma aplicação como o Adobe Scan.<button class="tooltip-close" @click.stop="citizenCardTooltipVisible = false"><span class="material-symbols-outlined">close</span></button></span></span>, <strong>PDF com comprovativo de residência</strong> <span class="tooltip-wrapper"><button @click="proofOfResidenceTooltipVisible = !proofOfResidenceTooltipVisible" class="help-tooltip"><span class="material-symbols-outlined">help</span></button><span v-if="proofOfResidenceTooltipVisible" class="tooltip-box">Portal das Finanças > Login > Serviços > Documentos e Certidões > Requerer Certidão > Domicílio Fiscal > Confirmar > Obter<button class="tooltip-close" @click.stop="proofOfResidenceTooltipVisible = false"><span class="material-symbols-outlined">close</span></button></span></span> e <strong>se pertence a uma equipa federada ou não</strong>.</li>
            <li>Se precisar de registar membros adicionais (jogadores ou staff) após o primeiro registo, contacte a organização.</li>
            <li>Se uma equipa não tiver um selecionador associado no início do torneio, <strong>não poderá participar</strong>, por isso se não selecionar um selecionador agora, certifique-se que contacta a organização para o fazer.</li>
          </ul>

          <div class="privacy-acceptance mt-6 p-4 border border-surface-200 rounded-lg bg-surface-50">
            <div class="flex align-items-start gap-3">
              <P-Checkbox v-model="privacyAccepted" :binary="true" inputId="privacyAccept" />
              <label for="privacyAccept" class="text-surface-700 leading-7">
                Declaro que li e aceito a
                <span class="text-primary font-medium cursor-pointer hover:underline" @click="goToPrivacy">
                  Política de Privacidade
                </span>
                e que todos os jogadores e membros do staff da minha equipa tomaram conhecimento e aceitam os termos da mesma. Todos os dados fornecidos são verdadeiros e atuais.
              </label>
            </div>
          </div>
        </div>

        <!-- Step 1: Team Info -->
        <div v-show="currentStep === 1" class="step-content">
          <h2>Informações da Equipa</h2>
          <P-FloatLabel class="field" variant="on">
            <P-InputText id="teamName" v-model="teamData.name" fluid />
            <label for="teamName">Nome da Equipa *</label>
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
            <label for="tournament">Torneio *</label>
          </P-FloatLabel>
        </div>

        <!-- Step 2: Responsible Info -->
        <div v-show="currentStep === 2" class="step-content">
          <h2>Responsável da Equipa</h2>
          <P-FloatLabel class="field" variant="on">
            <P-InputText id="responsibleName" v-model="teamData.responsible_name" fluid />
            <label for="responsibleName">Nome *</label>
          </P-FloatLabel>
          <P-FloatLabel class="field" variant="on">
            <P-InputText id="responsibleEmail" v-model="teamData.responsible_email" type="email" fluid />
            <label for="responsibleEmail">Email *</label>
          </P-FloatLabel>
          <P-FloatLabel class="field" variant="on">
            <P-InputText id="responsiblePhone" v-model="teamData.responsible_phone" fluid />
            <label for="responsiblePhone">Telemóvel *</label>
          </P-FloatLabel>
        </div>

        <!-- Step 3: Players -->
        <div v-show="currentStep === 3" class="step-content">
          <div class="step-header">
            <h2>Jogadores ({{ TOURNAMENT.MIN_PLAYERS }} a {{ TOURNAMENT.MAX_PLAYERS }})</h2>
          </div>

          <div v-for="player in playerForms" :key="player.id" class="player-fieldset">
            <PlayerForm
              :index="playerForms.indexOf(player)"
              :showLegend="true"
              :showDelete="true"
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
        <div v-show="currentStep === 4" class="step-content">
          <h2>Equipa Técnica (Opcional)</h2>
          <p class="optional-note">Todos os campos são opcionais</p>

          <div class="staff-grid">
            <StaffMemberForm
              id="coach"
              legend="Treinador Principal"
              v-model="staffForms.main_coach.data"
              v-model:enabled="staffForms.main_coach.enabled"
              v-model:files="staffForms.main_coach.files"
            />
            <StaffMemberForm
              id="assistantCoach"
              legend="Treinador Adjunto"
              v-model="staffForms.assistant_coach.data"
              v-model:enabled="staffForms.assistant_coach.enabled"
              v-model:files="staffForms.assistant_coach.files"
            />
            <StaffMemberForm
              id="deputy1"
              legend="Primeiro Delegado"
              v-model="staffForms.first_deputy.data"
              v-model:enabled="staffForms.first_deputy.enabled"
              v-model:files="staffForms.first_deputy.files"
            />
            <StaffMemberForm
              id="deputy2"
              legend="Segundo Delegado"
              v-model="staffForms.second_deputy.data"
              v-model:enabled="staffForms.second_deputy.enabled"
              v-model:files="staffForms.second_deputy.files"
            />
            <StaffMemberForm
              id="physio"
              legend="Fisioterapeuta"
              v-model="staffForms.physiotherapist.data"
              v-model:enabled="staffForms.physiotherapist.enabled"
              v-model:files="staffForms.physiotherapist.files"
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
            <span v-if="submitting" class="material-symbols-outlined">progress_activity</span>
            <span v-else class="material-symbols-outlined">check</span>
            <span v-if="submitting && registrationProgress.step">{{ registrationProgress.step }}</span>
            <span v-else>Submeter</span>
          </P-Button>
        </div>
      </div>
    </div>

    <P-Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useTournamentStore } from "@stores/tournaments";
import { TOURNAMENT } from "@/constants";
import { isUnderAge } from "@/utils";
import { useRegistrationDeadline } from "@composables/useRegistrationDeadline";
import PlayerForm from "@components/forms/PlayerForm.vue";
import StaffMemberForm from "@components/forms/StaffMemberForm.vue";
import {
  registerTeamStart,
  registerAddStaff,
  registerAddPlayer,
  registerComplete,
  cancelRegistration,
  type RegisterStaffData,
  type RegisterPlayerData,
} from "@router/backend/services/team";

const citizenCardTooltipVisible = ref(false);
const proofOfResidenceTooltipVisible = ref(false);

interface PlayerFormData {
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

interface StaffMemberData {
  name: string;
  birth_date: Date | null;
  address: string;
  place_of_birth: string;
  fiscal_number: string;
}

interface StaffFiles {
  citizenCard?: File | null;
}

interface PlayerFormEntry {
  id: string;
  data: PlayerFormData;
  files: PlayerFiles;
}

interface StaffFormEntry {
  enabled: boolean;
  data: StaffMemberData;
  files: StaffFiles;
}

const currentStep = ref(0);
const privacyAccepted = ref(false);
const submitting = ref(false);
const registrationProgress = ref({ current: 0, total: 0, step: "" });
let currentTeamId: string | null = null;

const steps = [
  { label: "Instruções" },
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
  assistant_coach: StaffFormEntry;
  physiotherapist: StaffFormEntry;
  first_deputy: StaffFormEntry;
  second_deputy: StaffFormEntry;
}>({
  main_coach: { enabled: false, data: createEmptyStaffMember(), files: { citizenCard: null } },
  assistant_coach: { enabled: false, data: createEmptyStaffMember(), files: { citizenCard: null } },
  physiotherapist: { enabled: false, data: createEmptyStaffMember(), files: { citizenCard: null } },
  first_deputy: { enabled: false, data: createEmptyStaffMember(), files: { citizenCard: null } },
  second_deputy: { enabled: false, data: createEmptyStaffMember(), files: { citizenCard: null } }
});

const toast = useToast();
const router = useRouter();
const { isOpen: isRegistrationOpen } = useRegistrationDeadline();

const playerForms = reactive<PlayerFormEntry[]>([]);

const tournamentStore = useTournamentStore();

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
    federation_exams_up_to_date: false,
    is_goalkeeper: false
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

function goToPrivacy() {
  router.push("/privacy");
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
  if (currentStep.value === 0 && !privacyAccepted.value) {
    toast.add({ severity: "error", summary: "Erro", detail: "Tem de aceitar a Política de Privacidade para continuar", life: 3000 });
    return;
  }
  if (currentStep.value === 1 && (!teamData.name || !teamData.tournament)) {
    toast.add({ severity: "error", summary: "Erro", detail: "Preencha o nome da equipa e selecione o torneio", life: 3000 });
    return;
  }
  if (currentStep.value === 2 && (!teamData.responsible_name || !teamData.responsible_email || !teamData.responsible_phone)) {
    toast.add({ severity: "error", summary: "Erro", detail: "Preencha todos os campos do responsável", life: 3000 });
    return;
  }
  if (currentStep.value === 3) {
    if (playerForms.length < TOURNAMENT.MIN_PLAYERS) {
      toast.add({ severity: "error", summary: "Erro", detail: `É necessário um mínimo de ${TOURNAMENT.MIN_PLAYERS} jogadores`, life: 3000 });
      return;
    }
    for (let i = 0; i < playerForms.length; i++) {
      const player = playerForms[i];
      const errors: string[] = [];
      if (!player.data.name) errors.push(`Jogador ${i + 1}: Nome é obrigatório`);
      if (!player.data.birth_date) errors.push(`Jogador ${i + 1}: Data de Nascimento é obrigatória`);
      if (!player.data.fiscal_number) errors.push(`Jogador ${i + 1}: NIF é obrigatório`);
      if (!player.data.place_of_birth) errors.push(`Jogador ${i + 1}: Local de Nascimento é obrigatório`);
      if (!player.data.address) errors.push(`Jogador ${i + 1}: Morada é obrigatória`);
      if (player.data.is_federated && !player.data.federation_team) {
        errors.push(`Jogador ${i + 1}: Equipa Federada é obrigatória`);
      }
      if (!player.files.citizenCard) errors.push(`Jogador ${i + 1}: Cartão de Cidadão é obrigatório`);
      if (!player.files.proofOfResidency) errors.push(`Jogador ${i + 1}: Comprovativo de Residência é obrigatório`);
      if (isUnderAge(player.data.birth_date, TOURNAMENT.AGE_FOR_ENROLLMENT, TOURNAMENT.TOURNAMENT_START_DATE)) {
        errors.push(`Jogador ${i + 1}: Tem de ter pelo menos ${TOURNAMENT.AGE_FOR_ENROLLMENT} anos em ${TOURNAMENT.TOURNAMENT_START_DATE.toLocaleDateString('pt-PT')}`);
      } else if (isUnderAge(player.data.birth_date, TOURNAMENT.AGE_REQUIRES_AUTHORIZATION, TOURNAMENT.TOURNAMENT_START_DATE) && !player.files.authorization) {
        errors.push(`Jogador ${i + 1}: Autorização é obrigatória (menor de ${TOURNAMENT.AGE_REQUIRES_AUTHORIZATION} anos)`);
      }
      if (errors.length > 0) {
        toast.add({ severity: "error", summary: "Erro", detail: errors[0], life: 5000 });
        return;
      }
    }
  }
  if (currentStep.value === 4) {
    const staffTypes = [
      { key: "main_coach", label: "Treinador Principal", form: staffForms.main_coach },
      { key: "assistant_coach", label: "Treinador Adjunto", form: staffForms.assistant_coach },
      { key: "physiotherapist", label: "Fisioterapeuta", form: staffForms.physiotherapist },
      { key: "first_deputy", label: "Primeiro Delegado", form: staffForms.first_deputy },
      { key: "second_deputy", label: "Segundo Delegado", form: staffForms.second_deputy },
    ];
    for (const staff of staffTypes) {
      if (staff.form.enabled) {
        const errors: string[] = [];
        if (!staff.form.data.name) errors.push(`${staff.label}: Nome é obrigatório`);
        if (!staff.form.data.birth_date) errors.push(`${staff.label}: Data de Nascimento é obrigatória`);
        if (!staff.form.data.fiscal_number) errors.push(`${staff.label}: NIF é obrigatório`);
        if (!staff.form.files?.citizenCard) errors.push(`${staff.label}: Cartão de Cidadão é obrigatório`);
      }
    }
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
  submitting.value = true;
  currentTeamId = null;

  const staffCount = [
    staffForms.main_coach,
    staffForms.assistant_coach,
    staffForms.physiotherapist,
    staffForms.first_deputy,
    staffForms.second_deputy,
  ].filter(s => s.enabled && s.data.name).length;
  const totalSteps = 1 + staffCount + playerForms.length + 1;
  let currentStep = 0;

  const updateProgress = (step: string) => {
    currentStep++;
    registrationProgress.value = { current: currentStep, total: totalSteps, step };
  };

  const showError = (detail: string) => {
    toast.add({ severity: "error", summary: "Erro", detail, life: 5000 });
  };

  try {
    updateProgress("A criar equipa...");
    const teamResponse = await registerTeamStart({
      tournament: teamData.tournament,
      name: teamData.name,
      responsible_name: teamData.responsible_name,
      responsible_email: teamData.responsible_email,
      responsible_phone: teamData.responsible_phone,
    });

    if (teamResponse.status !== 201) {
      showError("Falha ao criar equipa");
      return;
    }

    if (!('id' in teamResponse.data)) {
      showError("Falha ao criar equipa");
      return;
    }

    currentTeamId = teamResponse.data.id;

    const staffTypes = [
      { key: "main_coach", type: "Coach" as const, form: staffForms.main_coach },
      { key: "assistant_coach", type: "AssistantCoach" as const, form: staffForms.assistant_coach },
      { key: "physiotherapist", type: "Physiotherapist" as const, form: staffForms.physiotherapist },
      { key: "first_deputy", type: "GameDeputy" as const, form: staffForms.first_deputy },
      { key: "second_deputy", type: "GameDeputy" as const, form: staffForms.second_deputy },
    ];

    for (const staff of staffTypes) {
      if (staff.form.enabled && staff.form.data.name && currentTeamId) {
        const citizenCard = staff.form.files?.citizenCard;
        if (!staff.form.data.name ||
            !staff.form.data.birth_date ||
            !staff.form.data.fiscal_number ||
            !citizenCard ||
            !(citizenCard instanceof File)) {
          showError(`Preencha todos os campos do ${staff.key === "main_coach" ? "treinador" : staff.key === "assistant_coach" ? "treinador adjunto" : staff.key === "physiotherapist" ? "fisioterapeuta" : "delegado"}`);
          return;
        }

        updateProgress(`A adicionar ${staff.key === "main_coach" ? "treinador" : staff.key === "assistant_coach" ? "treinador adjunto" : staff.key === "physiotherapist" ? "fisioterapeuta" : "delegado"}...`);

        const staffData: RegisterStaffData = {
          team_id: currentTeamId,
          staff_type: staff.type,
          name: staff.form.data.name,
          birth_date: staff.form.data.birth_date?.toISOString() || "",
          address: staff.form.data.address,
          place_of_birth: staff.form.data.place_of_birth,
          fiscal_number: staff.form.data.fiscal_number,
          files: {
            citizenCard: staff.form.files?.citizenCard!,
          },
        };

        await registerAddStaff(staffData);
      }
    }

    for (let i = 0; i < playerForms.length; i++) {
      if (!currentTeamId) break;

      updateProgress(`A adicionar jogador ${i + 1}/${playerForms.length}...`);

      const playerData: RegisterPlayerData = {
        team_id: currentTeamId,
        name: playerForms[i].data.name,
        birth_date: playerForms[i].data.birth_date?.toISOString() || "",
        address: playerForms[i].data.address,
        place_of_birth: playerForms[i].data.place_of_birth,
        fiscal_number: playerForms[i].data.fiscal_number,
        is_federated: playerForms[i].data.is_federated,
        federation_team: playerForms[i].data.federation_team,
        federation_exams_up_to_date: playerForms[i].data.federation_exams_up_to_date,
        files: {
          citizenCard: playerForms[i].files.citizenCard || undefined,
          proofOfResidency: playerForms[i].files.proofOfResidency || undefined,
          authorization: playerForms[i].files.authorization || undefined,
        },
      };

      await registerAddPlayer(playerData);
    }

    if (currentTeamId) {
      updateProgress("A concluir registo...");
      await registerComplete(currentTeamId);
    }

    toast.add({ severity: "success", summary: "Sucesso", detail: "Equipa registada com sucesso", life: 3000 });
    setTimeout(() => {
      router.push("/");
    }, 1500);

  } catch (error: unknown) {
    console.error(error);
    const err = error as { response?: { data?: { detail?: string } } };
    showError(err.response?.data?.detail || "Erro durante o registo");

    if (currentTeamId) {
      try {
        await cancelRegistration(currentTeamId);
      } catch {
        // ignore cancellation errors
      }
    }
  } finally {
    submitting.value = false;
    registrationProgress.value = { current: 0, total: 0, step: "" };
    currentTeamId = null;
  }
}
</script>

<style scoped>
.team-registration {
  padding: 1rem;
  width: 100%;
  max-width: 90%;
  margin: 0 auto;
  background: var(--color-stone-50);
}

@media (min-width: 640px) {
  .team-registration {
    padding: 1.5rem;
    max-width: 85%;
  }
}

@media (min-width: 1024px) {
  .team-registration {
    padding: 2rem;
    max-width: 80%;
  }
}

@media (min-width: 1536px) {
  .team-registration {
    padding: 2rem;
    max-width: 1400px;
  }
}

.registration-header {
  margin-bottom: 1rem;
}

.registration-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-stone-900);
  margin: 0 0 0.25rem 0;
}

.registration-header p {
  color: var(--color-stone-500);
  margin: 0;
  font-size: 0.875rem;
}

.form-card {
  background: white;
  border: 1px solid var(--color-stone-200);
  border-radius: 12px;
  padding: 1rem;
  width: 100%;
}

@media (min-width: 768px) {
  .form-card {
    padding: 1.5rem;
  }
}

@media (min-width: 1280px) {
  .form-card {
    padding: 2rem;
    border-radius: 16px;
  }
}

.form-container {
  margin-top: 1rem;
}

.registration-progress {
  margin-top: 1rem;
  padding: 0.75rem;
  background: var(--p-surface-50);
  border-radius: 8px;
}

.registration-progress .p-progressbar {
  height: 8px;
}

.progress-text {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-stone-500);
  text-align: center;
}

.step-content h2 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-stone-900);
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
  color: var(--color-stone-500);
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

@media (min-width: 768px) {
  .staff-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .staff-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.player-fieldset {
  position: relative;
  margin-bottom: 0.75rem;
  padding: 1rem;
  background: var(--p-surface-50);
  border: 1px solid var(--color-stone-200);
  border-radius: 8px;
}

@media (min-width: 1024px) {
  .player-fieldset {
    padding: 1.5rem;
  }
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
  border-top: 1px solid var(--color-stone-200);
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

.help-tooltip {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-stone-500);
  padding: 0 0.25rem;
  vertical-align: middle;
  display: inline-flex;
  align-items: center;
}

.help-tooltip:hover {
  color: var(--p-primary-600);
}

.help-tooltip .material-symbols-outlined {
  font-size: 1rem;
}

.tooltip-wrapper {
  position: relative;
  display: inline-flex;
}

.tooltip-box {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--p-surface-800);
  color: var(--p-surface-0);
  padding: 0.75rem 2rem 0.75rem 0.75rem;
  border-radius: 6px;
  font-weight: normal;
  font-size: 0.875rem;
  width: max-content;
  max-width: 300px;
  z-index: 100;
  margin-bottom: 0.5rem;
}

.tooltip-box::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: var(--p-surface-800);
}

.tooltip-box .tooltip-close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: none;
  border: none;
  color: var(--p-surface-300);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: flex-start;
}

.tooltip-box .tooltip-close:hover {
  color: var(--p-surface-0);
}

.tooltip-box .tooltip-close .material-symbols-outlined {
  font-size: 1rem;
}
</style>
