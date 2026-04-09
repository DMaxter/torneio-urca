import { defineStore } from "pinia";
import { ref } from "vue";

import { type User, type ChangePassword } from "@router/backend/services/user/types";
import * as userService from "@router/backend/services/user";
import { createGenericStore } from "@stores/base";

export const useUserStore = defineStore("usersStore", () => {
  const users = ref<User[]>([]);

  const base = createGenericStore("User", users, {
    getAll: userService.getUsers,
    create: userService.createUser,
  });

  async function deleteUser(userId: string) {
    try {
      await userService.deleteUser(userId);
      return { success: true, content: null };
    } catch {
      return { success: false, content: null };
    }
  }

  async function changePassword(userId: string, passwordData: ChangePassword) {
    try {
      await userService.changePassword(userId, passwordData);
      return { success: true, content: null };
    } catch {
      return { success: false, content: null };
    }
  }

  return {
    users,
    getUsers: base.getAll,
    createUser: base.create,
    changePassword,
    deleteUser,
    init: base.init,
    add: base.add,
    remove: base.remove,
  };
});
