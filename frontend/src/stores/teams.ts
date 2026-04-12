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

  async function deleteTeam(teamId: string) {
    try {
      const { status } = await teamService.deleteTeam(teamId);
      if (status === 204) {
        base.remove(teamId);
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  async function updateTeam(teamId: string, team: CreateTeam) {
    try {
      const { status, data } = await teamService.updateTeam(teamId, team);
      if (status === 200) {
        base.update(data as Team);
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  return {
    teams,
    getTeams: base.getAll,
    forceGetTeams: base.forceGetAll,
    createTeam: base.create,
    deleteTeam,
    updateTeam,
    init: base.init,
    add: base.add,
    update: base.update,
    remove: base.remove,
  };
});
