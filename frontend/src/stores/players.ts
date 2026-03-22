import { defineStore } from "pinia";
import { ref } from "vue";

import { type Player, CreatePlayer } from "@router/backend/services/player/types";
import * as playerService from "@router/backend/services/player";
import { createGenericStore } from "@stores/base";

export const usePlayerStore = defineStore("playersStore", () => {
  const players = ref<Player[]>([]);

  const base = createGenericStore("Player", players, {
    getAll: playerService.getPlayers,
    create: playerService.createPlayer,
  });

  async function confirmPlayer(playerId: string) {
    const { status, data } = await playerService.confirmPlayer(playerId);
    if (status === 200) {
      base.update(data as Player);
      return { success: true, content: null };
    }
    return { success: false, content: ((data as unknown) as Error).message, status };
  }

  return {
    players,
    getPlayers: base.getAll,
    createPlayer: base.create,
    confirmPlayer,
    init: base.init,
    add: base.add,
    update: base.update,
    remove: base.remove,
  };
});
