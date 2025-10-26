<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Torneios">
    <P-DataTable :value="tournamentStore.tournaments">
      <P-Column field="id" header="ID"></P-Column>
      <P-Column field="name" header="Nome"></P-Column>
      <!--TODO: DELETE AND EDIT -->
    </P-DataTable>
    <template #footer>
      <P-Button @click="tournamentStore.getTournaments()">Atualizar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import { useTournamentStore } from "@stores/tournaments";

const enabled = defineModel<boolean>();

const tournamentStore = useTournamentStore();
onMounted(async () => {
  await tournamentStore.getTournaments()
});
</script>
