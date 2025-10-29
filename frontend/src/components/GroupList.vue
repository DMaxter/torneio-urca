<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Equipas">
    <P-DataTable :value="groupStore.groups">
      <P-Column field="id" header="ID" />
      <P-Column field="name" header="Nome" />
      <P-Column field="teams" header="Equipas" />
    </P-DataTable>
    <template #footer>
      <P-Button @click="groupStore.getGroups()">Atualizar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import { useGroupStore } from "@stores/groups";

const enabled = defineModel<boolean>();

const groupStore = useGroupStore();
onMounted(async () => {
  await groupStore.getGroups()
});
</script>
