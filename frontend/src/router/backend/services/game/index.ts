import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateGame, Game, GameStatus, AssignGoalDto, AssignCardDto } from "@router/backend/services/game/types";

// Serialize date as local ISO string (no UTC conversion) so the backend stores
// and returns the same wall-clock time, avoiding timezone shift on roundtrip.
function toLocalISOString(date: Date): string {
  const p = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())}T${p(date.getHours())}:${p(date.getMinutes())}:${p(date.getSeconds())}`;
}

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
  if (game.scheduled_date != null) body.scheduled_date = toLocalISOString(game.scheduled_date as Date);
  if (game.home_placeholder) body.home_placeholder = game.home_placeholder;
  if (game.away_placeholder) body.away_placeholder = game.away_placeholder;
  return await http.post("/games", body);
}

export async function updateGame(gameId: string, scheduledDate: Date | null): Promise<AxiosResponse<Game | Error>> {
  return await http.patch(`/games/${gameId}`, {
    scheduled_date: scheduledDate ? toLocalISOString(scheduledDate) : null,
  });
}

export async function deleteGame(gameId: string): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/games/${gameId}`);
}

export async function updateGameCall(callId: string, players: { player: string; number: number | null }[]): Promise<AxiosResponse<any | Error>> {
  return await http.patch(`/games/calls/${callId}`, { players });
}

export async function updateGameStatus(gameId: string, status: GameStatus): Promise<AxiosResponse<Game | Error>> {
  return await http.patch(`/games/${gameId}/status`, { status });
}

export async function confirmGameCalls(gameId: string): Promise<AxiosResponse<Game | Error>> {
  return await http.patch(`/games/${gameId}/confirm-calls`);
}

export async function getGame(gameId: string): Promise<AxiosResponse<Game | Error>> {
  return await http.get(`/games/${gameId}`);
}

export async function assignGoal(goal: AssignGoalDto): Promise<AxiosResponse<any | Error>> {
  return await http.post("/goals", goal);
}

export async function assignCard(card: AssignCardDto): Promise<AxiosResponse<any | Error>> {
  return await http.post("/cards", card);
}
