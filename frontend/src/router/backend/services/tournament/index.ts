import { http } from "@router/backend/api";
import type { APIResponse, Error } from "@router/backend/types";
import type { CreateTournament, Tournament } from "@router/backend/services/tournament/types";

export async function getTournaments() {
  return await http.get<APIResponse<Tournament[] | Error>>("/tournaments");
}

export async function createTournament(tournament: CreateTournament): Promise<APIResponse<Tournament | Error>> {
  return await http.post("/tournaments", tournament);
}
