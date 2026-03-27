import { defineStore } from "pinia";
import { ref } from "vue";

import { type Player, CreatePlayer, CreateAdminPlayer } from "@router/backend/services/player/types";
import * as playerService from "@router/backend/services/player";
import { createGenericStore } from "@stores/base";

export const usePlayerStore = defineStore("playersStore", () => {
  const players = ref<Player[]>([]);

  const base = createGenericStore("Player", players, {
    getAll: playerService.getPlayers,
    create: playerService.createPlayer,
  });

  async function createAdminPlayer(player: CreateAdminPlayer) {
    try {
      const { status, data } = await playerService.createAdminPlayer(player);
      if (status === 201) {
        return { success: true, content: data as Player };
      }
      return { success: false, content: null };
    } catch {
      return { success: false, content: null };
    }
  }

  async function confirmPlayer(playerId: string) {
    try {
      const { status, data } = await playerService.confirmPlayer(playerId);
      if (status === 200) {
        base.update(data as Player);
        return { success: true, content: null };
      }
      return { success: false, content: null };
    } catch {
      return { success: false, content: null };
    }
  }

  async function deletePlayer(playerId: string) {
    try {
      const { status } = await playerService.deletePlayer(playerId);
      if (status === 204) {
        base.remove(playerId);
        return { success: true, content: null };
      }
      return { success: false, content: null };
    } catch {
      return { success: false, content: null };
    }
  }

  return {
    players,
    getPlayers: base.getAll,
    createPlayer: base.create,
    createAdminPlayer,
    confirmPlayer,
    deletePlayer,
    init: base.init,
    add: base.add,
    update: base.update,
    remove: base.remove,
  };
});
