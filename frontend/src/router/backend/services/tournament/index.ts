import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateTournament, Tournament } from "@router/backend/services/tournament/types";

export async function getTournaments(): Promise<AxiosResponse<Tournament[] | Error>> {
  return await http.get("/tournaments");
}

export async function createTournament(tournament: CreateTournament): Promise<AxiosResponse<Tournament | Error>> {
  return await http.post("/tournaments", tournament);
}

export async function deleteTournament(tournamentId: string): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/tournaments/${tournamentId}`);
}

export type KnockoutPreview = {
  game_id: string;
  label: string;
  phase: string;
  home_placeholder: string;
  away_placeholder: string;
  home_resolved: string | null;
  away_resolved: string | null;
};

export type PreviewKnockoutResponse = {
  complete: boolean;
  remaining: number;
  knockout: KnockoutPreview[];
  message?: string;
  canAdvance?: boolean;
};

export async function previewKnockout(tournamentId: string): Promise<AxiosResponse<PreviewKnockoutResponse | Error>> {
  return await http.get(`/tournaments/${tournamentId}/preview-knockout`);
}

export type AdvanceResponse = {
  success: boolean;
  updated_games: number;
  games: string[];
};

export async function advanceToKnockout(tournamentId: string): Promise<AxiosResponse<AdvanceResponse | Error>> {
  return await http.post(`/tournaments/${tournamentId}/advance-phase`);
}
