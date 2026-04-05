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
              <div v-if="selectedGame.home_call" class="space-y-2">
                <div v-if="selectedGame.home_call.players.length === 0" class="text-center py-4">
                  <P-Button label="Popular Chamada" icon="group_add" severity="info" @click="populateCall('home')" />
                </div>
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
                    <span class="material-symbols-outlined text-sm">delete</span>
                  </P-Button>
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
              <div v-if="selectedGame.away_call" class="space-y-2">
                <div v-if="selectedGame.away_call.players.length === 0" class="text-center py-4">
                  <P-Button label="Popular Chamada" icon="group_add" severity="info" @click="populateCall('away')" />
                </div>
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
                    <span class="material-symbols-outlined text-sm">delete</span>
                  </P-Button>
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
          <P-Button label="Guardar Chamada" icon="save" severity="secondary" @click="submitCall" />
          <P-Button label="Fechar Chamada" icon="check_circle" severity="success" @click="showConfirmDialog = true" />
          <P-Button label="Cancelar Jogo" icon="close" severity="danger" @click="showCancelDialog = true" />
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
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

function onTournamentChange() {
  selectedGameId.value = "";
  selectedGame.value = null;
}

async function onGameChange() {
  const game = gameStore.games.find(g => g.id === selectedGameId.value);
  if (game) {
    selectedGame.value = JSON.parse(JSON.stringify(game));
  }
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
  } catch (e) {
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
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao confirmar chamadas";
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
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao cancelar jogo";
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
  } catch (e) {
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
