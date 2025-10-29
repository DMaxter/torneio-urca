<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Utilizadores">
    <P-DataTable :value="userStore.users">
      <P-Column field="id" header="ID" />
      <P-Column field="gender" header="Género" />
      <P-Column field="name" header="Nome" />
      <P-Column field="confirmed" header="Confirmado" />
      <P-Column field="birth_date" header="Data de Nascimento" />
      <P-Column field="roles" header="Funções" />
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
