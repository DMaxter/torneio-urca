<template>
  <div class="p-2 w-full mx-auto bg-stone-50 min-h-screen md:p-4">
    <div class="mb-3">
      <h1 class="text-lg font-bold text-stone-900 mb-0.5 md:text-xl">Calendário de Jogos</h1>
      <p class="text-stone-500 text-xs">Jogos agendados de todos os torneios</p>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <P-ProgressSpinner />
    </div>

    <div v-else-if="calendarDays.length === 0" class="text-center py-12 text-stone-400">
      <span class="material-symbols-outlined text-5xl mb-3 block">calendar_month</span>
      <p>Nenhum jogo agendado de momento.</p>
    </div>

    <div v-else class="grid gap-1.5" :class="gridCols">
      <div
        v-for="day in calendarDays"
        :key="day.date"
        class="border border-stone-200 rounded-lg overflow-hidden bg-white shadow-sm"
      >
        <div class="bg-stone-100 px-1.5 py-1 border-b border-stone-200">
          <span class="text-xs font-semibold text-stone-700 capitalize">{{ formatDateShort(day.date) }}</span>
        </div>
        <div class="divide-y divide-stone-100">
          <div
            v-for="slot in day.slots"
            :key="slot.time"
            class="px-1.5 py-0.5"
            :class="[getSlotClass(slot), { 'cursor-pointer hover:brightness-95 transition-all': slot.game }]"
            @click="slot.game && openGameResult(slot.game)"
          >
            <div class="flex items-center gap-1">
              <p class="text-xs font-semibold text-stone-400 shrink-0 w-8">{{ slot.time }}</p>
              <template v-if="slot.game">
                <span class="text-xs font-medium text-stone-700 truncate flex-1">{{ getHomeName(slot.game) }}</span>
                <span
                  class="text-xs font-bold tabular-nums px-1 rounded shrink-0 min-w-[2.5rem] text-center"
                  :class="getScoreClass(slot.game)"
                >{{ getScoreDisplay(slot.game) }}</span>
                <span class="text-xs font-medium text-stone-700 truncate flex-1 text-right">{{ getAwayName(slot.game) }}</span>
              </template>
              <template v-else>
                <span class="text-xs text-stone-300 italic">livre</span>
              </template>
            </div>
            <div v-if="slot.game" class="flex items-center gap-1 pl-8">
              <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="getColor(slot.game.tournament).dot"></span>
              <p class="text-xs text-stone-400 truncate flex-1 text-[0.65rem]">{{ getGameInfo(slot.game) }}</p>
              <span v-if="slot.game.status === GameStatus.InProgress" class="font-bold text-green-600 shrink-0 text-[0.65rem]">● AO VIVO</span>
              <span v-else-if="slot.game.status === GameStatus.Finished" class="font-semibold text-red-500 shrink-0 text-[0.65rem]">Terminado</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Game Result Dialog -->
    <GameResultDialog v-model:visible="gameResultVisible" :game="selectedGame" />
    <!-- Legend -->
    <div v-if="activeTournaments.length > 1" class="mt-6 flex flex-wrap gap-4">
      <div v-for="t in activeTournaments" :key="t.id" class="flex items-center gap-1.5 text-xs text-stone-500">
        <span class="w-2.5 h-2.5 rounded-full shrink-0" :class="getColor(t.id).dot"></span>
        {{ t.name }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useGameStore } from "@stores/games";
import { useGameDayStore } from "@stores/game_days";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { useTournamentColors } from "@/composables/useTournamentColors";
import { useDateFormatter } from "@/composables/useDateFormatter";
import type { Game } from "@router/backend/services/game/types";
import { GameStatus } from "@router/backend/services/game/types";
import * as gameService from "@router/backend/services/game";

const { getColor } = useTournamentColors();
const { formatDateShort } = useDateFormatter();

const gameStore = useGameStore();
const gameDayStore = useGameDayStore();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const loading = ref(true);

const gameResultVisible = ref(false);
const selectedGame = ref<Game | null>(null);

function openGameResult(game: Game) {
  selectedGame.value = game;
  gameResultVisible.value = true;
}

interface Slot {
  time: string;
  game: Game | null;
  datetime: Date;
}

interface CalendarDay {
  date: string;
  slots: Slot[];
}

const calendarDays = computed<CalendarDay[]>(() => {
  const scheduledGames = gameStore.games.filter(g => g.scheduled_date);

  const dateSlotMap = new Map<string, Map<string, { time: string; datetime: Date }>>();
  for (const day of gameDayStore.gameDays) {
    if (!dateSlotMap.has(day.date)) dateSlotMap.set(day.date, new Map());
    const slotMap = dateSlotMap.get(day.date)!;
    for (let i = 0; i < Number(day.num_games); i++) {
      const time = slotTime(day.start_time, i);
      if (!slotMap.has(time))
        slotMap.set(time, { time, datetime: slotDatetime(day.date, day.start_time, i) });
    }
  }

  const sortKey = (time: string) => {
    const [h, m] = time.split(":").map(Number);
    return h < 12 ? h * 60 + m + 24 * 60 : h * 60 + m;
  };

  return [...dateSlotMap.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, slotMap]) => {
      const slots: Slot[] = [...slotMap.values()]
        .sort((a, b) => sortKey(a.time) - sortKey(b.time))
        .map(({ time, datetime }) => ({
          time,
          datetime,
          game: scheduledGames.find(g => {
            const sd = new Date(g.scheduled_date!);
            return sd.getFullYear() === datetime.getFullYear() &&
                   sd.getMonth() === datetime.getMonth() &&
                   sd.getDate() === datetime.getDate() &&
                   sd.getHours() === datetime.getHours() &&
                   sd.getMinutes() === datetime.getMinutes();
          }) ?? null,
        }));
      return { date, slots };
    });
});

const gridCols = computed(() => {
  const n = calendarDays.value.length;
  if (n <= 2) return "grid-cols-1 sm:grid-cols-2";
  return "grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5";
});

const activeTournaments = computed(() => {
  const ids = new Set(
    calendarDays.value.flatMap(d => d.slots.filter(s => s.game).map(s => s.game!.tournament))
  );
  return tournamentStore.tournaments.filter(t => ids.has(t.id));
});

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



function getTeamName(id: string): string {
  return teamStore.teams.find(t => t.id === id)?.name ?? id;
}

function getHomeName(game: Game): string {
  return game.home_call ? getTeamName(game.home_call.team) : (game.home_placeholder ?? "?");
}

function getAwayName(game: Game): string {
  return game.away_call ? getTeamName(game.away_call.team) : (game.away_placeholder ?? "?");
}

function getScore(game: Game): { home: number; away: number } | null {
  if (game.status === GameStatus.Scheduled) return null;
  const homeName = getHomeName(game);
  const awayName = getAwayName(game);
  let home = 0, away = 0;
  for (const e of game.events) {
    if ("Goal" in e) {
      const goal = (e as { Goal?: { team_name: string } }).Goal;
      if (goal && goal.team_name === homeName) home++;
      else if (goal && goal.team_name === awayName) away++;
    }
  }
  return { home, away };
}

function getScoreDisplay(game: Game): string {
  if (game.status === GameStatus.Scheduled) return "- -";
  const score = getScore(game);
  if (!score) return "- -";
  return `${score.home} - ${score.away}`;
}

function getScoreClass(game: Game): string {
  if (game.status === GameStatus.InProgress) return "bg-green-100 text-green-700";
  if (game.status === GameStatus.Finished) return "bg-stone-100 text-stone-600";
  return "text-stone-400";
}

function getSlotClass(slot: Slot): string {
  if (!slot.game) return "";
  const game = slot.game;
  const border = getColor(game.tournament).slot;
  if (game.status === GameStatus.InProgress) return `bg-green-50 ${border}`;
  if (game.phase === "quarter_final") return `bg-sky-50 ${border}`;
  if (game.phase === "semi_final")    return `bg-emerald-50 ${border}`;
  if (game.phase === "third_place")   return `bg-violet-50 ${border}`;
  if (game.phase === "final")         return `bg-amber-50 ${border}`;
  return border;
}

const PHASE_LABEL: Record<string, string> = {
  quarter_final: "Quartos de Final",
  semi_final: "Meias Finais",
  third_place: "3º / 4º Lugar",
  final: "Final",
};

function getGroupName(game: Game): string {
  if (!game.home_call || !game.away_call) return "";
  return groupStore.groups.find(
    g => g.tournament === game.tournament &&
         g.teams.includes(game.home_call!.team) &&
         g.teams.includes(game.away_call!.team)
  )?.name ?? "";
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
    return num > 0 ? `${label} · Jogo ${num}` : label;
  }
  return [getGroupName(game), getRoundName(game)].filter(Boolean).join(" · ");
}

let pollInterval: ReturnType<typeof setInterval>;

async function pollGames() {
  await gameStore.forceGetGames();
}

onMounted(async () => {
  await Promise.all([
    gameStore.getGames(),
    gameDayStore.getGameDays(),
    groupStore.getGroups(),
    teamStore.getTeams(),
    tournamentStore.getTournaments(),
  ]);
  loading.value = false;
  pollInterval = setInterval(pollGames, 120000);
});

onUnmounted(() => clearInterval(pollInterval));
</script>
