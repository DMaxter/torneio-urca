import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateGame, Game } from "@router/backend/services/game/types";

export async function getGames(): Promise<AxiosResponse<Game[] | Error>> {
  return await http.get("/games");
}

export async function createGame(game: CreateGame): Promise<AxiosResponse<Game | Error>> {
  return await http.post("/games", game);
}
