import { defineStore } from "pinia";
import { ref } from "vue";

import { type Tournament } from "@router/backend/services/tournament/types";
import * as tournamentService from "@router/backend/services/tournament";
import { createGenericStore } from "@stores/base";

export const useTournamentStore = defineStore("tournamentsStore", () => {
  const tournaments = ref<Tournament[]>([]);

  const base = createGenericStore("Tournament", tournaments, {
    getAll: tournamentService.getTournaments,
    create: tournamentService.createTournament,
  });

  async function deleteTournament(tournamentId: string) {
    try {
      const { status } = await tournamentService.deleteTournament(tournamentId);
      if (status === 204) {
        base.remove(tournamentId);
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  return {
    tournaments,
    getTournaments: base.getAll,
    forceGetTournaments: base.forceGetAll,
    createTournament: base.create,
    deleteTournament,
    init: base.init,
    add: base.add,
    remove: base.remove,
  };
});
