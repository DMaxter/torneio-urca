import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { Router } from "vue-router";

import type { LoginCredentials } from "@router/backend/services/auth/types";
import * as authService from "@router/backend/services/auth";
import { USER_ROLES } from "@router/backend/services/user/types";
import { getUsers } from "@router/backend/services/user";
import type { User } from "@router/backend/services/user/types";

/**
 * Pinia store managing the current user's authentication and authorization state.
 * This includes user metadata, roles, and assigned access control permissions.
 */
export const useAuthStore = defineStore("auth", () => {
  const username = ref<string | null>(null);
  const userId = ref<string | null>(null);
  const roles = ref<string[]>([]);
  const assignedGames = ref<string[]>([]);
  const assignedGamesForCalls = ref<string[]>([]);
  const initialized = ref(false);

  /**
   * Checks if the user is authenticated (has a valid username session).
   */
  const isAuthenticated = computed(() => !!username.value);
  /**
   * Checks if the user has the 'admin' super-permission based on username.
   */
  const isAdmin = computed(() => username.value === "admin");
  const canManagePlayers = computed(() => roles.value.includes(USER_ROLES.MANAGE_PLAYERS));
  const canManageGames = computed(() => roles.value.includes(USER_ROLES.MANAGE_GAMES));
  const canManageGameEvents = computed(() => roles.value.includes(USER_ROLES.MANAGE_GAME_EVENTS));
  const canFillGameCalls = computed(() => roles.value.includes(USER_ROLES.FILL_GAME_CALLS));
  // Apenas utilizadores com a role explícita — admin NÃO tem automaticamente
  const canOpenCalendar = computed(() => roles.value.includes(USER_ROLES.OPEN_CALENDAR));
  const canManageAnnouncements = computed(() => roles.value.includes(USER_ROLES.ANNOUNCER));

  /**
   * Determines if the user possesses a specific role.
   * @param role - Role string to check.
   * @returns Boolean indicating whether the role is assigned.
   */
  function hasRole(role: string): boolean {
    return roles.value.includes(role);
  }

  /**
   * Validates if the user has specific assigned management rights for a game.
   * @param gameId - The ID of the game.
   * @returns True if the user has explicit management access.
   */
  function hasGameAccess(gameId: string): boolean {
    return assignedGames.value.includes(gameId);
  }

  /**
   * Validates if the user is authorized to manage calls for a specific game.
   * @param gameId - The ID of the game.
   * @returns True if the user has call filling access.
   */
  function hasCallAccess(gameId: string): boolean {
    return assignedGamesForCalls.value.includes(gameId);
  }

  /**
   * Initializes the authentication store by verifying tokens and pulling user entity context.
   * Performs an API call to getCurrentUser and populates privileges.
   */
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

  /**
   * Authenticates the user with login credentials and delegates routing state.
   * 
   * @param credentials - Represents the submitted username/password payload.
   * @param router - Vue router instance for redirecting after successful authentication.
   * @returns Status object specifying `success`.
   */
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

  /**
   * Logs out the user, clearing the backend session token and destroying the frontend state.
   * 
   * @param router - Vue router instance for redirection to the login view.
   */
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
    canOpenCalendar,
    canManageAnnouncements,
    hasRole,
    hasGameAccess,
    hasCallAccess,
    init,
    login,
    logout,
    refreshRoles,
  };
});
