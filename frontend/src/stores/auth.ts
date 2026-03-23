import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

import type { LoginCredentials } from "@router/backend/services/auth/types";
import * as authService from "@router/backend/services/auth";

const TOKEN_KEY = "auth_token";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY));
  const username = ref<string | null>(null);
  const router = useRouter();

  const isAuthenticated = computed(() => !!token.value);

  function setToken(newToken: string) {
    token.value = newToken;
    localStorage.setItem(TOKEN_KEY, newToken);
  }

  function clearToken() {
    token.value = null;
    username.value = null;
    localStorage.removeItem(TOKEN_KEY);
  }

  async function login(credentials: LoginCredentials): Promise<{ success: boolean; content?: string }> {
    try {
      const response = await authService.login(credentials);
      if (response.status === 200 && response.data && "access_token" in response.data) {
        setToken(response.data.access_token);
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  function logout() {
    clearToken();
    router.push("/login");
  }

  return {
    token,
    username,
    isAuthenticated,
    login,
    logout,
    clearToken,
  };
});
