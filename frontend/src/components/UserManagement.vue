<template>
  <P-Dialog
    v-model:visible="enabled"
    modal
    :header="creating ? 'Criar Utilizador' : 'Alterar Palavra-passe'"
    class="w-[350px]"
  >
    <P-FloatLabel v-if="creating" class="mt-[10px]" variant="on">
      <P-InputText id="username" v-model="userForm.username" fluid />
      <label for="username">Nome de Utilizador</label>
    </P-FloatLabel>
    <div v-if="creating" class="mt-[10px]">
      <P-FloatLabel variant="on">
        <P-InputText id="password" v-model="userForm.password" type="password" fluid />
        <label for="password">Palavra-passe</label>
      </P-FloatLabel>
    </div>
    <div v-else class="flex flex-column gap-3">
      <P-FloatLabel variant="on">
        <P-InputText id="current-password" v-model="passwords.current_password" type="password" fluid />
        <label for="current-password">Palavra-passe Atual</label>
      </P-FloatLabel>
      <P-FloatLabel variant="on">
        <P-InputText id="new-password" v-model="passwords.new_password" type="password" fluid />
        <label for="new-password">Nova Palavra-passe</label>
      </P-FloatLabel>
    </div>
    <template #footer>
      <P-Button severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
      <P-Button @click="createOrUpdate">
        {{ creating ? "Criar" : "Alterar" }}
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useToast } from "primevue/usetoast";

import { CreateUser, type User, ChangePassword } from "@router/backend/services/user/types";
import { useUserStore } from "@stores/users";

const toast = useToast();
const enabled = defineModel<boolean>();
const props = defineProps<{
  user?: User;
}>();

const creating = computed(() => props.user === undefined);

interface UserFormData {
  username: string;
  password: string;
}

const userForm = ref<UserFormData>({ username: "", password: "" });
const passwords = ref<ChangePassword>({ current_password: "", new_password: "" });

onMounted(() => {
  if (!creating.value) {
    userForm.value.username = props.user!.username;
  }
});

const userStore = useUserStore();

async function createOrUpdate() {
  if (creating.value) {
    await create();
  } else {
    await changePassword();
  }
}

async function create() {
  if (!userForm.value.username || !userForm.value.password) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Preencha todos os campos", life: 3000 });
    return;
  }
  const result = await userStore.createUser(userForm.value as CreateUser);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Utilizador criado com sucesso", life: 3000 });
    close();
  }
}

async function changePassword() {
  if (!passwords.value.current_password || !passwords.value.new_password) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Preencha todos os campos", life: 3000 });
    return;
  }
  const result = await userStore.changePassword(props.user!.id, passwords.value);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Palavra-passe alterada com sucesso", life: 3000 });
    close();
  }
}

function close() {
  enabled.value = false;
  userForm.value = { username: "", password: "" };
  passwords.value = { current_password: "", new_password: "" };
}
</script>
