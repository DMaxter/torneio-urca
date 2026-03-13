<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Equipas">
    <P-DataTable :value="teamStore.teams">
      <P-Column field="id" header="ID" />
      <P-Column field="name" header="Nome" />
    </P-DataTable>
    <template #footer>
      <P-Button @click="teamStore.getTeams()">Atualizar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import { useTeamStore } from "@stores/teams";

const enabled = defineModel<boolean>();

const teamStore = useTeamStore();
onMounted(async () => {
  await teamStore.getTeams()
});
</script>
