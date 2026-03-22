import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreatePlayer, CreateAdminPlayer, Player } from "@router/backend/services/player/types";

export async function getPlayers(): Promise<AxiosResponse<Player[] | Error>> {
  return await http.get("/players");
}

export async function getPlayer(playerId: string): Promise<AxiosResponse<Player | Error>> {
  return await http.get(`/players/${playerId}`);
}

export async function createPlayer(player: CreatePlayer): Promise<AxiosResponse<Player | Error>> {
  return await http.post("/players", player);
}

export async function createAdminPlayer(player: CreateAdminPlayer): Promise<AxiosResponse<Player | Error>> {
  return await http.post("/players/admin", player);
}

export async function confirmPlayer(playerId: string): Promise<AxiosResponse<Player | Error>> {
  return await http.patch(`/players/${playerId}/confirm`);
}
