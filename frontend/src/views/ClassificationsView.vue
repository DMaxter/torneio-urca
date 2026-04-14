<template>
  <div class="classifications p-4 w-full mx-auto bg-stone-50 md:p-6">
    <div class="mb-6 md:mb-8">
      <h1 class="text-xl font-bold text-stone-900 mb-1 md:text-2xl">Classificações</h1>
      <p class="text-stone-500 text-sm md:text-base">Ver classificações dos grupos</p>
    </div>

    <div class="mb-4">
      <P-Select
        v-model="selectedTournament"
        :options="tournaments"
        optionLabel="name"
        optionValue="id"
        placeholder="Selecionar Torneio"
        class="w-full md:w-64"
        @change="loadGroups"
      />
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <P-ProgressSpinner />
    </div>

    <div v-else-if="selectedTournament && groups.length === 0" class="text-center py-8 text-stone-500">
      <span class="material-symbols-outlined text-4xl mb-2">info</span>
      <p>Não existem grupos para este torneio</p>
    </div>

    <div v-else-if="classifications.length > 0" class="space-y-6">
      <div v-for="classification in classifications" :key="classification.group_id" class="bg-white border border-stone-300 rounded-xl overflow-hidden">
        <div class="bg-stone-100 px-4 py-3 border-b border-stone-200">
          <h2 class="text-lg font-semibold text-stone-900">{{ classification.group_name }}</h2>
        </div>

        <div class="overflow-x-auto">
          <P-DataTable :value="classification.standings" stripedRows class="text-sm">
            <P-Column field="position" header="#" class="w-[3rem]">
              <template #body="{ data }">
                <span class="font-bold">{{ data.position }}</span>
              </template>
            </P-Column>
            <P-Column field="team_name" header="Equipa">
              <template #body="{ data }">
                <div class="font-medium">{{ data.team_name }}</div>
              </template>
            </P-Column>
            <P-Column field="points" header="Pontos" class="text-center">
              <template #body="{ data }">
                <span class="font-bold text-primary">{{ data.points }}</span>
              </template>
            </P-Column>
            <P-Column field="games" header="J" class="text-center" />
            <P-Column field="wins" header="V" class="text-center" />
            <P-Column field="ties" header="E" class="text-center" />
            <P-Column field="losses" header="D" class="text-center" />
            <P-Column field="goals_scored" header="GM" class="text-center" />
            <P-Column field="goals_suffered" header="GS" class="text-center" />
            <P-Column field="goal_difference" header="DG" class="text-center">
              <template #body="{ data }">
                <span :class="data.goal_difference > 0 ? 'text-green-600' : data.goal_difference < 0 ? 'text-red-600' : ''">
                  {{ data.goal_difference > 0 ? '+' : '' }}{{ data.goal_difference }}
                </span>
              </template>
            </P-Column>
          </P-DataTable>
        </div>
      </div>
    </div>

    <div v-else-if="selectedTournament" class="text-center py-8 text-stone-500">
      <span class="material-symbols-outlined text-4xl mb-2">leaderboard</span>
      <p>Selecione um grupo para ver a classificação</p>
    </div>

    <div v-else class="text-center py-8 text-stone-500">
      <span class="material-symbols-outlined text-4xl mb-2">emoji_events</span>
      <p>Selecione um torneio para ver as classificações</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useTournamentStore } from "@stores/tournaments";
import { useGroupStore } from "@stores/groups";
import { getClassification } from "@router/backend/services/group";
import type { Classification } from "@router/backend/services/group/types";

const tournamentStore = useTournamentStore();
const groupStore = useGroupStore();

const tournaments = ref<{ id: string; name: string }[]>([]);
const groups = ref<{ id: string; name: string; tournament: string }[]>([]);
const classifications = ref<Classification[]>([]);
const selectedTournament = ref<string | null>(null);
const loading = ref(false);

onMounted(async () => {
  await tournamentStore.getTournaments();
  tournaments.value = tournamentStore.tournaments.map(t => ({ id: t.id, name: t.name }));
});

async function loadGroups() {
  if (!selectedTournament.value) {
    groups.value = [];
    classifications.value = [];
    return;
  }

  loading.value = true;
  classifications.value = [];

  await groupStore.getGroups();
  groups.value = groupStore.groups
    .filter(g => g.tournament === selectedTournament.value)
    .map(g => ({ id: g.id, name: g.name, tournament: g.tournament }));

  for (const group of groups.value) {
    try {
      const response = await getClassification(group.id);
      if (response.status === 200 && response.data && "standings" in response.data) {
        classifications.value.push(response.data);
      }
    } catch (e) {
      console.error(`Failed to load classification for group ${group.id}`, e);
    }
  }

  loading.value = false;
}
</script>
