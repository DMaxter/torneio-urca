import { defineStore } from "pinia";
import { ref } from "vue";

import type { CreateGame, Game } from "@router/backend/services/game/types";
import { API } from "@router/backend";
import type { APIResponse } from "@router/backend/types";
import { AxiosError } from "axios";

export const useGameStore = defineStore("gamesStore", () => {
  const games = ref<Game[]>([]);

  function init(data: Game[]) {
    games.value = data;
  }

  function add(game: Game) {
    games.value.push(game);
  }

  function remove(id: string) {
    const index = games.value.findIndex((g) => g.id === id);

    if (index === -1) {
      console.error(`Game ${id} not in store`);
      return
    }

    games.value.splice(index, 1);
  }

  async function getGames(): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.games.getGames();

      if (status === 200) {
        init(data as Game[]);

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

  async function createGame(game: CreateGame): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.games.createGame(game);

      if (status === 200) {
        add(data as Game);

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
    games, getGames, createGame
  };
});
