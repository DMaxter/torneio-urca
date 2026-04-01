<template>
  <P-Dialog v-model:visible="enabled" modal header="Jogos" class="w-11/12 md:w-8/12 lg:w-6/12">
    <div class="flex flex-col gap-4">
      <p v-if="byTournament.length === 0" class="text-sm text-stone-400 text-center py-4">
        Nenhum jogo encontrado.
      </p>

      <div v-for="tournament in byTournament" :key="tournament.id" class="border border-stone-200 rounded-lg overflow-hidden">
        <div class="bg-stone-100 px-3 py-2 text-sm font-semibold text-stone-700">
          {{ tournament.name }}
        </div>
        <div class="divide-y divide-stone-100">
          <div v-for="group in tournament.groups" :key="group.name" class="p-3">
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
    </div>

    <template #footer>
      <P-Button severity="secondary" @click="enabled = false">
        <span class="material-symbols-outlined">close</span>
        Fechar
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useGameStore } from "@stores/games";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";

const enabled = defineModel<boolean>();

const gameStore = useGameStore();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

function getTeamName(id: string) {
  return teamStore.teams.find(t => t.id === id)?.name ?? id;
}

function findGroup(tournamentId: string, homeTeamId: string, awayTeamId: string) {
  return groupStore.groups.find(
    g => g.tournament === tournamentId && g.teams.includes(homeTeamId) && g.teams.includes(awayTeamId)
  );
}


interface MatchEntry {
  home: string;
  away: string;
  homeId: string;
  awayId: string;
  status: number;
}

const byTournament = computed(() => {
  return tournamentStore.tournaments
    .map(tournament => {
      const tournamentGames = gameStore.games.filter(g => g.tournament === tournament.id);
      if (!tournamentGames.length) return null;

      const groups = groupStore.groups.filter(g => g.tournament === tournament.id);

      const groupMap: Record<string, { name: string; matches: MatchEntry[] }> = {};
      for (const group of groups) {
        groupMap[group.id] = { name: group.name, matches: [] };
      }
      const ungrouped: MatchEntry[] = [];

      for (const game of tournamentGames) {
        const homeId = game.home_call?.team ?? "";
        const awayId = game.away_call?.team ?? "";
        const group = findGroup(tournament.id, homeId, awayId);
        const entry: MatchEntry = {
          homeId,
          awayId,
          home: getTeamName(homeId),
          away: getTeamName(awayId),
          status: game.status,
        };
        if (group) {
          groupMap[group.id].matches.push(entry);
        } else {
          ungrouped.push(entry);
        }
      }

      const groupsWithRounds = Object.values(groupMap)
        .filter(g => g.matches.length > 0)
        .map(g => ({ name: g.name, rounds: buildRounds(g.matches) }));

      if (ungrouped.length) {
        groupsWithRounds.push({ name: "Sem grupo", rounds: [ungrouped] });
      }

      return { id: tournament.id, name: tournament.name, groups: groupsWithRounds };
    })
    .filter(t => t !== null);
});

function buildRounds(matches: MatchEntry[]): MatchEntry[][] {
  const teamIds = [...new Set(matches.flatMap(m => [m.homeId, m.awayId]))];
  const teams = teamIds.length % 2 === 1 ? [...teamIds, "bye"] : [...teamIds];
  const n = teams.length;
  const rounds: MatchEntry[][] = [];

  for (let r = 0; r < n - 1; r++) {
    const round: MatchEntry[] = [];
    for (let i = 0; i < n / 2; i++) {
      const home = teams[i];
      const away = teams[n - 1 - i];
      if (home !== "bye" && away !== "bye") {
        const match = matches.find(
          m => (m.homeId === home && m.awayId === away) || (m.homeId === away && m.awayId === home)
        );
        if (match) round.push(match);
      }
    }
    if (round.length) rounds.push(round);
    teams.splice(1, 0, teams.pop()!);
  }

  return rounds;
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
