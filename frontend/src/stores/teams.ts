import { defineStore } from "pinia";
import { ref } from "vue";

import type { CreateTeam, Team } from "@router/backend/services/team/types";
import { API } from "@router/backend";
import type { APIResponse } from "@router/backend/types";
import { AxiosError } from "axios";

export const useTeamStore = defineStore("teamsStore", () => {
  const teams = ref<Team[]>([]);

  function init(data: Team[]) {
    teams.value = data;
  }

  function add(team: Team) {
    teams.value.push(team);
  }

  function remove(id: string) {
    const index = teams.value.findIndex((t) => t.id === id);

    if (index === -1) {
      console.error(`team ${id} not in store`);
      return
    }

    teams.value.splice(index, 1);
  }

  async function getTeams(): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.teams.getTeams();

      if (status === 200) {
        init(data as Team[]);

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

  async function createTeam(team: CreateTeam): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.teams.createTeam(team);

      if (status === 200) {
        add(data as Team);

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
    teams, getTeams, createTeam
  };
});
