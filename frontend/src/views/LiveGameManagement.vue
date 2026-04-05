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

    <!-- Current Minute Display -->
    <div v-if="game" class="mb-4 p-3 bg-white border border-stone-300 rounded-lg text-center">
      <div class="text-sm text-stone-500">Minuto atual</div>
      <div class="text-4xl font-bold text-stone-900">{{ currentMinute }}'</div>
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
          <div class="grid grid-cols-2 gap-2">
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
          </div>
        </div>

        <!-- Away Team Box -->
        <div class="bg-white border-4 border-red-500 rounded-xl p-4 shadow-lg" :class="{'border-red-600': selectedTeam === game.away_call?.team}">
          <div class="text-center mb-3">
            <div class="text-lg font-bold text-red-800">{{ getTeamName(game.away_call?.team) }}</div>
            <div class="text-5xl font-bold text-stone-900 mt-2">{{ awayScore }}</div>
          </div>
          <div class="grid grid-cols-2 gap-2">
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
            <div class="font-bold text-stone-600 text-xl w-16 text-center">{{ getEventMinute(event) }}'</div>
            <div class="flex-1">
              <div class="text-base font-semibold text-stone-900">{{ getEventDescription(event) }}</div>
              <div v-if="getEventTeamName(event)" class="text-sm text-stone-500">{{ getEventTeamName(event) }}</div>
            </div>
            <div class="text-2xl">{{ getEventIcon(event) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-12 text-stone-400">
      <span class="material-symbols-outlined text-6xl mb-4">sports_soccer</span>
      <p>Jogo não encontrado</p>
    </div>

    <!-- Event Dialog -->
    <PDialog v-model:visible="eventDialogVisible" modal :header="eventDialogTitle" class="w-11/12 md:w-1/2 lg:w-1/3">
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
            
            <div v-else>
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

        <!-- Minute Input (common) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-stone-700 mb-2">Minuto</label>
          <div class="flex gap-2 items-center">
            <P-Button 
              icon="remove" 
              severity="secondary" 
              @click="minute = Math.max(0, minute - 1)"
            />
            <P-InputNumber 
              v-model="minute" 
              :min="0" 
              :max="99" 
              class="flex-1 text-2xl text-center"
              inputClass="text-center"
            />
            <P-Button 
              icon="add" 
              severity="secondary" 
              @click="minute = Math.min(99, minute + 1)"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex gap-2 w-full justify-between">
          <P-Button severity="secondary" @click="closeEventDialog">Cancelar</P-Button>
          <P-Button 
            :severity="eventType === 'goal' ? 'success' : 'warning'" 
            :loading="saving"
            :disabled="!canSubmitEvent"
            @click="submitEvent"
          >
            {{ eventType === 'goal' ? 'Marcar Golo' : 'Dar Cartão' }}
          </P-Button>
        </div>
      </template>
    </PDialog>
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
import type { Game, GameEvent, Goal, Foul } from "@router/backend/services/game/types";
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
const selectedTeam = ref<string | null>(null); // Used in template for highlighting
const eventTeam = ref<string | null>(null); // The team for the event being created
const eventType = ref<'goal' | 'card' | null>(null);
const minute = ref<number>(0);
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
  return `Registar Cartão - ${teamName}`;
});

const homeTeamId = computed(() => game.value?.home_call?.team || '');
const awayTeamId = computed(() => game.value?.away_call?.team || '');

const homeScore = computed(() => {
  return events.value.filter(e => 'Goal' in e && !(e as Goal).own_goal && (e as Goal).team_name === getTeamName(homeTeamId.value)).length;
});

const awayScore = computed(() => {
  return events.value.filter(e => 'Goal' in e && !(e as Goal).own_goal && (e as Goal).team_name === getTeamName(awayTeamId.value)).length;
});

const currentMinute = computed(() => {
  if (events.value.length === 0) return 0;
  const lastEvent = sortedEvents.value[0];
  return getEventMinute(lastEvent);
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
  // This would ideally fetch staff for the selected team
  // For now, return empty or a placeholder
  return [];
});

const canSubmitEvent = computed(() => {
  if (!eventTeam.value || !eventType.value || minute.value < 0) return false;
  
  if (eventType.value === 'goal') {
    if (selectedGoalType.value === 'own_goal') return true; // No player selection needed for own goals in our simplified version
    return playerNumber.value !== null;
  }
  
  if (eventType.value === 'card') {
    if (cardTarget.value === 'player') {
      return playerNumber.value !== null && cardType.value;
    } else {
      return staffId.value !== null && cardType.value;
    }
  }
  
  return false;
});

const sortedEvents = computed(() => {
  return [...events.value].sort((a, b) => {
    return getEventMinute(a) - getEventMinute(b);
  });
});

// Methods
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

function getEventBorderClass(event: GameEvent): string {
  if ('Goal' in event) {
    return (event as Goal).own_goal ? 'border-orange-200 bg-orange-50' : 'border-green-200 bg-green-50';
  }
  if ('Foul' in event) {
    return 'border-red-200 bg-red-50';
  }
  return '';
}

function getEventIcon(event: GameEvent): string {
  if ('Goal' in event) {
    return (event as Goal).own_goal ? '🔨' : '⚽';
  }
  if ('Foul' in event) {
    return (event as Foul).card === 'Yellow' ? '🟨' : '🟥';
  }
  return '';
}

function getEventMinute(event: GameEvent): number {
  if ('Goal' in event) return (event as Goal).minute;
  if ('Foul' in event) return (event as Foul).minute;
  return 0;
}

function getEventTeamName(event: GameEvent): string {
  if ('Goal' in event) return (event as Goal).team_name;
  if ('Foul' in event) return (event as Foul).team_name;
  return '';
}

function getEventDescription(event: GameEvent): string {
  if ('Goal' in event) {
    const goal = event as Goal;
    return goal.own_goal ? `Auto-golo de ${goal.player_name}` : `Golo de ${goal.player_name}`;
  }
  if ('Foul' in event) {
    const foul = event as Foul;
    const cardText = foul.card === 'Yellow' ? 'Amarelo' : 'Vermelho';
    const target = foul.staff_name && foul.staff_name !== '' ? foul.staff_name : foul.player_name;
    return `${target} - Cartão ${cardText}`;
  }
  return '';
}

function openEventDialog(teamId: string | undefined, type: 'goal' | 'card') {
  if (!teamId) return;
  
  selectedTeam.value = teamId;
  eventTeam.value = teamId;
  eventType.value = type;
  selectedGoalType.value = 'regular';
  cardType.value = 'Yellow';
  cardTarget.value = 'player';
  playerNumber.value = null;
  staffId.value = null;
  minute.value = currentMinute.value;
  eventDialogVisible.value = true;
}

function closeEventDialog() {
  eventDialogVisible.value = false;
}

async function submitEvent() {
  if (!canSubmitEvent.value || !game.value) return;
  
  saving.value = true;
  
  try {
    const baseDto = {
      tournament: game.value.tournament,
      game: game.value.id,
      team: eventTeam.value!,
      minute: minute.value,
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
      const dto = {
        ...baseDto,
        player_number: cardTarget.value === 'player' ? playerNumber.value : null,
        card: cardType.value,
      };
      await gameService.assignCard(dto);
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Cartão registado', life: 3000 });
    }

    // Reload game to get updated events
    await loadGame();
    
    // Reset minute to current match time
    minute.value = currentMinute.value;
    
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || 'Erro ao registar evento';
    toast.add({ severity: 'error', summary: 'Erro', detail: msg, life: 3000 });
  } finally {
    saving.value = false;
    closeEventDialog();
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

// Refresh events periodically
let refreshInterval: number = 0;

onMounted(async () => {
  await Promise.all([
    teamStore.getTeams(),
    tournamentStore.getTournaments(),
  ]);
  await loadGame();
  // Refresh every 10 seconds
  refreshInterval = setInterval(loadGame, 10000);
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
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
