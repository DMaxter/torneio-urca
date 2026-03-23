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
      <P-Column header="Ações" :style="{ width: '120px' }">
        <template #body="{ data }">
          <div class="flex gap-2">
            <span
              class="material-symbols-outlined delete-icon"
              @click="confirmDelete(data)"
            >
              person_remove
            </span>
          </div>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button label="Atualizar" @click="userStore.getUsers()">
        <span class="material-symbols-outlined">sync</span>
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="deleteDialog" modal header="Confirmar" :style="{ width: '350px' }">
    <p>Tem a certeza que deseja eliminar o utilizador <strong>{{ userToDelete?.username }}</strong>?</p>
    <template #footer>
      <P-Button severity="danger" label="Eliminar" @click="handleDelete" />
      <P-Button severity="secondary" label="Cancelar" @click="deleteDialog = false" />
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";

import { useUserStore } from "@stores/users";
import type { User } from "@router/backend/services/user/types";

const toast = useToast();
const enabled = defineModel<boolean>();
const userStore = useUserStore();

const deleteDialog = ref(false);
const userToDelete = ref<User | null>(null);

onMounted(async () => {
  await userStore.getUsers();
});

function confirmDelete(user: User) {
  userToDelete.value = user;
  deleteDialog.value = true;
}

async function handleDelete() {
  if (!userToDelete.value) return;
  const result = await userStore.deleteUser(userToDelete.value.id);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Utilizador eliminado", life: 3000 });
    await userStore.getUsers();
  }
  deleteDialog.value = false;
  userToDelete.value = null;
}
</script>

<style scoped>
.delete-icon {
  cursor: pointer;
  color: #dc2626;
  font-size: 24px;
}

.delete-icon:hover {
  opacity: 0.7;
}
</style>
