import type { AxiosResponse } from "axios";
import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateGameDay, GameDay } from "./types";

export async function getGameDays(): Promise<AxiosResponse<GameDay[] | Error>> {
  return await http.get("/game-days");
}

export async function createGameDay(day: CreateGameDay): Promise<AxiosResponse<GameDay | Error>> {
  return await http.post("/game-days", day);
}

export async function deleteGameDay(id: string): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/game-days/${id}`);
}
