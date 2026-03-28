<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Torneios" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-DataTable :value="tournamentStore.tournaments" striped-rows size="small">
      <P-Column field="name" header="Nome">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>🏆</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Equipas">
        <template #body="{ data }">
          <P-Tag :value="`${data.teams?.length || 0}`" severity="info" />
        </template>
      </P-Column>
      <P-Column header="Jogos">
        <template #body="{ data }">
          <P-Tag :value="`${data.games?.length || 0}`" severity="success" />
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="tournamentStore.getTournaments()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTournamentStore } from "@stores/tournaments";

const enabled = defineModel<boolean>();
const tournamentStore = useTournamentStore();

onMounted(async () => {
  await tournamentStore.getTournaments();
});
</script>
