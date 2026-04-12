<template>
  <P-Dialog v-model:visible="enabled" modal header="Jogos" class="w-11/12 md:w-8/12 lg:w-6/12">
    <div class="flex flex-col gap-4">
      <p v-if="byTournament.length === 0" class="text-sm text-stone-400 text-center py-4">
        Nenhum jogo encontrado.
      </p>

      <div v-for="tournament in byTournament" :key="tournament.id" class="border border-stone-200 rounded-lg overflow-hidden">
        <div class="bg-stone-100 px-3 py-2 flex items-center justify-between">
          <span class="text-sm font-semibold text-stone-700">{{ tournament.name }}</span>
          <span
            v-if="!tournamentHasScheduledGames(tournament.id)"
            class="material-symbols-outlined text-base cursor-pointer text-red-500 hover:text-red-700"
            v-tooltip.left="'Eliminar todos os jogos deste torneio'"
            @click="promptDelete(tournament.id, tournament.name)"
          >delete_sweep</span>
          <span
            v-else
            class="material-symbols-outlined text-base text-stone-300 cursor-not-allowed"
            v-tooltip.left="'Não é possível eliminar jogos com agendamentos'"
          >delete_sweep</span>
        </div>

        <!-- Group stage -->
        <div class="divide-y divide-stone-100">
          <div v-for="group in tournament.groups" :key="group.name" class="p-3">
            <p class="font-semibold text-stone-700 text-sm mb-2">{{ group.name }}</p>
            <div v-for="(round, ri) in group.rounds" :key="ri" class="mb-2">
              <p class="text-xs font-semibold text-stone-400 mb-1">Jornada {{ ri + 1 }}</p>
              <ul class="space-y-1">
                <li 
                  v-for="(match, i) in round" 
                  :key="i" 
                  class="text-xs text-stone-600 flex items-center gap-1 p-1 rounded hover:bg-stone-50 cursor-pointer transition-colors"
                  @click="openGameResult(match.id)"
                >
                  <P-Tag :severity="getStatusSeverity(match.status)" :value="getStatusLabel(match.status)" class="shrink-0 text-[10px]" v-tooltip.top="getStatusTooltip(match.status)" />
                  <span class="truncate">{{ match.home }}</span>
                  <span class="text-stone-400 shrink-0">vs</span>
                  <span class="truncate">{{ match.away }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Knockout phase -->
        <div v-if="tournament.knockout.length > 0">
          <div class="bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700 border-t border-stone-200">
            Fase a Eliminar
          </div>
          <div class="divide-y divide-stone-100">
            <div 
              v-for="game in tournament.knockout" 
              :key="game.id" 
              class="px-3 py-2 flex items-center gap-3 hover:bg-stone-50 cursor-pointer transition-colors"
              @click="openGameResult(game.id)"
            >
              <P-Tag :severity="getStatusSeverity(game.status)" :value="getStatusLabel(game.status)" class="shrink-0 text-[10px]" v-tooltip.top="getStatusTooltip(game.status)" />
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
      </div>
    </div>

    <template #footer>
      <P-Button severity="secondary" @click="enabled = false">
        <span class="material-symbols-outlined">close</span>
        Fechar
      </P-Button>
    </template>
  </P-Dialog>

  <GameResultDialog v-model:visible="gameResultVisible" :game="selectedDetailedGame" />

  <P-Dialog v-model:visible="showDeleteConfirm" modal header="Confirmar Eliminação" class="w-11/12 md:w-6/12">
    <p>Tem a certeza que deseja eliminar <strong>todos os jogos</strong> do torneio <strong>{{ tournamentToDelete?.name }}</strong>?</p>
    <p class="text-red-600 mt-2 text-sm">Esta ação não pode ser desfeita.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showDeleteConfirm = false">Cancelar</P-Button>
      <P-Button severity="danger" :loading="deleting" @click="confirmDeleteAll">Eliminar todos</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { useGameStore } from "@stores/games";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import type { GameStatus, Game } from "@router/backend/services/game/types";

const enabled = defineModel<boolean>();
const toast = useToast();

const gameStore = useGameStore();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const gameResultVisible = ref(false);
const selectedDetailedGame = ref<Game | null>(null);

function openGameResult(gameId: string) {
  const g = gameStore.games.find(x => x.id === gameId);
  if (g) {
    selectedDetailedGame.value = g;
    gameResultVisible.value = true;
  }
}

const showDeleteConfirm = ref(false);
const deleting = ref(false);
const tournamentToDelete = ref<{ id: string; name: string } | null>(null);

function getTeamName(id: string) {
  return teamStore.teams.find(t => t.id === id)?.name ?? id;
}

function findGroup(tournamentId: string, homeTeamId: string, awayTeamId: string) {
  return groupStore.groups.find(
    g => g.tournament === tournamentId && g.teams.includes(homeTeamId) && g.teams.includes(awayTeamId)
  );
}

function tournamentHasScheduledGames(tournamentId: string): boolean {
  return gameStore.games.some(g => g.tournament === tournamentId && g.scheduled_date);
}

function promptDelete(id: string, name: string) {
  tournamentToDelete.value = { id, name };
  showDeleteConfirm.value = true;
}

async function confirmDeleteAll() {
  if (!tournamentToDelete.value) return;
  deleting.value = true;
  let allOk = true;

  const games = gameStore.games.filter(g => g.tournament === tournamentToDelete.value!.id);
  for (const game of games) {
    const result = await gameStore.deleteGame(game.id);
    if (!result.success) allOk = false;
  }

  deleting.value = false;
  showDeleteConfirm.value = false;
  tournamentToDelete.value = null;

  if (allOk) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Todos os jogos eliminados", life: 3000 });
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Alguns jogos não foram eliminados", life: 3000 });
  }
}

function getPlaceholderChunks(text: string): { position?: string, baseStr?: string, name?: string, original: string } {
  const match = text.match(/^(\d+º)\s+(Classificado)\s+(.+)$/);
  if (match) {
    return { position: match[1], baseStr: match[2], name: match[3], original: text };
  }
  return { original: text };
}

const KNOCKOUT_PHASE_ORDER: Record<string, number> = {
  quarter_final: 0,
  semi_final: 1,
  third_place: 2,
  final: 3,
};

const KNOCKOUT_PHASE_LABEL: Record<string, string> = {
  quarter_final: "Quartos",
  semi_final: "Meias",
  third_place: "3º e 4º",
  final: "Final",
};

interface MatchEntry {
  id: string;
  home: string;
  away: string;
  homeId: string;
  awayId: string;
  status: GameStatus;
}

interface KnockoutEntry {
  id: string;
  label: string;
  home: string;
  away: string;
  status: GameStatus;
}

const byTournament = computed(() => {
  return tournamentStore.tournaments
    .map(tournament => {
      const tournamentGames = gameStore.games.filter(g => g.tournament === tournament.id);
      if (!tournamentGames.length) return null;

      const groupGames = tournamentGames.filter(g => g.phase === "group");
      const knockoutGames = tournamentGames.filter(g => g.phase !== "group");

      const groups = groupStore.groups.filter(g => g.tournament === tournament.id);
      const groupMap: Record<string, { name: string; teams: string[]; matches: MatchEntry[] }> = {};
      for (const group of groups) {
        groupMap[group.id] = { name: group.name, teams: group.teams, matches: [] };
      }
      const ungrouped: MatchEntry[] = [];

      for (const game of groupGames) {
        const homeId = game.home_call?.team ?? "";
        const awayId = game.away_call?.team ?? "";
        const group = findGroup(tournament.id, homeId, awayId);
        const entry: MatchEntry = { id: game.id, homeId, awayId, home: getTeamName(homeId), away: getTeamName(awayId), status: game.status };
        if (group) {
          groupMap[group.id].matches.push(entry);
        } else {
          ungrouped.push(entry);
        }
      }

      const groupsWithRounds = Object.values(groupMap)
        .filter(g => g.matches.length > 0)
        .map(g => ({ name: g.name, rounds: buildRounds(g.matches, g.teams) }));

      if (ungrouped.length) {
        groupsWithRounds.push({ name: "Sem grupo", rounds: [ungrouped] });
      }

      // Build knockout list ordered by phase
      const knockout: KnockoutEntry[] = knockoutGames
        .sort((a, b) => (KNOCKOUT_PHASE_ORDER[a.phase] ?? 99) - (KNOCKOUT_PHASE_ORDER[b.phase] ?? 99))
        .map(g => ({
          id: g.id,
          label: g.home_placeholder?.startsWith("Vencedor Quarto") || g.home_placeholder?.startsWith("Perdedor")
            ? (KNOCKOUT_PHASE_LABEL[g.phase] ?? g.phase)
            : (KNOCKOUT_PHASE_LABEL[g.phase] ?? g.phase),
          home: g.home_placeholder ?? getTeamName(g.home_call?.team ?? ""),
          away: g.away_placeholder ?? getTeamName(g.away_call?.team ?? ""),
          status: g.status,
        }));

      return { id: tournament.id, name: tournament.name, groups: groupsWithRounds, knockout };
    })
    .filter(t => t !== null);
});

function buildRounds(matches: MatchEntry[], groupTeams: string[]): MatchEntry[][] {
  const teams = groupTeams.length % 2 === 1 ? [...groupTeams, "bye"] : [...groupTeams];
  const n = teams.length;
  const rounds: MatchEntry[][] = [];

  for (let r = 0; r < n - 1; r++) {
    for (let i = 0; i < n / 2; i++) {
      const home = teams[i];
      const away = teams[n - 1 - i];
      if (home !== "bye" && away !== "bye") {
        const match = matches.find(
          m => (m.homeId === home && m.awayId === away) || (m.homeId === away && m.awayId === home)
        );
        if (match) rounds.push([match]);
      }
    }
    teams.splice(1, 0, teams.pop()!);
  }

  return rounds;
}

function getStatusSeverity(status: number | string) {
  const s = String(status);
  switch (s) {
    case "0":
    case "Scheduled": return "secondary";
    case "1":
    case "CallsPending": return "warn";
    case "2":
    case "ReadyToStart": return "info";
    case "3":
    case "InProgress": return "success";
    case "4":
    case "Finished": return "contrast";
    case "5":
    case "Canceled": return "danger";
    default: return "secondary";
  }
}

function getStatusLabel(status: number | string) {
  const s = String(status);
  switch (s) {
    case "0":
    case "Scheduled": return "Ag.";
    case "1":
    case "CallsPending": return "Cham.";
    case "2":
    case "ReadyToStart": return "Pronto";
    case "3":
    case "InProgress": return "Jogo";
    case "4":
    case "Finished": return "Fim";
    case "5":
    case "Canceled": return "Canc.";
    default: return "?";
  }
}

function getStatusTooltip(status: number | string) {
  const s = String(status);
  switch (s) {
    case "0":
    case "Scheduled": return "Agendado";
    case "1":
    case "CallsPending": return "Chamadas Pendentes";
    case "2":
    case "ReadyToStart": return "Pronto - Pode iniciar o jogo";
    case "3":
    case "InProgress": return "Em Progresso";
    case "4":
    case "Finished": return "Terminado";
    case "5":
    case "Canceled": return "Cancelado";
    default: return "Desconhecido";
  }
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
