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

  return {
    groups,
    getGroups: base.getAll,
    createGroup: base.create,
    init: base.init,
    add: base.add,
    remove: base.remove,
  };
});
