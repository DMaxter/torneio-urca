import { defineStore } from "pinia";
import { ref } from "vue";

import { type CreateUser, User } from "@router/backend/services/user/types";
import { API } from "@router/backend";
import type { APIResponse } from "@router/backend/types";
import { AxiosError } from "axios";

export const useUserStore = defineStore("usersStore", () => {
  const users = ref<User[]>([]);

  function init(data: User[]) {
    users.value = data;
  }

  function add(user: User) {
    users.value.push(user);
  }

  function remove(id: string) {
    const index = users.value.findIndex((t) => t.id === id);

    if (index === -1) {
      console.error(`User ${id} not in store`);
      return
    }

    users.value.splice(index, 1);
  }

  async function getUsers(): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.users.getUsers();

      if (status === 200) {
        init((data as User[]).map((u) => new User(u)));

        return {
          success: true,
          content: null
        };
      } else {
        return {
          success: false,
          content: ((data as unknown) as Error).message,
          status: status,
        };
      }
    } catch (error) {
      const _error = error as AxiosError<string>;

      return {
        success: false,
        status: _error.response?.status,
        content: null
      };
    }
  }

  async function createUser(user: CreateUser): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.users.createUser(user);

      if (status === 200) {
        add(new User(data as User));

        return {
          success: true,
          content: null,
        };
      } else {
        return {
          success: false,
          content: ((data as unknown) as Error).message,
          status: status,
        };
      }
    } catch (error) {
      const _error = error as AxiosError<string>;

      return {
        success: false,
        status: _error.response?.status,
        content: null
      };
    }
  }

  return {
    users, getUsers, createUser
  };
});
