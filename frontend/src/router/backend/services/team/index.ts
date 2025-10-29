import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateTeam, Team } from "@router/backend/services/team/types";

export async function getTeams(): Promise<AxiosResponse<Team[] | Error>> {
  return await http.get("/teams");
}

export async function createTeam(team: CreateTeam): Promise<AxiosResponse<Team | Error>> {
  return await http.post("/teams", team);
}
