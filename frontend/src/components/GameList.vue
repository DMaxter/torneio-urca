<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Jogos">
    <P-DataTable :value="gameStore.games">
      <P-Column field="id" header="ID" />
      <P-Column field="scheduled_date" header="Horário" />
      <P-Column field="home_call.team" header="Equipa da Casa" />
      <P-Column field="away_call.team" header="Equipa Visitante" />
    </P-DataTable>
    <template #footer>
      <P-Button @click="gameStore.getGames()">Atualizar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import { useGameStore } from "@stores/games";

const enabled = defineModel<boolean>();

const gameStore = useGameStore();
onMounted(async () => {
  await gameStore.getGames()
});
</script>
