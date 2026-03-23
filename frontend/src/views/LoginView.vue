<template>
  <div class="min-h-screen flex items-center justify-center bg-stone-100">
    <div class="bg-white p-8 rounded-xl shadow-md w-full max-w-md">
      <h1 class="text-center mb-6 text-2xl font-bold text-stone-900">Iniciar Sessão</h1>
      <P-FloatLabel class="mt-4" variant="on">
        <P-InputText id="username" v-model="credentials.username" fluid />
        <label for="username">Nome de Utilizador</label>
      </P-FloatLabel>
      <P-FloatLabel class="mt-4" variant="on">
        <P-InputText id="password" v-model="credentials.password" type="password" fluid />
        <label for="password">Palavra-passe</label>
      </P-FloatLabel>
      <P-Button
        class="mt-6 w-full"
        @click="handleLogin"
        :loading="loading"
        fluid
      >
        <span class="material-symbols-outlined">login</span>
        Entrar
      </P-Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";

import { useAuthStore } from "@stores/auth";
import type { LoginCredentials } from "@router/backend/services/auth/types";

const router = useRouter();
const toast = useToast();
const authStore = useAuthStore();

const credentials = ref<LoginCredentials>({ username: "", password: "" });
const loading = ref(false);

async function handleLogin() {
  if (!credentials.value.username || !credentials.value.password) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Preencha todos os campos", life: 3000 });
    return;
  }

  loading.value = true;
  const result = await authStore.login(credentials.value);
  loading.value = false;

  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Sessão iniciada", life: 2000 });
    router.push("/admin");
  }
}
</script>

<style scoped>
</style>
