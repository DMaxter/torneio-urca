<template>
  <P-Dialog v-model:visible="enabled" modal header="Ver Grupos" class="w-11/12 md:w-10/12 lg:w-9/10 xl:w-4/5">
    <div v-if="groupStore.groups.length === 0" class="text-center text-stone-400 py-6 text-sm">
      Nenhum grupo encontrado.
    </div>

    <div v-else class="flex flex-col gap-6">
      <div v-for="tournament in groupsByTournament" :key="tournament.id">
        <p class="text-sm font-semibold text-stone-600 mb-2">🏆 {{ tournament.name }}</p>
        <div class="border border-stone-200 rounded-lg overflow-hidden">
          <div class="grid gap-px bg-stone-200" :class="gridCols(tournament.groups.length)">
            <div v-for="group in tournament.groups" :key="group.id" class="bg-white p-3">
              <p class="font-semibold text-stone-800 mb-2 text-sm">
                {{ group.name }}
                <span class="text-stone-400 font-normal">({{ group.teams?.length || 0 }})</span>
              </p>
              <ul class="space-y-1">
                <li
                  v-for="teamId in group.teams"
                  :key="teamId"
                  class="text-xs text-stone-600 truncate"
                >
                  {{ getTeamName(teamId) }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <P-Button severity="secondary" @click="groupStore.getGroups()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";

const enabled = defineModel<boolean>();

const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

onMounted(async () => {
  await groupStore.getGroups();
  await teamStore.getTeams();
  await tournamentStore.getTournaments();
});

const groupsByTournament = computed(() => {
  return tournamentStore.tournaments
    .map(t => ({
      id: t.id,
      name: t.name,
      groups: groupStore.groups.filter(g => g.tournament === t.id),
    }))
    .filter(t => t.groups.length > 0);
});

function gridCols(n: number): string {
  if (n <= 2) return "grid-cols-2";
  if (n <= 4) return "grid-cols-4";
  return "grid-cols-4";
}

function getTeamName(teamId: string): string {
  return teamStore.teams.find(t => t.id === teamId)?.name || teamId;
}
</script>
