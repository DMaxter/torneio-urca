<template>
  <P-Dialog v-model:visible="enabled" modal header="Gerar Jogos" class="w-11/12 md:w-8/12 lg:w-6/12">
    <div class="flex flex-col gap-4">
      <template v-if="!generated">
        <P-FloatLabel variant="on">
          <P-Select
            id="tournament"
            v-model="selectedTournament"
            :options="availableTournaments"
            optionLabel="name"
            optionValue="id"
            optionDisabled="disabled"
            fluid
            @change="onTournamentChange"
          />
          <label for="tournament">Torneio</label>
        </P-FloatLabel>

        <!-- Knockout-only mode (no groups) -->
        <template v-if="knockoutOnlyMode">
          <P-FloatLabel variant="on">
            <P-Select
              id="startingPhase"
              v-model="startingPhase"
              :options="phaseOptions"
              optionLabel="label"
              optionValue="value"
              optionDisabled="disabled"
              fluid
              :disabled="!selectedTournament"
              @change="onPhaseChange"
            />
            <label for="startingPhase">Fase inicial</label>
          </P-FloatLabel>

          <div v-if="directKnockoutGames.length > 0" class="border border-amber-200 rounded-lg overflow-hidden">
            <div class="bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-700">
              Fase a Eliminar — {{ directKnockoutGames.length }} jogos
            </div>
            <div class="divide-y divide-stone-100">
              <div
                v-for="game in directKnockoutGames"
                :key="game.label"
                class="px-3 py-2 flex items-center gap-3"
                :class="game.homeTeamId ? 'bg-white' : 'bg-stone-50'"
              >
                <span class="text-xs font-semibold text-amber-600 shrink-0 whitespace-nowrap w-44">{{ game.label }}</span>
                <span class="text-xs truncate" :class="game.homeTeamId ? 'text-stone-800 font-medium' : 'text-stone-400 italic'">{{ game.home }}</span>
                <span class="text-xs text-stone-400 shrink-0">vs</span>
                <span class="text-xs truncate" :class="game.awayTeamId ? 'text-stone-800 font-medium' : 'text-stone-400 italic'">{{ game.away }}</span>
              </div>
            </div>
          </div>

          <p v-if="selectedTournament && tournamentTeams.length < 4" class="text-sm text-red-500 text-center py-2">
            São necessárias pelo menos 4 equipas para gerar a fase a eliminar.
          </p>
        </template>

        <!-- Group-based mode (groups exist) -->
        <template v-else>
          <!-- Group stage preview -->
          <div v-if="preview.length > 0" class="border border-stone-200 rounded-lg overflow-hidden">
            <div class="bg-stone-100 px-3 py-2 text-sm font-semibold text-stone-600">
              Fase de Grupos — {{ totalGroupGames }} jogo{{ totalGroupGames !== 1 ? 's' : '' }} em {{ preview.length }} grupo{{ preview.length !== 1 ? 's' : '' }}
            </div>
            <div class="divide-y divide-stone-100">
              <div v-for="group in preview" :key="group.name" class="p-3">
                <p class="font-semibold text-stone-700 text-sm mb-2">{{ group.name }}</p>
                <div v-for="(round, ri) in group.rounds" :key="ri" class="mb-2">
                  <p class="text-xs font-semibold text-stone-400 mb-1">Jornada {{ ri + 1 }}</p>
                  <ul class="space-y-1">
                    <li v-for="(match, i) in round" :key="i" class="text-xs text-stone-600 flex items-center gap-1">
                      <span class="truncate">{{ match.home }}</span>
                      <span class="text-stone-400 shrink-0">vs</span>
                      <span class="truncate">{{ match.away }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Knockout phase preview (placeholders) -->
          <div v-if="knockoutPreview.length > 0" class="border border-amber-200 rounded-lg overflow-hidden">
            <div class="bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-700">
              Fase a Eliminar — {{ knockoutPreview.length }} jogos
            </div>
            <div class="divide-y divide-stone-100">
              <div v-for="game in knockoutPreview" :key="game.label" class="px-3 py-2 flex items-center gap-3">
                <span class="text-xs font-semibold text-amber-600 shrink-0 whitespace-nowrap w-48">{{ game.label }}</span>
                <span class="text-xs text-stone-600 truncate" v-html="formatPlaceholder(game.home)"></span>
                <span class="text-xs text-stone-400 shrink-0">vs</span>
                <span class="text-xs text-stone-600 truncate" v-html="formatPlaceholder(game.away)"></span>
              </div>
            </div>
          </div>

          <p v-if="selectedTournament && preview.length === 0" class="text-sm text-stone-400 text-center py-2">
            Nenhum grupo encontrado para este torneio.
          </p>
          <p v-if="selectedTournament && preview.length > 0 && knockoutPreview.length === 0" class="text-xs text-stone-400 text-center">
            São necessários 4 grupos para gerar a fase a eliminar.
          </p>
        </template>
      </template>

      <!-- Success state -->
      <template v-else>
        <div class="border border-green-200 rounded-lg overflow-hidden">
          <div class="bg-green-50 px-3 py-2 text-sm font-semibold text-green-700">
            {{ getTournamentName(selectedTournament) }} — {{ totalGeneratedGames }} jogos gerados com sucesso
          </div>

          <!-- Group phase success -->
          <template v-if="!knockoutOnlyMode">
            <div class="divide-y divide-stone-100">
              <div v-for="group in preview" :key="group.name" class="p-3">
                <p class="font-semibold text-stone-700 text-sm mb-2">{{ group.name }}</p>
                <div v-for="(round, ri) in group.rounds" :key="ri" class="mb-2">
                  <p class="text-xs font-semibold text-stone-400 mb-1">Jornada {{ ri + 1 }}</p>
                  <ul class="space-y-1">
                    <li v-for="(match, i) in round" :key="i" class="text-xs text-stone-600 flex items-center gap-1">
                      <span class="truncate">{{ match.home }}</span>
                      <span class="text-stone-400 shrink-0">vs</span>
                      <span class="truncate">{{ match.away }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            <div v-if="knockoutPreview.length > 0">
              <div class="bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700">Fase a Eliminar</div>
              <div v-for="game in knockoutPreview" :key="game.label" class="px-3 py-2 flex items-center gap-3 border-t border-stone-100">
                <span class="text-xs font-semibold text-amber-600 shrink-0 whitespace-nowrap w-48">{{ game.label }}</span>
                <span class="text-xs text-stone-600 truncate" v-html="formatPlaceholder(game.home)"></span>
                <span class="text-xs text-stone-400 shrink-0">vs</span>
                <span class="text-xs text-stone-600 truncate" v-html="formatPlaceholder(game.away)"></span>
              </div>
            </div>
          </template>

          <!-- Knockout-only success -->
          <template v-else>
            <div class="divide-y divide-stone-100">
              <div
                v-for="game in directKnockoutGames"
                :key="game.label"
                class="px-3 py-2 flex items-center gap-3"
                :class="game.homeTeamId ? 'bg-white' : 'bg-stone-50'"
              >
                <span class="text-xs font-semibold text-amber-600 shrink-0 whitespace-nowrap w-44">{{ game.label }}</span>
                <span class="text-xs truncate" :class="game.homeTeamId ? 'text-stone-800 font-medium' : 'text-stone-400 italic'">{{ game.home }}</span>
                <span class="text-xs text-stone-400 shrink-0">vs</span>
                <span class="text-xs truncate" :class="game.awayTeamId ? 'text-stone-800 font-medium' : 'text-stone-400 italic'">{{ game.away }}</span>
              </div>
            </div>
          </template>
        </div>
      </template>
    </div>

    <template #footer>
      <P-Button v-if="!generated" severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
      <P-Button
        v-if="!generated"
        :disabled="!canGenerate || loading"
        :loading="loading"
        @click="generate"
      >
        <span class="material-symbols-outlined">sports_soccer</span>
        Gerar Jogos
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

import { CreateGame, CreateGameCall } from "@router/backend/services/game/types";
import type { GamePhase } from "@router/backend/services/game/types";
import { useGameStore } from "@stores/games";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";

const toast = useToast();
const enabled = defineModel<boolean>();

const gameStore = useGameStore();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const selectedTournament = ref<string>("");
const loading = ref(false);
const generated = ref(false);
const startingPhase = ref<"semi_final" | "quarter_final">("semi_final");

interface MatchPreview {
  home: string;
  away: string;
  homeId: string;
  awayId: string;
}

interface GroupPreview {
  name: string;
  rounds: MatchPreview[][];
}

interface KnockoutGamePreview {
  label: string;
  home: string;
  away: string;
  phase: GamePhase;
}

interface DirectKnockoutGame {
  label: string;
  phase: GamePhase;
  homeTeamId: string | null;
  awayTeamId: string | null;
  home: string;
  away: string;
}

const preview = ref<GroupPreview[]>([]);
const knockoutPreview = ref<KnockoutGamePreview[]>([]);
const directKnockoutGames = ref<DirectKnockoutGame[]>([]);
const shuffledTeamIds = ref<string[]>([]);

const tournamentTeams = computed(() =>
  teamStore.teams.filter(t => t.tournament === selectedTournament.value)
);

const knockoutOnlyMode = computed(() => {
  if (!selectedTournament.value) return false;
  return !groupStore.groups.some(g => g.tournament === selectedTournament.value);
});

const phaseOptions = computed(() => [
  {
    label: "Meias-finais (4 equipas)",
    value: "semi_final" as const,
    disabled: tournamentTeams.value.length < 4,
  },
  {
    label: "Quartos de Final (8 equipas)",
    value: "quarter_final" as const,
    disabled: tournamentTeams.value.length < 8,
  },
]);

const totalGroupGames = computed(() =>
  preview.value.reduce((sum, g) => sum + g.rounds.reduce((s, r) => s + r.length, 0), 0)
);

const totalGeneratedGames = computed(() =>
  knockoutOnlyMode.value
    ? directKnockoutGames.value.length
    : totalGroupGames.value + knockoutPreview.value.length
);

const canGenerate = computed(() => {
  if (!selectedTournament.value) return false;
  if (knockoutOnlyMode.value) {
    const needed = startingPhase.value === "quarter_final" ? 8 : 4;
    return tournamentTeams.value.length >= needed && directKnockoutGames.value.length > 0;
  }
  return preview.value.length > 0;
});

const availableTournaments = computed(() =>
  tournamentStore.tournaments.map(t => ({
    ...t,
    disabled: gameStore.games.some(g => g.tournament === t.id),
  }))
);

function getTeamName(id: string) {
  return teamStore.teams.find(t => t.id === id)?.name ?? id;
}

function getTournamentName(id: string) {
  return tournamentStore.tournaments.find(t => t.id === id)?.name ?? id;
}

function buildRounds(teamIds: string[]): MatchPreview[][] {
  const teams = teamIds.length % 2 === 1 ? [...teamIds, "bye"] : [...teamIds];
  const n = teams.length;
  const rounds: MatchPreview[][] = [];

  for (let r = 0; r < n - 1; r++) {
    for (let i = 0; i < n / 2; i++) {
      const home = teams[i];
      const away = teams[n - 1 - i];
      if (home !== "bye" && away !== "bye") {
        rounds.push([{ homeId: home, awayId: away, home: getTeamName(home), away: getTeamName(away) }]);
      }
    }
    teams.splice(1, 0, teams.pop()!);
  }

  return rounds;
}

function formatPlaceholder(text: string): string {
  return text.replace(
    /^(\d+º)\s+(Classificado)\s+(.+)$/,
    '<strong>$1</strong> $2 — <strong>$3</strong>'
  );
}

function computeKnockoutPreview(groups: { name: string }[]) {
  const sorted = [...groups].sort((a, b) => a.name.localeCompare(b.name));

  // Always include Final and 3rd/4th place match
  const baseKnockout: KnockoutGamePreview[] = [
    { label: "3º e 4º Lugar", phase: "third_place" as const, home: "Perdedor Meia Final", away: "Perdedor Meia Final" },
    { label: "Final", phase: "final" as const, home: "Vencedor Meia Final", away: "Vencedor Meia Final" },
  ];

  if (groups.length >= 4) {
    // 4+ groups: full quarter_final bracket + semifinals
    const [A, B, C, D] = sorted.map(g => g.name);
    knockoutPreview.value = [
      { label: "Quartos de Final - Jogo 1", phase: "quarter_final", home: `1º Classificado ${A}`, away: `2º Classificado ${B}` },
      { label: "Quartos de Final - Jogo 2", phase: "quarter_final", home: `1º Classificado ${C}`, away: `2º Classificado ${D}` },
      { label: "Quartos de Final - Jogo 3", phase: "quarter_final", home: `2º Classificado ${C}`, away: `1º Classificado ${D}` },
      { label: "Quartos de Final - Jogo 4", phase: "quarter_final", home: `2º Classificado ${A}`, away: `1º Classificado ${B}` },
      { label: "Meia Final - Jogo 1", phase: "semi_final", home: "Vencedor Quartos de Final - Jogo 1", away: "Vencedor Quartos de Final - Jogo 2" },
      { label: "Meia Final - Jogo 2", phase: "semi_final", home: "Vencedor Quartos de Final - Jogo 3", away: "Vencedor Quartos de Final - Jogo 4" },
      ...baseKnockout,
    ];
  } else if (groups.length >= 2) {
    // 2-3 groups: semifinals + final + 3rd place
    const [A, B] = sorted.map(g => g.name);
    knockoutPreview.value = [
      { label: "Meia Final - Jogo 1", phase: "semi_final", home: `1º Classificado ${A}`, away: `2º Classificado ${B}` },
      { label: "Meia Final - Jogo 2", phase: "semi_final", home: `1º Classificado ${B}`, away: `2º Classificado ${A}` },
      ...baseKnockout,
    ];
  } else if (groups.length === 1) {
    // 1 group: just final + 3rd/4th (top 2 from group)
    knockoutPreview.value = [
      { label: "3º e 4º Lugar", phase: "third_place", home: "3º Classificado", away: "4º Classificado" },
      { label: "Final", phase: "final", home: "1º Classificado", away: "2º Classificado" },
    ];
  } else {
    knockoutPreview.value = [];
  }
}

function buildDirectKnockout() {
  const t = shuffledTeamIds.value;
  const games: DirectKnockoutGame[] = [];

  if (startingPhase.value === "semi_final") {
    games.push({ label: "Meia Final - Jogo 1", phase: "semi_final",  homeTeamId: t[0], awayTeamId: t[1], home: getTeamName(t[0]), away: getTeamName(t[1]) });
    games.push({ label: "Meia Final - Jogo 2", phase: "semi_final",  homeTeamId: t[2], awayTeamId: t[3], home: getTeamName(t[2]), away: getTeamName(t[3]) });
    games.push({ label: "3º e 4º Lugar",       phase: "third_place", homeTeamId: null, awayTeamId: null, home: "Perdedor Meia Final - Jogo 1", away: "Perdedor Meia Final - Jogo 2" });
    games.push({ label: "Final",               phase: "final",       homeTeamId: null, awayTeamId: null, home: "Vencedor Meia Final - Jogo 1", away: "Vencedor Meia Final - Jogo 2" });
  } else {
    games.push({ label: "Quartos de Final - Jogo 1", phase: "quarter_final", homeTeamId: t[0], awayTeamId: t[1], home: getTeamName(t[0]), away: getTeamName(t[1]) });
    games.push({ label: "Quartos de Final - Jogo 2", phase: "quarter_final", homeTeamId: t[2], awayTeamId: t[3], home: getTeamName(t[2]), away: getTeamName(t[3]) });
    games.push({ label: "Quartos de Final - Jogo 3", phase: "quarter_final", homeTeamId: t[4], awayTeamId: t[5], home: getTeamName(t[4]), away: getTeamName(t[5]) });
    games.push({ label: "Quartos de Final - Jogo 4", phase: "quarter_final", homeTeamId: t[6], awayTeamId: t[7], home: getTeamName(t[6]), away: getTeamName(t[7]) });
    games.push({ label: "Meia Final - Jogo 1", phase: "semi_final",  homeTeamId: null, awayTeamId: null, home: "Vencedor Quartos de Final - Jogo 1", away: "Vencedor Quartos de Final - Jogo 2" });
    games.push({ label: "Meia Final - Jogo 2", phase: "semi_final",  homeTeamId: null, awayTeamId: null, home: "Vencedor Quartos de Final - Jogo 3", away: "Vencedor Quartos de Final - Jogo 4" });
    games.push({ label: "3º e 4º Lugar",       phase: "third_place", homeTeamId: null, awayTeamId: null, home: "Perdedor Meia Final - Jogo 1",       away: "Perdedor Meia Final - Jogo 2" });
    games.push({ label: "Final",               phase: "final",       homeTeamId: null, awayTeamId: null, home: "Vencedor Meia Final - Jogo 1",       away: "Vencedor Meia Final - Jogo 2" });
  }

  directKnockoutGames.value = games;
}

function onTournamentChange() {
  directKnockoutGames.value = [];
  preview.value = [];
  knockoutPreview.value = [];

  if (!selectedTournament.value) return;

  if (knockoutOnlyMode.value) {
    const count = tournamentTeams.value.length;
    startingPhase.value = count >= 8 ? "quarter_final" : "semi_final";
    shuffledTeamIds.value = [...tournamentTeams.value].sort(() => Math.random() - 0.5).map(t => t.id);
    buildDirectKnockout();
  } else {
    const groups = groupStore.groups.filter(g => g.tournament === selectedTournament.value);
    preview.value = groups.map(group => ({ name: group.name, rounds: buildRounds(group.teams) }));
    computeKnockoutPreview(groups);
  }
}

function onPhaseChange() {
  shuffledTeamIds.value = [...tournamentTeams.value].sort(() => Math.random() - 0.5).map(t => t.id);
  buildDirectKnockout();
}

async function generate() {
  loading.value = true;
  let allOk = true;

  if (knockoutOnlyMode.value) {
    for (const game of directKnockoutGames.value) {
      const dto = new CreateGame();
      dto.tournament = selectedTournament.value;
      dto.phase = game.phase;

      if (game.homeTeamId && game.awayTeamId) {
        dto.home_call = new CreateGameCall();
        dto.home_call.team = game.homeTeamId;
        dto.away_call = new CreateGameCall();
        dto.away_call.team = game.awayTeamId;
        dto.home_placeholder = null;
        dto.away_placeholder = null;
      } else {
        dto.home_call = null;
        dto.away_call = null;
        dto.home_placeholder = game.home;
        dto.away_placeholder = game.away;
      }

      const result = await gameStore.createGame(dto);
      if (!result.success) {
        allOk = false;
        toast.add({ severity: "error", summary: "Erro", detail: `Falha ao criar ${game.label}`, life: 4000 });
      }
    }
  } else {
    for (const group of preview.value) {
      for (const round of group.rounds) {
        for (const match of round) {
          const dto = new CreateGame();
          dto.tournament = selectedTournament.value;
          dto.home_call = new CreateGameCall();
          dto.home_call.team = match.homeId;
          dto.away_call = new CreateGameCall();
          dto.away_call.team = match.awayId;
          dto.phase = "group";

          const result = await gameStore.createGame(dto);
          if (!result.success) {
            allOk = false;
            toast.add({ severity: "error", summary: "Erro", detail: `Falha ao criar jogo ${match.home} vs ${match.away}`, life: 4000 });
          }
        }
      }
    }

    for (const ko of knockoutPreview.value) {
      const dto = new CreateGame();
      dto.tournament = selectedTournament.value;
      dto.home_call = null;
      dto.away_call = null;
      dto.phase = ko.phase;
      dto.home_placeholder = ko.home;
      dto.away_placeholder = ko.away;

      const result = await gameStore.createGame(dto);
      if (!result.success) {
        allOk = false;
        toast.add({ severity: "error", summary: "Erro", detail: `Falha ao criar jogo ${ko.label}`, life: 4000 });
      }
    }
  }

  loading.value = false;
  if (allOk) generated.value = true;
}

function close() {
  enabled.value = false;
  preview.value = [];
  knockoutPreview.value = [];
  directKnockoutGames.value = [];
  selectedTournament.value = "";
  generated.value = false;
  startingPhase.value = "semi_final";
}

onMounted(async () => {
  await Promise.all([
    gameStore.getGames(),
    groupStore.getGroups(),
    teamStore.getTeams(),
    tournamentStore.getTournaments(),
  ]);
});
</script>
