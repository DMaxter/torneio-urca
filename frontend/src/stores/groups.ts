import { defineStore } from "pinia";
import { ref } from "vue";

import { type Group, CreateGroup } from "@router/backend/services/group/types";
import * as groupService from "@router/backend/services/group";
import { createGenericStore } from "@stores/base";

export const useGroupStore = defineStore("groupsStore", () => {
  const groups = ref<Group[]>([]);

  const base = createGenericStore("Group", groups, {
    getAll: groupService.getGroups,
    create: groupService.createGroup,
  });

  async function deleteGroup(groupId: string) {
    try {
      const { status } = await groupService.deleteGroup(groupId);
      if (status === 204) {
        base.remove(groupId);
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  async function createGroup(group: CreateGroup) {
    try {
      const { status, data } = await groupService.createGroup(group);
      if (status === 201) {
        base.add(data as Group);
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  async function updateGroup(groupId: string, group: CreateGroup) {
    try {
      const { status, data } = await groupService.updateGroup(groupId, group);
      if (status === 200) {
        base.update(data as Group);
        return { success: true };
      }
      return { success: false, error: null };
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: { error?: string }; error?: string } } };
      const errorMessage = error.response?.data?.detail?.error || error.response?.data?.error || null;
      return { success: false, error: errorMessage };
    }
  }

  return {
    groups,
    getGroups: base.getAll,
    forceGetGroups: base.forceGetAll,
    createGroup,
    deleteGroup,
    updateGroup,
    init: base.init,
    add: base.add,
    remove: base.remove,
  };
});
