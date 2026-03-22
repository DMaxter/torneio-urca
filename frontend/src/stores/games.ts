import { defineStore } from "pinia";
import { ref } from "vue";

import { type Game, CreateGame } from "@router/backend/services/game/types";
import * as gameService from "@router/backend/services/game";
import { createGenericStore } from "@stores/base";

export const useGameStore = defineStore("gamesStore", () => {
  const games = ref<Game[]>([]);

  const base = createGenericStore("Game", games, {
    getAll: gameService.getGames,
    create: gameService.createGame,
  });

  return {
    games,
    getGames: base.getAll,
    createGame: base.create,
    init: base.init,
    add: base.add,
    remove: base.remove,
  };
});
