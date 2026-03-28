import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateTeam, Team } from "@router/backend/services/team/types";
import type { Player } from "@router/backend/services/player/types";

export async function getTeams(): Promise<AxiosResponse<Team[] | Error>> {
  return await http.get("/teams");
}

export async function getTeam(teamId: string): Promise<AxiosResponse<Team | Error>> {
  return await http.get(`/teams/${teamId}`);
}

export async function getTeamPlayers(teamId: string): Promise<AxiosResponse<Player[] | Error>> {
  return await http.get(`/teams/${teamId}/players`);
}

export async function createTeam(team: CreateTeam): Promise<AxiosResponse<Team | Error>> {
  return await http.post("/teams", team);
}

export async function deleteTeam(teamId: string): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/teams/${teamId}`);
}

export async function updateTeam(teamId: string, team: CreateTeam): Promise<AxiosResponse<Team | Error>> {
  return await http.put(`/teams/${teamId}`, team);
}
