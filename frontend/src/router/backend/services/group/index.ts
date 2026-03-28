import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateGroup, Group } from "@router/backend/services/group/types";

export async function getGroups(): Promise<AxiosResponse<Group[] | Error>> {
  return await http.get("/groups");
}

export async function createGroup(group: CreateGroup): Promise<AxiosResponse<Group | Error>> {
  return await http.post("/groups", group);
}

export async function updateGroup(groupId: string, group: CreateGroup): Promise<AxiosResponse<Group | Error>> {
  return await http.put(`/groups/${groupId}`, group);
}

export async function deleteGroup(groupId: string): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/groups/${groupId}`);
}
