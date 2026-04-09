import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";

export async function assignCard(data: {
  tournament: string;
  game: string;
  team: string;
  player_number?: number;
  staff_id?: string;
  card: "Yellow" | "Red";
  minute: number;
}): Promise<AxiosResponse<unknown | Error>> {
  return await http.post("/cards", data);
}
