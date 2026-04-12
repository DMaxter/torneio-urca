<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Utilizadores" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-DataTable :value="userStore.users" striped-rows size="small">
      <P-Column field="username" header="Nome de Utilizador">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>👤</span>
            <span class="font-medium">{{ data.username }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Ações" class="w-[120px]">
        <template #body="{ data }">
          <div class="flex gap-2 items-center">
            <span
              class="material-symbols-outlined text-red-600 text-xl cursor-pointer hover:opacity-70"
              @click="confirmDelete(data)"
            >
              person_remove
            </span>
            <span class="text-xs text-stone-500">Eliminar</span>
          </div>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="userStore.forceGetUsers()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="deleteDialog" modal header="Confirmar" class="w-11/12 md:w-8/12">
    <p>Tem a certeza que deseja eliminar o utilizador <strong>{{ userToDelete?.username }}</strong>?</p>
    <template #footer>
      <P-Button severity="danger" @click="handleDelete">
        <span class="material-symbols-outlined text-red-600">delete</span>
        Eliminar
      </P-Button>
      <P-Button severity="secondary" @click="deleteDialog = false">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
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
