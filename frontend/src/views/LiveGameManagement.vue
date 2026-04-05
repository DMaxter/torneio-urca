<template>
  <div class="live-game p-2 md:p-4 w-full mx-auto bg-stone-50 md:p-6">
    <div class="mb-4 md:mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-stone-900 mb-1 md:text-2xl">Jogo ao Vivo</h1>
        <p v-if="game" class="text-stone-500 text-sm md:text-base">
          {{ getTournamentName(game.tournament) }} - {{ getPhaseLabel(game.phase) }}
        </p>
        <div v-if="game" class="text-lg font-semibold text-stone-800 mt-1">
          {{ getTeamName(game.home_call?.team) }} <span class="text-stone-400 mx-2">vs</span> {{ getTeamName(game.away_call?.team) }}
        </div>
      </div>
      <div class="flex gap-2">
        <P-Button severity="danger" @click="finishGame" v-if="game">
          <span class="material-symbols-outlined">stop_circle</span>
          <span class="hidden sm:inline">Terminar</span>
        </P-Button>
        <P-Button severity="secondary" @click="router.back()">
          <span class="material-symbols-outlined">arrow_back</span>
          <span class="hidden sm:inline">Voltar</span>
        </P-Button>
      </div>
    </div>

    <!-- Period and Clock Display -->
    <div v-if="game" class="mb-4 grid grid-cols-2 gap-4">
      <div class="bg-white border border-stone-300 rounded-xl p-4 text-center">
        <div class="text-sm text-stone-500">Período</div>
        <div class="text-3xl font-bold text-stone-900">{{ getPeriodLabel(game.current_period) }}</div>
        <div v-if="game.current_period > 0" class="text-xs text-stone-400">{{ getPeriodTypeLabel(game.current_period) }}</div>
      </div>
      <div class="bg-white border border-stone-300 rounded-xl p-4 text-center">
        <div class="text-sm text-stone-500">Cronómetro</div>
        <div class="text-4xl font-bold text-stone-900 mt-1">{{ timerDisplay }}</div>
        <div class="text-xs text-stone-400">
          {{ getTimerLabel(game.current_period) }}
        </div>
      </div>
    </div>

    <!-- Period Controls -->
    <div v-if="game && game.status === 'InProgress'" class="mb-4 flex gap-2 justify-center flex-wrap">
      <P-Button
        v-if="game.current_period === 0"
        label="Iniciar Período"
        severity="success"
        size="large"
        @click="startPeriod"
      />
      <template v-else>
        <P-Button
          v-if="showResumeButton"
          :label="resumeButtonLabel"
          severity="success"
          size="large"
          @click="resumePeriod"
        />
        <P-Button
          v-if="game.timer_active"
          label="Parar"
          severity="warning"
          size="large"
          @click="stopTimer"
        />
        <P-Button
          v-if="game.current_period < 5"
          :label="getNextPeriodLabel(game.current_period)"
          :severity="getNextPeriodSeverity(game.current_period)"
          size="large"
          :disabled="!canProceedToNextPeriod"
          v-tooltip.top="getNextPeriodTooltip(game.current_period)"
          @click="endPeriod"
        />
        <P-Button
          v-else-if="game.current_period === 4"
          :label="getNextPeriodLabel(game.current_period)"
          :severity="getNextPeriodSeverity(game.current_period)"
          size="large"
          :disabled="!canProceedToNextPeriod"
          v-tooltip.top="getNextPeriodTooltip(game.current_period)"
          @click="startPenalties"
        />
        <P-Button
          v-if="game.current_period >= 5"
          label="Finalizar Jogo"
          severity="danger"
          size="large"
          @click="finishGame"
        />
      </template>
    </div>

    <div v-if="game" class="space-y-4">
      <!-- Team Boxes -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Home Team Box -->
        <div class="bg-white border-4 border-blue-500 rounded-xl p-4 shadow-lg" :class="{'border-blue-600': selectedTeam === game.home_call?.team}">
          <div class="text-center mb-3">
            <div class="text-lg font-bold text-blue-800">{{ getTeamName(game.home_call?.team) }}</div>
            <div class="text-5xl font-bold text-stone-900 mt-2">{{ homeScore }}</div>
          </div>
          <div class="grid grid-cols-3 gap-2">
            <P-Button
              label="⚽ Golo"
              size="large"
              class="bg-green-600 hover:bg-green-700 text-white border-none"
              @click="openEventDialog(game.home_call?.team, 'goal')"
            />
            <P-Button
              label="🟨 Cartão"
              size="large"
              class="bg-yellow-500 hover:bg-yellow-600 text-white border-none"
              @click="openEventDialog(game.home_call?.team, 'card')"
            />
            <P-Button
              label="⚠️ Falta"
              size="large"
              class="bg-orange-500 hover:bg-orange-600 text-white border-none"
              @click="openEventDialog(game.home_call?.team, 'foul')"
            />
          </div>
        </div>

        <!-- Away Team Box -->
        <div class="bg-white border-4 border-red-500 rounded-xl p-4 shadow-lg" :class="{'border-red-600': selectedTeam === game.away_call?.team}">
          <div class="text-center mb-3">
            <div class="text-lg font-bold text-red-800">{{ getTeamName(game.away_call?.team) }}</div>
            <div class="text-5xl font-bold text-stone-900 mt-2">{{ awayScore }}</div>
          </div>
          <div class="grid grid-cols-3 gap-2">
            <P-Button
              label="⚽ Golo"
              size="large"
              class="bg-green-600 hover:bg-green-700 text-white border-none"
              @click="openEventDialog(game.away_call?.team, 'goal')"
            />
            <P-Button
              label="🟨 Cartão"
              size="large"
              class="bg-yellow-500 hover:bg-yellow-600 text-white border-none"
              @click="openEventDialog(game.away_call?.team, 'card')"
            />
            <P-Button
              label="⚠️ Falta"
              size="large"
              class="bg-orange-500 hover:bg-orange-600 text-white border-none"
              @click="openEventDialog(game.away_call?.team, 'foul')"
            />
          </div>
        </div>
      </div>

      <!-- Events Log -->
      <div class="bg-white border border-stone-300 rounded-xl p-4 max-h-96 overflow-y-auto">
        <h2 class="text-lg font-semibold text-stone-900 mb-4">Eventos do Jogo</h2>

        <div v-if="sortedEvents.length === 0" class="text-stone-400 text-center py-8">
          Nenhum evento registado
        </div>

        <div v-else class="space-y-2">
          <div v-for="(event, idx) in sortedEvents" :key="idx" 
               class="flex items-center gap-3 p-3 rounded-lg border-2"
               :class="getEventBorderClass(event)">
            <div class="font-bold text-stone-600 text-xl w-24 text-center shrink-0">
              <div>{{ getEventTimeDisplay(event) }}</div>
              <div class="text-xs text-stone-400 font-normal">{{ getEventTimestampFormatted(event) }}</div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-base font-semibold text-stone-900">{{ getEventDescription(event) }}</div>
              <div v-if="getEventMetadata(event)" class="text-xs text-stone-400">{{ getEventMetadata(event) }}</div>
            </div>
            <div class="text-2xl shrink-0">{{ getEventIcon(event) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-12 text-stone-400">
      <span class="material-symbols-outlined text-6xl mb-4">sports_soccer</span>
      <p>Jogo não encontrado</p>
    </div>

    <!-- Event Dialog -->
    <P-Dialog v-model:visible="eventDialogVisible" modal :header="eventDialogTitle" class="w-11/12 md:w-1/2 lg:w-1/3">
      <div class="p-4">
        <!-- Goal Dialog -->
        <div v-if="eventType === 'goal'">
          <div class="mb-4">
            <label class="block text-sm font-medium text-stone-700 mb-2">Tipo de Golo</label>
            <div class="flex gap-2">
              <P-Button
                :label="`Golo (${getTeamName(selectedTeam)})`"
                :severity="selectedGoalType === 'regular' ? 'success' : 'secondary'"
                class="flex-1"
                @click="selectedGoalType = 'regular'"
              />
              <P-Button
                label="Auto-Golo"
                :severity="selectedGoalType === 'own_goal' ? 'warning' : 'secondary'"
                class="flex-1"
                @click="selectedGoalType = 'own_goal'"
              />
            </div>
          </div>

          <div v-if="selectedGoalType === 'regular'">
            <div class="mb-4">
              <label class="block text-sm font-medium text-stone-700 mb-2">Jogador que Marcou</label>
              <div class="grid grid-cols-3 sm:grid-cols-5 gap-2">
                <P-Button
                  v-for="num in availableShirtNumbers"
                  :key="num"
                  :label="`#${num}`"
                  :severity="playerNumber === num ? 'success' : 'secondary'"
                  class="text-lg py-3"
                  @click="playerNumber = num"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Card Dialog -->
        <div v-if="eventType === 'card'">
          <div class="mb-4">
            <label class="block text-sm font-medium text-stone-700 mb-2">Tipo de Cartão</label>
            <div class="flex gap-2">
              <P-Button
                label="🟨 Amarelo"
                :severity="cardType === 'Yellow' ? 'warning' : 'secondary'"
                class="flex-1"
                @click="cardType = 'Yellow'"
              />
              <P-Button
                label="🟥 Vermelho"
                :severity="cardType === 'Red' ? 'danger' : 'secondary'"
                class="flex-1"
                @click="cardType = 'Red'"
              />
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-stone-700 mb-2">Atribuir a</label>
            <div class="flex gap-2 mb-2">
              <P-Button
                label="Jogador"
                :severity="cardTarget === 'player' ? 'info' : 'secondary'"
                class="flex-1"
                @click="cardTarget = 'player'"
              />
              <P-Button
                v-if="hasStaffForTeam"
                label="Staff"
                :severity="cardTarget === 'staff' ? 'info' : 'secondary'"
                class="flex-1"
                @click="cardTarget = 'staff'"
              />
            </div>

            <div v-if="cardTarget === 'player'">
              <label class="block text-sm font-medium text-stone-700 mb-2">Número do Jogador</label>
              <div class="grid grid-cols-3 sm:grid-cols-5 gap-2">
                <P-Button 
                  v-for="num in availableShirtNumbers" 
                  :key="num"
                  :label="`#${num}`" 
                  :severity="playerNumber === num ? 'success' : 'secondary'"
                  class="text-lg py-3"
                  @click="playerNumber = num"
                />
              </div>
            </div>

            <div v-else-if="hasStaffForTeam">
              <label class="block text-sm font-medium text-stone-700 mb-2">Membro do Staff</label>
              <P-Select 
                v-model="staffId"
                :options="staffOptions"
                optionLabel="label"
                optionValue="id"
                placeholder="Selecione o staff"
                class="w-full"
              />
            </div>
          </div>
        </div>

        <!-- Foul Dialog -->
        <div v-if="eventType === 'foul'">
          <div class="mb-4">
            <label class="block text-sm font-medium text-stone-700 mb-2">Jogador que Cometeu a Falta</label>
            <div class="grid grid-cols-3 sm:grid-cols-5 gap-2">
              <P-Button 
                v-for="num in availableShirtNumbers" 
                :key="num"
                :label="`#${num}`" 
                :severity="playerNumber === num ? 'warning' : 'secondary'"
                class="text-lg py-3"
                @click="playerNumber = num"
              />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex gap-2 w-full justify-between">
          <P-Button severity="secondary" @click="closeEventDialog">Cancelar</P-Button>
          <P-Button 
            :severity="eventType === 'goal' ? 'success' : eventType === 'foul' ? 'warning' : 'warning'" 
            :loading="saving"
            :disabled="!canSubmitEvent"
            @click="submitEvent"
          >
            {{ eventType === 'goal' ? 'Marcar Golo' : eventType === 'foul' ? 'Registar Falta' : 'Atribuir Cartão' }}
          </P-Button>
        </div>
      </template>
    </P-Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useGameStore } from "@stores/games";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import * as gameService from "@router/backend/services/game";
import type { Game, GameEvent } from "@router/backend/services/game/types";
import { GameStatus } from "@router/backend/services/game/types";
import type { CardType } from "@router/backend/services/game/types";

const router = useRouter();
const route = useRoute();
const toast = useToast();
const gameStore = useGameStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const gameId = route.params.gameId as string;
const game = ref<Game | null>(null);
const events = ref<GameEvent[]>([]);
const saving = ref(false);

// Event dialog state
const eventDialogVisible = ref(false);
const selectedTeam = ref<string | null>(null);
const eventTeam = ref<string | null>(null);
const eventType = ref<'goal' | 'card' | 'foul' | null>(null);
const playerNumber = ref<number | null>(null);
const cardType = ref<CardType>('Yellow');
const cardTarget = ref<'player' | 'staff'>('player');
const staffId = ref<string | null>(null);
const selectedGoalType = ref<'regular' | 'own_goal'>('regular');

const eventDialogTitle = computed(() => {
  if (!eventType.value || !eventTeam.value) return '';
  const teamName = getTeamName(eventTeam.value);
  if (eventType.value === 'goal') {
    return selectedGoalType.value === 'own_goal' ? 'Registar Auto-Golo' : `Registar Golo - ${teamName}`;
  }
  if (eventType.value === 'card') {
    return `Atribuir Cartão - ${teamName}`;
  }
  return `Registar Falta - ${teamName}`;
});

const homeTeamId = computed(() => game.value?.home_call?.team || '');
const awayTeamId = computed(() => game.value?.away_call?.team || '');

const homeScore = computed(() => {
  if (!game.value) return 0;
  const homeName = getTeamName(homeTeamId.value);
  return events.value.filter(e => {
    if ('Goal' in e) {
      const goal = (e as any).Goal;
      return goal.team_name === homeName;
    }
    return false;
  }).length;
});

const awayScore = computed(() => {
  if (!game.value) return 0;
  const awayName = getTeamName(awayTeamId.value);
  return events.value.filter(e => {
    if ('Goal' in e) {
      const goal = (e as any).Goal;
      return goal.team_name === awayName;
    }
    return false;
  }).length;
});

const availableShirtNumbers = computed(() => {
  if (!game.value || !eventTeam.value) return [];
  const call = eventTeam.value === homeTeamId.value ? game.value.home_call : game.value.away_call;
  if (!call) return [];

  const numbers = new Set<number>();
  call.players.forEach(p => {
    if (p.number !== null) numbers.add(p.number);
  });
  return Array.from(numbers).sort((a, b) => a - b);
});

const staffOptions = computed(() => {
  return [];
});

const hasStaffForTeam = computed(() => {
  // For now, always return false since we don't have staff data loaded per team
  // If staff options is empty, there's no staff to assign cards to
  return staffOptions.value.length > 0;
});

const canSubmitEvent = computed(() => {
  if (!eventTeam.value || !eventType.value) return false;

  if (eventType.value === 'goal') {
    if (selectedGoalType.value === 'own_goal') return true;
    return playerNumber.value !== null;
  }

  if (eventType.value === 'card') {
    if (cardTarget.value === 'player') {
      return playerNumber.value !== null && cardType.value;
    } else {
      return staffId.value !== null && cardType.value;
    }
  }

  if (eventType.value === 'foul') {
    return playerNumber.value !== null;
  }

  return false;
});

const currentElapsedSeconds = computed(() => {
  if (!game.value) return 0;
  let elapsed = game.value.period_elapsed_seconds;
  if (game.value.timer_active && game.value.timer_started_at) {
    const now = Date.now();
    const startTime = Date.parse(game.value.timer_started_at + 'Z');
    const activeElapsed = Math.floor((now - startTime) / 1000);
    elapsed += activeElapsed;
  }
  return elapsed;
});

const timerDisplay = computed(() => {
  if (!game.value) return '00:00';
  const durationSeconds = getDurationForPeriod(game.value.current_period);
  const remaining = Math.max(0, durationSeconds - currentElapsedSeconds.value);
  const mins = Math.floor(remaining / 60);
  const secs = remaining % 60;
  if (mins === 0) {
    // Show seconds and tenths
    const tenths = Math.floor((secs % 1) * 10);
    return `${secs}.${tenths}s`;
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
});

function getDurationForPeriod(period: number): number {
  if (period >= 1 && period <= 2) return 1200; // 20 minutes
  if (period >= 3 && period <= 4) return 300; // 5 minutes
  return 0; // not started or penalties/finished
}

function getTimerLabel(period: number): string {
  if (period >= 1 && period <= 2) return '20:00 min';
  if (period >= 3 && period <= 4) return '05:00 min';
  return '';
}

const canProceedToNextPeriod = computed(() => {
  if (!game.value) return false;
  if (game.value.current_period < 2) return true;
  if (game.value.current_period === 2) {
    return homeScore.value === awayScore.value;
  }
  if (game.value.current_period === 3) return true;
  if (game.value.current_period === 4) return true;
  return false;
});

const showResumeButton = computed(() => {
  if (!game.value) return false;
  if (game.value.timer_active) return false;
  const duration = getDurationForPeriod(game.value.current_period);
  if (duration === 0) return false;
  return currentElapsedSeconds.value < duration;
});

const resumeButtonLabel = computed(() => {
  if (!game.value) return 'Continuar';
  if (!game.value.timer_active && currentElapsedSeconds.value === 0) {
    return 'Iniciar Período';
  }
  return 'Continuar';
});

// Methods
function getPeriodLabel(period: number): string {
  if (period === 0) return 'Não iniciado';
  if (period <= 4) return `${period}º Período`;
  return 'Penalidades';
}

function getPeriodTypeLabel(period: number): string {
  if (period >= 1 && period <= 2) return 'Tempo Regular';
  if (period >= 3 && period <= 4) return 'Prolongamento';
  return 'Penalidades';
}

function getTournamentName(id: string): string {
  const t = tournamentStore.tournaments.find(t => t.id === id);
  return t ? t.name : id;
}

function getTeamName(id?: string | null): string {
  if (!id) return '';
  const team = teamStore.teams.find(t => t.id === id);
  return team ? team.name : id;
}

function getPhaseLabel(phase: string): string {
  const labels: Record<string, string> = {
    group: 'Grupo',
    quarter_final: 'Quartos',
    semi_final: 'Meias',
    final: 'Final',
    third_place: '3º/4º',
  };
  return labels[phase] || phase;
}

function getNextPeriodLabel(currentPeriod: number): string {
  if (currentPeriod === 2) return 'Próximo Período (Prolongamento)';
  if (currentPeriod === 3) return 'Próximo Período';
  if (currentPeriod === 4) return 'Iniciar Penalidades';
  return 'Próximo Período';
}

function getNextPeriodSeverity(currentPeriod: number): string {
  return 'info';
}

function getNextPeriodTooltip(currentPeriod: number): string {
  if (currentPeriod === 2) {
    return canProceedToNextPeriod.value ? 'Avançar para o prolongamento (período 3)' : 'O prolongamento só pode ser jogado se o placar estiver empatado';
  }
  if (currentPeriod === 4) {
    return canProceedToNextPeriod.value ? 'Iniciar período de penalidades (período 5)' : 'As penalidades só podem ser jogadas se o placar estiver empatado';
  }
  return 'Avançar para o próximo período';
}

function getEventBorderClass(event: GameEvent): string {
  if ('Goal' in event) {
    const goal = (event as any).Goal;
    return goal.own_goal ? 'border-orange-200 bg-orange-50' : 'border-green-200 bg-green-50';
  }
  if ('Foul' in event) {
    const foul = (event as any).Foul;
    if (foul.card === null || foul.card === undefined) {
      return 'border-orange-200 bg-orange-50';
    }
    return 'border-red-200 bg-red-50';
  }
  if ('PeriodStart' in event || 'PeriodResume' in event) {
    return 'border-blue-200 bg-blue-50';
  }
  if ('PeriodEnd' in event || 'PeriodPause' in event) {
    return 'border-gray-200 bg-gray-50';
  }
  return '';
}

function getEventIcon(event: GameEvent): string {
  if ('Goal' in event) {
    const goal = (event as any).Goal;
    return goal.own_goal ? '🥅' : '⚽';
  }
  if ('Foul' in event) {
    const foul = (event as any).Foul;
    if (foul.card === null || foul.card === undefined) {
      return '⚠️';
    }
    return foul.card === 'Yellow' ? '🟨' : '🟥';
  }
  if ('PeriodStart' in event) {
    return '▶️';
  }
  if ('PeriodResume' in event) {
    return '▶️';
  }
  if ('PeriodEnd' in event) {
    return '⏹️';
  }
  if ('PeriodPause' in event) {
    return '⏸️';
  }
  return '';
}

function getEventDescription(event: GameEvent): string {
  if ('Goal' in event) {
    const goal = (event as any).Goal;
    if (goal.own_goal) {
      const committedBy = goal.own_goal_committed_by || 'Equipa adversária';
      return `Auto-golo de ${committedBy}`;
    }
    const name = goal.player_name || 'Jogador desconhecido';
    return `Golo de ${name}`;
  }
  if ('Foul' in event) {
    const foul = (event as any).Foul;
    if (foul.card === null || foul.card === undefined) {
      return `${foul.player_name} - Falta`;
    }
    const cardText = foul.card === 'Yellow' ? 'Amarelo' : 'Vermelho';
    return `${foul.player_name} - Cartão ${cardText}`;
  }
  if ('PeriodStart' in event) {
    const ps = (event as any).PeriodStart;
    const isOvertime = ps.period >= 3 && ps.period <= 4;
    return isOvertime ? `Início do Prolongamento (${ps.period}º)` : `Início do ${ps.period}º Período`;
  }
  if ('PeriodResume' in event) {
    const pr = (event as any).PeriodResume;
    const isOvertime = pr.period >= 3 && pr.period <= 4;
    return isOvertime ? `Retoma do Prolongamento (${pr.period}º)` : `Retoma do ${pr.period}º Período`;
  }
  if ('PeriodEnd' in event) {
    const pe = (event as any).PeriodEnd;
    const isOvertime = pe.period >= 3 && pe.period <= 4;
    return isOvertime ? `Fim do Prolongamento (${pe.period}º)` : `Fim do ${pe.period}º Período`;
  }
  if ('PeriodPause' in event) {
    const pp = (event as any).PeriodPause;
    const isOvertime = pp.period >= 3 && pp.period <= 4;
    return isOvertime ? `Pausa no Prolongamento (${pp.period}º)` : `Pausa no ${pp.period}º Período`;
  }
  return '';
}

function getEventMinute(event: GameEvent): number {
  if ('Goal' in event) {
    const goal = (event as any).Goal;
    return goal.minute;
  }
  if ('Foul' in event) {
    const foul = (event as any).Foul;
    return foul.minute;
  }
  return 0;
}

function getEventPeriod(event: GameEvent): number {
  if ('Goal' in event) {
    const goal = (event as any).Goal;
    return goal.period || 0;
  }
  if ('Foul' in event) {
    const foul = (event as any).Foul;
    return foul.period || 0;
  }
  return 0;
}

function getEventPeriodLabel(event: GameEvent): string {
  const period = getEventPeriod(event);
  if (period === 0) return 'Não iniciado';
  if (period <= 4) return `${period}º Período`;
  return 'Penalidades';
}

function getEventTimeDisplay(event: GameEvent): string {
  const period = getEventPeriod(event);

  if (period === 5) {
    return 'Pen.';
  }

  if ('PeriodStart' in event || 'PeriodEnd' in event || 'PeriodPause' in event) {
    const ps = (event as any).PeriodStart || (event as any).PeriodEnd || (event as any).PeriodPause;
    return `P${ps.period}`;
  }

  const goal = (event as any).Goal || (event as any).Foul;
  if (!goal) return '';

  const minute = goal.minute || 0;
  const second = goal.second !== undefined ? goal.second : 0;

  let maxMinute = 0;
  if (period >= 1 && period <= 2) maxMinute = 20;
  else if (period >= 3 && period <= 4) maxMinute = 5;

  let timeStr = '';
  if (minute === 0) {
    timeStr = `${second}"`;
  } else if (minute === maxMinute) {
    timeStr = `${minute}'${second}"`;
  } else {
    timeStr = `${minute}'`;
  }

  return `${timeStr} (P${period})`;
}

function getEventTimestamp(event: GameEvent): number {
  const getTs = (raw: string | undefined) => {
    if (!raw) return 0;
    // Treat naive timestamps as UTC by appending 'Z'
    const utc = raw.endsWith('Z') ? raw : raw + 'Z';
    return new Date(utc).getTime();
  };
  
  if ('Goal' in event) {
    const goal = (event as any).Goal;
    return getTs(goal.timestamp);
  }
  if ('Foul' in event) {
    const foul = (event as any).Foul;
    return getTs(foul.timestamp);
  }
  if ('PeriodStart' in event) {
    const ps = (event as any).PeriodStart;
    return getTs(ps.timestamp);
  }
  if ('PeriodResume' in event) {
    const pr = (event as any).PeriodResume;
    return getTs(pr.timestamp);
  }
  if ('PeriodEnd' in event) {
    const pe = (event as any).PeriodEnd;
    return getTs(pe.timestamp);
  }
  if ('PeriodPause' in event) {
    const pp = (event as any).PeriodPause;
    return getTs(pp.timestamp);
  }
  return 0;
}

function getEventTimestampFormatted(event: GameEvent): string {
  const ts = getEventTimestamp(event);
  if (!ts) return '';
  return new Date(ts).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function getEventMetadata(event: GameEvent): string {
  // For period start/end/pause/resume events, don't show team name or period label
  if ('PeriodStart' in event || 'PeriodEnd' in event || 'PeriodPause' in event || 'PeriodResume' in event) {
    return '';
  }
  const teamName = getEventTeamName(event);
  const periodLabel = getEventPeriodLabel(event);
  if (teamName && periodLabel) {
    return `${teamName} - ${periodLabel}`;
  }
  return '';
}

const sortedEvents = computed(() => {
  // Map events with their original index for stable sorting
  const eventsWithIndex = events.value.map((e, i) => ({ event: e, index: i }));
  
  return eventsWithIndex
    .sort((a, b) => {
      // Sort by timestamp descending (most recent first)
      return getEventTimestamp(b.event) - getEventTimestamp(a.event);
    })
    .map(item => item.event);
});

function getEventTeamName(event: GameEvent): string {
  if ('Goal' in event) {
    const goal = (event as any).Goal;
    return goal.team_name;
  }
  if ('Foul' in event) {
    const foul = (event as any).Foul;
    return foul.team_name;
  }
  return '';
}

function getEventSecond(event: GameEvent): number {
  if ('Goal' in event) {
    const goal = (event as any).Goal;
    return goal.second !== undefined ? goal.second : 0;
  }
  if ('Foul' in event) {
    const foul = (event as any).Foul;
    return foul.second !== undefined ? foul.second : 0;
  }
  return 0;
}

function openEventDialog(teamId: string | undefined, type: 'goal' | 'card' | 'foul') {
  if (!teamId) return;
  
  selectedTeam.value = teamId;
  eventTeam.value = teamId;
  eventType.value = type;
  selectedGoalType.value = 'regular';
  cardType.value = 'Yellow';
  cardTarget.value = 'player';
  playerNumber.value = null;
  staffId.value = null;
  eventDialogVisible.value = true;
}

function closeEventDialog() {
  eventDialogVisible.value = false;
}

async function submitEvent() {
  if (!canSubmitEvent.value || !game.value) return;
  
  saving.value = true;
  
  try {
    const currentMinute = Math.floor(currentElapsedSeconds.value / 60);
    const baseDto = {
      tournament: game.value.tournament,
      game: game.value.id,
      team: eventTeam.value!,
      minute: currentMinute,
    };

    if (eventType.value === 'goal') {
      const dto = {
        ...baseDto,
        player_number: playerNumber.value,
        own_goal: selectedGoalType.value === 'own_goal',
      };
      await gameService.assignGoal(dto);
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Golo registado', life: 3000 });
    } else if (eventType.value === 'card') {
      const cardTypeValue: CardType = cardType.value;
      const dto = {
        ...baseDto,
        player_number: cardTarget.value === 'player' ? playerNumber.value : null,
        card: cardTypeValue,
      };
      await gameService.assignCard(dto);
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Cartão registado', life: 3000 });
    } else if (eventType.value === 'foul') {
      const dto = {
        ...baseDto,
        player_number: cardTarget.value === 'player' ? playerNumber.value : null,
      };
      await gameService.assignFoul(dto);
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Falta registada', life: 3000 });
    }

    await loadGame();
    
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || 'Erro ao registar evento';
    toast.add({ severity: 'error', summary: 'Erro', detail: msg, life: 3000 });
  } finally {
    saving.value = false;
    closeEventDialog();
  }
}

async function startPeriod() {
  if (!game.value) return;
  
  try {
    const response = await gameService.updatePeriod(game.value.id, { action: 'start_new' });
    if (response.status === 200) {
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Período iniciado', life: 3000 });
      await loadGame();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || 'Erro ao iniciar período';
    toast.add({ severity: 'error', summary: 'Erro', detail: msg, life: 3000 });
  }
}

async function resumePeriod() {
  if (!game.value) return;
  
  try {
    const response = await gameService.updatePeriod(game.value.id, { action: 'resume' });
    if (response.status === 200) {
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Timer retomado', life: 3000 });
      await loadGame();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || 'Erro ao retomar timer';
    toast.add({ severity: 'error', summary: 'Erro', detail: msg, life: 3000 });
  }
}

async function stopTimer() {
  if (!game.value) return;
  
  try {
    const response = await gameService.updatePeriod(game.value.id, { action: 'stop' });
    if (response.status === 200) {
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Timer parado', life: 3000 });
      await loadGame();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || 'Erro ao parar timer';
    toast.add({ severity: 'error', summary: 'Erro', detail: msg, life: 3000 });
  }
}

async function endPeriod() {
  if (!game.value) return;
  
  const confirmed = confirm('Tem a certeza que deseja terminar o período?');
  if (!confirmed) return;
  
  try {
    const response = await gameService.updatePeriod(game.value.id, { action: 'end' });
    if (response.status === 200) {
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Período terminado', life: 3000 });
      await loadGame();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || 'Erro ao terminar período';
    toast.add({ severity: 'error', summary: 'Erro', detail: msg, life: 3000 });
  }
}

async function startPenalties() {
  if (!game.value) return;
  
  try {
    const response = await gameService.updatePeriod(game.value.id, { action: 'start_new', period: 5 });
    if (response.status === 200) {
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Iniciando penalidades', life: 3000 });
      await loadGame();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || 'Erro ao iniciar penalidades';
    toast.add({ severity: 'error', summary: 'Erro', detail: msg, life: 3000 });
  }
}

async function loadGame() {
  const response = await gameService.getGame(gameId);
  if (response.status === 200 && response.data && 'id' in response.data) {
    game.value = response.data as Game;
    events.value = response.data.events || [];
  } else {
    game.value = null;
  }
}

async function finishGame() {
  if (!game.value) return;
  
  const confirmed = confirm('Tem a certeza que deseja terminar este jogo?');
  if (!confirmed) return;
  
  try {
    const response = await gameService.updateGameStatus(game.value.id, GameStatus.Finished);
    if (response.status === 200) {
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Jogo terminado', life: 3000 });
      router.push('/admin');
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || 'Erro ao terminar jogo';
    toast.add({ severity: 'error', summary: 'Erro', detail: msg, life: 3000 });
  }
}

let refreshInterval: number = 0;
let timerTickInterval: number = 0;

onMounted(async () => {
  await Promise.all([
    teamStore.getTeams(),
    tournamentStore.getTournaments(),
  ]);
  await loadGame();
  
  refreshInterval = setInterval(loadGame, 10000);
  
  timerTickInterval = setInterval(() => {
    if (game.value?.timer_active) {
      game.value = { ...game.value };
    }
  }, 1000);
});
</script>

<style lang="scss" scoped>
.live-game {
  max-width: 1200px;
  margin: 0 auto;
}

:deep(.p-button) {
  font-weight: 600;
}
</style>
