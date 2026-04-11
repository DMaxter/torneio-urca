<template>
  <div class="game-calls p-4 w-full mx-auto bg-stone-50 md:p-6">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-stone-900 mb-1 md:text-2xl">Chamada de Jogadores</h1>
        <p v-if="selectedGame" class="text-stone-500 text-sm md:text-base">
          {{ getTournamentName(selectedGame.tournament) }} - {{ getPhaseLabel(selectedGame.phase) }} - {{ getTeamName(selectedGame.home_call?.team) }} vs {{ getTeamName(selectedGame.away_call?.team) }}
        </p>
      </div>
      <P-Button severity="secondary" @click="router.push('/admin')">
        <span class="material-symbols-outlined">arrow_back</span>
        <span class="hidden sm:inline">Voltar</span>
      </P-Button>
    </div>

    <div class="bg-white border border-stone-300 rounded-xl p-4 md:p-6">
      <div v-if="selectedGame" class="space-y-6">
        <div class="flex flex-col md:flex-row gap-6">
          <!-- Home Team -->
          <div class="flex-1 border border-stone-200 rounded-lg overflow-hidden">
            <div class="bg-blue-50 px-3 py-2 border-b border-stone-200">
              <span class="font-semibold text-blue-800">Equipa da Casa - {{ getTeamName(selectedGame.home_call?.team) }}</span>
            </div>
            <div class="p-3">
              <div v-if="selectedGame.home_call" class="space-y-4">
                <div class="space-y-2">
                  <div
                    v-for="playerEntry in selectedGame.home_call.players"
                    :key="playerEntry.player"
                    class="flex items-center gap-2"
                  >
                    <span class="text-sm text-stone-600 flex-1 truncate">{{ getPlayerName(playerEntry.player, selectedGame.home_call.team) }}</span>
                    <P-InputNumber
                      v-model="playerEntry.number"
                      :min="1"
                      :max="99"
                      placeholder="#"
                      class="w-16"
                    />
                    <P-Button
                      severity="danger"
                      text
                      rounded
                      size="small"
                      @click="removePlayer('home', playerEntry.player)"
                    >
                      <span class="material-symbols-outlined text-sm text-red-600">delete</span>
                    </P-Button>
                  </div>
                </div>

                <div class="pt-4 border-t border-stone-100 space-y-3">
                  <div class="flex gap-2">
                    <P-Select
                      v-model="selectedPlayerToAddHome"
                      :options="getAvailablePlayers('home')"
                      optionLabel="name"
                      optionValue="id"
                      placeholder="Adicionar jogador..."
                      filter
                      class="flex-1"
                    />
                    <P-Button
                      severity="secondary"
                      @click="addIndividualPlayer('home')"
                      :disabled="!selectedPlayerToAddHome"
                    >
                      <span class="material-symbols-outlined">add</span>
                    </P-Button>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <P-Button
                      severity="info"
                      text
                      size="small"
                      @click="addAllRemainingPlayers('home')"
                      :disabled="getAvailablePlayers('home').length === 0"
                    >
                      <span class="material-symbols-outlined">group_add</span>
                      <span class="ml-1">Adicionar Restantes</span>
                    </P-Button>
                    <P-Button
                      severity="warn"
                      text
                      size="small"
                      @click="confirmReset('home')"
                    >
                      <span class="material-symbols-outlined">restart_alt</span>
                      <span class="ml-1 text-xs">Reset</span>
                    </P-Button>
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-stone-400">Sem chamada definida</p>
            </div>
          </div>

          <!-- Away Team -->
          <div class="flex-1 border border-stone-200 rounded-lg overflow-hidden">
            <div class="bg-red-50 px-3 py-2 border-b border-stone-200">
              <span class="font-semibold text-red-800">Equipa Visitante - {{ getTeamName(selectedGame.away_call?.team) }}</span>
            </div>
            <div class="p-3">
              <div v-if="selectedGame.away_call" class="space-y-4">
                <div class="space-y-2">
                  <div
                    v-for="playerEntry in selectedGame.away_call.players"
                    :key="playerEntry.player"
                    class="flex items-center gap-2"
                  >
                    <span class="text-sm text-stone-600 flex-1 truncate">{{ getPlayerName(playerEntry.player, selectedGame.away_call.team) }}</span>
                    <P-InputNumber
                      v-model="playerEntry.number"
                      :min="1"
                      :max="99"
                      placeholder="#"
                      class="w-16"
                    />
                    <P-Button
                      severity="danger"
                      text
                      rounded
                      size="small"
                      @click="removePlayer('away', playerEntry.player)"
                    >
                      <span class="material-symbols-outlined text-sm text-red-600">delete</span>
                    </P-Button>
                  </div>
                </div>

                <div class="pt-4 border-t border-stone-100 space-y-3">
                  <div class="flex gap-2">
                    <P-Select
                      v-model="selectedPlayerToAddAway"
                      :options="getAvailablePlayers('away')"
                      optionLabel="name"
                      optionValue="id"
                      placeholder="Adicionar jogador..."
                      filter
                      class="flex-1"
                    />
                    <P-Button
                      severity="secondary"
                      @click="addIndividualPlayer('away')"
                      :disabled="!selectedPlayerToAddAway"
                    >
                      <span class="material-symbols-outlined">add</span>
                    </P-Button>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <P-Button
                      severity="info"
                      text
                      size="small"
                      @click="addAllRemainingPlayers('away')"
                      :disabled="getAvailablePlayers('away').length === 0"
                    >
                      <span class="material-symbols-outlined">group_add</span>
                      <span class="ml-1">Adicionar Restantes</span>
                    </P-Button>
                    <P-Button
                      severity="warn"
                      text
                      size="small"
                      @click="confirmReset('away')"
                    >
                      <span class="material-symbols-outlined">restart_alt</span>
                      <span class="ml-1 text-xs">Reset</span>
                    </P-Button>
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-stone-400">Sem chamada definida</p>
            </div>
          </div>
        </div>

        <div v-if="saving" class="flex items-center gap-2 text-sm text-stone-500">
          <span class="material-symbols-outlined animate-spin text-lg">sync</span>
          A guardar...
        </div>
        <div v-else class="flex gap-2">
          <P-Button severity="secondary" @click="submitCall">
            <span class="material-symbols-outlined">save</span>
            <span class="ml-1">Guardar</span>
          </P-Button>
          <P-Button severity="success" @click="showConfirmDialog = true">
            <span class="material-symbols-outlined">check</span>
            <span class="ml-1">Confirmar</span>
          </P-Button>
          <P-Button severity="danger" @click="showCancelDialog = true">
            <span class="material-symbols-outlined">close</span>
            <span class="ml-1">Cancelar Jogo</span>
          </P-Button>
        </div>
      </div>

      <div v-else-if="selectedGameId && !selectedGame" class="text-center py-8 text-stone-400">
        <span class="material-symbols-outlined text-4xl mb-2">sports_soccer</span>
        <p>Jogo sem chamadas</p>
      </div>
    </div>
  </div>

  <P-Dialog v-model:visible="showConfirmDialog" modal header="Confirmar Chamada" class="w-11/12 md:w-6/12">
    <p>Tem a certeza que deseja fechar a chamada?</p>
    <p class="text-orange-600 mt-2 text-sm">Esta ação não pode ser desfeita. A chamada não poderá ser alterada depois de confirmada.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showConfirmDialog = false">Cancelar</P-Button>
      <P-Button severity="success" :loading="saving" @click="closeAndConfirmCall">Confirmar</P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showCancelDialog" modal header="Cancelar Jogo" class="w-11/12 md:w-6/12">
    <p>Tem a certeza que deseja cancelar este jogo?</p>
    <p class="text-red-600 mt-2 text-sm">Esta ação não pode ser desfeita.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showCancelDialog = false">Voltar</P-Button>
      <P-Button severity="danger" :loading="saving" @click="cancelGame">Cancelar Jogo</P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showResetDialog" modal header="Reiniciar Chamada" class="w-11/12 md:w-6/12">
    <p>Deseja mesmo reiniciar esta chamada?</p>
    <p class="text-orange-600 mt-2 text-sm">Todos os números de camisola atribuídos serão perdidos e a chamada será preenchida com todos os jogadores da equipa.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showResetDialog = false">Cancelar</P-Button>
      <P-Button severity="warn" @click="handleReset">Confirmar Reinício</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useGameStore } from "@stores/games";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { usePlayerStore } from "@stores/players";
import * as gameService from "@router/backend/services/game";
import type { Game } from "@router/backend/services/game/types";
import { GameStatus } from "@router/backend/services/game/types";
import { http } from "@router/backend/api";

const router = useRouter();
const route = useRoute();
const toast = useToast();
const gameStore = useGameStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const playerStore = usePlayerStore();

const selectedTournamentId = ref<string>("");
const selectedGameId = ref<string>("");
const selectedGame = ref<Game | null>(null);
const saving = ref(false);
const showConfirmDialog = ref(false);
const showCancelDialog = ref(false);
const showResetDialog = ref(false);
const resetSide = ref<"home" | "away" | null>(null);

const selectedPlayerToAddHome = ref<string | null>(null);
const selectedPlayerToAddAway = ref<string | null>(null);

function getAvailablePlayers(side: "home" | "away") {
  const game = selectedGame.value;
  if (!game) return [];

  const call = side === "home" ? game.home_call : game.away_call;
  if (!call) return [];

  const teamPlayers = playerStore.players.filter(p => p.team === call.team);
  const playersInCall = new Set(call.players.map(p => p.player));

  return teamPlayers
    .filter(p => !playersInCall.has(p.id))
    .sort((a, b) => a.name.localeCompare(b.name));
}

function addIndividualPlayer(side: "home" | "away") {
  const playerId = side === "home" ? selectedPlayerToAddHome.value : selectedPlayerToAddAway.value;
  if (!playerId || !selectedGame.value) return;

  const call = side === "home" ? selectedGame.value.home_call : selectedGame.value.away_call;
  if (!call) return;

  call.players.push({ player: playerId, number: null });

  if (side === "home") selectedPlayerToAddHome.value = null;
  else selectedPlayerToAddAway.value = null;
}

function addAllRemainingPlayers(side: "home" | "away") {
  const available = getAvailablePlayers(side);
  const call = side === "home" ? selectedGame.value?.home_call : selectedGame.value?.away_call;
  if (!call) return;

  available.forEach(p => {
    call.players.push({ player: p.id, number: null });
  });
}

function confirmReset(side: "home" | "away") {
  resetSide.value = side;
  showResetDialog.value = true;
}

async function handleReset() {
  if (!resetSide.value) return;
  await populateCall(resetSide.value);
  showResetDialog.value = false;
  resetSide.value = null;
}

function getTeamName(teamId: string | undefined) {
  if (!teamId) return "";
  return teamStore.teams.find(t => t.id === teamId)?.name || teamId;
}

function getTournamentName(tournamentId: string) {
  return tournamentStore.tournaments.find(t => t.id === tournamentId)?.name || tournamentId;
}

function getPhaseLabel(phase: string) {
  switch (phase) {
    case "group": return "Fase de Grupos";
    case "quarter_final": return "Quartos de Final";
    case "semi_final": return "Meias Finais";
    case "final": return "Final";
    case "third_place": return "3º/4º Lugar";
    default: return phase;
  }
}

function getPlayerName(playerId: string, teamId: string | undefined) {
  if (!teamId) return playerId;
  const player = playerStore.players.find(p => p.id === playerId && p.team === teamId);
  return player?.name || playerId;
}

async function removePlayer(side: "home" | "away", playerId: string) {
  if (!selectedGame.value) return;

  const call = side === "home"
    ? selectedGame.value.home_call
    : selectedGame.value.away_call;
  if (!call) return;

  call.players = call.players.filter(p => p.player !== playerId);
}

async function submitCall() {
  const game = selectedGame.value;
  if (!game) return;

  if (!game.home_call || !game.away_call) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Jogo sem chamadas", life: 3000 });
    return;
  }

  saving.value = true;

  try {
    await gameService.updateGameCall(game.home_call.id, game.home_call.players);
    await gameService.updateGameCall(game.away_call.id, game.away_call.players);

    gameStore.games = gameStore.games.map(g =>
      g.id === game.id ? game : g
    );

    toast.add({ severity: "success", summary: "Sucesso", detail: "Chamada guardada com sucesso", life: 3000 });
  } catch {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível guardar a chamada", life: 3000 });
  } finally {
    saving.value = false;
  }
}

async function closeAndConfirmCall() {
  const game = selectedGame.value;
  if (!game) return;

  if (!game.home_call || !game.away_call) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Jogo sem chamadas", life: 3000 });
    return;
  }

  saving.value = true;

  try {
    await gameService.updateGameCall(game.home_call.id, game.home_call.players);
    await gameService.updateGameCall(game.away_call.id, game.away_call.players);

    await gameService.confirmGameCalls(game.id);

    toast.add({ severity: "success", summary: "Sucesso", detail: "Chamada confirmada com sucesso", life: 3000 });
    router.push("/admin");
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: { error?: string } } } };
    const msg = err.response?.data?.detail?.error || "Erro ao confirmar chamadas";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  } finally {
    saving.value = false;
  }
}

async function cancelGame() {
  const game = selectedGame.value;
  if (!game) return;

  saving.value = true;

  try {
    await gameService.updateGameStatus(game.id, GameStatus.Canceled);

    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogo cancelado", life: 3000 });
    router.push("/admin");
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: { error?: string } } } };
    const msg = err.response?.data?.detail?.error || "Erro ao cancelar jogo";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  } finally {
    saving.value = false;
  }
}

async function populateCall(side: "home" | "away") {
  const game = selectedGame.value;
  if (!game) return;

  const callId = side === "home" ? game.home_call?.id : game.away_call?.id;
  if (!callId) return;

  try {
    const response = await http.patch(`/games/calls/${callId}/populate`);
    if (response.status === 200) {
      const updatedCall = response.data;
      if (side === "home" && selectedGame.value?.home_call) {
        selectedGame.value.home_call.players = updatedCall.players;
      } else if (selectedGame.value?.away_call) {
        selectedGame.value.away_call.players = updatedCall.players;
      }
    }
  } catch {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível popular a chamada", life: 3000 });
  }
}

onMounted(async () => {
  const queryTournament = route.query.tournament as string;
  const queryGame = route.query.game as string;

  if (!queryTournament || !queryGame) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Selecione um jogo primeiro", life: 3000 });
    router.push("/admin");
    return;
  }

  await gameStore.getGames();
  await teamStore.getTeams();
  await tournamentStore.getTournaments();
  await playerStore.getPlayers();

  selectedTournamentId.value = queryTournament;
  selectedGameId.value = queryGame;
  const game = gameStore.games.find(g => g.id === queryGame);
  if (game) {
    selectedGame.value = JSON.parse(JSON.stringify(game));
  }
});
</script>

<style scoped>
:deep(.p-inputnumber-input) {
  width: 2.5rem;
}
</style>
