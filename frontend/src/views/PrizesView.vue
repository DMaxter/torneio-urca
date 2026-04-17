<template>
  <div class="prizes-view p-4 w-full mx-auto bg-stone-50 md:p-6">
    <div class="mb-6 md:mb-8">
      <h1 class="text-xl font-bold text-stone-900 mb-1 md:text-2xl">Prémios</h1>
      <p class="text-stone-500 text-sm md:text-base">Ver prémios do torneio</p>
    </div>

    <div class="mb-4 flex items-center gap-2">
      <P-Select
        v-model="selectedTournament"
        :options="tournaments"
        optionLabel="name"
        optionValue="id"
        placeholder="Selecionar Torneio"
        class="w-full md:w-64"
        @change="loadPrizes"
      />
      <button
        class="p-2 rounded-full text-orange-500 hover:bg-orange-50 transition-colors cursor-pointer disabled:opacity-50"
        :disabled="loading"
        @click="loadPrizes"
        v-tooltip.top="'Atualizar'"
      >
        <span v-if="loading" class="material-symbols-outlined animate-spin">sync</span>
        <span v-else class="material-symbols-outlined">refresh</span>
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <P-ProgressSpinner />
    </div>

    <div v-else-if="selectedTournament && !prizes" class="text-center py-8 text-stone-500">
      <span class="material-symbols-outlined text-4xl mb-2">emoji_events</span>
      <p>Não existem prémios para este torneio</p>
    </div>

    <div v-else-if="prizes" class="space-y-6">
      <div class="bg-white border border-stone-300 rounded-xl overflow-hidden">
        <div class="bg-yellow-100 px-4 py-3 border-b border-yellow-200">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-yellow-700 text-xl">military_tech</span>
            <h2 class="text-lg font-semibold text-stone-900">Melhor Marcador</h2>
          </div>
        </div>
        <div class="overflow-x-auto">
          <P-DataTable :value="prizes.best_scorer" stripedRows class="text-sm">
            <P-Column field="position" header="#" class="w-[3rem]">
              <template #body="{ data }">
                <span class="font-bold" :class="getPositionClass(data.position)">{{ data.position }}</span>
              </template>
            </P-Column>
            <P-Column field="player_name" header="Jogador">
              <template #body="{ data }">
                <div class="font-medium">{{ data.player_name || 'Jogador não identificado' }}</div>
              </template>
            </P-Column>
            <P-Column field="team_name" header="Equipa" />
            <P-Column field="goals" header="Golos" class="text-center">
              <template #body="{ data }">
                <span class="font-bold text-yellow-700">{{ data.goals }}</span>
              </template>
            </P-Column>
            <P-Column field="games" header="Jogos" class="text-center" />
          </P-DataTable>
        </div>
      </div>

      <div class="bg-white border border-stone-300 rounded-xl overflow-hidden">
        <div class="bg-blue-100 px-4 py-3 border-b border-blue-200">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-blue-700 text-xl">shield</span>
            <h2 class="text-lg font-semibold text-stone-900">Melhor Defesa</h2>
          </div>
        </div>
        <div class="overflow-x-auto">
          <P-DataTable :value="prizes.best_defense" stripedRows class="text-sm">
            <P-Column field="position" header="#" class="w-[3rem]">
              <template #body="{ data }">
                <span class="font-bold" :class="getPositionClass(data.position)">{{ data.position }}</span>
              </template>
            </P-Column>
            <P-Column field="team_name" header="Equipa" />
            <P-Column field="goals_suffered" header="Golos Sofridos" class="text-center">
              <template #body="{ data }">
                <span class="font-bold text-blue-700">{{ data.goals_suffered }}</span>
              </template>
            </P-Column>
            <P-Column field="games" header="Jogos" class="text-center" />
          </P-DataTable>
        </div>
      </div>

      <div class="bg-white border border-stone-300 rounded-xl overflow-hidden">
        <div class="bg-green-100 px-4 py-3 border-b border-green-200">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-green-700 text-xl">handshake</span>
            <h2 class="text-lg font-semibold text-stone-900">Taça Disciplina</h2>
          </div>
        </div>
        <div class="overflow-x-auto">
          <P-DataTable :value="prizes.fair_play" stripedRows class="text-sm">
            <P-Column field="position" header="#" class="w-[3rem]">
              <template #body="{ data }">
                <span class="font-bold" :class="getPositionClass(data.position)">{{ data.position }}</span>
              </template>
            </P-Column>
            <P-Column field="team_name" header="Equipa" />
            <P-Column field="cards" header="Cartões" class="text-center">
              <template #body="{ data }">
                <span class="font-bold text-green-700">{{ data.cards }}</span>
              </template>
            </P-Column>
            <P-Column field="games" header="Jogos" class="text-center" />
          </P-DataTable>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-8 text-stone-500">
      <span class="material-symbols-outlined text-4xl mb-2">emoji_events</span>
      <p>Selecione um torneio para ver os prémios</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useTournamentStore } from "@stores/tournaments";
import { getPrizes } from "@router/backend/services/prizes";
import type { Prizes } from "@router/backend/services/prizes/types";

const tournamentStore = useTournamentStore();

const tournaments = ref<{ id: string; name: string }[]>([]);
const prizes = ref<Prizes | null>(null);
const selectedTournament = ref<string | null>(null);
const loading = ref(false);

onMounted(async () => {
  await tournamentStore.getTournaments();
  tournaments.value = tournamentStore.tournaments.map(t => ({ id: t.id, name: t.name }));
});

async function loadPrizes() {
  if (!selectedTournament.value) {
    prizes.value = null;
    return;
  }

  loading.value = true;
  prizes.value = null;

  try {
    const response = await getPrizes(selectedTournament.value);
    if (response.status === 200 && response.data && "best_scorer" in response.data) {
      prizes.value = response.data;
    }
  } catch (e) {
    console.error("Failed to load prizes", e);
  }

  loading.value = false;
}

function getPositionClass(position: number): string {
  if (position === 1) return "text-yellow-600 text-xl";
  if (position === 2) return "text-gray-500";
  if (position === 3) return "text-amber-700";
  return "text-stone-600";
}
</script>