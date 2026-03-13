<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Utilizadores">
    <P-DataTable :value="userStore.users">
      <P-Column field="id" header="ID" />
      <P-Column field="username" header="Nome de Utilizador" />
    </P-DataTable>
    <template #footer>
      <P-Button @click="userStore.getUsers()">Atualizar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import { useUserStore } from "@stores/users";

const enabled = defineModel<boolean>();

const userStore = useUserStore();
onMounted(async () => {
  await userStore.getUsers()
});
</script>
