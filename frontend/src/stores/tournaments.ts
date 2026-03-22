import { defineStore } from "pinia";
import { ref } from "vue";

import { type Tournament, type CreateTournament } from "@router/backend/services/tournament/types";
import * as tournamentService from "@router/backend/services/tournament";
import { createGenericStore } from "@stores/base";

export const useTournamentStore = defineStore("tournamentsStore", () => {
  const tournaments = ref<Tournament[]>([]);

  const base = createGenericStore("Tournament", tournaments, {
    getAll: tournamentService.getTournaments,
    create: tournamentService.createTournament,
  });

  return {
    tournaments,
    getTournaments: base.getAll,
    createTournament: base.create,
    init: base.init,
    add: base.add,
    remove: base.remove,
  };
});
