import { defineStore } from "pinia";
import { ref } from "vue";

import type { CreatePlayer, Player } from "@router/backend/services/player/types";
import { API } from "@router/backend";
import type { APIResponse } from "@router/backend/types";
import { AxiosError } from "axios";

export const usePlayerStore = defineStore("playersStore", () => {
  const players = ref<Player[]>([]);

  function init(data: Player[]) {
    players.value = data;
  }

  function add(player: Player) {
    players.value.push(player);
  }

  function update(player: Player) {
    const index = players.value.findIndex((p) => p.id === player.id);
    if (index !== -1) {
      players.value[index] = player;
    }
  }

  function remove(id: string) {
    const index = players.value.findIndex((p) => p.id === id);
    if (index === -1) {
      console.error(`player ${id} not in store`);
      return;
    }
    players.value.splice(index, 1);
  }

  async function getPlayers(): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.players.getPlayers();
      if (status === 200) {
        init(data as Player[]);
        return { success: true, content: null };
      } else {
        return { success: false, content: ((data as unknown) as Error).message, status };
      }
    } catch (error) {
      const _error = error as AxiosError<string>;
      return { success: false, status: _error.response?.status, content: null };
    }
  }

  async function createPlayer(player: CreatePlayer): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.players.createPlayer(player);
      if (status === 201) {
        add(data as Player);
        return { success: true, content: null };
      } else {
        return { success: false, content: ((data as unknown) as Error).message, status };
      }
    } catch (error) {
      const _error = error as AxiosError<string>;
      return { success: false, status: _error.response?.status, content: null };
    }
  }

  async function confirmPlayer(playerId: string): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await API.players.confirmPlayer(playerId);
      if (status === 200) {
        update(data as Player);
        return { success: true, content: null };
      } else {
        return { success: false, content: ((data as unknown) as Error).message, status };
      }
    } catch (error) {
      const _error = error as AxiosError<string>;
      return { success: false, status: _error.response?.status, content: null };
    }
  }

  return { players, getPlayers, createPlayer, confirmPlayer };
});
