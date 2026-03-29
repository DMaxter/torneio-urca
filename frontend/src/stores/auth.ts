import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

import type { LoginCredentials } from "@router/backend/services/auth/types";
import * as authService from "@router/backend/services/auth";

const COOKIE_NAME = "auth_token";

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? match[2] : null;
}

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

const storedToken = getCookie(COOKIE_NAME);
const initialDecoded = storedToken
  ? decodeToken(storedToken)
  : { user_id: null, username: null };

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(storedToken);
  const username = ref<string | null>(initialDecoded.username);
  const userId = ref<string | null>(initialDecoded.user_id);
  const router = useRouter();

  const isAuthenticated = computed(() => !!token.value);

  function setToken(newToken: string) {
    token.value = newToken;
    const decoded = decodeToken(newToken);
    userId.value = decoded.user_id;
    username.value = decoded.username;
  }

  function clearToken() {
    token.value = null;
    username.value = null;
    userId.value = null;
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

  async function logout() {
    try {
      await authService.logout();
    } catch {
    }
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
