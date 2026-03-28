<template>
  <P-Dialog v-model:visible="enabled" modal header="Alterar Palavra-passe" class="w-11/12 md:w-8/12 lg:w-6/12">
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="currentPassword" v-model="passwords.current_password" type="password" fluid />
      <label for="currentPassword">Palavra-passe Atual</label>
    </P-FloatLabel>
    <P-FloatLabel class="field mt-4" variant="on">
      <P-InputText id="newPassword" v-model="passwords.new_password" type="password" fluid />
      <label for="newPassword">Nova Palavra-passe</label>
    </P-FloatLabel>
    <P-FloatLabel class="field mt-4" variant="on">
      <P-InputText id="confirmPassword" v-model="confirmPassword" type="password" fluid />
      <label for="confirmPassword">Confirmar Palavra-passe</label>
    </P-FloatLabel>
    <template #footer>
      <P-Button severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
      <P-Button @click="change" :loading="loading">
        <span class="material-symbols-outlined">save</span>
        Guardar
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useToast } from "primevue/usetoast";
import { useUserStore } from "@stores/users";
import { useAuthStore } from "@stores/auth";

const toast = useToast();
const enabled = defineModel<boolean>();
const userStore = useUserStore();
const authStore = useAuthStore();

const loading = ref(false);
const passwords = ref({ current_password: "", new_password: "" });
const confirmPassword = ref("");

async function change() {
  if (!passwords.value.current_password || !passwords.value.new_password) {
    toast.add({ severity: "warn", summary: "Campos obrigatórios", detail: "Preencha todos os campos", life: 3000 });
    return;
  }

  if (passwords.value.new_password !== confirmPassword.value) {
    toast.add({ severity: "warn", summary: "Erro", detail: "As palavras-passe não coincidem", life: 3000 });
    return;
  }

  if (passwords.value.new_password.length < 6) {
    toast.add({ severity: "warn", summary: "Erro", detail: "A palavra-passe deve ter pelo menos 6 caracteres", life: 3000 });
    return;
  }

  loading.value = true;
  const result = await userStore.changePassword(authStore.userId!, passwords.value);
  loading.value = false;

  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Palavra-passe alterada", life: 3000 });
    close();
  }
}

function close() {
  passwords.value = { current_password: "", new_password: "" };
  confirmPassword.value = "";
  enabled.value = false;
}
</script>

<style scoped>
.field {
  margin-top: 0.5rem;
}
</style>
