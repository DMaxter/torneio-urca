<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Utilizador' : 'Editar Utilizador'">
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="username" v-model="user.username" />
      <label for="username">Nome de Utilizador</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="password" v-model="user.password" type="password" />
      <label for="password">Palavra-passe</label>
    </P-FloatLabel>
    <template #footer>
      <P-Button @click="createOrUpdate">{{ creating ? "Criar" : "Alterar" }}</P-Button>
      <P-Button @click="close">Cancelar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useToast } from "primevue/usetoast";

import { CreateUser, type User } from "@router/backend/services/user/types";
import { useUserStore } from "@stores/users";

const toast = useToast();
const enabled = defineModel<boolean>();
const props = defineProps<{
  user?: User
}>();

const creating = computed(() => props.user === undefined);

interface UserForm {
  username: string;
  password: string;
}

const user = ref<UserForm>({ username: "", password: "" });
onMounted(() => {
  if (!creating.value) {
    user.value.username = props.user!.username;
    user.value.password = "";
  }
});

const userStore = useUserStore();

async function createOrUpdate() {
  if (creating.value) {
    await create();
  } else {
    await update();
  }
}

async function create() {
  const result = await userStore.createUser(user.value as CreateUser);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Utilizador criado com sucesso", life: 3000 });
    close();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: result.content || "Erro ao criar utilizador", life: 3000 });
  }
}

async function update() {
  toast.add({ severity: "warn", summary: "Em desenvolvimento", detail: "Funcionalidade de edição ainda não disponível", life: 3000 });
}

function close() {
  enabled.value = false;
}
</script>

<style lang="scss" scoped>
.field {
  margin-top: 10px;
}
</style>
