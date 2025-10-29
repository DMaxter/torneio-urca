import { defineStore } from "pinia";
import { ref } from "vue";

import type { CreateGroup, Group } from "@router/backend/services/group/types";
import { API } from "@router/backend";
import type { APIResponse } from "@router/backend/types";
import { AxiosError } from "axios";

export const useGroupStore = defineStore("groupsStore", () => {
  const groups = ref<Group[]>([]);

  function init(data: Group[]) {
    groups.value = data;
  }

  function add(group: Group) {
    groups.value.push(group);
  }

  function remove(id: string) {
    const index = groups.value.findIndex((g) => g.id === id);

    if (index === -1) {
      console.error(`Group ${id} not in store`);
      return
    }

    groups.value.splice(index, 1);
  }

  async function getGroups(): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.groups.getGroups();

      if (status === 200) {
        init(data as Group[]);

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
      }
    }
  }

  async function createGroup(group: CreateGroup): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.groups.createGroup(group);

      if (status === 200) {
        add(data as Group);

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
    groups, getGroups, createGroup
  };
});
