<template>
  <div class="px-4 py-6">
    <div class="grid grid-cols-1 lg:grid-cols-[1fr_minmax(0,480px)_1fr] gap-4 items-start">

      <!-- COLUNA ESQUERDA — grupos pares (A, C, E…) -->
      <aside class="space-y-4">
        <ClassificationPanel
          v-for="c in classificationsLeft"
          :key="c.group_id"
          :classification="c"
        />
      </aside>

      <!-- COLUNA CENTRAL — jogos + live -->
      <div class="space-y-4 min-w-0">

        <!-- JOGOS DE HOJE -->
        <section class="bg-white border border-stone-200 rounded-2xl shadow-sm overflow-hidden">
          <div class="bg-stone-100 px-4 py-2.5 flex items-center gap-2 text-sm font-semibold text-stone-600">
            <span class="material-symbols-outlined text-base">today</span>
            Jogos de Hoje
          </div>
          <div v-if="todayGames.length === 0" class="text-sm text-stone-400 text-center py-8">
            Sem jogos agendados para hoje.
          </div>
          <div class="divide-y divide-stone-100">
            <div
              v-for="game in todayGames"
              :key="game.id"
              class="flex items-center gap-2 px-4 py-3 transition-colors"
              :class="game.status === GameStatus.InProgress ? 'bg-green-50' : ''"
            >
              <span class="text-xs text-stone-400 w-10 shrink-0 font-mono tabular-nums">{{ getGameHour(game) }}</span>
              <span class="w-2 h-2 rounded-full shrink-0" :style="{ background: getTournamentColor(game.tournament) }"></span>
              <span class="text-sm font-medium text-stone-700 text-right flex-1 truncate">{{ getHomeName(game) }}</span>
              <span
                class="px-2 py-0.5 rounded-md text-xs font-bold tabular-nums shrink-0 min-w-[52px] text-center"
                :class="getScoreClass(game)"
              >{{ getScoreDisplay(game) }}</span>
              <span class="text-sm font-medium text-stone-700 text-left flex-1 truncate">{{ getAwayName(game) }}</span>
              <span class="text-xs shrink-0 font-semibold w-16 text-right" :class="getStatusClass(game)">
                {{ getStatusLabel(game) }}
              </span>
            </div>
          </div>
        </section>

        <!-- JOGO AO VIVO -->
        <section v-if="liveGame" class="rounded-2xl border-2 border-green-400 bg-green-50 overflow-hidden">
          <div class="bg-green-500 text-white px-4 py-2 flex items-center gap-2 text-sm font-bold">
            <span class="animate-pulse">●</span>
            AO VIVO — {{ getTournamentName(liveGame.tournament) }}
            <span class="ml-auto font-normal opacity-80">{{ getPeriodLabel(liveGame.current_period) }}</span>
          </div>
          <div class="px-6 py-5">
            <div class="flex items-center justify-between gap-4 mb-3">
              <span class="text-base font-bold text-stone-800 text-right flex-1 leading-tight">{{ getHomeName(liveGame) }}</span>
              <div class="flex items-center gap-3 shrink-0">
                <span class="text-5xl font-black text-green-700 tabular-nums">{{ liveScore.home }}</span>
                <span class="text-3xl text-stone-400 font-light">–</span>
                <span class="text-5xl font-black text-green-700 tabular-nums">{{ liveScore.away }}</span>
              </div>
              <span class="text-base font-bold text-stone-800 text-left flex-1 leading-tight">{{ getAwayName(liveGame) }}</span>
            </div>
            <div class="text-center mb-4" v-if="liveGame.current_period > 0">
              <span class="text-2xl font-mono font-bold text-stone-700">{{ timerDisplay }}</span>
              <span class="ml-2 text-xs text-stone-400">restantes</span>
            </div>
            <div v-if="recentEvents.length > 0" class="border-t border-green-200 pt-3 space-y-1.5">
              <p class="text-xs font-semibold text-stone-500 mb-2">Últimas incidências</p>
              <div
                v-for="(item, i) in recentEvents"
                :key="i"
                class="flex items-center gap-2 text-sm text-stone-700 bg-white rounded-lg px-3 py-1.5"
              >
                <span class="text-base shrink-0">{{ getEventIcon(item) }}</span>
                <span class="flex-1">{{ getEventDescription(item) }}</span>
                <span class="text-xs text-stone-400 shrink-0">{{ getEventMinute(item) }}</span>
              </div>
            </div>
          </div>
        </section>

      </div>

      <!-- COLUNA DIREITA — grupos ímpares (B, D, F…) -->
      <aside class="space-y-4">
        <ClassificationPanel
          v-for="c in classificationsRight"
          :key="c.group_id"
          :classification="c"
        />
      </aside>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, defineComponent, h } from "vue";
import { useGameStore } from "@stores/games";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { getClassification } from "@router/backend/services/group";
import { GameStatus } from "@router/backend/services/game/types";
import type { Game, GameEvent, FoulEvent } from "@router/backend/services/game/types";
import type { Classification } from "@router/backend/services/group/types";

// ── Inline classification panel component ─────────────────
const ClassificationPanel = defineComponent({
  props: { classification: { type: Object as () => Classification, required: true } },
  setup(props) {
    return () => h("div", { class: "bg-white border border-stone-200 rounded-xl overflow-hidden shadow-sm" }, [
      h("div", { class: "bg-stone-100 px-3 py-2 text-xs font-semibold text-stone-600" }, props.classification.group_name),
      h("table", { class: "w-full text-xs" }, [
        h("thead", {}, h("tr", { class: "border-b border-stone-100 text-stone-400" }, [
          h("th", { class: "px-2 py-1.5 text-left w-5" }, "#"),
          h("th", { class: "px-2 py-1.5 text-left" }, "Equipa"),
          h("th", { class: "px-2 py-1.5 text-center" }, "J"),
          h("th", { class: "px-2 py-1.5 text-center" }, "V"),
          h("th", { class: "px-2 py-1.5 text-center" }, "E"),
          h("th", { class: "px-2 py-1.5 text-center" }, "D"),
          h("th", { class: "px-2 py-1.5 text-center" }, "DG"),
          h("th", { class: "px-2 py-1.5 text-center font-bold text-stone-500" }, "Pts"),
        ])),
        h("tbody", {}, props.classification.standings.map(s =>
          h("tr", { key: s.team_id, class: "border-b border-stone-50 last:border-0 hover:bg-stone-50" }, [
            h("td", { class: "px-2 py-1.5 text-stone-400" }, s.position),
            h("td", { class: "px-2 py-1.5 font-medium text-stone-800 max-w-[120px] truncate" }, s.team_name),
            h("td", { class: "px-2 py-1.5 text-center text-stone-600" }, s.games),
            h("td", { class: "px-2 py-1.5 text-center text-stone-600" }, s.wins),
            h("td", { class: "px-2 py-1.5 text-center text-stone-600" }, s.ties),
            h("td", { class: "px-2 py-1.5 text-center text-stone-600" }, s.losses),
            h("td", { class: "px-2 py-1.5 text-center text-stone-600" }, s.goal_difference > 0 ? `+${s.goal_difference}` : s.goal_difference),
            h("td", { class: "px-2 py-1.5 text-center font-bold text-stone-900" }, s.points),
          ])
        )),
      ]),
    ]);
  },
});

const gameStore = useGameStore();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const classifications = ref<Classification[]>([]);

// All classifications ordered: tournament 0 groups first, then tournament 1
const allClassificationsSorted = computed(() => {
  const t0 = tournamentStore.tournaments[0];
  const t1 = tournamentStore.tournaments[1];
  const ids0 = t0 ? groupStore.groups.filter(g => g.tournament === t0.id).map(g => g.id) : [];
  const ids1 = t1 ? groupStore.groups.filter(g => g.tournament === t1.id).map(g => g.id) : [];
  return [
    ...classifications.value.filter(c => ids0.includes(c.group_id)),
    ...classifications.value.filter(c => ids1.includes(c.group_id)),
  ];
});

// Even indices → left column, odd indices → right column
const classificationsLeft = computed(() => allClassificationsSorted.value.filter((_, i) => i % 2 === 0));
const classificationsRight = computed(() => allClassificationsSorted.value.filter((_, i) => i % 2 === 1));

// ── Computed ──────────────────────────────────────────────

const todayGames = computed(() => {
  const today = new Date();
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  return gameStore.games
    .filter(g => {
      if (!g.scheduled_date) return false;
      const d = new Date(g.scheduled_date);
      const ds = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
      return ds === todayStr;
    })
    .sort((a, b) => new Date(a.scheduled_date!).getTime() - new Date(b.scheduled_date!).getTime());
});

const liveGame = computed(() =>
  gameStore.games.find(g => g.status === GameStatus.InProgress) ?? null
);

const liveScore = computed(() => {
  if (!liveGame.value) return { home: 0, away: 0 };
  return getScore(liveGame.value);
});

const recentEvents = computed(() => {
  if (!liveGame.value) return [];
  return [...liveGame.value.events]
    .filter(e => "Goal" in e || "Foul" in e || "Penalty" in e || "PeriodStart" in e || "PeriodEnd" in e)
    .reverse()
    .slice(0, 8);
});

// ── Timer ─────────────────────────────────────────────────

const tickMs = ref(0); // updated every 100ms to drive reactivity for the timer

const currentElapsedSeconds = computed(() => {
  void tickMs.value; // reactive dependency
  if (!liveGame.value) return 0;
  let elapsed = liveGame.value.period_elapsed_seconds;
  if (liveGame.value.timer_active && liveGame.value.timer_started_at) {
    const startTime = Date.parse(liveGame.value.timer_started_at + "Z");
    elapsed += (Date.now() - startTime) / 1000;
  }
  const duration = getDurationForPeriod(liveGame.value.current_period);
  if (duration > 0 && elapsed > duration) elapsed = duration;
  return elapsed;
});

const timerDisplay = computed(() => {
  if (!liveGame.value) return "00:00";
  const duration = getDurationForPeriod(liveGame.value.current_period);
  const remaining = Math.max(0, duration - currentElapsedSeconds.value);
  const mins = Math.floor(remaining / 60);
  const secs = Math.floor(remaining % 60);
  if (mins === 0) return `${secs}.${Math.floor((remaining % 1) * 10)}s`;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
});

function getDurationForPeriod(period: number): number {
  if (period >= 1 && period <= 2) return 1200;
  if (period >= 3 && period <= 4) return 300;
  return 0;
}

function getPeriodLabel(period: number): string {
  if (period === 0) return "Não iniciado";
  if (period <= 2) return `${period}º Período`;
  if (period <= 4) return `Prolongamento (${period - 2}º)`;
  return "Penalidades";
}

// ── Team / Game helpers ───────────────────────────────────

function getTeamName(id: string): string {
  return teamStore.teams.find(t => t.id === id)?.name ?? id;
}

function getHomeName(game: Game): string {
  return game.home_call ? getTeamName(game.home_call.team) : (game.home_placeholder ?? "?");
}

function getAwayName(game: Game): string {
  return game.away_call ? getTeamName(game.away_call.team) : (game.away_placeholder ?? "?");
}

function getScore(game: Game): { home: number; away: number } {
  const homeName = getHomeName(game);
  const awayName = getAwayName(game);
  let home = 0, away = 0;
  for (const e of game.events) {
    if ("Goal" in e) {
      const goal = (e as { Goal: { team_name: string } }).Goal;
      if (goal.team_name === homeName) home++;
      else if (goal.team_name === awayName) away++;
    }
  }
  return { home, away };
}

function getScoreDisplay(game: Game): string {
  if (game.status === GameStatus.Scheduled || game.status === GameStatus.CallsPending || game.status === GameStatus.ReadyToStart) return "–  –";
  const s = getScore(game);
  return `${s.home}  –  ${s.away}`;
}

function getScoreClass(game: Game): string {
  if (game.status === GameStatus.InProgress) return "bg-green-100 text-green-700";
  if (game.status === GameStatus.Finished) return "bg-stone-100 text-stone-600";
  return "text-stone-300";
}

function getStatusLabel(game: Game): string {
  if (game.status === GameStatus.InProgress) return "● Ao Vivo";
  if (game.status === GameStatus.Finished) return "Terminado";
  if (game.status === GameStatus.Canceled) return "Cancelado";
  return game.scheduled_date ? getGameHour(game) : "–";
}

function getStatusClass(game: Game): string {
  if (game.status === GameStatus.InProgress) return "text-green-600";
  if (game.status === GameStatus.Finished) return "text-stone-400";
  return "text-stone-400";
}

function getGameHour(game: Game): string {
  if (!game.scheduled_date) return "";
  const d = new Date(game.scheduled_date);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function getTournamentName(id: string): string {
  return tournamentStore.tournaments.find(t => t.id === id)?.name ?? "";
}

const TOURNAMENT_COLORS = ["#f43f5e", "#8b5cf6", "#3b82f6", "#10b981"];

function getTournamentColor(id: string): string {
  const idx = tournamentStore.tournaments.findIndex(t => t.id === id);
  return TOURNAMENT_COLORS[idx] ?? "#6b7280";
}

// ── Event helpers ─────────────────────────────────────────

function getEventIcon(event: GameEvent): string {
  if ("Goal" in event) return (event as { Goal: { own_goal: boolean } }).Goal.own_goal ? "🥅" : "⚽";
  if ("Penalty" in event) return (event as { Penalty: { scored: boolean } }).Penalty.scored ? "✅" : "❌";
  if ("Foul" in event) {
    const foul = (event as { Foul: { card: string | null } }).Foul;
    if (!foul.card) return "⚠️";
    return foul.card === "Yellow" ? "🟨" : "🟥";
  }
  if ("PeriodStart" in event || "PeriodResume" in event) return "▶️";
  if ("PeriodEnd" in event) return "⏹️";
  if ("PeriodPause" in event) return "⏸️";
  if ("Manual" in event) return "📝";
  return "";
}

function getEventDescription(event: GameEvent): string {
  if ("Goal" in event) {
    const goal = (event as { Goal: { own_goal: boolean; own_goal_committed_by?: string; player_name?: string; team_name: string } }).Goal;
    if (goal.own_goal) return `Auto-golo (${goal.own_goal_committed_by ?? goal.team_name})`;
    return `Golo de ${goal.player_name ?? "?"} (${goal.team_name})`;
  }
  if ("Penalty" in event) {
    const p = (event as { Penalty: { scored: boolean; player_name: string; team_name: string } }).Penalty;
    return `${p.player_name} ${p.scored ? "marcou" : "falhou"} penalti (${p.team_name})`;
  }
  if ("Foul" in event) {
    const foul = (event as { Foul: FoulEvent }).Foul;
    const name = foul.staff_name || foul.player_name || "Desconhecido";
    if (!foul.card) return `Falta — ${name}`;
    return `Cartão ${foul.card === "Yellow" ? "Amarelo" : "Vermelho"} — ${name}`;
  }
  if ("PeriodStart" in event) {
    const p = (event as { PeriodStart: { period: number } }).PeriodStart;
    return `Início ${getPeriodLabel(p.period)}`;
  }
  if ("PeriodEnd" in event) {
    const p = (event as { PeriodEnd: { period: number } }).PeriodEnd;
    return `Fim ${getPeriodLabel(p.period)}`;
  }
  if ("PeriodPause" in event) return "Pausa";
  if ("PeriodResume" in event) return "Retoma";
  if ("Manual" in event) return (event as { Manual: { description: string } }).Manual.description;
  return "";
}

function getEventMinute(event: GameEvent): string {
  const inner = Object.values(event as Record<string, unknown>)[0] as Record<string, unknown>;
  if (inner && typeof inner.minute === "number") {
    const m = inner.minute;
    const s = typeof inner.second === "number" ? inner.second : 0;
    return `${m}:${String(s).padStart(2, "0")}`;
  }
  return "";
}

// ── Polling & classifications ─────────────────────────────

async function pollGames() {
  await gameStore.forceGetGames();
}

async function loadClassifications() {
  const groups = groupStore.groups;
  const results: Classification[] = [];
  for (const g of groups) {
    const res = await getClassification(g.id);
    if (res.status === 200 && "standings" in res.data) {
      results.push(res.data as Classification);
    }
  }
  classifications.value = results;
}

let gamesPollInterval: ReturnType<typeof setInterval>;
let classificationsPollInterval: ReturnType<typeof setInterval>;
let timerInterval: ReturnType<typeof setInterval>;

onMounted(async () => {
  await Promise.all([
    gameStore.getGames(),
    groupStore.getGroups(),
    teamStore.getTeams(),
    tournamentStore.getTournaments(),
  ]);
  await loadClassifications();

  gamesPollInterval = setInterval(pollGames, 10000);
  classificationsPollInterval = setInterval(loadClassifications, 30000);
  timerInterval = setInterval(() => { tickMs.value = Date.now(); }, 100);
});

onUnmounted(() => {
  clearInterval(gamesPollInterval);
  clearInterval(classificationsPollInterval);
  clearInterval(timerInterval);
});
</script>
