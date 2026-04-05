<template>
  <div class="game-calls p-4 w-full mx-auto bg-stone-50 md:p-6">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-stone-900 mb-1 md:text-2xl">Chamada de Jogadores</h1>
        <p class="text-stone-500 text-sm md:text-base">Atribuir números de camisola aos jogadores chamados</p>
      </div>
      <P-Button severity="secondary" @click="router.push('/admin')">
        <span class="material-symbols-outlined">arrow_back</span>
        <span class="hidden sm:inline">Voltar</span>
      </P-Button>
    </div>

    <div class="bg-white border border-stone-300 rounded-xl p-4 md:p-6">
      <div class="mb-6">
        <label class="block text-sm font-medium text-stone-700 mb-2">Selecionar Torneio</label>
        <P-Dropdown
          v-model="selectedTournamentId"
          :options="tournaments"
          optionLabel="name"
          optionValue="id"
          placeholder="Escolha um torneio..."
          class="w-full"
          @change="onTournamentChange"
        />
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium text-stone-700 mb-2">Selecionar Jogo</label>
        <P-Dropdown
          v-model="selectedGameId"
          :options="filteredGames"
          optionLabel="label"
          optionValue="id"
          placeholder="Escolha um jogo..."
          class="w-full"
          :disabled="!selectedTournamentId"
          @change="onGameChange"
        />
      </div>

      <div v-if="selectedGame" class="space-y-6">
        <div class="flex flex-col md:flex-row gap-6">
          <!-- Home Team -->
          <div class="flex-1 border border-stone-200 rounded-lg overflow-hidden">
            <div class="bg-blue-50 px-3 py-2 border-b border-stone-200">
              <span class="font-semibold text-blue-800">{{ getTeamName(selectedGame.home_call?.team) }}</span>
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
              <span class="font-semibold text-red-800">{{ getTeamName(selectedGame.away_call?.team) }}</span>
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
        <P-Button v-else label="Guardar Chamada" icon="save" severity="success" @click="submitCall" />
      </div>

      <div v-else-if="selectedGameId && !selectedGame" class="text-center py-8 text-stone-400">
        <span class="material-symbols-outlined text-4xl mb-2">sports_soccer</span>
        <p>Jogo sem chamadas</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useGameStore } from "@stores/games";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { usePlayerStore } from "@stores/players";
import * as gameService from "@router/backend/services/game";
import type { Game } from "@router/backend/services/game/types";
import { http } from "@router/backend/api";

const router = useRouter();
const toast = useToast();
const gameStore = useGameStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const playerStore = usePlayerStore();

const selectedTournamentId = ref<string>("");
const selectedGameId = ref<string>("");
const selectedGame = ref<Game | null>(null);
const saving = ref(false);

const tournaments = computed(() => tournamentStore.tournaments);

const filteredGames = computed(() => {
  if (!selectedTournamentId.value) return [];
  return gameStore.games
    .filter(g => g.tournament === selectedTournamentId.value && g.home_call && g.away_call)
    .map(g => {
      const homeTeam = teamStore.teams.find(t => t.id === g.home_call?.team);
      const awayTeam = teamStore.teams.find(t => t.id === g.away_call?.team);
      const homeName = homeTeam?.name || g.home_placeholder || "Casa";
      const awayName = awayTeam?.name || g.away_placeholder || "Fora";
      const phaseLabel = g.phase === "group" ? "Fase de Grupos" :
                         g.phase === "quarter_final" ? "quartos" :
                         g.phase === "semi_final" ? "meias" :
                         g.phase === "final" ? "final" :
                         g.phase === "third_place" ? "3º/4º" : g.phase;
      return {
        id: g.id,
        label: `${homeName} vs ${awayName} (${phaseLabel})`
      };
    });
});

function getTeamName(teamId: string | undefined) {
  if (!teamId) return "";
  return teamStore.teams.find(t => t.id === teamId)?.name || teamId;
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
  await gameStore.getGames();
  await teamStore.getTeams();
  await tournamentStore.getTournaments();
  await playerStore.getPlayers();
});
</script>

<style scoped>
:deep(.p-inputnumber-input) {
  width: 2.5rem;
}
</style>
