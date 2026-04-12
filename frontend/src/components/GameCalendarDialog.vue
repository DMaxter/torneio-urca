<template>
  <P-Dialog v-model:visible="enabled" modal header="Calendário de Jogos" class="w-11/12 md:w-10/12 lg:w-9/12">
    <div class="flex flex-col gap-4">

      <!-- Last action feedback -->
      <div v-if="lastAction && !selectedGame" class="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-1.5 text-sm text-green-700">
        <span class="material-symbols-outlined text-base shrink-0">check_circle</span>
        <span class="flex-1">
          {{ lastAction.prefix }}
          <template v-for="(g, idx) in lastAction.games" :key="idx">
            <strong>{{ g.teams }}</strong><template v-if="g.date"> <em class="text-xs opacity-75"><strong>{{ g.date }}</strong></em></template>
            <template v-if="idx < lastAction.games.length - 1">{{ lastAction.separator }}</template>
          </template>
          {{ lastAction.suffix }}
        </span>
        <P-Button size="small" severity="secondary" class="shrink-0 invisible pointer-events-none" aria-hidden="true">
          <span class="material-symbols-outlined text-sm">sports_score</span>
          Registar Jogo
        </P-Button>
        <span class="material-symbols-outlined text-base cursor-pointer shrink-0" @click="lastAction = null">close</span>
      </div>

      <!-- Selection hint -->
      <div v-if="selectedGame" class="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-1.5 text-sm text-blue-700">
        <span class="material-symbols-outlined text-base shrink-0">info</span>
        <span class="flex-1 min-w-0">
          <strong>{{ getGameLabel(selectedGame) }}</strong>
          selecionado — clica numa slot vazia ou noutro jogo para trocar.
        </span>
        <P-Button size="small" severity="info" class="shrink-0" @click="onRegisterGame(selectedGame)">
          <span class="material-symbols-outlined text-sm">sports_score</span>
          Registar Jogo
        </P-Button>
        <span class="material-symbols-outlined text-base cursor-pointer shrink-0" @click="selectedGame = null; lastAction = null">close</span>
      </div>

      <!-- Calendar -->
      <div v-if="calendarDays.length > 0" class="grid gap-3" :class="gridCols">
        <div
          v-for="day in calendarDays"
          :key="day.date"
          class="border border-stone-200 rounded-lg overflow-hidden"
        >
          <div class="bg-stone-100 px-3 py-2 text-xs font-semibold text-stone-600">
            {{ formatDateShort(day.date) }}
          </div>
          <div class="divide-y divide-stone-100">
            <div
              v-for="slot in day.slots"
              :key="slot.time"
              class="px-3 py-2 min-h-[48px] cursor-pointer transition-colors"
              :class="getSlotClass(slot)"
              @click="onSlotClick(slot)"
            >
              <div class="flex items-center justify-between">
                <p class="text-xs font-semibold text-stone-400">{{ slot.time }}</p>
                <span
                  v-if="slot.game && !selectedGame"
                  class="material-symbols-outlined text-sm text-stone-300 hover:text-red-500 cursor-pointer"
                  v-tooltip.top="'Limpar agendamento'"
                  @click.stop="promptClearSchedule(slot.game)"
                >event_busy</span>
              </div>
              <template v-if="slot.game">
                <p class="text-xs font-medium text-stone-700 truncate leading-tight">
                  {{ getGameLabel(slot.game) }}
                </p>
                <p class="text-xs text-stone-400">{{ getGameInfo(slot.game) }}</p>
              </template>
              <template v-else>
                <p class="text-xs text-stone-300 italic">livre</p>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Unscheduled games grouped by tournament -->
      <div v-if="unscheduledByTournament.length > 0" class="flex flex-col gap-2">
        <div
          v-for="group in unscheduledByTournament"
          :key="group.tournamentId"
          class="border border-orange-200 rounded-lg overflow-hidden"
        >
          <div class="bg-orange-50 px-3 py-2 flex items-center justify-between">
            <span class="text-sm font-semibold text-orange-700">
              {{ group.name }} — {{ group.games.length }} jogo{{ group.games.length !== 1 ? 's' : '' }} sem data
            </span>
            <P-Button
              size="small"
              severity="warn"
              :disabled="!canDistribute(group.tournamentId)"
              :loading="distributingTournamentId === group.tournamentId"
              v-tooltip.left="!canDistribute(group.tournamentId) ? 'Só é possível distribuir quando todos os jogos do torneio estão sem data' : ''"
              @click="distribute(group.tournamentId)"
            >
              <span class="material-symbols-outlined">event</span>
              Distribuir
            </P-Button>
          </div>
          <div class="flex flex-wrap gap-2 p-3">
            <div
              v-for="game in group.games"
              :key="game.id"
              class="border rounded-lg px-2 py-1 text-xs cursor-pointer transition-colors"
              :class="selectedGame?.id === game.id
                ? 'bg-blue-100 border-blue-400 text-blue-700'
                : getPhaseChipClass(game)"
              @click="onUnscheduledClick(game)"
            >
              <div class="font-medium leading-tight">{{ getGameLabel(game) }}</div>
              <div class="opacity-60 leading-tight mt-0.5">{{ getGameInfo(game) }}</div>
            </div>
          </div>
        </div>
      </div>

      <p v-if="calendarDays.length === 0 && unscheduledByTournament.length === 0" class="text-sm text-stone-400 text-center py-2">
        Nenhum jogo nem dias de jogo configurados.
      </p>
    </div>

    <template #footer>
      <P-Button severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Fechar
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showClearConfirm" modal header="Confirmar remoção" class="w-11/12 md:w-5/12">
    <p class="text-sm">Tem a certeza que deseja retirar <strong>{{ gameToRemove ? getGameLabel(gameToRemove) : '' }}</strong> do calendário?</p>
    <template #footer>
      <P-Button severity="secondary" @click="showClearConfirm = false">Cancelar</P-Button>
      <P-Button severity="danger" @click="confirmClearSchedule">Retirar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { useGameStore } from "@stores/games";
import { useGameDayStore } from "@stores/game_days";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { useTournamentColors } from "@/composables/useTournamentColors";
import type { Game } from "@router/backend/services/game/types";

const { getColor } = useTournamentColors();
import { useDateFormatter } from "@/composables/useDateFormatter";

const { formatDateShort } = useDateFormatter();

const toast = useToast();
const emit = defineEmits<{ 'register-game': [game: Game] }>();
const enabled = defineModel<boolean>();

const gameStore = useGameStore();
const gameDayStore = useGameDayStore();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const selectedGame = ref<Game | null>(null);
const lastAction = ref<ActionLog | null>(null);
const distributingTournamentId = ref<string | null>(null);
const showClearConfirm = ref(false);
const gameToRemove = ref<Game | null>(null);

interface Slot {
  time: string;
  game: Game | null;
  datetime: Date;
}

interface ActionLog {
  prefix: string;
  games: { teams: string; date: string }[];
  separator?: string;
  suffix?: string;
}

interface CalendarDay {
  date: string;
  slots: Slot[];
}

interface GameEntry extends Game {
  groupName: string;
  round: number;
}

const calendarDays = ref<CalendarDay[]>([]);

const gridCols = computed(() => {
  const n = calendarDays.value.length;
  if (n <= 2) return "grid-cols-1 sm:grid-cols-2";
  return "grid-cols-2 lg:grid-cols-4";
});

const unscheduledByTournament = computed(() => {
  const map = new Map<string, Game[]>();
  for (const game of gameStore.games) {
    if (!game.scheduled_date) {
      if (!map.has(game.tournament)) map.set(game.tournament, []);
      map.get(game.tournament)!.push(game);
    }
  }
  return [...map.entries()]
    .map(([tournamentId, games]) => ({
      tournamentId,
      name: tournamentStore.tournaments.find(t => t.id === tournamentId)?.name ?? tournamentId,
      games,
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
});

function canDistribute(tournamentId: string): boolean {
  const total = gameStore.games.filter(g => g.tournament === tournamentId).length;
  if (total === 0) return false;
  const unscheduled = gameStore.games.filter(g => g.tournament === tournamentId && !g.scheduled_date).length;
  if (unscheduled !== total) return false;
  return gameDayStore.gameDays.length > 0;
}

function getTeamName(id: string) {
  return teamStore.teams.find(t => t.id === id)?.name ?? id;
}

function getTournamentName(id: string) {
  return tournamentStore.tournaments.find(t => t.id === id)?.name ?? id;
}

function getGroupName(game: Game): string {
  if (!game.home_call || !game.away_call) return "";
  const group = groupStore.groups.find(
    g => g.tournament === game.tournament &&
         g.teams.includes(game.home_call!.team) &&
         g.teams.includes(game.away_call!.team)
  );
  return group?.name ?? "";
}

function getRoundName(game: Game): string {
  if (!game.home_call || !game.away_call) return "";
  const group = groupStore.groups.find(
    g => g.tournament === game.tournament &&
         g.teams.includes(game.home_call!.team) &&
         g.teams.includes(game.away_call!.team)
  );
  if (!group) return "";
  const teams = group.teams.length % 2 === 1 ? [...group.teams, "bye"] : [...group.teams];
  const n = teams.length;
  let jornada = 1;
  for (let r = 0; r < n - 1; r++) {
    for (let i = 0; i < n / 2; i++) {
      const home = teams[i];
      const away = teams[n - 1 - i];
      if (home === "bye" || away === "bye") continue;
      if ((home === game.home_call!.team && away === game.away_call!.team) ||
          (home === game.away_call!.team && away === game.home_call!.team)) {
        return `Jornada ${jornada}`;
      }
      jornada++;
    }
    teams.splice(1, 0, teams.pop()!);
  }
  return "";
}

function getGameLabel(game: Game): string {
  if (game.home_call && game.away_call) {
    return `${getTeamName(game.home_call.team)} vs ${getTeamName(game.away_call.team)}`;
  }
  return `${game.home_placeholder ?? "?"} vs ${game.away_placeholder ?? "?"}`;
}

const PHASE_LABEL: Record<string, string> = {
  quarter_final: "Quartos de Final",
  semi_final: "Meias Finais",
  third_place: "3º e 4º Lugar",
  final: "Final",
};

function getKnockoutGameNumber(game: Game): number {
  const samePhase = gameStore.games
    .filter(g => g.tournament === game.tournament && g.phase === game.phase)
    .sort((a, b) => a.id.localeCompare(b.id));
  return samePhase.findIndex(g => g.id === game.id) + 1;
}

function getGameInfo(game: Game): string {
  if (game.phase !== "group") {
    const label = PHASE_LABEL[game.phase] ?? game.phase;
    const num = getKnockoutGameNumber(game);
    return num > 0 ? `${label}, Jogo ${num}` : label;
  }
  return [getGroupName(game), getRoundName(game)].filter(Boolean).join(", ");
}

function getGameLog(game: Game, datetime?: Date | null): { teams: string; date: string } {
  const dt = datetime ?? (game.scheduled_date ? new Date(game.scheduled_date) : null);
  const datePart = dt
    ? dt.toLocaleDateString("pt-PT", { weekday: "short", day: "numeric", month: "2-digit" }) +
      " " + String(dt.getHours()).padStart(2, "0") + ":" + String(dt.getMinutes()).padStart(2, "0") + "h"
    : "sem data";
  return { teams: getGameLabel(game), date: datePart };
}

function promptClearSchedule(game: Game) {
  gameToRemove.value = game;
  showClearConfirm.value = true;
}

async function confirmClearSchedule() {
  showClearConfirm.value = false;
  if (gameToRemove.value) await clearSchedule(gameToRemove.value);
  gameToRemove.value = null;
}

async function clearSchedule(game: Game) {
  const result = await gameStore.updateGame(game.id, null);
  if (!result.success) {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível limpar o agendamento", life: 3000 });
  } else {
    lastAction.value = { prefix: `Agendamento removido: `, games: [getGameLog(game)] };
  }
  loadCalendar(true);
}



// Build a global datetime key for deduplication and occupation checks
function datetimeKey(date: string, time: string): string {
  return `${date}T${time}`;
}

// Compute the correct Date for a slot, advancing the calendar date if hours overflow midnight
function slotDatetime(dateStr: string, startTime: string, slotIndex: number): Date {
  const [h, m] = startTime.split(":").map(Number);
  const totalMin = h * 60 + m + slotIndex * 60;
  const base = new Date(`${dateStr}T00:00:00`);
  base.setMinutes(base.getMinutes() + totalMin);
  return base;
}

function slotTime(startTime: string, slotIndex: number): string {
  const [h, m] = startTime.split(":").map(Number);
  const totalMin = h * 60 + m + slotIndex * 60;
  const hh = String(Math.floor(totalMin / 60) % 24).padStart(2, "0");
  const mm = String(totalMin % 60).padStart(2, "0");
  return `${hh}:${mm}`;
}

function loadCalendar(preserveAction = false) {
  selectedGame.value = null;
  if (!preserveAction) lastAction.value = null;

  // Merge all game days from all tournaments, deduplicated by datetime
  const dateSlotMap = new Map<string, Map<string, Slot>>();

  for (const day of gameDayStore.gameDays) {
    if (!dateSlotMap.has(day.date)) dateSlotMap.set(day.date, new Map());
    const slotMap = dateSlotMap.get(day.date)!;

    for (let i = 0; i < Number(day.num_games); i++) {
      const time = slotTime(day.start_time, i);
      if (!slotMap.has(time)) {
        // datetime uses slotDatetime so overflow past midnight gets correct timestamp
        slotMap.set(time, { time, game: null, datetime: slotDatetime(day.date, day.start_time, i) });
      }
    }
  }

  const scheduledGames = gameStore.games.filter(g => g.scheduled_date);

  calendarDays.value = [...dateSlotMap.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, slotMap]) => {
      // Sort slots so early-morning times (00-11h) appear after late-night times (12-23h)
      const sortKey = (time: string) => {
        const [h, m] = time.split(":").map(Number);
        return h < 12 ? h * 60 + m + 24 * 60 : h * 60 + m;
      };
      const slots = [...slotMap.values()].sort((a, b) => sortKey(a.time) - sortKey(b.time));
      for (const slot of slots) {
        slot.game = scheduledGames.find(g => {
          const sd = new Date(g.scheduled_date!);
          return sd.getFullYear() === slot.datetime.getFullYear() &&
                 sd.getMonth() === slot.datetime.getMonth() &&
                 sd.getDate() === slot.datetime.getDate() &&
                 sd.getHours() === slot.datetime.getHours() &&
                 sd.getMinutes() === slot.datetime.getMinutes();
        }) ?? null;
      }
      return { date, slots };
    });
}

function getPhaseSlotClass(game: Game): string {
  const border = getColor(game.tournament).slot;
  if (game.phase === "quarter_final") return `bg-sky-50 hover:bg-sky-100 ${border}`;
  if (game.phase === "semi_final")    return `bg-emerald-50 hover:bg-emerald-100 ${border}`;
  if (game.phase === "third_place")   return `bg-violet-50 hover:bg-violet-100 ${border}`;
  if (game.phase === "final")         return `bg-violet-50 hover:bg-violet-100 ${border}`;
  return `hover:bg-stone-50 ${border}`;
}

function getPhaseChipClass(game: Game): string {
  const border = getColor(game.tournament).chip;
  if (game.phase === "quarter_final") return `bg-sky-50 border ${border} text-sky-700`;
  if (game.phase === "semi_final")    return `bg-emerald-50 border ${border} text-emerald-700`;
  if (game.phase === "third_place")   return `bg-violet-50 border ${border} text-violet-700`;
  if (game.phase === "final")         return `bg-violet-50 border ${border} text-violet-700`;
  return `bg-white border ${border || "border-stone-200"} text-stone-600 hover:border-blue-300`;
}

function isSlotAllowedForGame(slot: Slot, game: Game): boolean {
  const dateKey = `${slot.datetime.getFullYear()}-${String(slot.datetime.getMonth() + 1).padStart(2, "0")}-${String(slot.datetime.getDate()).padStart(2, "0")}`;
  return gameDayStore.gameDays.some(d => d.tournament === game.tournament && d.date === dateKey);
}

function getSlotClass(slot: Slot) {
  if (slot.game && selectedGame.value?.id === slot.game.id) {
    return "bg-blue-50 border-l-2 border-blue-400";
  }
  if (slot.game) return getPhaseSlotClass(slot.game);
  if (selectedGame.value) {
    if (isSlotAllowedForGame(slot, selectedGame.value)) {
      return "hover:bg-green-50 border-l-2 border-dashed border-green-300";
    }
    return "opacity-40 cursor-not-allowed";
  }
  return "";
}

async function onSlotClick(slot: Slot) {
  if (!selectedGame.value) {
    if (slot.game) selectedGame.value = slot.game;
    return;
  }

  if (slot.game && slot.game.id === selectedGame.value.id) {
    selectedGame.value = null;
    return;
  }

  // Block move to a slot not configured for this game's tournament
  if (!isSlotAllowedForGame(slot, selectedGame.value)) {
    toast.add({ severity: "warn", summary: "Não permitido", detail: `Este dia não está disponível para o torneio ${getTournamentName(selectedGame.value.tournament)}`, life: 3000 });
    return;
  }

  const movingGame = selectedGame.value;
  selectedGame.value = null;

  if (slot.game) {
    const swapGame = slot.game;
    // Validate swap: swapGame must also be allowed in movingGame's current slot
    if (movingGame.scheduled_date) {
      const movingSlot = { datetime: new Date(movingGame.scheduled_date) } as Slot;
      if (!isSlotAllowedForGame(movingSlot, swapGame)) {
        toast.add({ severity: "warn", summary: "Não permitido", detail: `${getGameLabel(swapGame)} não pode ser movido para um dia do torneio ${getTournamentName(movingGame.tournament)}`, life: 3000 });
        loadCalendar(true);
        return;
      }
    }
    const [r1, r2] = await Promise.all([
      gameStore.updateGame(movingGame.id, slot.datetime),
      gameStore.updateGame(swapGame.id, movingGame.scheduled_date ? new Date(movingGame.scheduled_date) : null),
    ]);
    if (!r1.success || !r2.success) {
      toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível trocar os jogos", life: 3000 });
    } else {
      lastAction.value = {
        prefix: `Troca: `,
        games: [getGameLog(movingGame, slot.datetime), getGameLog(swapGame, movingGame.scheduled_date ? new Date(movingGame.scheduled_date) : null)],
        separator: ` ↔ `
      };
    }
  } else {
    const result = await gameStore.updateGame(movingGame.id, slot.datetime);
    if (!result.success) {
      toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível mover o jogo", life: 3000 });
    } else {
      lastAction.value = { prefix: `Movido: `, games: [getGameLog(movingGame, slot.datetime)] };
    }
  }

  loadCalendar(true);
}

function onUnscheduledClick(game: Game) {
  selectedGame.value = selectedGame.value?.id === game.id ? null : game;
}

function buildOrderedGames(tournamentId: string): GameEntry[] {
  const groups = groupStore.groups.filter(g => g.tournament === tournamentId);
  const tournamentGames = gameStore.games.filter(g => g.tournament === tournamentId);

  // Each entry is one game (1 game per jornada), ordered sequentially per group
  const groupJornadas: GameEntry[][] = groups.map(group => {
    const teams = group.teams.length % 2 === 1 ? [...group.teams, "bye"] : [...group.teams];
    const n = teams.length;
    const jornadas: GameEntry[] = [];

    for (let r = 0; r < n - 1; r++) {
      for (let i = 0; i < n / 2; i++) {
        const home = teams[i];
        const away = teams[n - 1 - i];
        if (home !== "bye" && away !== "bye") {
          const game = tournamentGames.find(
            g => (g.home_call?.team === home && g.away_call?.team === away) ||
                 (g.home_call?.team === away && g.away_call?.team === home)
          );
          if (game) jornadas.push({ ...game, groupName: group.name, round: jornadas.length + 1 });
        }
      }
      teams.splice(1, 0, teams.pop()!);
    }
    return jornadas;
  });

  // Interleave by jornada index: jornada 1 of all groups, then jornada 2, etc.
  const maxJornadas = Math.max(...groupJornadas.map(g => g.length), 0);
  const result: GameEntry[] = [];
  for (let j = 0; j < maxJornadas; j++) {
    for (const groupJ of groupJornadas) {
      if (groupJ[j]) result.push(groupJ[j]);
    }
  }

  const phaseOrder: Record<string, number> = { quarter_final: 0, semi_final: 1, third_place: 2, final: 3 };
  const knockoutGames = tournamentGames
    .filter(g => g.phase !== "group")
    .sort((a, b) => (phaseOrder[a.phase] ?? 99) - (phaseOrder[b.phase] ?? 99));
  for (const g of knockoutGames) {
    result.push({ ...g, groupName: "", round: 0 });
  }

  return result;
}

async function distribute(tournamentId: string) {
  distributingTournamentId.value = tournamentId;

  // Build slot list using only game days configured for this tournament, sorted by datetime
  const slotSet = new Map<string, { date: string; time: string; datetime: Date }>();
  for (const day of gameDayStore.gameDays.filter(d => d.tournament === tournamentId)) {
    for (let i = 0; i < Number(day.num_games); i++) {
      const time = slotTime(day.start_time, i);
      const key = datetimeKey(day.date, time);
      if (!slotSet.has(key)) {
        slotSet.set(key, { date: day.date, time, datetime: slotDatetime(day.date, day.start_time, i) });
      }
    }
  }

  const allSlots = [...slotSet.values()].sort((a, b) => a.datetime.getTime() - b.datetime.getTime());

  // Find occupied slots (any game, any tournament)
  const occupiedKeys = new Set(
    gameStore.games
      .filter(g => g.scheduled_date)
      .map(g => {
        const sd = new Date(g.scheduled_date!);
        const hh = String(sd.getHours()).padStart(2, "0");
        const mm = String(sd.getMinutes()).padStart(2, "0");
        const yyyy = sd.getFullYear();
        const mo = String(sd.getMonth() + 1).padStart(2, "0");
        const dd = String(sd.getDate()).padStart(2, "0");
        return datetimeKey(`${yyyy}-${mo}-${dd}`, `${hh}:${mm}`);
      })
  );

  const freeSlots = allSlots.filter(s => !occupiedKeys.has(datetimeKey(s.date, s.time)));
  const ordered = buildOrderedGames(tournamentId).filter(g => !g.scheduled_date);

  let allOk = true;
  for (let i = 0; i < Math.min(ordered.length, freeSlots.length); i++) {
    const result = await gameStore.updateGame(ordered[i].id, freeSlots[i].datetime);
    if (!result.success) allOk = false;
  }

  distributingTournamentId.value = null;

  if (allOk) {
    const assigned = Math.min(ordered.length, freeSlots.length);
    lastAction.value = {
      prefix: `${getTournamentName(tournamentId)}: ${assigned} jogo${assigned !== 1 ? 's' : ''} distribuídos com sucesso`,
      games: []
    };
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Alguns jogos não foram agendados", life: 4000 });
  }

  loadCalendar(true);
}

function onRegisterGame(game: Game) {
  emit("register-game", game);
  close();
}

function close() {
  enabled.value = false;
  selectedGame.value = null;
  lastAction.value = null;
  calendarDays.value = [];
}



onMounted(async () => {
  await Promise.all([
    gameStore.getGames(),
    gameDayStore.getGameDays(),
    groupStore.getGroups(),
    teamStore.getTeams(),
    tournamentStore.getTournaments(),
  ]);
  loadCalendar();
});
</script>
