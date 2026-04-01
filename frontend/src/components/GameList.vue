<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Jogos" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-DataTable :value="gameStore.games" striped-rows size="small" responsiveLayout="scroll">
      <P-Column header="Torneio">
        <template #body="{ data }">
          <span class="text-sm text-stone-500">{{ getTournamentName(data.tournament) }}</span>
        </template>
      </P-Column>
      <P-Column header="Equipa da Casa">
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <span>🏠</span>
            <span class="font-medium">{{ getTeamName(data.home_call?.team) }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Equipa Visitante">
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <span>✈️</span>
            <span class="font-medium">{{ getTeamName(data.away_call?.team) }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Estado" style="width: 120px">
        <template #body="{ data }">
          <P-Tag :severity="getStatusSeverity(data.status)" :value="getStatusLabel(data.status)" />
        </template>
      </P-Column>
      <P-Column header="Eliminar todos" style="width: 110px">
        <template #body="{ data }">
          <span
            class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
            @click="promptDeleteTournamentGames(data.tournament)"
            v-tooltip.top="'Eliminar todos os jogos deste torneio'"
          >delete_sweep</span>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="gameStore.getGames()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showDeleteConfirm" modal header="Confirmar Eliminação" class="w-11/12 md:w-6/12">
    <p>Tem a certeza que deseja eliminar <strong>todos os {{ tournamentGamesToDelete.length }} jogos</strong> do torneio <strong>{{ getTournamentName(tournamentToDelete) }}</strong>?</p>
    <p class="text-red-600 mt-2 text-sm">Esta ação não pode ser desfeita.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showDeleteConfirm = false">Cancelar</P-Button>
      <P-Button severity="danger" :loading="deleting" @click="confirmDeleteAll">Eliminar todos</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { useGameStore } from "@stores/games";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { GameStatus } from "@router/backend/services/game/types";

const enabled = defineModel<boolean>();
const toast = useToast();
const gameStore = useGameStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const showDeleteConfirm = ref(false);
const tournamentToDelete = ref("");
const deleting = ref(false);

const tournamentGamesToDelete = computed(() =>
  gameStore.games.filter(g => g.tournament === tournamentToDelete.value)
);

function getTeamName(teamId: string): string {
  return teamStore.teams.find(t => t.id === teamId)?.name ?? "N/A";
}

function getTournamentName(tournamentId: string): string {
  return tournamentStore.tournaments.find(t => t.id === tournamentId)?.name ?? "-";
}

function promptDeleteTournamentGames(tournamentId: string) {
  tournamentToDelete.value = tournamentId;
  showDeleteConfirm.value = true;
}

async function confirmDeleteAll() {
  deleting.value = true;
  let allOk = true;

  for (const game of tournamentGamesToDelete.value) {
    const result = await gameStore.deleteGame(game.id);
    if (!result.success) allOk = false;
  }

  deleting.value = false;
  showDeleteConfirm.value = false;
  tournamentToDelete.value = "";

  if (allOk) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Todos os jogos eliminados", life: 3000 });
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Alguns jogos não foram eliminados", life: 3000 });
  }
}

function getStatusSeverity(status: number) {
  switch (status) {
    case GameStatus.NotStarted: return "secondary";
    case GameStatus.InProgress: return "info";
    case GameStatus.Finished: return "success";
    case GameStatus.Canceled: return "danger";
    default: return "secondary";
  }
}

function getStatusLabel(status: number) {
  switch (status) {
    case GameStatus.NotStarted: return "Por iniciar";
    case GameStatus.InProgress: return "Em progresso";
    case GameStatus.Finished: return "Terminado";
    case GameStatus.Canceled: return "Cancelado";
    default: return "Desconhecido";
  }
}

onMounted(async () => {
  await gameStore.getGames();
  await teamStore.getTeams();
  await tournamentStore.getTournaments();
});
</script>
