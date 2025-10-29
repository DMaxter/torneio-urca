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
