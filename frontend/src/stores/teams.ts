import { defineStore } from "pinia";
import { ref } from "vue";

import { type Team, CreateTeam } from "@router/backend/services/team/types";
import * as teamService from "@router/backend/services/team";
import { createGenericStore } from "@stores/base";

export const useTeamStore = defineStore("teamsStore", () => {
  const teams = ref<Team[]>([]);

  const base = createGenericStore("Team", teams, {
    getAll: teamService.getTeams,
    create: teamService.createTeam,
  });

  return {
    teams,
    getTeams: base.getAll,
    createTeam: base.create,
    init: base.init,
    add: base.add,
    remove: base.remove,
  };
});
