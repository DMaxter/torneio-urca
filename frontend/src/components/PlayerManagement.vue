<template>
  <P-Dialog v-model:visible="enabled" modal :header="dialogTitle" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-FloatLabel class="mt-4 mb-4" variant="on">
      <P-Select id="playerTournament" v-model="playerTournament" :options="tournaments" optionLabel="name" optionValue="id" @change="onTournamentChange" fluid />
      <label for="playerTournament">Torneio</label>
    </P-FloatLabel>
    <PlayerForm 
      :modelValue="playerFormData" 
      :files="playerFiles" 
      @update:modelValue="playerFormData = $event" 
      @update:files="playerFiles = $event" 
      :showLegend="false" 
      :showDelete="false" 
      :showTeam="true" 
      :teamOptions="availableTeams" 
    />
    <template #footer>
      <P-Button severity="secondary" @click="enabled = false">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
      <P-Button :loading="loading" @click="savePlayer">
        <span class="material-symbols-outlined">check</span>
        Guardar
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { usePlayerStore } from "@stores/players";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import type { Player } from "@router/backend/services/player/types";
import { CreateAdminPlayer } from "@router/backend/services/player/types";
import { isUnderAge } from "@/utils";
import { TOURNAMENT } from "@/constants";
import PlayerForm from "./forms/PlayerForm.vue";

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

function createEmptyPlayerData(): PlayerFormData {
  return {
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
  };
}

function createEmptyPlayerFiles(): PlayerFiles {
  return {
    citizenCard: null,
    proofOfResidency: null,
    authorization: null
  };
}

const toast = useToast();
const enabled = defineModel<boolean>();

const props = defineProps<{
  player?: Player;
}>();

const playerStore = usePlayerStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const loading = ref(false);
const playerFormData = ref(createEmptyPlayerData());
const playerFiles = ref(createEmptyPlayerFiles());
const playerTournament = ref("");

const dialogTitle = computed(() => props.player ? "Editar Jogador" : "Criar Jogador");

const tournaments = computed(() => tournamentStore.tournaments);
const availableTeams = computed(() => {
  if (!playerTournament.value) return [];
  return teamStore.teams.filter(t => t.tournament === playerTournament.value);
});
const cannotEnroll = computed(() => isUnderAge(playerFormData.value.birth_date, TOURNAMENT.AGE_FOR_ENROLLMENT, TOURNAMENT.TOURNAMENT_START_DATE));
  const isMinor = computed(() => isUnderAge(playerFormData.value.birth_date, TOURNAMENT.AGE_REQUIRES_AUTHORIZATION, TOURNAMENT.TOURNAMENT_START_DATE));

onMounted(async () => {
  if (tournamentStore.tournaments.length === 0) {
    await tournamentStore.getTournaments();
  }
  if (teamStore.teams.length === 0) {
    await teamStore.getTeams();
  }
});

watch(() => enabled.value, (open) => {
  if (open) {
    openDialog();
  }
}, { immediate: true });

function onTournamentChange() {
  playerFormData.value = { ...playerFormData.value, team: "" };
}

function openDialog() {
  if (props.player) {
    const team = teamStore.teams.find(t => t.players.includes(props.player!.id));
    playerTournament.value = team?.tournament ?? "";
    playerFormData.value = {
      team: team?.id ?? "",
      name: props.player.name,
      birth_date: props.player.birth_date ? new Date(props.player.birth_date) : null,
      address: props.player.address ?? "",
      place_of_birth: props.player.place_of_birth ?? "",
      fiscal_number: props.player.fiscal_number,
      is_federated: props.player.is_federated,
      federation_team: props.player.federation_team ?? "",
      federation_exams_up_to_date: props.player.federation_exams_up_to_date,
      is_goalkeeper: props.player.is_goalkeeper
    };
  } else {
    playerTournament.value = "";
    playerFormData.value = createEmptyPlayerData();
  }
  playerFiles.value = createEmptyPlayerFiles();
}

async function savePlayer() {
  if (!playerFormData.value.name || !playerFormData.value.birth_date || !playerFormData.value.team || !playerTournament.value) {
    toast.add({ severity: "warn", summary: "Campos obrigatórios", detail: "Preencha todos os campos obrigatórios", life: 3000 });
    return;
  }
  
  if (!props.player) {
    if (!playerFiles.value.citizenCard) {
      toast.add({ severity: "warn", summary: "Documento obrigatório", detail: "É necessário enviar o Cartão de Cidadão", life: 3000 });
      return;
    }
    if (!playerFiles.value.proofOfResidency) {
      toast.add({ severity: "warn", summary: "Documento obrigatório", detail: "É necessário enviar o Comprovativo de Residência", life: 3000 });
      return;
    }
    if (cannotEnroll.value) {
      toast.add({ severity: "error", summary: "Idade mínima", detail: `Tem de ter pelo menos ${TOURNAMENT.AGE_FOR_ENROLLMENT} anos em ${TOURNAMENT.TOURNAMENT_START_DATE.toLocaleDateString('pt-PT')}`, life: 3000 });
      return;
    }
    if (isMinor.value && !playerFiles.value.authorization) {
      toast.add({ severity: "warn", summary: "Autorização necessária", detail: `É necessário enviar a autorização para menores de ${TOURNAMENT.AGE_REQUIRES_AUTHORIZATION} anos`, life: 3000 });
      return;
    }
  }

  loading.value = true;

  const playerData: CreateAdminPlayer = {
    name: playerFormData.value.name,
    birth_date: playerFormData.value.birth_date,
    team: playerFormData.value.team,
    tournament: playerTournament.value,
    fiscal_number: playerFormData.value.fiscal_number,
    address: playerFormData.value.address,
    place_of_birth: playerFormData.value.place_of_birth,
    is_federated: playerFormData.value.is_federated,
    federation_team: playerFormData.value.federation_team,
    federation_exams_up_to_date: playerFormData.value.federation_exams_up_to_date,
    is_goalkeeper: playerFormData.value.is_goalkeeper,
  };

let result;
  if (props.player) {
    result = await playerStore.updatePlayer(props.player.id, playerData);
  } else {
    result = await playerStore.createAdminPlayer(
      playerData,
      playerFiles.value.citizenCard ?? undefined,
      playerFiles.value.proofOfResidency ?? undefined,
      playerFiles.value.authorization ?? undefined
    );
  }
   
  loading.value = false;

  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: props.player ? "Jogador atualizado" : "Jogador criado com sucesso", life: 3000 });
    await teamStore.getTeams();
    enabled.value = false;
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Erro ao guardar jogador. Verifique os dados e tente novamente.", life: 3000 });
  }
}
</script>