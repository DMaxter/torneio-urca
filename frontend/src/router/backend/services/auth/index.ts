import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { LoginCredentials, Token, CurrentUser } from "@router/backend/services/auth/types";

export async function login(credentials: LoginCredentials): Promise<AxiosResponse<Token | Error>> {
  return await http.post("/auth/login", credentials);
}

export async function logout(): Promise<AxiosResponse<void | Error>> {
  return await http.post("/auth/logout");
}

export async function getCurrentUser(): Promise<AxiosResponse<CurrentUser | null>> {
  return await http.get("/auth/me");
}
