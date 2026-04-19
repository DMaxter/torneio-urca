<template>
  <P-Dialog v-model:visible="enabled" modal header="Gestão de Jogos" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <div class="flex flex-col gap-4">
       <div class="flex flex-wrap gap-2 items-center">
         <P-Select
           v-model="selectedTournamentId"
           :options="tournaments"
           optionLabel="name"
           optionValue="id"
           placeholder="Filtrar por torneio..."
           class="w-full sm:w-64"
           showClear
         />
         <P-Select
           v-model="selectedStatusFilter"
           :options="statusFilterOptions"
           optionLabel="label"
           optionValue="value"
           placeholder="Estado..."
           class="w-full sm:w-40"
           showClear
         />
       </div>

      <P-DataTable :value="sortedGames" striped-rows size="small" responsiveLayout="scroll" :loading="loading">
        <P-Column>
          <template #header>
            <div class="w-full text-center font-semibold">Data</div>
          </template>
          <template #body="{ data }">
            <div class="text-center">{{ formatDateTime(data.scheduled_date) }}</div>
          </template>
        </P-Column>
        <P-Column>
          <template #header>
            <div class="w-full text-center font-semibold">Torneio</div>
          </template>
          <template #body="{ data }">
            <div class="text-center">{{ getTournamentName(data.tournament) }}</div>
          </template>
        </P-Column>
        <P-Column>
          <template #header>
            <div class="w-full text-center font-semibold">Equipas</div>
          </template>
          <template #body="{ data }">
            <div class="flex items-center gap-1 text-sm justify-center">
              <span class="font-medium truncate max-w-24">{{ getGameTeamName(data, 'home') }}</span>
              <span class="text-stone-400">vs</span>
              <span class="font-medium truncate max-w-24">{{ getGameTeamName(data, 'away') }}</span>
            </div>
          </template>
        </P-Column>
        <P-Column>
          <template #header>
            <div class="w-full text-center font-semibold">Fase</div>
          </template>
          <template #body="{ data }">
            <div class="text-center">{{ getPhaseLabel(data.phase) }}</div>
          </template>
        </P-Column>
        <P-Column class="w-[120px]">
          <template #header>
            <div class="w-full text-center font-semibold">Estado</div>
          </template>
          <template #body="{ data }">
            <div class="text-center">
              <P-Tag :severity="getStatusSeverity(data.status)" :value="getStatusLabel(data.status)" />
            </div>
          </template>
        </P-Column>
        <P-Column class="w-[200px]">
          <template #header>
            <div class="w-full text-center font-semibold">Ação</div>
          </template>
          <template #body="{ data }">
            <div class="flex flex-wrap gap-1 items-center justify-center">
              <P-Button
                v-if="canStartCalls() && isScheduled(data.status)"
                label="Iniciar Chamadas"
                size="small"
                severity="info"
                @click="startCalls(data.id)"
                v-tooltip.top="'Iniciar o processo de chamadas de jogadores'"
              />
              <P-Button
                v-if="canFillCalls(data.id) && isCallsPending(data.status)"
                label="Preencher Chamadas"
                size="small"
                severity="warn"
                @click="goToGameCallsForGame(data)"
                v-tooltip.top="'Gerir as chamadas de jogadores'"
              />
              <P-Button
                v-if="canStartGameForId(data.id) && isReadyToStart(data.status)"
                label="Iniciar Jogo"
                size="small"
                severity="success"
                @click="startGame(data.id)"
                v-tooltip.top="'Iniciar o jogo'"
              />
              <P-Button
                v-if="canViewLiveGameForId(data.id) && isInProgress(data.status)"
                label="Ver Jogo"
                size="small"
                severity="success"
                @click="viewLiveGame(data.id)"
                v-tooltip.top="'Ver detalhes do jogo'"
              />
              <P-Button
                v-if="canManageGames && isFinished(data.status)"
                label="Ver Resultados"
                size="small"
                severity="secondary"
                @click="viewGameLog(data.id)"
                v-tooltip.top="'Ver registo do jogo'"
              />
            </div>
          </template>
        </P-Column>
      </P-DataTable>

      <p v-if="filteredGames.length === 0 && !loading" class="text-sm text-stone-400 text-center py-4">
        Nenhum jogo encontrado.
      </p>
    </div>

    <template #footer>
      <div class="mt-3 flex gap-2 w-full justify-between">
        <P-Button severity="secondary" @click="enabled = false">
          <span class="material-symbols-outlined">close</span>
          Fechar
        </P-Button>
        <P-Button @click="refresh">
          <span class="material-symbols-outlined">sync</span>
          Atualizar
        </P-Button>
      </div>
    </template>
  </P-Dialog>

  <GameResultDialog v-model:visible="gameResultVisible" :game="selectedDetailedGame" />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useGameStore } from "@stores/games";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { usePlayerStore } from "@stores/players";
import { useAuthStore } from "@stores/auth";
import { GameStatus, type Game } from "@router/backend/services/game/types";
import * as gameService from "@router/backend/services/game";
import { useDateFormatter } from "@/composables/useDateFormatter";
import { useApiErrorToast } from "@/composables/useApiErrorToast";

const authStore = useAuthStore();
const { handleApiError } = useApiErrorToast();
const { formatDateTime } = useDateFormatter();

const enabled = defineModel<boolean>();
const router = useRouter();
const toast = useToast();
const gameStore = useGameStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const playerStore = usePlayerStore();

const loading = ref(false);
const selectedTournamentId = ref<string>("");
const selectedStatusFilter = ref<string>("");

const gameResultVisible = ref(false);
const selectedDetailedGame = ref<Game | null>(null);

const statusFilterOptions = computed(() => [
  { label: "Agendado", value: "Scheduled" },
  { label: "Chamadas Pendentes", value: "CallsPending" },
  { label: "Pronto", value: "ReadyToStart" },
  { label: "Em Progresso", value: "InProgress" },
  { label: "Terminado", value: "Finished" },
  { label: "Cancelado", value: "Canceled" },
]);

const tournaments = computed(() => tournamentStore.tournaments);

const filteredGames = computed(() => {
  let games = gameStore.games;

  if (selectedTournamentId.value) {
    games = games.filter(g => g.tournament === selectedTournamentId.value);
  }

  if (selectedStatusFilter.value) {
    games = games.filter(g => g.status === selectedStatusFilter.value);
  }

  return games;
});

const sortedGames = computed(() => {
  const activeStatuses = ["Scheduled", "CallsPending", "ReadyToStart", "InProgress"];

  const activeGames = [...filteredGames.value]
    .filter(g => activeStatuses.includes(String(g.status)))
    .sort((a, b) => {
      if (!a.scheduled_date) return 1;
      if (!b.scheduled_date) return -1;
      return new Date(a.scheduled_date).getTime() - new Date(b.scheduled_date).getTime();
    });

  const finishedGames = [...filteredGames.value]
    .filter(g => !activeStatuses.includes(String(g.status)))
    .sort((a, b) => {
      if (!a.scheduled_date) return 1;
      if (!b.scheduled_date) return -1;
      return new Date(b.scheduled_date).getTime() - new Date(a.scheduled_date).getTime();
    });

  return [...activeGames, ...finishedGames];
});



function getTeamName(teamId: string): string {
  return teamStore.teams.find(t => t.id === teamId)?.name ?? "N/A";
}

function getGameTeamName(game: Game, side: "home" | "away"): string {
  const call = side === "home" ? game.home_call : game.away_call;
  if (call) return getTeamName(call.team);
  const placeholder = side === "home" ? game.home_placeholder : game.away_placeholder;
  return placeholder ?? "N/A";
}

function getTournamentName(tournamentId: string): string {
  return tournamentStore.tournaments.find(t => t.id === tournamentId)?.name ?? "-";
}

function getPhaseLabel(phase: string) {
  switch (phase) {
    case "group": return "Grupos";
    case "quarter_final": return "Quartos";
    case "semi_final": return "Meias";
    case "final": return "Final";
    case "third_place": return "3º/4º";
    default: return phase;
  }
}

function isScheduled(status: string) { return status === "Scheduled" || status === "0"; }
function isCallsPending(status: string) { return status === "CallsPending" || status === "1"; }
function isReadyToStart(status: string) { return status === "ReadyToStart" || status === "2"; }
function isInProgress(status: string) { return status === "InProgress" || status === "3"; }
function isFinished(status: string) { return status === "Finished" || status === "4"; }

function getStatusSeverity(status: string) {
  const s = String(status);
  if (s === "Scheduled" || s === "0") return "secondary";
  if (s === "CallsPending" || s === "1") return "warn";
  if (s === "ReadyToStart" || s === "2") return "info";
  if (s === "InProgress" || s === "3") return "success";
  if (s === "Finished" || s === "4") return "contrast";
  if (s === "Canceled" || s === "5") return "danger";
  return "secondary";
}

function getStatusLabel(status: string) {
  const s = String(status);
  if (s === "Scheduled" || s === "0") return "Agendado";
  if (s === "CallsPending" || s === "1") return "Chamadas";
  if (s === "ReadyToStart" || s === "2") return "Pronto";
  if (s === "InProgress" || s === "3") return "Em Jogo";
  if (s === "Finished" || s === "4") return "Terminado";
  if (s === "Canceled" || s === "5") return "Cancelado";
  return "?";
}

const canManageGames = computed(() => authStore.canManageGames);

function canStartCalls(): boolean {
  return authStore.canManageGames;
}

function canFillCalls(gameId: string): boolean {
  return authStore.canManageGames || (authStore.canFillGameCalls && authStore.hasCallAccess(gameId));
}



function canStartGameForId(gameId: string): boolean {
  return authStore.canManageGames || (authStore.canManageGameEvents && authStore.hasGameAccess(gameId));
}



function canViewLiveGameForId(gameId: string): boolean {
  return authStore.canManageGames || (authStore.canManageGameEvents && authStore.hasGameAccess(gameId));
}

async function startCalls(gameId: string) {
  try {
    const response = await gameService.updateGameStatus(gameId, GameStatus.CallsPending);
    if (response.status === 200) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Chamadas iniciadas", life: 3000 });
      await refresh();
    }
  } catch (e: unknown) {
    handleApiError(e, "Erro ao iniciar chamadas");
  }
}



async function startGame(gameId: string) {
  try {
    const response = await gameService.updateGameStatus(gameId, GameStatus.InProgress);
    if (response.status === 200) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Jogo iniciado", life: 3000 });
      await refresh();
    }
  } catch (e: unknown) {
    handleApiError(e, "Erro ao iniciar jogo");
  }
}

function goToGameCallsForGame(game: Game) {
  selectedTournamentId.value = game.tournament;
  enabled.value = false;
  router.push({ path: "/game-calls", query: { tournament: game.tournament, game: game.id } });
}

function viewLiveGame(gameId: string) {
  enabled.value = false;
  router.push(`/admin/live-game/${gameId}`);
}

async function viewGameLog(gameId: string) {
  const g = gameStore.games.find(x => x.id === gameId);
  if (g) {
    selectedDetailedGame.value = g;
    gameResultVisible.value = true;
    
    // Refresh data in background to ensure latest events
    const { status, data } = await gameService.getGame(gameId);
    if (status === 200 && data) {
      selectedDetailedGame.value = data as Game;
      // Update global store too
      const idx = gameStore.games.findIndex(x => x.id === gameId);
      if (idx !== -1) gameStore.games[idx] = data as Game;
    }
  }
}

async function refresh() {
  loading.value = true;
  await gameStore.forceGetGames();
  loading.value = false;
}

onMounted(async () => {
  await Promise.all([
    gameStore.getGames(),
    teamStore.getTeams(),
    tournamentStore.getTournaments(),
    playerStore.getPlayers(),
  ]);
});
</script>
