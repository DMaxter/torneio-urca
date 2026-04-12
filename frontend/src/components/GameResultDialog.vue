<template>
  <P-Dialog
    v-model:visible="visible"
    modal
    :header="`Resultado - ${getTournamentName(game?.tournament)}`"
    class="w-11/12 md:w-[600px]"
    :breakpoints="{ '960px': '75vw', '640px': '95vw' }"
  >
    <div v-if="game" class="flex flex-col gap-6">
      <!-- Scoreboard Header -->
      <div class="bg-stone-900 text-white rounded-xl p-6 shadow-xl relative overflow-hidden">
        <div class="absolute inset-0 opacity-10 pointer-events-none">
          <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-stone-100 to-transparent"></div>
        </div>

        <div class="relative z-10">
          <div class="text-center text-[10px] uppercase tracking-widest text-stone-400 font-bold mb-4">
            {{ getPhaseLabel(game.phase) }} • {{ formatDateTime(game.scheduled_date) }}
          </div>

          <div class="flex items-center justify-between gap-4">
            <!-- Home Team -->
            <div class="flex-1 flex flex-col items-center text-center">
              <div class="text-xs font-semibold text-stone-400 mb-2 uppercase tracking-tight">CASA</div>
              <div class="text-lg font-bold leading-tight min-h-[3rem] flex items-center h-full">
                {{ getHomeDisplayName() }}
              </div>
            </div>

            <!-- Score -->
            <div class="flex flex-col items-center px-4">
              <div class="flex items-center gap-3">
                <span class="text-5xl font-black tabular-nums">{{ homeScore }}</span>
                <span class="text-3xl font-bold text-stone-600">-</span>
                <span class="text-5xl font-black tabular-nums">{{ awayScore }}</span>
              </div>
              <div v-if="isShootout" class="mt-2 text-amber-400 font-bold text-sm uppercase tracking-wider">
                Pen: {{ homePenaltyScore }} - {{ awayPenaltyScore }}
              </div>
              <div v-else-if="isStatus(game.status, 'InProgress')" class="mt-2 text-green-500 font-bold text-[10px] animate-pulse uppercase">
                EM JOGO
              </div>
              <div v-else-if="isStatus(game.status, 'Finished')" class="mt-2 text-stone-500 font-bold text-[10px] uppercase">
                FINALIZADO
              </div>
              <div v-else-if="isStatus(game.status, 'Canceled')" class="mt-2 text-red-500 font-bold text-[10px] uppercase">
                CANCELADO
              </div>
              <div v-else class="mt-2 text-stone-400 font-bold text-[10px] uppercase">
                AGENDADO
              </div>
            </div>

            <!-- Away Team -->
            <div class="flex-1 flex flex-col items-center text-center">
              <div class="text-xs font-semibold text-stone-400 mb-2 uppercase tracking-tight">VISITANTE</div>
              <div class="text-lg font-bold leading-tight min-h-[3rem] flex items-center h-full">
                {{ getAwayDisplayName() }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Events Timeline -->
      <div v-if="importantEvents.length > 0" class="flex flex-col gap-4">
        <h3 class="text-sm font-bold text-stone-900 border-b border-stone-100 pb-2 mb-2 flex items-center gap-2">
          <span class="material-symbols-outlined text-base">format_list_bulleted</span>
          Acontecimentos do Jogo
        </h3>

        <div class="space-y-4">
          <div
            v-for="(event, idx) in sortedEvents"
            :key="idx"
            class="flex items-start gap-4 group"
          >
            <!-- Time Indicator -->
            <div class="w-16 shrink-0 text-right pt-0.5">
              <span class="text-xs font-bold text-stone-400 group-hover:text-stone-600 transition-colors">
                {{ getEventTimeDisplay(event) }}
              </span>
            </div>

            <!-- Connection Line Decor -->
            <div class="flex flex-col items-center self-stretch">
              <div class="w-2.5 h-2.5 rounded-full border-2 shrink-0 transition-transform group-hover:scale-125" :class="getEventDotClass(event)"></div>
              <div v-if="idx < sortedEvents.length - 1" class="w-px flex-1 bg-stone-100 my-1 group-hover:bg-stone-200"></div>
            </div>

            <!-- Event Content -->
            <div class="flex-1 pb-4">
              <div class="flex items-center justify-between gap-2">
                <span class="text-sm font-semibold text-stone-800">{{ getEventDescription(event) }}</span>
                <span class="text-lg">{{ getEventIcon(event) }}</span>
              </div>
              <div class="text-[10px] font-bold text-stone-400 uppercase tracking-wide mt-0.5">
                {{ getEventTeamName(event) || 'Aviso' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-12 text-stone-400">
        <span class="material-symbols-outlined text-4xl mb-2 opacity-20">history</span>
        <p class="text-sm italic">Nenhum evento relevante registado para este jogo.</p>
      </div>
    </div>

    <div v-else-if="loading" class="flex justify-center items-center py-20">
      <P-ProgressSpinner strokeWidth="4" />
    </div>

    <template #footer>
      <div class="flex justify-end">
        <P-Button severity="secondary" @click="visible = false">
          <span class="material-symbols-outlined">close</span>
          Fechar
        </P-Button>
      </div>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { useGameStore } from "@stores/games";
import { useDateFormatter } from "@/composables/useDateFormatter";
import { GameStatus, type Game, type GameEvent } from "@router/backend/services/game/types";
import * as gameService from "@router/backend/services/game";

const visible = defineModel<boolean>("visible", { default: false });
const props = defineProps<{
  game: Game | null;
}>();

const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const gameStore = useGameStore();
const { formatDateTime } = useDateFormatter();

const localGame = ref<Game | null>(null);
const loading = ref(false);
const isRefreshing = ref(false);
let refreshInterval: number | undefined;

// Use localGame if available (has full details), otherwise use props.game
const game = computed(() => localGame.value || props.game);

async function refreshGame() {
  if (!props.game?.id || isRefreshing.value) return;

  isRefreshing.value = true;
  loading.value = true;
  try {
    const { status, data } = await gameService.getGame(props.game.id);
    if (status === 200 && data) {
      localGame.value = data as Game;
      // Also update the store to keep everything in sync
      const idx = gameStore.games.findIndex(g => g.id === props.game!.id);
      if (idx !== -1) gameStore.games[idx] = data as Game;
    }
  } catch (e) {
    console.error("Error fetching game details:", e);
  } finally {
    loading.value = false;
    isRefreshing.value = false;
  }
}

function startRefreshInterval() {
  if (refreshInterval) clearInterval(refreshInterval);
  if (game.value && isStatus(game.value.status, 'InProgress')) {
    refreshInterval = setInterval(refreshGame, 10000); // Refresh every 10 seconds
  }
}

function stopRefreshInterval() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = undefined;
  }
}

watch(() => props.game?.id, (newId) => {
  if (newId && visible.value) {
    refreshGame();
    startRefreshInterval();
  } else {
    localGame.value = null;
    stopRefreshInterval();
  }
}, { immediate: true });

watch(visible, (val) => {
  if (val) {
    if (props.game?.id && !localGame.value) {
      refreshGame();
    }
    startRefreshInterval();
  } else {
    stopRefreshInterval();
  }
});

watch(() => game.value?.status, (newStatus) => {
  if (visible.value) {
    if (isStatus(newStatus, 'InProgress')) {
      startRefreshInterval();
    } else {
      stopRefreshInterval();
    }
  }
});

import { onUnmounted } from "vue";

onUnmounted(() => {
  stopRefreshInterval();
});


function isStatus(currentStatus: any, target: keyof typeof GameStatus): boolean {
  const s = String(currentStatus);
  const targetValue = GameStatus[target];

  // Handle both string values and potential integer codes
  if (s === targetValue) return true;

  const codes: Record<string, string> = {
    "Scheduled": "0",
    "CallsPending": "1",
    "ReadyToStart": "2",
    "InProgress": "3",
    "Finished": "4",
    "Canceled": "5"
  };

  return s === codes[target];
}

function getTournamentName(id?: string): string {
  if (!id) return '';
  return tournamentStore.tournaments.find(t => t.id === id)?.name || id;
}

function getTeamName(id?: string | null): string {
  if (!id) return '';
  const team = teamStore.teams.find(t => t.id === id);
  return team ? team.name : id;
}

function getHomeDisplayName(): string {
  if (!game.value) return '?';
  return getTeamName(game.value.home_call?.team) || game.value.home_placeholder || '?';
}

function getAwayDisplayName(): string {
  if (!game.value) return '?';
  return getTeamName(game.value.away_call?.team) || game.value.away_placeholder || '?';
}

function getPhaseLabel(phase?: string): string {
  if (!phase) return '';
  const labels: Record<string, string> = {
    group: 'Fase de Grupos',
    quarter_final: 'Quartos de Final',
    semi_final: 'Meias Finais',
    final: 'Final',
    third_place: '3º/4º Lugar',
  };
  return labels[phase] || phase;
}

// Scores calculation
const homeScore = computed(() => {
  if (!game.value) return 0;
  const homeName = getHomeDisplayName();

  return (game.value.events || []).filter(e => {
    if ('Goal' in e) {
      const goal = e.Goal;
      // Match by team name (from placeholder or actual team name)
      return goal.team_name === homeName;
    }
    return false;
  }).length;
});

const awayScore = computed(() => {
  if (!game.value) return 0;
  const awayName = getAwayDisplayName();

  return (game.value.events || []).filter(e => {
    if ('Goal' in e) {
      const goal = e.Goal;
      return goal.team_name === awayName;
    }
    return false;
  }).length;
});

const isShootout = computed(() => game.value?.current_period === 5);

const homePenaltyScore = computed(() => {
  if (!game.value || !game.value.home_call) return 0;
  const homeName = getTeamName(game.value.home_call.team);
  return (game.value.events || []).filter(e => {
    if ('Penalty' in e) return e.Penalty.team_name === homeName && e.Penalty.scored;
    return false;
  }).length;
});

const awayPenaltyScore = computed(() => {
  if (!game.value || !game.value.away_call) return 0;
  const awayName = getTeamName(game.value.away_call.team);
  return (game.value.events || []).filter(e => {
    if ('Penalty' in e) return e.Penalty.team_name === awayName && e.Penalty.scored;
    return false;
  }).length;
});

// Event filtering and sorting
const importantEvents = computed(() => {
  if (!game.value) return [];
  return (game.value.events || []).filter(e =>
    'Goal' in e || 'Penalty' in e || ('Foul' in e && (e.Foul.card || e.Foul.is_direct_free_kick)) || 'PeriodStart' in e || 'PeriodEnd' in e
  );
});

const sortedEvents = computed(() => {
  return [...importantEvents.value].sort((a, b) => {
    const timeA = getEventTimestamp(a);
    const timeB = getEventTimestamp(b);
    return timeA - timeB;
  });
});

function getEventTimestamp(event: GameEvent): number {
  if ('Goal' in event) return new Date(event.Goal.timestamp).getTime();
  if ('Penalty' in event) return new Date(event.Penalty.timestamp).getTime();
  if ('Foul' in event) return new Date(event.Foul.timestamp).getTime();
  if ('PeriodStart' in event) return new Date(event.PeriodStart.timestamp).getTime();
  if ('PeriodEnd' in event) return new Date(event.PeriodEnd.timestamp).getTime();
  if ('PeriodPause' in event) return new Date(event.PeriodPause.timestamp).getTime();
  if ('PeriodResume' in event) return new Date(event.PeriodResume.timestamp).getTime();
  return 0;
}

function getEventTimeDisplay(event: GameEvent): string {
  let period = 0;
  let minute = 0;

  if ('Goal' in event) { period = event.Goal.period; minute = event.Goal.minute; }
  else if ('Penalty' in event) { period = event.Penalty.period; minute = event.Penalty.minute; }
  else if ('Foul' in event) { period = event.Foul.period; minute = event.Foul.minute; }
  else if ('PeriodStart' in event) { period = event.PeriodStart.period; return `P${period} INI`; }
  else if ('PeriodEnd' in event) { period = event.PeriodEnd.period; return `P${period} FIM`; }

  if (period === 5) return 'PEN';
  return `${minute}' (P${period})`;
}

function getEventIcon(event: GameEvent): string {
  if ('Goal' in event) return event.Goal.own_goal ? '🥅' : '⚽';
  if ('Penalty' in event) return event.Penalty.scored ? '✅' : '❌';
  if ('Foul' in event) {
    if (event.Foul.card === 'Yellow') return '🟨';
    if (event.Foul.card === 'Red') return '🟥';
    return '⚠️';
  }
  if ('PeriodStart' in event) return '▶️';
  if ('PeriodEnd' in event) return '⏹️';
  return '';
}

function getEventDescription(event: GameEvent): string {
  if ('Goal' in event) {
    if (event.Goal.own_goal) return `Auto-golo (${event.Goal.own_goal_committed_by || 'equipa adversária'})`;
    return `Golo de ${event.Goal.player_name || 'Jogador'}`;
  }
  if ('Penalty' in event) {
    return `${event.Penalty.player_name} ${event.Penalty.scored ? 'marcou' : 'falhou'} penalti`;
  }
  if ('Foul' in event) {
    const name = event.Foul.staff_name || event.Foul.player_name || 'Desconhecido';
    if (event.Foul.card) return `${name} - Cartão ${event.Foul.card === 'Yellow' ? 'Amarelo' : 'Vermelho'}`;
    return `${name} - Falta (Livre Direto)`;
  }
  if ('PeriodStart' in event) return `Início do ${event.PeriodStart.period}º Período`;
  if ('PeriodEnd' in event) return `Final do ${event.PeriodEnd.period}º Período`;
  return '';
}

function getEventTeamName(event: GameEvent): string {
  if ('Goal' in event) return event.Goal.team_name;
  if ('Penalty' in event) return event.Penalty.team_name;
  if ('Foul' in event) return event.Foul.team_name;
  return '';
}

function getEventDotClass(event: GameEvent): string {
  if ('Goal' in event) return 'border-green-500 bg-green-500';
  if ('Penalty' in event) return event.Penalty.scored ? 'border-green-500 bg-green-500' : 'border-red-500 bg-red-500';
  if ('Foul' in event) {
    if (event.Foul.card === 'Yellow') return 'border-yellow-400 bg-yellow-400';
    if (event.Foul.card === 'Red') return 'border-red-600 bg-red-600';
    return 'border-orange-400 bg-orange-400';
  }
  return 'border-stone-300 bg-stone-300';
}
</script>

<style scoped>
.game-result {
  max-height: 80vh;
  overflow-y: auto;
}
</style>
