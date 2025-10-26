import { defineStore } from "pinia";
import { ref } from "vue";

import type { CreateTournament, Tournament } from "@router/backend/services/tournament/types";
import { API } from "@router/backend";
import type { APIResponse } from "@router/backend/types";
import { AxiosError } from "axios";

export const useTournamentStore = defineStore("tournamentsStore", () => {
  const tournaments = ref<Tournament[]>([]);

  function init(data: Tournament[]) {
    tournaments.value = data;
  }

  function add(tournament: Tournament) {
    tournaments.value.push(tournament);
  }

  function remove(id: string) {
    const index = tournaments.value.findIndex((t) => t.id === id);

    if (index === -1) {
      console.error(`Tournament ${id} not in store`);
      return
    }

    tournaments.value.splice(index, 1);
  }

  async function getTournaments(): Promise<APIResponse<string | null>> {
    try {
      const res = await API.tournaments.getTournaments();
      console.log(res);
      const { status, data } = res;

      if (status === 200) {
        init(data as Tournament[]);

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

  async function createTournament(tournament: CreateTournament): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.tournaments.createTournament(tournament);

      if (status === 200) {
        add(data as Tournament);

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
      console.error(_error);

      return {
        success: false,
        status: _error.response?.status,
        content: null
      };
    }
  }

  return {
    tournaments, getTournaments, createTournament
  };
});
