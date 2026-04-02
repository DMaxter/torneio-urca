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
            @change="computePreview"
          />
          <label for="tournament">Torneio</label>
        </P-FloatLabel>

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

        <!-- Knockout phase preview -->
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

      <template v-else>
        <div class="border border-green-200 rounded-lg overflow-hidden">
          <div class="bg-green-50 px-3 py-2 text-sm font-semibold text-green-700">
            {{ getTournamentName(selectedTournament) }} — {{ totalGroupGames + knockoutPreview.length }} jogos gerados com sucesso
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
          <div v-if="knockoutPreview.length > 0">
            <div class="bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700">Fase a Eliminar</div>
            <div v-for="game in knockoutPreview" :key="game.label" class="px-3 py-2 flex items-center gap-3 border-t border-stone-100">
              <span class="text-xs font-semibold text-amber-600 shrink-0 whitespace-nowrap w-48">{{ game.label }}</span>
              <span class="text-xs text-stone-600 truncate" v-html="formatPlaceholder(game.home)"></span>
              <span class="text-xs text-stone-400 shrink-0">vs</span>
              <span class="text-xs text-stone-600 truncate" v-html="formatPlaceholder(game.away)"></span>
            </div>
          </div>
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
        :disabled="preview.length === 0 || loading"
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

const preview = ref<GroupPreview[]>([]);
const knockoutPreview = ref<KnockoutGamePreview[]>([]);

const totalGroupGames = computed(() =>
  preview.value.reduce((sum, g) => sum + g.rounds.reduce((s, r) => s + r.length, 0), 0)
);

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
    const round: MatchPreview[] = [];
    for (let i = 0; i < n / 2; i++) {
      const home = teams[i];
      const away = teams[n - 1 - i];
      if (home !== "bye" && away !== "bye") {
        round.push({
          homeId: home,
          awayId: away,
          home: getTeamName(home),
          away: getTeamName(away),
        });
      }
    }
    rounds.push(round);
    teams.splice(1, 0, teams.pop()!);
  }

  return rounds;
}

// "1º Classificado Grupo A" → "<b>1º</b> Classificado — <b>Grupo A</b>"
function formatPlaceholder(text: string): string {
  return text.replace(
    /^(\d+º)\s+(Classificado)\s+(.+)$/,
    '<strong>$1</strong> $2 — <strong>$3</strong>'
  );
}

function computeKnockoutPreview(groups: { name: string }[]) {
  if (groups.length < 4) {
    knockoutPreview.value = [];
    return;
  }

  const sorted = [...groups].sort((a, b) => a.name.localeCompare(b.name));
  const [A, B, C, D] = sorted.map(g => g.name);

  knockoutPreview.value = [
    { label: "Quartos de Final - Jogo 1", phase: "quarter_final", home: `1º Classificado ${A}`, away: `2º Classificado ${B}` },
    { label: "Quartos de Final - Jogo 2", phase: "quarter_final", home: `1º Classificado ${C}`, away: `2º Classificado ${D}` },
    { label: "Quartos de Final - Jogo 3", phase: "quarter_final", home: `2º Classificado ${C}`, away: `1º Classificado ${D}` },
    { label: "Quartos de Final - Jogo 4", phase: "quarter_final", home: `2º Classificado ${A}`, away: `1º Classificado ${B}` },
    { label: "Meia Final - Jogo 1",       phase: "semi_final",    home: "Vencedor Quartos de Final - Jogo 1", away: "Vencedor Quartos de Final - Jogo 2" },
    { label: "Meia Final - Jogo 2",       phase: "semi_final",    home: "Vencedor Quartos de Final - Jogo 3", away: "Vencedor Quartos de Final - Jogo 4" },
    { label: "3º e 4º Lugar",           phase: "third_place",   home: "Perdedor Meia Final - Jogo 1",       away: "Perdedor Meia Final - Jogo 2" },
    { label: "Final",                   phase: "final",         home: "Vencedor Meia Final - Jogo 1",       away: "Vencedor Meia Final - Jogo 2" },
  ];
}

function computePreview() {
  const groups = groupStore.groups.filter(g => g.tournament === selectedTournament.value);
  if (!groups.length) {
    preview.value = [];
    knockoutPreview.value = [];
    return;
  }

  preview.value = groups.map(group => ({
    name: group.name,
    rounds: buildRounds(group.teams),
  }));

  computeKnockoutPreview(groups);
}

async function generate() {
  loading.value = true;
  let allOk = true;

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

  loading.value = false;

  if (allOk) {
    generated.value = true;
  }
}

function close() {
  enabled.value = false;
  preview.value = [];
  knockoutPreview.value = [];
  selectedTournament.value = "";
  generated.value = false;
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
