<template>
  <P-Dialog v-model:visible="enabled" modal header="Distribuir Jogos" class="w-11/12 md:w-9/12 lg:w-7/12">
    <div class="flex flex-col gap-4">
      <template v-if="!distributed">
        <P-FloatLabel variant="on">
          <P-Select
            id="tournament"
            v-model="selectedTournament"
            :options="availableTournaments"
            optionLabel="name"
            optionValue="id"
            optionDisabled="disabled"
            fluid
            @change="computeDistribution"
          />
          <label for="tournament">Torneio</label>
        </P-FloatLabel>

        <!-- Preview -->
        <div v-if="selectedTournament && slots.length > 0" class="border border-stone-200 rounded-lg overflow-hidden">
          <div class="bg-stone-100 px-3 py-2 text-sm font-semibold text-stone-600">
            Pré-visualização — {{ assignedCount }} jogo{{ assignedCount !== 1 ? 's' : '' }} distribuídos por {{ slots.length }} dia{{ slots.length !== 1 ? 's' : '' }}
          </div>
          <div class="divide-y divide-stone-100 max-h-80 overflow-y-auto">
            <div v-for="slot in slots" :key="slot.date" class="p-3">
              <p class="font-semibold text-stone-700 text-sm mb-1">
                {{ formatDateLong(slot.date) }}
                <span class="text-stone-400 font-normal text-xs ml-1">{{ slot.startTime }} · {{ slot.games.length }} jogo{{ slot.games.length !== 1 ? 's' : '' }}</span>
              </p>
              <ul class="space-y-1">
                <li v-for="(g, i) in slot.games" :key="g.id" class="text-xs text-stone-600 flex items-center gap-1">
                  <span class="text-stone-400 shrink-0">{{ formatGameTime(slot.startTime, i) }}</span>
                   <span class="truncate">{{ getTeamName(g.home_call?.team || '') }} vs {{ getTeamName(g.away_call?.team || '') }}</span>
                  <span class="ml-1 text-stone-400 shrink-0 whitespace-nowrap">({{ g.groupName }}, Jornada {{ g.round }})</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Unassigned games -->
        <div v-if="unassigned.length > 0" class="border border-orange-200 rounded-lg overflow-hidden">
          <div class="bg-orange-50 px-3 py-2 text-sm font-semibold text-orange-700">
            {{ unassigned.length }} jogo{{ unassigned.length !== 1 ? 's' : '' }} sem dia disponível
          </div>
          <ul class="divide-y divide-stone-100 max-h-40 overflow-y-auto">
            <li v-for="g in unassigned" :key="g.id" class="px-3 py-2 text-xs text-stone-600 flex items-center gap-1">
               <span class="truncate">{{ getTeamName(g.home_call?.team || '') }}</span>
               <span class="text-stone-400 shrink-0">vs</span>
               <span class="truncate">{{ getTeamName(g.away_call?.team || '') }}</span>
              <span class="ml-1 text-stone-400 shrink-0">({{ g.groupName }}, Jornada {{ g.round }})</span>
            </li>
          </ul>
          <div class="px-3 py-2 text-xs text-orange-600 bg-orange-50">
            Adicione mais dias ou aumente o nº de jogos por dia no calendário de dias de jogo.
          </div>
        </div>

        <p v-if="selectedTournament && slots.length === 0 && !loading" class="text-sm text-stone-400 text-center py-2">
          Nenhum dia de jogo configurado para este torneio.
        </p>
      </template>

      <template v-else>
        <div class="border border-green-200 rounded-lg overflow-hidden">
          <div class="bg-green-50 px-3 py-2 text-sm font-semibold text-green-700">
            {{ assignedCount }} jogos distribuídos com sucesso
          </div>
          <p v-if="unassigned.length > 0" class="px-3 py-2 text-sm text-orange-600">
            {{ unassigned.length }} jogos ficaram sem data — adicione mais dias no calendário.
          </p>
        </div>
      </template>
    </div>

    <template #footer>
      <P-Button v-if="!distributed" severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
      <P-Button
        v-if="!distributed"
        :disabled="slots.length === 0 || loading"
        :loading="loading"
        @click="distribute"
      >
        <span class="material-symbols-outlined">event</span>
        Distribuir
      </P-Button>
      <P-Button v-else @click="close">
        <span class="material-symbols-outlined">check</span>
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
import { useDateFormatter } from "@/composables/useDateFormatter";

const toast = useToast();
const enabled = defineModel<boolean>();
const { formatDateLong } = useDateFormatter();

const gameStore = useGameStore();
const gameDayStore = useGameDayStore();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const selectedTournament = ref<string>("");
const loading = ref(false);
const distributed = ref(false);

interface GameEntry extends Game {
  groupName: string;
  round: number;
}

interface DaySlot {
  date: string;
  startTime: string;
  capacity: number;
  games: GameEntry[];
}

const slots = ref<DaySlot[]>([]);
const unassigned = ref<GameEntry[]>([]);

const assignedCount = computed(() => slots.value.reduce((s, d) => s + d.games.length, 0));

const availableTournaments = computed(() =>
  tournamentStore.tournaments.map(t => ({
    ...t,
    disabled: !gameStore.games.some(g => g.tournament === t.id) ||
              gameStore.games.some(g => g.tournament === t.id && g.scheduled_date),
  }))
);

function getTeamName(id: string) {
  return teamStore.teams.find(t => t.id === id)?.name ?? id;
}



function formatGameTime(startTime: string, index: number): string {
  const [h, m] = startTime.split(":").map(Number);
  const total = h * 60 + m + index * 60;
  const hh = String(Math.floor(total / 60) % 24).padStart(2, "0");
  const mm = String(total % 60).padStart(2, "0");
  return `${hh}:${mm}`;
}

// Build rounds across all groups, interleaved: round1_groupA, round1_groupB, round2_groupA...
function buildOrderedGames(): GameEntry[] {
  const groups = groupStore.groups.filter(g => g.tournament === selectedTournament.value);
  const tournamentGames = gameStore.games.filter(g => g.tournament === selectedTournament.value);

  // Build rounds per group using round-robin order
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

  // Interleave: take one game per group per round
  const maxRounds = Math.max(...groupRounds.map(gr => gr.length));
  const result: GameEntry[] = [];
  for (let i = 0; i < maxRounds; i++) {
    for (const gr of groupRounds) {
      if (gr[i]) result.push(gr[i]);
    }
  }
  return result;
}

function computeDistribution() {
  const days = gameDayStore.gameDays
    .filter(d => d.tournament === selectedTournament.value)
    .sort((a, b) => a.date.localeCompare(b.date));

  if (!days.length) {
    slots.value = [];
    unassigned.value = [];
    return;
  }

  const ordered = buildOrderedGames();
  const daySlots: DaySlot[] = days.map(d => ({
    date: d.date,
    startTime: d.start_time,
    capacity: Number(d.num_games),
    games: [],
  }));

  let slotIdx = 0;
  const remaining: GameEntry[] = [];

  for (const game of ordered) {
    // Advance to next slot with capacity
    while (slotIdx < daySlots.length && daySlots[slotIdx].games.length >= daySlots[slotIdx].capacity) {
      slotIdx++;
    }
    if (slotIdx < daySlots.length) {
      daySlots[slotIdx].games.push(game);
    } else {
      remaining.push(game);
    }
  }

  slots.value = daySlots.filter(d => d.games.length > 0);
  unassigned.value = remaining;
}

async function distribute() {
  loading.value = true;
  let allOk = true;

  for (const slot of slots.value) {
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

  loading.value = false;

  if (allOk) {
    distributed.value = true;
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Alguns jogos não foram agendados", life: 4000 });
  }
}

function close() {
  enabled.value = false;
  selectedTournament.value = "";
  slots.value = [];
  unassigned.value = [];
  distributed.value = false;
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
