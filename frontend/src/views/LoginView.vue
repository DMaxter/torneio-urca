<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Iniciar Sessão</h1>
      <P-FloatLabel class="field" variant="on">
        <P-InputText id="username" v-model="credentials.username" fluid />
        <label for="username">Nome de Utilizador</label>
      </P-FloatLabel>
      <P-FloatLabel class="field" variant="on">
        <P-InputText id="password" v-model="credentials.password" type="password" fluid />
        <label for="password">Palavra-passe</label>
      </P-FloatLabel>
      <P-Button
        class="mt-10 field"
        label="Entrar"
        @click="handleLogin"
        :loading="loading"
        fluid
      >
        <span class="material-symbols-outlined">login</span>
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
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-card h1 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #1c1917;
  font-size: 1.5rem;
}

.field {
  margin-top: 1rem;
}

.field:first-of-type {
  margin-top: 0;
}
</style>
