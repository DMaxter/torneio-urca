<template>
  <P-Dialog v-model:visible="enabled" modal header="Calendário de Jogos" class="w-11/12 md:w-10/12 lg:w-9/12">
    <div class="flex flex-col gap-4">

      <!-- Tournament selector -->
      <P-FloatLabel variant="on">
        <P-Select
          id="tournament"
          v-model="selectedTournament"
          :options="tournamentStore.tournaments"
          optionLabel="name"
          optionValue="id"
          fluid
          @change="loadCalendar"
        />
        <label for="tournament">Torneio</label>
      </P-FloatLabel>

      <!-- Last action feedback -->
      <div v-if="lastAction && !selectedGame" class="flex items-start gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-2 text-sm text-green-700">
        <span class="material-symbols-outlined text-base shrink-0 mt-0.5">check_circle</span>
        <span v-html="lastAction" class="flex-1"></span>
        <span class="material-symbols-outlined text-base cursor-pointer shrink-0" @click="lastAction = ''">close</span>
      </div>

      <!-- Selection hint -->
      <div v-if="selectedGame" class="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 text-sm text-blue-700">
        <span class="material-symbols-outlined text-base">info</span>
        <span>
          <strong>{{ getGameLabel(selectedGame) }}</strong>
          selecionado — clica numa slot vazia ou noutro jogo para trocar.
        </span>
        <span class="material-symbols-outlined text-base cursor-pointer ml-auto" @click="selectedGame = null">close</span>
      </div>

      <!-- Calendar -->
      <div v-if="calendarDays.length > 0" class="grid gap-3" :class="gridCols">
        <div
          v-for="day in calendarDays"
          :key="day.date"
          class="border border-stone-200 rounded-lg overflow-hidden"
        >
          <div class="bg-stone-100 px-3 py-2 text-xs font-semibold text-stone-600">
            {{ formatDate(day.date) }}
          </div>
          <div class="divide-y divide-stone-100">
            <div
              v-for="slot in day.slots"
              :key="slot.time"
              class="px-3 py-2 min-h-[48px] cursor-pointer transition-colors"
              :class="getSlotClass(slot)"
              @click="onSlotClick(slot, day.date)"
            >
              <div class="flex items-center justify-between">
                <p class="text-xs font-semibold text-stone-400">{{ slot.time }}</p>
                <span
                  v-if="slot.game && !selectedGame"
                  class="material-symbols-outlined text-sm text-stone-300 hover:text-red-500 cursor-pointer"
                  v-tooltip.top="'Limpar agendamento'"
                  @click.stop="clearSchedule(slot.game)"
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

      <!-- Unscheduled games -->
      <div v-if="unscheduledGames.length > 0" class="border border-orange-200 rounded-lg overflow-hidden">
        <div class="bg-orange-50 px-3 py-2 flex items-center justify-between">
          <span class="text-sm font-semibold text-orange-700">
            {{ unscheduledGames.length }} jogo{{ unscheduledGames.length !== 1 ? 's' : '' }} sem data
          </span>
          <P-Button
            size="small"
            severity="warn"
            :disabled="!canDistribute"
            :loading="distributing"
            v-tooltip.left="!canDistribute ? 'Só é possível distribuir quando todos os jogos estão sem data' : ''"
            @click="distribute"
          >
            <span class="material-symbols-outlined">event</span>
            Distribuir
          </P-Button>
        </div>
        <div class="flex flex-wrap gap-2 p-3">
          <div
            v-for="game in unscheduledGames"
            :key="game.id"
            class="border rounded-lg px-2 py-1 text-xs cursor-pointer transition-colors"
            :class="selectedGame?.id === game.id
              ? 'bg-blue-100 border-blue-400 text-blue-700'
              : getPhaseChipClass(game)"
            @click="onUnscheduledClick(game)"
          >
            {{ getGameLabel(game) }}
            <span class="opacity-50 ml-1">{{ getGameBadge(game) }}</span>
          </div>
        </div>
      </div>

      <p v-if="selectedTournament && calendarDays.length === 0" class="text-sm text-stone-400 text-center py-2">
        Nenhum jogo agendado nem dias configurados para este torneio.
      </p>
    </div>

    <template #footer>
      <P-Button severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Fechar
      </P-Button>
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
import type { Game } from "@router/backend/services/game/types";

const toast = useToast();
const enabled = defineModel<boolean>();

const gameStore = useGameStore();
const gameDayStore = useGameDayStore();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const selectedTournament = ref<string>("");
const selectedGame = ref<Game | null>(null);
const lastAction = ref<string>("");
const distributing = ref(false);

interface Slot {
  time: string;
  game: Game | null;
  datetime: Date;
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
  if (n <= 4) return "grid-cols-2 lg:grid-cols-4";
  return "grid-cols-2 lg:grid-cols-4";
});

const unscheduledGames = computed(() =>
  gameStore.games.filter(g =>
    g.tournament === selectedTournament.value && !g.scheduled_date
  )
);

const canDistribute = computed(() => {
  if (!selectedTournament.value) return false;
  const total = gameStore.games.filter(g => g.tournament === selectedTournament.value).length;
  if (total === 0) return false;
  const days = gameDayStore.gameDays.filter(d => d.tournament === selectedTournament.value);
  if (days.length === 0) return false;
  return unscheduledGames.value.length === total;
});

function getTeamName(id: string) {
  return teamStore.teams.find(t => t.id === id)?.name ?? id;
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
  for (let r = 0; r < n - 1; r++) {
    for (let i = 0; i < n / 2; i++) {
      const home = teams[i];
      const away = teams[n - 1 - i];
      if ((home === game.home_call!.team && away === game.away_call!.team) ||
          (home === game.away_call!.team && away === game.home_call!.team)) {
        return `Jornada ${r + 1}`;
      }
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

function getGameInfo(game: Game): string {
  if (game.phase !== "group") {
    return PHASE_LABEL[game.phase] ?? game.phase;
  }
  return [getGroupName(game), getRoundName(game)].filter(Boolean).join(", ");
}

function getGameBadge(game: Game): string {
  const group = getGroupName(game);
  const round = getRoundName(game);
  const groupLetter = group ? group.replace(/[^A-Za-z0-9]/g, "").slice(-1).toUpperCase() : "";
  const roundNum = round ? round.replace(/\D/g, "") : "";
  if (groupLetter && roundNum) return `${groupLetter}${roundNum}`;
  if (groupLetter) return groupLetter;
  if (roundNum) return `J${roundNum}`;
  return "";
}

function formatGameLabel(game: Game, datetime?: Date): string {
  const dt = datetime ?? (game.scheduled_date ? new Date(game.scheduled_date) : null);
  const datePart = dt
    ? dt.toLocaleDateString("pt-PT", { weekday: "short", day: "numeric", month: "2-digit" }) +
      " " + String(dt.getHours()).padStart(2, "0") + ":" + String(dt.getMinutes()).padStart(2, "0") + "h"
    : "sem data";
  const group = getGroupName(game);
  const round = getRoundName(game);
  const groupRound = [group, round].filter(Boolean).join(" · ");
  const teams = `<strong>${getGameLabel(game)}</strong>`;
  const groupRoundPart = groupRound ? ` <em class="text-xs opacity-75">${groupRound}</em>` : "";
  const datePart2 = datePart ? ` <em class="text-xs opacity-75"><strong>${datePart}</strong></em>` : "";
  return `${teams}${groupRoundPart}${datePart2}`;
}

async function clearSchedule(game: Game) {
  const result = await gameStore.updateGame(game.id, null);
  if (!result.success) {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível limpar o agendamento", life: 3000 });
  } else {
    lastAction.value = `Agendamento removido: ${formatGameLabel(game)}`;
  }
  loadCalendar(true);
}

function formatDate(dateKey: string) {
  return new Date(dateKey + "T12:00:00").toLocaleDateString("pt-PT", {
    weekday: "short", day: "numeric", month: "short",
  });
}

function loadCalendar(preserveAction = false) {
  selectedGame.value = null;
  if (!preserveAction) lastAction.value = "";
  const days = gameDayStore.gameDays
    .filter(d => d.tournament === selectedTournament.value)
    .sort((a, b) => a.date.localeCompare(b.date));

  const scheduledGames = gameStore.games.filter(
    g => g.tournament === selectedTournament.value && g.scheduled_date
  );

  calendarDays.value = days.map(day => {
    const slots: Slot[] = [];
    for (let i = 0; i < day.num_games; i++) {
      const [h, m] = day.start_time.split(":").map(Number);
      const totalMin = h * 60 + m + i * 60;
      const hh = String(Math.floor(totalMin / 60) % 24).padStart(2, "0");
      const mm = String(totalMin % 60).padStart(2, "0");
      const time = `${hh}:${mm}`;
      const datetime = new Date(`${day.date}T${time}:00`);

      const game = scheduledGames.find(g => {
        const sd = new Date(g.scheduled_date!);
        return sd.getFullYear() === datetime.getFullYear() &&
               sd.getMonth() === datetime.getMonth() &&
               sd.getDate() === datetime.getDate() &&
               sd.getHours() === datetime.getHours() &&
               sd.getMinutes() === datetime.getMinutes();
      }) ?? null;

      slots.push({ time, game, datetime });
    }
    return { date: day.date, slots };
  });
}

function getPhaseSlotClass(phase: string): string {
  if (phase === "quarter_final") return "bg-sky-50 hover:bg-sky-100";
  if (phase === "semi_final")    return "bg-emerald-50 hover:bg-emerald-100";
  if (phase === "third_place")   return "bg-violet-50 hover:bg-violet-100";
  if (phase === "final")         return "bg-violet-50 hover:bg-violet-100";
  return "hover:bg-stone-50";
}

function getPhaseChipClass(game: Game): string {
  if (game.phase === "quarter_final") return "bg-sky-50 border-sky-300 text-sky-700 hover:border-sky-400";
  if (game.phase === "semi_final")    return "bg-emerald-50 border-emerald-300 text-emerald-700 hover:border-emerald-400";
  if (game.phase === "third_place")   return "bg-violet-50 border-violet-300 text-violet-700 hover:border-violet-400";
  if (game.phase === "final")         return "bg-violet-50 border-violet-300 text-violet-700 hover:border-violet-400";
  return "bg-white border-stone-200 text-stone-600 hover:border-blue-300";
}

function getSlotClass(slot: Slot) {
  if (slot.game && selectedGame.value?.id === slot.game.id) {
    return "bg-blue-50 border-l-2 border-blue-400";
  }
  if (slot.game && slot.game.phase !== "group") return getPhaseSlotClass(slot.game.phase);
  if (slot.game) return "hover:bg-stone-50";
  if (selectedGame.value) return "hover:bg-green-50 border-l-2 border-dashed border-green-300";
  return "";
}

async function onSlotClick(slot: Slot, _date: string) {
  if (!selectedGame.value) {
    if (slot.game) selectedGame.value = slot.game;
    return;
  }

  if (slot.game && slot.game.id === selectedGame.value.id) {
    selectedGame.value = null;
    return;
  }

  const movingGame = selectedGame.value;
  selectedGame.value = null;

  if (slot.game) {
    const swapGame = slot.game;
    const [r1, r2] = await Promise.all([
      gameStore.updateGame(movingGame.id, slot.datetime),
      gameStore.updateGame(swapGame.id, movingGame.scheduled_date ? new Date(movingGame.scheduled_date) : null),
    ]);
    if (!r1.success || !r2.success) {
      toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível trocar os jogos", life: 3000 });
    } else {
      lastAction.value = `Troca: ${formatGameLabel(movingGame, slot.datetime)} ↔ ${formatGameLabel(swapGame, movingGame.scheduled_date ? new Date(movingGame.scheduled_date) : undefined)}`;
    }
  } else {
    const result = await gameStore.updateGame(movingGame.id, slot.datetime);
    if (!result.success) {
      toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível mover o jogo", life: 3000 });
    } else {
      lastAction.value = `Movido: ${formatGameLabel(movingGame, slot.datetime)}`;
    }
  }

  loadCalendar(true);
}

function onUnscheduledClick(game: Game) {
  selectedGame.value = selectedGame.value?.id === game.id ? null : game;
}

function buildOrderedGames(): GameEntry[] {
  const groups = groupStore.groups.filter(g => g.tournament === selectedTournament.value);
  const tournamentGames = gameStore.games.filter(g => g.tournament === selectedTournament.value);

  const groupRounds: GameEntry[][] = groups.map(group => {
    const teams = group.teams.length % 2 === 1 ? [...group.teams, "bye"] : [...group.teams];
    const n = teams.length;
    const ordered: GameEntry[] = [];

    for (let r = 0; r < n - 1; r++) {
      for (let i = 0; i < n / 2; i++) {
        const home = teams[i];
        const away = teams[n - 1 - i];
        if (home !== "bye" && away !== "bye") {
          const game = tournamentGames.find(
            g => (g.home_call?.team === home && g.away_call?.team === away) ||
                 (g.home_call?.team === away && g.away_call?.team === home)
          );
          if (game) ordered.push({ ...game, groupName: group.name, round: r + 1 });
        }
      }
      teams.splice(1, 0, teams.pop()!);
    }
    return ordered;
  });

  const maxRounds = Math.max(...groupRounds.map(gr => gr.length), 0);
  const result: GameEntry[] = [];
  for (let i = 0; i < maxRounds; i++) {
    for (const gr of groupRounds) {
      if (gr[i]) result.push(gr[i]);
    }
  }

  // Append knockout games in phase order after all group games
  const phaseOrder: Record<string, number> = { quarter_final: 0, semi_final: 1, third_place: 2, final: 3 };
  const knockoutGames = tournamentGames
    .filter(g => g.phase !== "group")
    .sort((a, b) => (phaseOrder[a.phase] ?? 99) - (phaseOrder[b.phase] ?? 99));
  for (const g of knockoutGames) {
    result.push({ ...g, groupName: "", round: 0 });
  }

  return result;
}

async function distribute() {
  distributing.value = true;
  const days = gameDayStore.gameDays
    .filter(d => d.tournament === selectedTournament.value)
    .sort((a, b) => a.date.localeCompare(b.date));

  const daySlots = days.map(d => ({
    date: d.date,
    startTime: d.start_time,
    capacity: Number(d.num_games),
    games: [] as GameEntry[],
  }));

  const ordered = buildOrderedGames();
  let slotIdx = 0;

  for (const game of ordered) {
    while (slotIdx < daySlots.length && daySlots[slotIdx].games.length >= daySlots[slotIdx].capacity) {
      slotIdx++;
    }
    if (slotIdx < daySlots.length) {
      daySlots[slotIdx].games.push(game);
    }
  }

  let allOk = true;
  for (const slot of daySlots) {
    for (let i = 0; i < slot.games.length; i++) {
      const game = slot.games[i];
      const [h, m] = slot.startTime.split(":").map(Number);
      const totalMinutes = h * 60 + m + i * 60;
      const hh = Math.floor(totalMinutes / 60) % 24;
      const mm = totalMinutes % 60;
      const dt = new Date(`${slot.date}T${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:00`);
      const result = await gameStore.updateGame(game.id, dt);
      if (!result.success) allOk = false;
    }
  }

  distributing.value = false;

  if (allOk) {
    const assigned = daySlots.reduce((s, d) => s + d.games.length, 0);
    lastAction.value = `${assigned} jogo${assigned !== 1 ? 's' : ''} distribuídos com sucesso`;
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Alguns jogos não foram agendados", life: 4000 });
  }

  loadCalendar(true);
}

function close() {
  enabled.value = false;
  selectedTournament.value = "";
  selectedGame.value = null;
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
});
</script>
