import { defineStore } from "pinia";
import { ref } from "vue";

import { type User, CreateUser } from "@router/backend/services/user/types";
import * as userService from "@router/backend/services/user";
import { createGenericStore } from "@stores/base";

export const useUserStore = defineStore("usersStore", () => {
  const users = ref<User[]>([]);

  const base = createGenericStore("User", users, {
    getAll: userService.getUsers,
    create: userService.createUser,
  });

  return {
    users,
    getUsers: base.getAll,
    createUser: base.create,
    init: base.init,
    add: base.add,
    remove: base.remove,
  };
});
