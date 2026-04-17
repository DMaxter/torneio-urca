import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { Prizes } from "@router/backend/services/prizes/types";

export async function getPrizes(tournamentId: string): Promise<AxiosResponse<Prizes | Error>> {
  return await http.get(`/prizes/${tournamentId}`);
}