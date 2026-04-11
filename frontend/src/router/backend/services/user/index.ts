import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateUser, User, ChangePassword, UpdateUserRoles, AssignUserGames, AssignUserGamesForCalls } from "@router/backend/services/user/types";

export async function getUsers(): Promise<AxiosResponse<User[] | Error>> {
  return await http.get("/users");
}

export async function createUser(user: CreateUser): Promise<AxiosResponse<User | Error>> {
  return await http.post("/users", user);
}

export async function changePassword(
  userId: string,
  passwordData: ChangePassword
): Promise<AxiosResponse<User | Error>> {
  return await http.patch(`/users/${userId}/password`, passwordData);
}

export async function deleteUser(userId: string): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/users/${userId}`);
}

export async function updateUserRoles(userId: string, roles: UpdateUserRoles): Promise<AxiosResponse<User | Error>> {
  return await http.patch(`/users/${userId}/roles`, roles);
}

export async function assignUserGames(userId: string, games: AssignUserGames): Promise<AxiosResponse<User | Error>> {
  return await http.patch(`/users/${userId}/games`, games);
}

export async function assignUserGamesForCalls(userId: string, games: AssignUserGamesForCalls): Promise<AxiosResponse<User | Error>> {
  return await http.patch(`/users/${userId}/games/calls`, games);
}
