import type { AxiosResponse } from "axios";
import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { Staff } from "@router/backend/services/staff/types";

export async function getStaff(): Promise<AxiosResponse<Staff[] | Error>> {
  return await http.get("/staff");
}
