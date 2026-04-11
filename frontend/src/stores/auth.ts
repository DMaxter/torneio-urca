import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { Router } from "vue-router";

import type { LoginCredentials } from "@router/backend/services/auth/types";
import * as authService from "@router/backend/services/auth";
import { USER_ROLES } from "@router/backend/services/user/types";
import { getUsers } from "@router/backend/services/user";
import type { User } from "@router/backend/services/user/types";

export const useAuthStore = defineStore("auth", () => {
  const username = ref<string | null>(null);
  const userId = ref<string | null>(null);
  const roles = ref<string[]>([]);
  const assignedGames = ref<string[]>([]);
  const assignedGamesForCalls = ref<string[]>([]);
  const initialized = ref(false);

  const isAuthenticated = computed(() => !!username.value);
  const isAdmin = computed(() => username.value === "admin");
  const canManagePlayers = computed(() => roles.value.includes(USER_ROLES.MANAGE_PLAYERS));
  const canManageGames = computed(() => roles.value.includes(USER_ROLES.MANAGE_GAMES));
  const canManageGameEvents = computed(() => roles.value.includes(USER_ROLES.MANAGE_GAME_EVENTS));
  const canFillGameCalls = computed(() => roles.value.includes(USER_ROLES.FILL_GAME_CALLS));

  function hasRole(role: string): boolean {
    return roles.value.includes(role);
  }

  function hasGameAccess(gameId: string): boolean {
    return assignedGames.value.includes(gameId);
  }

  function hasCallAccess(gameId: string): boolean {
    return assignedGamesForCalls.value.includes(gameId);
  }

  async function init() {
    if (initialized.value) return;
    
    try {
      const response = await authService.getCurrentUser();
      if (response.status === 200 && response.data) {
        username.value = response.data.username;
        userId.value = response.data.user_id;
        
        const usersRes = await getUsers();
        if (usersRes.status === 200 && usersRes.data && Array.isArray(usersRes.data)) {
          const currentUser = (usersRes.data as User[]).find((u: User) => u.username === username.value);
          if (currentUser) {
            roles.value = currentUser.roles || [];
            assignedGames.value = currentUser.assigned_games || [];
            assignedGamesForCalls.value = currentUser.assigned_games_for_calls || [];
          }
        }
      }
    } catch {
      username.value = null;
      userId.value = null;
      roles.value = [];
      assignedGames.value = [];
      assignedGamesForCalls.value = [];
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
    roles.value = [];
    assignedGames.value = [];
    initialized.value = false;
    router.push("/login");
  }

  function refreshRoles(newRoles: string[], newAssignedGames: string[], newAssignedGamesForCalls: string[] = []) {
    roles.value = newRoles;
    assignedGames.value = newAssignedGames;
    assignedGamesForCalls.value = newAssignedGamesForCalls;
  }

  return {
    username,
    userId,
    roles,
    assignedGames,
    assignedGamesForCalls,
    isAuthenticated,
    isAdmin,
    canManagePlayers,
    canManageGames,
    canManageGameEvents,
    canFillGameCalls,
    hasRole,
    hasGameAccess,
    hasCallAccess,
    init,
    login,
    logout,
    refreshRoles,
  };
});
