import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateUser, User } from "@router/backend/services/user/types";

export async function getUsers(): Promise<AxiosResponse<User[] | Error>> {
  return await http.get("/users");
}

export async function createUser(user: CreateUser): Promise<AxiosResponse<User | Error>> {
  return await http.post("/users", user);
}
