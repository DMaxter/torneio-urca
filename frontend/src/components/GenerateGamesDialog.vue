<template>
  <P-Dialog v-model:visible="enabled" modal header="Gerar Jogos" class="w-11/12 md:w-8/12 lg:w-6/12">
    <div class="mt-3 flex flex-col gap-4">
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
              <span class="text-xs text-stone-600 truncate">
                <template v-if="getPlaceholderChunks(game.home).position">
                  <strong>{{ getPlaceholderChunks(game.home).position }}</strong> {{ getPlaceholderChunks(game.home).baseStr }} — <strong>{{ getPlaceholderChunks(game.home).name }}</strong>
                </template>
                <template v-else>{{ game.home }}</template>
              </span>
              <span class="text-xs text-stone-400 shrink-0">vs</span>
              <span class="text-xs text-stone-600 truncate">
                <template v-if="getPlaceholderChunks(game.away).position">
                  <strong>{{ getPlaceholderChunks(game.away).position }}</strong> {{ getPlaceholderChunks(game.away).baseStr }} — <strong>{{ getPlaceholderChunks(game.away).name }}</strong>
                </template>
                <template v-else>{{ game.away }}</template>
              </span>
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

      <!-- Success state -->
      <template v-else>
        <div class="border border-green-200 rounded-lg overflow-hidden">
          <div class="bg-green-50 px-3 py-2 text-sm font-semibold text-green-700">
            {{ getTournamentName(selectedTournament) }} — {{ totalGeneratedGames }} jogos gerados com sucesso
          </div>

          <!-- Group phase -->
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
          <!-- Knockout phase preview -->
          <div v-if="knockoutPreview.length > 0">
            <div class="bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700">Fase a Eliminar</div>
            <div v-for="game in knockoutPreview" :key="game.label" class="px-3 py-2 flex items-center gap-3 border-t border-stone-100">
              <span class="text-xs font-semibold text-amber-600 shrink-0 whitespace-nowrap w-48">{{ game.label }}</span>
              <span class="text-xs text-stone-600 truncate">
                <template v-if="getPlaceholderChunks(game.home).position">
                  <strong>{{ getPlaceholderChunks(game.home).position }}</strong> {{ getPlaceholderChunks(game.home).baseStr }} — <strong>{{ getPlaceholderChunks(game.home).name }}</strong>
                </template>
                <template v-else>{{ game.home }}</template>
              </span>
              <span class="text-xs text-stone-400 shrink-0">vs</span>
              <span class="text-xs text-stone-600 truncate">
                <template v-if="getPlaceholderChunks(game.away).position">
                  <strong>{{ getPlaceholderChunks(game.away).position }}</strong> {{ getPlaceholderChunks(game.away).baseStr }} — <strong>{{ getPlaceholderChunks(game.away).name }}</strong>
                </template>
                <template v-else>{{ game.away }}</template>
              </span>
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
import { ref, computed, onMounted, watch } from "vue";
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
  groupId: string;
  rounds: MatchPreview[][];
}

interface KnockoutGamePreview {
  label: string;
  home: string;
  away: string;
  phase: GamePhase;
  home_group_ref?: string;
  home_group_position?: number;
  away_group_ref?: string;
  away_group_position?: number;
  next_game_winner?: string;
  next_game_loser?: string;
}



const preview = ref<GroupPreview[]>([]);
const knockoutPreview = ref<KnockoutGamePreview[]>([]);

const canGenerate = computed(() => selectedTournament.value && preview.value.length > 0);

const totalGroupGames = computed(() =>
  preview.value.reduce((sum, g) => sum + g.rounds.reduce((s, r) => s + r.length, 0), 0)
);

const totalGeneratedGames = computed(() =>
  totalGroupGames.value + knockoutPreview.value.length
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

function getPlaceholderChunks(text: string): { position?: string, baseStr?: string, name?: string, original: string } {
  const match = text.match(/^(\d+º)\s+(Classificado)\s+(.+)$/);
  if (match) {
    return { position: match[1], baseStr: match[2], name: match[3], original: text };
  }
  return { original: text };
}

function computeKnockoutPreview(groups: { id: string; name: string }[]) {
   const sorted = [...groups].sort((a, b) => a.name.localeCompare(b.name));

  // Always include Final and 3rd/4th place match
  // Order: Final first so it's indexed BEFORE 3rd in backward iteration
  const baseKnockout: KnockoutGamePreview[] = [
    { label: "Final", phase: "final" as const, home: "Vencedor Meia Final", away: "Vencedor Meia Final" },
    { label: "3º e 4º Lugar", phase: "third_place" as const, home: "Perdedor Meia Final", away: "Perdedor Meia Final" },
  ];

if (groups.length >= 4) {
     // 4+ groups: full quarter_final bracket + semifinals
     // Order for single-pass creation: Final, 3rd, SF, QF
     // So refs can be resolved when creating each game
     const sortedGroups = sorted as { id: string; name: string }[];
     const [A, B, C, D] = sortedGroups;
     knockoutPreview.value = [
       // Final and 3rd place (no refs) - created first
       ...baseKnockout,
       // Semi Finals - reference Final/3rd place (created second)
       { label: "Meia Final - Jogo 1", phase: "semi_final", home: `Vencedor Quartos de Final - Jogo 1`, away: `Vencedor Quartos de Final - Jogo 2`, next_game_winner: "Final_HOME", next_game_loser: "3º e 4º Lugar_HOME" },
       { label: "Meia Final - Jogo 2", phase: "semi_final", home: `Vencedor Quartos de Final - Jogo 3`, away: `Vencedor Quartos de Final - Jogo 4`, next_game_winner: "Final_AWAY", next_game_loser: "3º e 4º Lugar_AWAY" },
       // Quarter Finals - reference Semi Finals (created third)
       { label: "Quartos de Final - Jogo 1", phase: "quarter_final" as const, home: `1º Classificado ${A.name}`, away: `2º Classificado ${B.name}`, home_group_ref: A.id, home_group_position: 1, away_group_ref: B.id, away_group_position: 2, next_game_winner: "Meia Final - Jogo 1_HOME" },
       { label: "Quartos de Final - Jogo 2", phase: "quarter_final" as const, home: `1º Classificado ${B.name}`, away: `2º Classificado ${A.name}`, home_group_ref: B.id, home_group_position: 1, away_group_ref: A.id, away_group_position: 2, next_game_winner: "Meia Final - Jogo 1_AWAY" },
       { label: "Quartos de Final - Jogo 3", phase: "quarter_final" as const, home: `1º Classificado ${C.name}`, away: `2º Classificado ${D.name}`, home_group_ref: C.id, home_group_position: 1, away_group_ref: D.id, away_group_position: 2, next_game_winner: "Meia Final - Jogo 2_HOME" },
       { label: "Quartos de Final - Jogo 4", phase: "quarter_final" as const, home: `1º Classificado ${D.name}`, away: `2º Classificado ${C.name}`, home_group_ref: D.id, home_group_position: 1, away_group_ref: C.id, away_group_position: 2, next_game_winner: "Meia Final - Jogo 2_AWAY" }
     ];
} else if (groups.length >= 2) {
     // 2-3 groups: semifinals + final + 3rd place
     const sortedGroups = sorted as { id: string; name: string }[];
     const [A, B] = sortedGroups;
     // Order for single-pass creation: Final, 3rd, SF
     // So refs can be resolved when creating each game
     knockoutPreview.value = [
       // Final and 3rd place (no refs) - created first
       { label: "3º e 4º Lugar", phase: "third_place" as const, home: "Perdedor Meia Final", away: "Perdedor Meia Final" },
       { label: "Final", phase: "final" as const, home: "Vencedor Meia Final", away: "Vencedor Meia Final" },
       // Semi Finals - winners go to Final, losers go to 3rd place (created second)
       { label: "Meia Final - Jogo 1", phase: "semi_final", home: `1º Classificado ${A.name}`, away: `2º Classificado ${B.name}`, home_group_ref: A.id, home_group_position: 1, away_group_ref: B.id, away_group_position: 2, next_game_winner: "Final_HOME", next_game_loser: "3º e 4º Lugar_HOME" },
       { label: "Meia Final - Jogo 2", phase: "semi_final", home: `1º Classificado ${B.name}`, away: `2º Classificado ${A.name}`, home_group_ref: B.id, home_group_position: 1, away_group_ref: A.id, away_group_position: 2, next_game_winner: "Final_AWAY", next_game_loser: "3º e 4º Lugar_AWAY" },
     ];
   }
}



async function onTournamentChange() {
  preview.value = [];
  knockoutPreview.value = [];

  if (!selectedTournament.value) return;

  await groupStore.getGroups();
  const groups = groupStore.groups.filter(g => g.tournament === selectedTournament.value);
  preview.value = groups.map(group => ({ name: group.name, groupId: group.id, rounds: buildRounds(group.teams) }));
  computeKnockoutPreview(groups);
}

async function generate() {
  loading.value = true;
  let allOk = true;

  // Create group phase games
  for (const groupPreview of preview.value) {
    for (const round of groupPreview.rounds) {
      for (const match of round) {
        const dto = new CreateGame();
        dto.tournament = selectedTournament.value;
        dto.home_call = new CreateGameCall();
        dto.home_call.team = match.homeId;
        dto.away_call = new CreateGameCall();
        dto.away_call.team = match.awayId;
        dto.phase = "group";
        // Include group reference to link game to group
        dto['group'] = groupPreview.groupId;

        const result = await gameStore.createGame(dto);
        if (!result.success) {
          allOk = false;
          toast.add({ severity: "error", summary: "Erro", detail: `Falha ao criar jogo ${match.home} vs ${match.away}`, life: 4000 });
        }
      }
    }
  }

  // Single pass: Create knockout games with next_game references
  // Games are in order: Final, 3rd, SF, QF - so referenced games exist from previous iterations
  const createdCalls: Record<string, string> = {};

  for (const ko of knockoutPreview.value) {
    const dto = new CreateGame();
    dto.tournament = selectedTournament.value;
    dto.home_call = null;
    dto.away_call = null;
    dto.phase = ko.phase;
    dto.label = ko.label;
    dto.home_placeholder = ko.home;
    dto.away_placeholder = ko.away;

    // Include group reference fields for knockout games
    dto['home_group_ref'] = ko.home_group_ref;
    dto['home_group_position'] = ko.home_group_position;
    dto['away_group_ref'] = ko.away_group_ref;
    dto['away_group_position'] = ko.away_group_position;

    // Include next_game references from previously created games
    if (ko.next_game_winner && createdCalls[ko.next_game_winner]) {
      dto['next_game_winner'] = createdCalls[ko.next_game_winner];
    }
    if (ko.next_game_loser && createdCalls[ko.next_game_loser]) {
      dto['next_game_loser'] = createdCalls[ko.next_game_loser];
    }

    const result = await gameStore.createGame(dto);
    if (!result.success) {
      allOk = false;
      toast.add({ severity: "error", summary: "Erro", detail: `Falha ao criar jogo ${ko.label}`, life: 4000 });
      continue;
    }

    // Store call IDs for future games to reference
    const game = result.entity;
    if (game?.home_call?.id) {
      createdCalls[`${ko.label}_HOME`] = game.home_call.id;
    }
    if (game?.away_call?.id) {
      createdCalls[`${ko.label}_AWAY`] = game.away_call.id;
    }
  }

  loading.value = false;
  if (allOk) generated.value = true;
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
    tournamentStore.getTournaments(),
    groupStore.getGroups(),
    teamStore.getTeams(),
    gameStore.getGames(),
  ]);
});
</script>
