import type { AxiosResponse } from "axios";

import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { CreateTeam, Team } from "@router/backend/services/team/types";
import type { Player } from "@router/backend/services/player/types";
import type { Staff } from "@router/backend/services/staff/types";

export async function getTeams(): Promise<AxiosResponse<Team[] | Error>> {
  return await http.get("/teams");
}

export async function getTeam(teamId: string): Promise<AxiosResponse<Team | Error>> {
  return await http.get(`/teams/${teamId}`);
}

export async function getTeamPlayers(teamId: string): Promise<AxiosResponse<Player[] | Error>> {
  return await http.get(`/teams/${teamId}/players`);
}

export async function createTeam(team: CreateTeam): Promise<AxiosResponse<Team | Error>> {
  return await http.post("/teams", team);
}

export async function deleteTeam(teamId: string): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/teams/${teamId}`);
}

export async function updateTeam(teamId: string, team: CreateTeam): Promise<AxiosResponse<Team | Error>> {
  return await http.put(`/teams/${teamId}`, team);
}

export interface RegisterTeamStartData {
  tournament: string;
  name: string;
  responsible_name: string;
  responsible_email: string;
  responsible_phone: string;
}

export interface RegisterStaffData {
  team_id: string;
  staff_type: "Coach" | "Physiotherapist" | "GameDeputy";
  name: string;
  birth_date: string;
  address?: string;
  place_of_birth?: string;
  fiscal_number: string;
  files?: {
    citizenCard?: File;
    proofOfResidency?: File;
  };
}

export interface RegisterPlayerData {
  team_id: string;
  name: string;
  birth_date: string;
  address?: string;
  place_of_birth?: string;
  fiscal_number: string;
  is_federated: boolean;
  federation_team?: string;
  federation_exams_up_to_date: boolean;
  files?: {
    citizenCard?: File;
    proofOfResidency?: File;
    authorization?: File;
  };
}

export async function registerTeamStart(data: RegisterTeamStartData): Promise<AxiosResponse<Team | Error>> {
  return await http.post("/teams/register/start", data);
}

export async function registerAddStaff(data: RegisterStaffData): Promise<AxiosResponse<Staff | Error>> {
  const formData = new FormData();
  formData.append("team_id", data.team_id);
  formData.append("staff_type", data.staff_type);
  formData.append("name", data.name);
  formData.append("birth_date", data.birth_date);
  formData.append("address", data.address || "");
  formData.append("place_of_birth", data.place_of_birth || "");
  formData.append("fiscal_number", data.fiscal_number);
  
  if (data.files?.citizenCard) {
    formData.append("citizen_card", data.files.citizenCard);
  }
  if (data.files?.proofOfResidency) {
    formData.append("proof_of_residency", data.files.proofOfResidency);
  }
  
  return await http.post("/teams/register/staff", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
}

export async function registerAddPlayer(data: RegisterPlayerData): Promise<AxiosResponse<Player | Error>> {
  const formData = new FormData();
  formData.append("team_id", data.team_id);
  formData.append("name", data.name);
  formData.append("birth_date", data.birth_date);
  formData.append("address", data.address || "");
  formData.append("place_of_birth", data.place_of_birth || "");
  formData.append("fiscal_number", data.fiscal_number);
  formData.append("is_federated", String(data.is_federated));
  formData.append("federation_team", data.federation_team || "");
  formData.append("federation_exams_up_to_date", String(data.federation_exams_up_to_date));
  
  if (data.files?.citizenCard) {
    formData.append("citizen_card", data.files.citizenCard);
  }
  if (data.files?.proofOfResidency) {
    formData.append("proof_of_residency", data.files.proofOfResidency);
  }
  if (data.files?.authorization) {
    formData.append("authorization", data.files.authorization);
  }
  
  return await http.post("/teams/register/player", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
}

export async function registerComplete(teamId: string): Promise<AxiosResponse<Team | Error>> {
  return await http.post("/teams/register/complete", { team_id: teamId });
}

export async function cancelRegistration(teamId: string): Promise<AxiosResponse<void | Error>> {
  return await http.delete(`/teams/register/${teamId}`);
}
