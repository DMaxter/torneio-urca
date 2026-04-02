import { defineStore } from "pinia";
import { ref } from "vue";

import { type Game } from "@router/backend/services/game/types";
import * as gameService from "@router/backend/services/game";

import { createGenericStore } from "@stores/base";

export const useGameStore = defineStore("gamesStore", () => {
  const games = ref<Game[]>([]);

  const base = createGenericStore("Game", games, {
    getAll: gameService.getGames,
    create: gameService.createGame,
  });

  async function updateGame(gameId: string, scheduledDate: Date | null) {
    try {
      const { status, data } = await gameService.updateGame(gameId, scheduledDate);
      if (status === 200) {
        const idx = games.value.findIndex(g => g.id === gameId);
        if (idx !== -1) games.value[idx] = data as Game;
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  async function deleteGame(gameId: string) {
    try {
      const { status } = await gameService.deleteGame(gameId);
      if (status === 204) {
        base.remove(gameId);
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  return {
    games,
    getGames: base.getAll,
    createGame: base.create,
    updateGame,
    deleteGame,
    init: base.init,
    add: base.add,
    remove: base.remove,
  };
});
