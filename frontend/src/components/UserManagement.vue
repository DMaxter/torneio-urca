<template>
  <P-Dialog
    v-model:visible="enabled"
    modal
    :header="creating ? 'Criar Utilizador' : 'Alterar Palavra-passe'"
    :style="{ width: '350px' }"
  >
    <P-FloatLabel v-if="creating" class="field" variant="on">
      <P-InputText id="username" v-model="user.username" />
      <label for="username">Nome de Utilizador</label>
    </P-FloatLabel>
    <div v-if="creating" class="field">
      <P-FloatLabel variant="on">
        <P-InputText id="password" v-model="user.password" type="password" />
        <label for="password">Palavra-passe</label>
      </P-FloatLabel>
    </div>
    <div v-else class="flex flex-column gap-3">
      <P-FloatLabel variant="on">
        <P-InputText id="current-password" v-model="passwords.current_password" type="password" />
        <label for="current-password">Palavra-passe Atual</label>
      </P-FloatLabel>
      <P-FloatLabel variant="on">
        <P-InputText id="new-password" v-model="passwords.new_password" type="password" />
        <label for="new-password">Nova Palavra-passe</label>
      </P-FloatLabel>
    </div>
    <template #footer>
      <P-Button @click="createOrUpdate">{{ creating ? "Criar" : "Alterar" }}</P-Button>
      <P-Button severity="secondary" @click="close">Cancelar</P-Button>
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

interface UserForm {
  username: string;
  password: string;
}

const user = ref<UserForm>({ username: "", password: "" });
const passwords = ref<ChangePassword>({ current_password: "", new_password: "" });

onMounted(() => {
  if (!creating.value) {
    user.value.username = props.user!.username;
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
  if (!user.value.username || !user.value.password) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Preencha todos os campos", life: 3000 });
    return;
  }
  const result = await userStore.createUser(user.value as CreateUser);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Utilizador criado com sucesso", life: 3000 });
    close();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: result.content || "Erro ao criar utilizador", life: 3000 });
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
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: result.content || "Erro ao alterar palavra-passe", life: 3000 });
  }
}

function close() {
  enabled.value = false;
  user.value = { username: "", password: "" };
  passwords.value = { current_password: "", new_password: "" };
}
</script>

<style lang="scss" scoped>
.field {
  margin-top: 10px;
}
</style>
