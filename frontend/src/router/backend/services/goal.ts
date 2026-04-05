import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";

export async function assignGoal(data: {
  tournament: string;
  game: string;
  team: string;
  player_number?: number;
  staff_id?: string;
  minute: number;
}): Promise<AxiosResponse<any | Error>> {
  return await http.post("/goals", data);
}
