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

export async function createAdminPlayer(player: CreateAdminPlayer, citizenCard?: File, proofOfResidency?: File, authorization?: File): Promise<AxiosResponse<Player | Error>> {
  const formData = new FormData();
  formData.append("team", player.team);
  formData.append("name", player.name);
  formData.append("birth_date", player.birth_date?.toISOString() || "");
  formData.append("tournament", player.tournament);
  formData.append("is_federated", String(player.is_federated));
  if (player.federation_team) {
    formData.append("federation_team", player.federation_team);
  }
  if (citizenCard) {
    formData.append("citizen_card", citizenCard);
  }
  if (proofOfResidency) {
    formData.append("proof_of_residency", proofOfResidency);
  }
  if (authorization) {
    formData.append("authorization", authorization);
  }
  
  return await http.post("/players/admin", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
}

export async function confirmPlayer(playerId: string): Promise<AxiosResponse<Player | Error>> {
  return await http.patch(`/players/${playerId}/confirm`);
}

export async function deletePlayer(playerId: string): Promise<AxiosResponse<Player | Error>> {
  return await http.delete(`/players/${playerId}`);
}

export async function updatePlayer(playerId: string, player: CreatePlayer): Promise<AxiosResponse<Player | Error>> {
  return await http.put(`/players/${playerId}`, player);
}
