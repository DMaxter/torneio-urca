import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateGame, Game } from "@router/backend/services/game/types";

export async function getGames(): Promise<AxiosResponse<Game[] | Error>> {
  return await http.get("/games");
}

export async function createGame(game: CreateGame): Promise<AxiosResponse<Game | Error>> {
  const body: Record<string, any> = {
    tournament: game.tournament,
    phase: game.phase,
  };
  if (game.home_call) body.home_call = game.home_call;
  if (game.away_call) body.away_call = game.away_call;
  if (game.scheduled_date != null) body.scheduled_date = game.scheduled_date;
  if (game.home_placeholder) body.home_placeholder = game.home_placeholder;
  if (game.away_placeholder) body.away_placeholder = game.away_placeholder;
  return await http.post("/games", body);
}

export async function updateGame(gameId: string, scheduledDate: Date | null): Promise<AxiosResponse<Game | Error>> {
  return await http.patch(`/games/${gameId}`, { scheduled_date: scheduledDate });
}

export async function deleteGame(gameId: string): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/games/${gameId}`);
}
