import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { LoginCredentials, Token } from "@router/backend/services/auth/types";

export async function login(credentials: LoginCredentials): Promise<AxiosResponse<Token | Error>> {
  return await http.post("/auth/login", credentials);
}
