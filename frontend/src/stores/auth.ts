import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

import type { LoginCredentials } from "@router/backend/services/auth/types";
import * as authService from "@router/backend/services/auth";

const TOKEN_KEY = "auth_token";

export const useAuthStore = defineStore("auth", () => {
  const storedToken = localStorage.getItem(TOKEN_KEY);
  const initialDecoded = storedToken
    ? (() => {
        try {
          const parts = storedToken.split(".");
          if (parts.length !== 3) return { user_id: null, username: null };
          const payload = JSON.parse(atob(parts[1]));
          return { user_id: payload.user_id || null, username: payload.sub || null };
        } catch {
          return { user_id: null, username: null };
        }
      })()
    : { user_id: null, username: null };

  const token = ref<string | null>(storedToken);
  const username = ref<string | null>(initialDecoded.username);
  const userId = ref<string | null>(initialDecoded.user_id);
  const router = useRouter();

  const isAuthenticated = computed(() => !!token.value);

  function decodeToken(tokenStr: string): { user_id: string | null; username: string | null } {
    try {
      const parts = tokenStr.split(".");
      if (parts.length !== 3) return { user_id: null, username: null };
      const payload = JSON.parse(atob(parts[1]));
      return {
        user_id: payload.user_id || null,
        username: payload.sub || null,
      };
    } catch {
      return { user_id: null, username: null };
    }
  }

  function setToken(newToken: string) {
    token.value = newToken;
    localStorage.setItem(TOKEN_KEY, newToken);
    const decoded = decodeToken(newToken);
    userId.value = decoded.user_id;
    username.value = decoded.username;
  }

  function clearToken() {
    token.value = null;
    username.value = null;
    userId.value = null;
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
    userId,
    isAuthenticated,
    login,
    logout,
    clearToken,
  };
});
