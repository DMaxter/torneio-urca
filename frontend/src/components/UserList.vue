<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Utilizadores" :style="{ width: '400px' }">
    <P-DataTable :value="userStore.users" striped-rows size="small">
      <P-Column field="username" header="Nome de Utilizador">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>👤</span>
            <span class="font-medium">{{ data.username }}</span>
          </div>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button label="Atualizar" icon="pi pi-refresh" @click="userStore.getUsers()" />
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useUserStore } from "@stores/users";

const enabled = defineModel<boolean>();
const userStore = useUserStore();

onMounted(async () => {
  await userStore.getUsers();
});
</script>
