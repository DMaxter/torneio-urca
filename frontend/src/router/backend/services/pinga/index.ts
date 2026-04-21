import type { AxiosResponse } from "axios";
import { http } from "@router/backend/api";
import type { TeamCount, DailyVoteHistory, ApiKeyResponse } from "./types";

export async function getCounts(): Promise<AxiosResponse<TeamCount[]>> {
  return await http.get("/pinga/counts");
}

export async function getHistory(): Promise<AxiosResponse<DailyVoteHistory[]>> {
  return await http.get("/pinga/history");
}

export async function getApiKey(): Promise<AxiosResponse<ApiKeyResponse>> {
  return await http.get("/pinga/api-key");
}

export async function rotateApiKey(): Promise<AxiosResponse<ApiKeyResponse>> {
  return await http.post("/pinga/api-key/rotate");
}