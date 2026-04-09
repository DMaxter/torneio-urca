import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { Router } from "vue-router";

import type { LoginCredentials } from "@router/backend/services/auth/types";
import * as authService from "@router/backend/services/auth";

export const useAuthStore = defineStore("auth", () => {
  const username = ref<string | null>(null);
  const userId = ref<string | null>(null);
  const initialized = ref(false);

  const isAuthenticated = computed(() => !!username.value);

  async function init() {
    if (initialized.value) return;
    
    try {
      const response = await authService.getCurrentUser();
      if (response.status === 200 && response.data) {
        username.value = response.data.username;
        userId.value = response.data.user_id;
      }
    } catch {
      username.value = null;
      userId.value = null;
    }
    initialized.value = true;
  }

  async function login(credentials: LoginCredentials, router: Router): Promise<{ success: boolean; content?: string }> {
    try {
      const response = await authService.login(credentials);
      if (response.status === 200 && response.data && "access_token" in response.data) {
        initialized.value = false;
        await init();
        router.push("/admin");
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  async function logout(router: Router) {
    try {
      await authService.logout();
    } catch {
      // ignore logout errors
    }
    username.value = null;
    userId.value = null;
    initialized.value = false;
    router.push("/login");
  }

  return {
    username,
    userId,
    isAuthenticated,
    init,
    login,
    logout,
  };
});
