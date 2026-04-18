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
      <div v-if="game.current_period < 5" class="bg-white border border-stone-300 rounded-xl p-4 text-center">
        <div class="text-sm text-stone-500">Cronómetro</div>
        <div class="flex items-center justify-center gap-2 mt-1">
          <div class="text-4xl font-bold text-stone-900 ml-6">{{ timerDisplay }}</div>
          <P-Button 
            v-if="!game.timer_active"
            icon="material-symbols-outlined" 
            text 
            rounded 
            class="text-stone-400 hover:text-stone-600"
            @click="openAdjustClock"
          >
            <span class="material-symbols-outlined text-xl">edit</span>
          </P-Button>
        </div>

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
          :severity="getNextPeriodSeverity()"
          size="large"
          :disabled="!canProceedToNextPeriod"
          v-tooltip.top="getNextPeriodTooltip(game.current_period)"
          @click="endPeriod"
        />
        <P-Button
          v-else-if="game.current_period === 4"
          :label="getNextPeriodLabel(game.current_period)"
          :severity="getNextPeriodSeverity()"
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
            <div class="flex items-center justify-center gap-6 mt-2">
              <div class="flex flex-col items-center">
                <div class="text-6xl font-black text-stone-900">{{ homeScore }}</div>
                <div v-if="isShootout" class="text-xl font-bold text-stone-400 mt-1">
                  Pen: {{ homePenaltyScore }}
                  <span class="ml-1">
                    <template v-for="(scored, idx) in homePenalties.slice(-5)" :key="idx">
                      <span v-if="scored">⚽</span>
                      <span v-else>❌</span>
                    </template>
                  </span>
                </div>
              </div>
              <div v-if="game.current_period > 0 && !isShootout" class="flex flex-col items-center">
                <div class="text-[10px] font-bold text-stone-500 uppercase tracking-widest mb-1">Faltas</div>
                <div 
                  class="text-3xl font-black px-4 py-1 rounded-xl border-2 transition-all duration-500"
                  :class="homeFoulLimitReached ? 'bg-red-600 text-white border-red-700 shadow-lg shadow-red-200 animate-pulse' : 'bg-stone-50 text-stone-400 border-stone-100'"
                >
                  {{ homeFouls }}
                </div>
                <div v-if="homeFoulLimitReached" class="text-[9px] font-bold text-red-600 uppercase mt-1">Livre Direto s/ Barreira</div>
              </div>
            </div>
          </div>
          <div class="grid gap-2" :class="isShootout ? 'grid-cols-2' : 'grid-cols-3'">
            <P-Button
              :label="isShootout ? '⚽ Penalti' : '⚽ Golo'"
              size="large"
              class="bg-green-600 hover:bg-green-700 text-white border-none"
              @click="openEventDialog(game.home_call?.team, isShootout ? 'penalty' : 'goal')"
            />
            <P-Button
              label="🟨 Cartão"
              size="large"
              class="bg-yellow-500 hover:bg-yellow-600 text-white border-none"
              @click="openEventDialog(game.home_call?.team, 'card')"
            />
            <P-Button
              v-if="!isShootout"
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
            <div class="flex items-center justify-center gap-6 mt-2">
              <div class="flex flex-col items-center">
                <div class="text-6xl font-black text-stone-900">{{ awayScore }}</div>
                <div v-if="isShootout" class="text-xl font-bold text-stone-400 mt-1">
                  Pen: {{ awayPenaltyScore }}
                  <span class="ml-1">
                    <template v-for="(scored, idx) in awayPenalties.slice(-5)" :key="idx">
                      <span v-if="scored">⚽</span>
                      <span v-else>❌</span>
                    </template>
                  </span>
                </div>
              </div>
              <div v-if="game.current_period > 0 && !isShootout" class="flex flex-col items-center">
                <div class="text-[10px] font-bold text-stone-500 uppercase tracking-widest mb-1">Faltas</div>
                <div 
                  class="text-3xl font-black px-4 py-1 rounded-xl border-2 transition-all duration-500"
                  :class="awayFoulLimitReached ? 'bg-red-600 text-white border-red-700 shadow-lg shadow-red-200 animate-pulse' : 'bg-stone-50 text-stone-400 border-stone-100'"
                >
                  {{ awayFouls }}
                </div>
                <div v-if="awayFoulLimitReached" class="text-[9px] font-bold text-red-600 uppercase mt-1">Livre Direto s/ Barreira</div>
              </div>
            </div>
          </div>
          <div class="grid gap-2" :class="isShootout ? 'grid-cols-2' : 'grid-cols-3'">
            <P-Button
              :label="isShootout ? '⚽ Penalti' : '⚽ Golo'"
              size="large"
              class="bg-green-600 hover:bg-green-700 text-white border-none"
              @click="openEventDialog(game.away_call?.team, isShootout ? 'penalty' : 'goal')"
            />
            <P-Button
              label="🟨 Cartão"
              size="large"
              class="bg-yellow-500 hover:bg-yellow-600 text-white border-none"
              @click="openEventDialog(game.away_call?.team, 'card')"
            />
            <P-Button
              v-if="!isShootout"
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
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-stone-900">Eventos do Jogo</h2>
          <P-Button severity="secondary" size="small" @click="manualEventDialogVisible = true">
            <span class="material-symbols-outlined mr-1">post_add</span>
            Evento Manual
          </P-Button>
        </div>


        <div v-if="sortedEventsWithIndex.length === 0" class="text-stone-400 text-center py-8">
          Nenhum evento registado
        </div>

        <div v-else class="space-y-2">
          <div v-for="item in sortedEventsWithIndex" :key="item.index" 
               class="flex items-center gap-3 p-3 rounded-lg border-2 group"
               :class="getEventBorderClass(item.event)">
            <div class="font-bold text-stone-600 text-xl w-24 text-center shrink-0">
              <div>{{ getEventTimeDisplay(item.event) }}</div>
              <div class="text-xs text-stone-400 font-normal">{{ getEventTimestampFormatted(item.event) }}</div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-base font-semibold text-stone-900">{{ getEventDescription(item.event) }}</div>
              <div v-if="getEventMetadata(item.event)" class="text-xs text-stone-400">{{ getEventMetadata(item.event) }}</div>
            </div>
            <div class="text-2xl shrink-0">{{ getEventIcon(item.event) }}</div>
            <button 
              class="material-symbols-outlined text-red-600 cursor-pointer hover:bg-red-50 rounded-full p-1 transition-colors shrink-0"
              @click="deleteEvent(item.index)"
              v-tooltip.top="'Eliminar evento'"
            >delete</button>
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
                @click="() => { selectedGoalType = 'own_goal'; playerNumber = null; }"
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

        <!-- Penalty Dialog -->
        <div v-if="eventType === 'penalty'">
          <div class="mb-4">
            <label class="block text-sm font-medium text-stone-700 mb-2">Resultado do Penalti</label>
            <div class="flex gap-2">
              <P-Button
                label="✅ Marcou"
                :severity="penaltyScored ? 'success' : 'secondary'"
                class="flex-1"
                @click="penaltyScored = true"
              />
              <P-Button
                label="❌ Falhou"
                :severity="!penaltyScored ? 'danger' : 'secondary'"
                class="flex-1"
                @click="penaltyScored = false"
              />
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-stone-700 mb-2">Jogador</label>
            <div class="grid grid-cols-3 sm:grid-cols-5 gap-2">
              <P-Button
                v-for="num in availableShirtNumbers"
                :key="num"
                :label="`#${num}`"
                :severity="playerNumber === num ? (penaltyScored ? 'success' : 'danger') : 'secondary'"
                class="text-lg py-3"
                @click="playerNumber = num"
              />
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
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <P-Button 
                  v-for="staff in staffOptions" 
                  :key="staff.id"
                  :severity="staffId === staff.id ? 'success' : 'secondary'"
                  class="py-3 px-2 h-auto"
                  @click="staffId = staff.id"
                >
                  <div class="flex flex-col items-center w-full">
                    <span class="text-sm font-bold truncate w-full text-center">{{ staff.shortName }}</span>
                    <span class="text-[10px] opacity-70 uppercase tracking-wider">{{ staff.type }}</span>
                  </div>
                </P-Button>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-3 p-3 bg-red-50 rounded-lg border border-red-100">
            <P-Checkbox v-model="isDirectFreeKick" :binary="true" inputId="isCardDFK" />
            <label for="isCardDFK" class="text-sm font-bold text-red-800 cursor-pointer select-none">
              Livre Direto? <span class="font-normal opacity-70">(Conta para o limite de 5 faltas)</span>
            </label>
          </div>
        </div>

        <!-- Foul Dialog -->
        <div v-if="eventType === 'foul'">
          <div class="mb-4">
            <div class="grid grid-cols-3 sm:grid-cols-5 gap-2 mb-4">
              <P-Button 
                v-for="num in availableShirtNumbers" 
                :key="num"
                :label="`#${num}`" 
                :severity="playerNumber === num ? 'warning' : 'secondary'"
                class="text-lg py-3"
                @click="playerNumber = num"
              />
            </div>
            <div class="flex items-center gap-3 p-3 bg-orange-50 rounded-lg border border-orange-100">
              <P-Checkbox v-model="isDirectFreeKick" :binary="true" inputId="isDFK" />
              <label for="isDFK" class="text-sm font-bold text-orange-800 cursor-pointer select-none">
                Livre Direto? <span class="font-normal opacity-70">(Conta para o limite de 5 faltas)</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex gap-2 w-full justify-between">
          <P-Button severity="secondary" @click="closeEventDialog">Cancelar</P-Button>
          <P-Button 
            :severity="eventType === 'goal' || eventType === 'penalty' ? 'success' : 'warning'" 
            :loading="saving"
            :disabled="!canSubmitEvent"
            @click="submitEvent"
          >
            {{ 
              eventType === 'goal' ? 'Marcar Golo' : 
              eventType === 'foul' ? 'Registar Falta' : 
              eventType === 'penalty' ? (penaltyScored ? 'Registar Penalti Marcado' : 'Registar Penalti Falhado') :
              'Atribuir Cartão' 
            }}
          </P-Button>
        </div>
      </template>
    </P-Dialog>
    
    <!-- Manual Event Dialog -->
    <P-Dialog v-model:visible="manualEventDialogVisible" modal header="Evento Manual" class="w-11/12 md:w-[450px]">
      <div class="p-2 md:p-4">
        <div class="mb-4">
          <label class="block text-sm font-medium text-stone-700 mb-2">Descrição do Evento</label>
          <P-Textarea 
            v-model="manualEventDescription" 
            rows="4" 
            class="w-full text-base" 
            placeholder="Ex: Substituição múltipla, Incidente, etc."
            autoResize
          />
        </div>
      </div>

      <template #footer>
        <div class="flex gap-2 w-full justify-between">
          <P-Button severity="secondary" @click="manualEventDialogVisible = false">Cancelar</P-Button>
          <P-Button 
            severity="primary" 
            :loading="saving"
            :disabled="!manualEventDescription.trim()"
            @click="submitManualEvent"
          >
            Registar Evento
          </P-Button>
        </div>
      </template>
    </P-Dialog>

    <!-- Adjust Clock Dialog -->
    <P-Dialog v-model:visible="adjustClockDialogVisible" modal header="Ajustar Cronómetro" class="w-11/12 md:w-[400px]">
      <div class="p-2 md:p-4">
        <div class="mb-4 flex flex-col sm:flex-row gap-4">
          <div class="flex-1">
            <label class="block text-sm font-medium text-stone-700 mb-2">Minutos</label>
            <P-InputNumber 
              v-model="adjMinute" 
              :min="0" 
              :max="30" 
              showButtons 
              buttonLayout="horizontal" 
              class="w-full"
              inputClass="w-full text-center font-bold text-xl"
            />
          </div>
          <div class="flex-1">
            <label class="block text-sm font-medium text-stone-700 mb-2">Segundos</label>
            <P-InputNumber 
              v-model="adjSecond" 
              :min="0" 
              :max="59" 
              showButtons 
              buttonLayout="horizontal" 
              class="w-full"
              inputClass="w-full text-center font-bold text-xl"
            />
          </div>
        </div>

        <p class="text-xs text-stone-500">
          Nota: Isto irá ajustar o cronómetro para o tempo total decorrido indicado.
        </p>
      </div>
      <template #footer>
        <div class="flex gap-2 w-full justify-between">
          <P-Button severity="secondary" @click="adjustClockDialogVisible = false">Cancelar</P-Button>
          <P-Button 
            severity="warning" 
            :loading="saving"
            @click="saveClockAdjustment"
          >
            Atualizar Tempo
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
import { useStaffStore } from "@stores/staff";
import * as gameService from "@router/backend/services/game";
import type { Game, GameEvent } from "@router/backend/services/game/types";
import { GameStatus } from "@router/backend/services/game/types";
import type { CardType } from "@router/backend/services/game/types";
import { useApiErrorToast } from "@/composables/useApiErrorToast";
import { getStaffTypeLabel } from "@/utils";

const router = useRouter();
const route = useRoute();
const toast = useToast();
const gameStore = useGameStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const staffStore = useStaffStore();
const { handleApiError } = useApiErrorToast();

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
const isDirectFreeKick = ref(false);
const penaltyScored = ref(true);

// Manual event state
const manualEventDialogVisible = ref(false);
const manualEventDescription = ref("");

// Clock adjustment state
const adjustClockDialogVisible = ref(false);
const adjMinute = ref(0);
const adjSecond = ref(0);


const eventDialogTitle = computed(() => {
  if (!eventType.value || !eventTeam.value) return '';
  const teamName = getTeamName(eventTeam.value);
  if (eventType.value === 'goal') {
    return selectedGoalType.value === 'own_goal' ? 'Registar Auto-Golo' : `Registar Golo - ${teamName}`;
  }
  if (eventType.value === 'card') {
    return `Atribuir Cartão - ${teamName}`;
  }
  if (eventType.value === 'penalty') {
    return `Registar Penalti - ${teamName}`;
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
      const goal = (e as { Goal: { team_name: string } }).Goal;
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
      const goal = (e as { Goal: { team_name: string } }).Goal;
      return goal.team_name === awayName;
    }
    return false;
  }).length;
});

function countFouls(teamId: string, currentPeriod: number) {
  if (!game.value) return 0;
  const teamName = getTeamName(teamId);
  return events.value.filter(e => {
    if ('Foul' in e) {
      const foul = (e as { Foul: FoulEvent }).Foul;
      if (foul.team_name !== teamName) return false;
      
      // Every foul that leads to a direct free kick counts. 
      // For cards it is always a free kick foul.
      if (!foul.is_direct_free_kick && !foul.card) return false;
      
      const p = foul.period;
      if (currentPeriod <= 1) {
        return p <= 1;
      } else {
        // Reset when moving from 1st to 2nd, but not to following (extra time)
        return p >= 2;
      }
    }
    return false;
  }).length;
}

const homeFouls = computed(() => countFouls(homeTeamId.value, game.value?.current_period || 0));
const awayFouls = computed(() => countFouls(awayTeamId.value, game.value?.current_period || 0));

const homeFoulLimitReached = computed(() => homeFouls.value >= 5);
const awayFoulLimitReached = computed(() => awayFouls.value >= 5);

const isShootout = computed(() => game.value?.current_period === 5);

const homePenaltyScore = computed(() => {
  if (!game.value) return 0;
  const homeName = getTeamName(homeTeamId.value);
  return events.value.filter(e => {
    if ('Penalty' in e) {
      const p = (e as { Penalty: { team_name: string; scored: boolean } }).Penalty;
      return p.team_name === homeName && p.scored;
    }
    return false;
  }).length;
});

const awayPenaltyScore = computed(() => {
  if (!game.value) return 0;
  const awayName = getTeamName(awayTeamId.value);
  return events.value.filter(e => {
    if ('Penalty' in e) {
      const p = (e as { Penalty: { team_name: string; scored: boolean } }).Penalty;
      return p.team_name === awayName && p.scored;
    }
    return false;
  }).length;
});

const homePenalties = computed(() => {
  if (!game.value) return [];
  const homeName = getTeamName(homeTeamId.value);
  return events.value
    .filter(e => {
      if ('Penalty' in e) {
        const p = (e as { Penalty: { team_name: string; scored: boolean } }).Penalty;
        return p.team_name === homeName;
      }
      return false;
    })
    .map(e => (e as { Penalty: { team_name: string; scored: boolean } }).Penalty.scored);
});

const awayPenalties = computed(() => {
  if (!game.value) return [];
  const awayName = getTeamName(awayTeamId.value);
  return events.value
    .filter(e => {
      if ('Penalty' in e) {
        const p = (e as { Penalty: { team_name: string; scored: boolean } }).Penalty;
        return p.team_name === awayName;
      }
      return false;
    })
    .map(e => (e as { Penalty: { team_name: string; scored: boolean } }).Penalty.scored);
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
  if (!game.value || !eventTeam.value) return [];
  const call = eventTeam.value === homeTeamId.value ? game.value.home_call : game.value.away_call;
  if (!call || !call.staff) return [];

  return call.staff.map(id => {
    const s = staffStore.staff.find(staff => staff.id === id);
    const name = s?.name || 'Desconhecido';
    const firstNames = name.split(' ');
    const shortName = firstNames.length > 1 ? `${firstNames[0]} ${firstNames[firstNames.length - 1]}` : name;
    
    return {
      id,
      label: `${name} (${getStaffTypeLabel(s?.staff_type)})`,
      shortName,
      type: getStaffTypeLabel(s?.staff_type)
    };
  });
});

const hasStaffForTeam = computed(() => {
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

  if (eventType.value === 'penalty') {
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
    const activeElapsed = (now - startTime) / 1000;
    elapsed += activeElapsed;
  }
  // Cap elapsed time at the period's duration
  const duration = getDurationForPeriod(game.value.current_period);
  if (duration > 0 && elapsed > duration) {
    elapsed = duration;
  }
  return elapsed;
});

const timerDisplay = computed(() => {
  if (!game.value) return '00:00';
  const durationSeconds = getDurationForPeriod(game.value.current_period);
  const remaining = Math.max(0, durationSeconds - currentElapsedSeconds.value);
  const mins = Math.floor(remaining / 60);
  const secs = Math.floor(remaining % 60);
  const tenths = Math.floor((remaining % 1) * 10);
  if (mins === 0) {
    // Show seconds and tenths
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

function getNextPeriodSeverity(): string {
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
    const goal = (event as { Goal: { own_goal: boolean } }).Goal;
    return goal.own_goal ? 'border-orange-200 bg-orange-50' : 'border-green-200 bg-green-50';
  }
  if ('Penalty' in event) {
    const p = (event as { Penalty: { scored: boolean } }).Penalty;
    return p.scored ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50';
  }
  if ('Foul' in event) {
    const foul = (event as { Foul: { card: string | null } }).Foul;
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
  if ('Manual' in event) {
    return 'border-stone-200 bg-stone-50';
  }
  return '';

}

function getEventIcon(event: GameEvent): string {
  if ('Goal' in event) {
    const goal = (event as { Goal: { own_goal: boolean } }).Goal;
    return goal.own_goal ? '🥅' : '⚽';
  }
  if ('Penalty' in event) {
    const p = (event as { Penalty: { scored: boolean } }).Penalty;
    return p.scored ? '✅' : '❌';
  }
  if ('Foul' in event) {
    const foul = (event as { Foul: { card: string | null } }).Foul;
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
  if ('Manual' in event) {
    return '📝';
  }
  return '';

}

function getEventDescription(event: GameEvent): string {
  if ('Goal' in event) {
    const goal = (event as { Goal: { own_goal: boolean; own_goal_committed_by?: string; player_name?: string } }).Goal;
    if (goal.own_goal) {
      const committedBy = goal.own_goal_committed_by || 'Equipa adversária';
      return `Auto-golo de ${committedBy}`;
    }
    const name = goal.player_name || 'Jogador desconhecido';
    return `Golo de ${name}`;
  }
  if ('Penalty' in event) {
    const p = (event as { Penalty: { scored: boolean; player_name: string } }).Penalty;
    const action = p.scored ? 'marcou' : 'falhou';
    return `${p.player_name} ${action} penalti`;
  }
  if ('Foul' in event) {
    const foul = (event as { Foul: FoulEvent }).Foul;
    const displayName = foul.staff_name || foul.player_name || 'Desconhecido';
    
    if (foul.card === null || foul.card === undefined) {
      const suffix = foul.is_direct_free_kick ? ' (Livre Direto)' : '';
      return `${displayName} - Falta${suffix}`;
    }
    const cardText = foul.card === 'Yellow' ? 'Amarelo' : 'Vermelho';
    return `${displayName} - Cartão ${cardText}`;
  }
  if ('PeriodStart' in event) {
    const ps = (event as { PeriodStart: { period: number } }).PeriodStart;
    const isOvertime = ps.period >= 3 && ps.period <= 4;
    return isOvertime ? `Início do Prolongamento (${ps.period}º)` : `Início do ${ps.period}º Período`;
  }
  if ('PeriodResume' in event) {
    const pr = (event as { PeriodResume: { period: number } }).PeriodResume;
    const isOvertime = pr.period >= 3 && pr.period <= 4;
    return isOvertime ? `Retoma do Prolongamento (${pr.period}º)` : `Retoma do ${pr.period}º Período`;
  }
  if ('PeriodEnd' in event) {
    const pe = (event as { PeriodEnd: { period: number } }).PeriodEnd;
    const isOvertime = pe.period >= 3 && pe.period <= 4;
    return isOvertime ? `Fim do Prolongamento (${pe.period}º)` : `Fim do ${pe.period}º Período`;
  }
  if ('PeriodPause' in event) {
    const pp = (event as { PeriodPause: { period: number } }).PeriodPause;
    const isOvertime = pp.period >= 3 && pp.period <= 4;
    return isOvertime ? `Pausa no Prolongamento (${pp.period}º)` : `Pausa no ${pp.period}º Período`;
  }
  if ('Manual' in event) {
    return (event as { Manual: { description: string } }).Manual.description;
  }
  return '';

}

function getEventPeriod(event: GameEvent): number {
  if ('Goal' in event) {
    const goal = (event as { Goal: { period?: number } }).Goal;
    return goal.period || 0;
  }
  if ('Penalty' in event) {
    const p = (event as { Penalty: { period?: number } }).Penalty;
    return p.period || 0;
  }
  if ('Foul' in event) {
    const foul = (event as { Foul: { period?: number } }).Foul;
    return foul.period || 0;
  }
  if ('PeriodStart' in event) {
    return (event as { PeriodStart: { period: number } }).PeriodStart.period || 0;
  }
  if ('PeriodResume' in event) {
    return (event as { PeriodResume: { period: number } }).PeriodResume.period || 0;
  }
  if ('PeriodEnd' in event) {
    return (event as { PeriodEnd: { period: number } }).PeriodEnd.period || 0;
  }
  if ('PeriodPause' in event) {
    return (event as { PeriodPause: { period: number } }).PeriodPause.period || 0;
  }
  if ('Manual' in event) {
    return (event as { Manual: { period: number } }).Manual.period || 0;
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

  if ('PeriodStart' in event) {
    const ps = (event as { PeriodStart: { period: number } }).PeriodStart;
    return `P${ps.period}`;
  }
  if ('PeriodEnd' in event) {
    const pe = (event as { PeriodEnd: { period: number } }).PeriodEnd;
    return `P${pe.period}`;
  }
  if ('PeriodPause' in event) {
    const pp = (event as { PeriodPause: { period: number } }).PeriodPause;
    return `P${pp.period}`;
  }
  if ('PeriodResume' in event) {
    const pr = (event as { PeriodResume: { period: number } }).PeriodResume;
    return `P${pr.period}`;
  }

  let minute = 0;
  let second = 0;
  if ('Goal' in event) {
    const goal = (event as { Goal: { minute: number; second?: number } }).Goal;
    minute = goal.minute || 0;
    second = goal.second !== undefined ? goal.second : 0;
  } else if ('Foul' in event) {
    const foul = (event as { Foul: { minute: number; second?: number } }).Foul;
    minute = foul.minute || 0;
    second = foul.second !== undefined ? foul.second : 0;
  } else if ('Manual' in event) {
    const manual = (event as { Manual: { minute: number; second?: number } }).Manual;
    minute = manual.minute || 0;
    second = manual.second !== undefined ? manual.second : 0;
  }

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
    const utc = raw.endsWith('Z') ? raw : raw + 'Z';
    return new Date(utc).getTime();
  };
  
  if ('Goal' in event) {
    const goal = (event as { Goal: { timestamp: string } }).Goal;
    return getTs(goal.timestamp);
  }
  if ('Penalty' in event) {
    const p = (event as { Penalty: { timestamp: string } }).Penalty;
    return getTs(p.timestamp);
  }
  if ('Foul' in event) {
    const foul = (event as { Foul: { timestamp: string } }).Foul;
    return getTs(foul.timestamp);
  }
  if ('PeriodStart' in event) {
    const ps = (event as { PeriodStart: { timestamp: string } }).PeriodStart;
    return getTs(ps.timestamp);
  }
  if ('PeriodResume' in event) {
    const pr = (event as { PeriodResume: { timestamp: string } }).PeriodResume;
    return getTs(pr.timestamp);
  }
  if ('PeriodEnd' in event) {
    const pe = (event as { PeriodEnd: { timestamp: string } }).PeriodEnd;
    return getTs(pe.timestamp);
  }
  if ('PeriodPause' in event) {
    const pp = (event as { PeriodPause: { timestamp: string } }).PeriodPause;
    return getTs(pp.timestamp);
  }
  if ('Manual' in event) {
    const manual = (event as { Manual: { timestamp: string } }).Manual;
    return getTs(manual.timestamp);
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

const sortedEventsWithIndex = computed(() => {
  const eventsWithIndex = events.value.map((e, i) => ({ event: e, index: i }));
  return eventsWithIndex.sort((a, b) => {
    return getEventTimestamp(b.event) - getEventTimestamp(a.event);
  });
});

function getEventTeamName(event: GameEvent): string {
  if ('Goal' in event) {
    const goal = (event as { Goal: { team_name: string } }).Goal;
    return goal.team_name;
  }
  if ('Penalty' in event) {
    const p = (event as { Penalty: { team_name: string } }).Penalty;
    return p.team_name;
  }
  if ('Foul' in event) {
    const foul = (event as { Foul: { team_name: string } }).Foul;
    return foul.team_name;
  }
  return '';
}

function openEventDialog(teamId: string | undefined, type: 'goal' | 'card' | 'foul' | 'penalty') {
  if (!teamId) return;
  
  selectedTeam.value = teamId;
  eventTeam.value = teamId;
  eventType.value = type;
  selectedGoalType.value = 'regular';
  cardType.value = 'Yellow';
  cardTarget.value = 'player';
  playerNumber.value = null;
  staffId.value = null;
  // Default to true for cards, false for fouls
  isDirectFreeKick.value = type === 'card';
  penaltyScored.value = true;
  eventDialogVisible.value = true;
}

function closeEventDialog() {
  eventDialogVisible.value = false;
}

async function submitEvent() {
  if (!canSubmitEvent.value || !game.value) return;
  
  saving.value = true;
  
  try {
    const totalSeconds = Math.floor(currentElapsedSeconds.value);
    const currentMinute = Math.floor(totalSeconds / 60);
    const currentSecond = totalSeconds % 60;
    
    const baseDto = {
      tournament: game.value.tournament,
      game: game.value.id,
      team: eventTeam.value!,
      minute: currentMinute,
      second: currentSecond,
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
      const dto: AssignCardDto = {
        ...baseDto,
        player_number: cardTarget.value === 'player' ? playerNumber.value : null,
        staff_id: cardTarget.value === 'staff' ? staffId.value : null,
        card: cardTypeValue,
        is_direct_free_kick: isDirectFreeKick.value,
      };
      await gameService.assignCard(dto);
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Cartão registado', life: 3000 });
    } else if (eventType.value === 'foul') {
      const dto: AssignFoulDto = {
        ...baseDto,
        player_number: playerNumber.value,
        is_direct_free_kick: isDirectFreeKick.value,
      };
      await gameService.assignFoul(dto);
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Falta registada', life: 3000 });
    } else if (eventType.value === 'penalty') {
      const dto: AssignPenaltyDto = {
        ...baseDto,
        player_number: playerNumber.value!,
        scored: penaltyScored.value,
      };
      await gameService.assignPenalty(dto);
      const msg = penaltyScored.value ? 'Penalti marcado' : 'Penalti falhado';
      toast.add({ severity: 'success', summary: 'Sucesso', detail: msg, life: 3000 });
    }

    await loadGame();
    await gameStore.forceGetGames();
    
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao registar evento');
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
      await gameStore.forceGetGames();
    }
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao iniciar período');
  }
}

async function resumePeriod() {
  if (!game.value) return;
  
  try {
    const action = game.value.period_elapsed_seconds === 0 ? 'start_new' : 'resume';
    const response = await gameService.updatePeriod(game.value.id, { action });
    if (response.status === 200) {
      const msg = action === 'start_new' ? 'Período iniciado' : 'Cronómetro retomado';
      toast.add({ severity: 'success', summary: 'Sucesso', detail: msg, life: 3000 });
      await loadGame();
      await gameStore.forceGetGames();
    }
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao retomar cronómetro');
  }
}

async function stopTimer() {
  if (!game.value) return;
  
  try {
    const response = await gameService.updatePeriod(game.value.id, { action: 'stop' });
    if (response.status === 200) {
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Cronómetro parado', life: 3000 });
      await loadGame();
      await gameStore.forceGetGames();
    }
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao parar cronómetro');
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
      await gameStore.forceGetGames();
    }
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao terminar período');
  }
}

async function startPenalties() {
  if (!game.value) return;
  
  try {
    const response = await gameService.updatePeriod(game.value.id, { action: 'start_new', period: 5 });
    if (response.status === 200) {
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Iniciando penalidades', life: 3000 });
      await loadGame();
      await gameStore.forceGetGames();
    }
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao iniciar penalidades');
  }
}

async function loadGame() {
  const response = await gameService.getGame(gameId);
  if (response.status === 200 && response.data && 'id' in response.data) {
    game.value = response.data as Game;
    events.value = response.data.events || [];

    // Update game in store so other views (e.g. CalendarView) react reactively
    const idx = gameStore.games.findIndex(g => g.id === gameId);
    if (idx !== -1) gameStore.games[idx] = response.data as Game;

    // Stop polling if game is finished
    if (game.value.status === GameStatus.Finished && refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = 0;
    }
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
      await gameStore.forceGetGames();
      router.push('/admin');
    }
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao terminar jogo');
  }
}

async function deleteEvent(eventIndex: number) {
  if (!game.value) return;
  
  const confirmed = confirm('Tem a certeza que deseja eliminar este evento?');
  if (!confirmed) return;
  
  try {
    const response = await gameService.deleteGameEvent(game.value.id, eventIndex);
    if (response.status === 204) {
      toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Evento eliminado', life: 3000 });
      await loadGame();
      await gameStore.forceGetGames();
    }
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao eliminar evento');
  }
}

function openAdjustClock() {
  if (!game.value) return;
  const duration = getDurationForPeriod(game.value.current_period);
  const remaining = Math.max(0, duration - currentElapsedSeconds.value);
  
  adjMinute.value = Math.floor(remaining / 60);
  adjSecond.value = Math.floor(remaining % 60);
  adjustClockDialogVisible.value = true;
}

async function saveClockAdjustment() {
  if (!game.value) return;
  
  saving.value = true;
  try {
    const duration = getDurationForPeriod(game.value.current_period);
    const targetRemaining = adjMinute.value * 60 + adjSecond.value;
    const targetElapsed = Math.max(0, duration - targetRemaining);
    
    await gameService.updatePeriod(game.value.id, { 
      action: 'set_seconds', 
      seconds: targetElapsed 
    });
    
    toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Cronómetro ajustado', life: 3000 });
    await loadGame();
    await gameStore.forceGetGames();
    adjustClockDialogVisible.value = false;
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao ajustar cronómetro');
  } finally {
    saving.value = false;
  }
}

async function submitManualEvent() {
  if (!game.value || !manualEventDescription.value.trim()) return;
  
  saving.value = true;
  try {
    await gameService.addManualEvent(game.value.id, manualEventDescription.value.trim());
    toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Evento registado', life: 3000 });
    await loadGame();
    await gameStore.forceGetGames();
    manualEventDescription.value = '';
    manualEventDialogVisible.value = false;
  } catch (e: unknown) {
    handleApiError(e, 'Erro ao registar evento manual');
  } finally {
    saving.value = false;
  }
}

let refreshInterval: number = 0;

let timerTickInterval: number = 0;

onMounted(async () => {
  await Promise.all([
    teamStore.getTeams(),
    tournamentStore.getTournaments(),
    staffStore.getStaff(),
  ]);
  await loadGame();
  
  refreshInterval = setInterval(loadGame, 10000);
  
  timerTickInterval = setInterval(async () => {
    if (game.value?.timer_active) {
      const duration = getDurationForPeriod(game.value.current_period);
      const elapsed = game.value.period_elapsed_seconds;
      const startTime = game.value.timer_started_at ? Date.parse(game.value.timer_started_at + 'Z') : 0;
      const activeElapsed = startTime > 0 ? (Date.now() - startTime) / 1000 : 0;
      const totalElapsed = elapsed + activeElapsed;
      
      // Auto-stop timer when it reaches 0
      if (duration > 0 && totalElapsed >= duration) {
        await stopTimer();
      } else {
        game.value = { ...game.value };
      }
    }
  }, 100);
});

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval);
  if (timerTickInterval) clearInterval(timerTickInterval);
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
