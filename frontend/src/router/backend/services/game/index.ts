import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateGame, Game, GameStatus, AssignGoalDto, AssignCardDto, AssignFoulDto, AssignPenaltyDto, UpdatePeriodDto } from "@router/backend/services/game/types";

function toLocalISOString(date: Date): string {
  const p = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())}T${p(date.getHours())}:${p(date.getMinutes())}:${p(date.getSeconds())}`;
}

export async function getGames(): Promise<AxiosResponse<Game[] | Error>> {
  return await http.get("/games");
}

export async function createGame(game: CreateGame): Promise<AxiosResponse<Game | Error>> {
  const body: Record<string, unknown> = {
    tournament: game.tournament,
    phase: game.phase,
  };
  if (game.label) body.label = game.label;
  if (game.home_call) body.home_call = { team: game.home_call.team };
  if (game.away_call) body.away_call = { team: game.away_call.team };
  if (game.scheduled_date != null) body.scheduled_date = toLocalISOString(game.scheduled_date as Date);
  if (game.home_placeholder) body.home_placeholder = game.home_placeholder;
  if (game.away_placeholder) body.away_placeholder = game.away_placeholder;
  // Include group reference fields for knockout games
  if (game.home_group_ref) body.home_group_ref = game.home_group_ref;
  if (game.home_group_position != null) body.home_group_position = game.home_group_position;
  if (game.away_group_ref) body.away_group_ref = game.away_group_ref;
  if (game.away_group_position != null) body.away_group_position = game.away_group_position;
  if (game.next_game_winner) body.next_game_winner = game.next_game_winner;
  if (game.next_game_loser) body.next_game_loser = game.next_game_loser;
  // Include group reference for group phase games
  if (game.group) body.group = game.group;
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

export async function updateGameCall(callId: string, players: { player: string; number: number | null }[], staff?: string[]): Promise<AxiosResponse<unknown | Error>> {
  return await http.patch(`/games/calls/${callId}`, { players, staff });
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

export async function updatePeriod(gameId: string, body: UpdatePeriodDto): Promise<AxiosResponse<Game | Error>> {
  return await http.patch(`/games/${gameId}/period`, body);
}

export async function assignGoal(goal: AssignGoalDto): Promise<AxiosResponse<unknown | Error>> {
  return await http.post("/goals", goal);
}

export async function assignCard(card: AssignCardDto): Promise<AxiosResponse<unknown | Error>> {
  return await http.post("/cards", card);
}

export async function assignFoul(foul: AssignFoulDto): Promise<AxiosResponse<unknown | Error>> {
  return await http.post("/fouls", foul);
}

export async function assignPenalty(penalty: AssignPenaltyDto): Promise<AxiosResponse<unknown | Error>> {
  return await http.post(`/games/${penalty.game}/penalties`, penalty);
}

export async function deleteGameEvent(gameId: string, eventIndex: number): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/games/${gameId}/events/${eventIndex}`);
}

export async function addManualEvent(gameId: string, description: string): Promise<AxiosResponse<unknown | Error>> {
  return await http.post(`/games/${gameId}/events`, { description });
}

