import type { AxiosResponse } from "axios";
import { http } from "@router/backend/api";
import type { Error } from "@router/backend/types";
import type { Staff } from "@router/backend/services/staff/types";

export async function getStaff(): Promise<AxiosResponse<Staff[] | Error>> {
  return await http.get("/staff");
}

export interface CreateAdminStaff {
  name: string;
  birth_date: string;
  staff_type: "Coach" | "AssistantCoach" | "Physiotherapist" | "GameDeputy";
  fiscal_number: string;
  team_id: string;
  tournament_id: string;
  address?: string;
  place_of_birth?: string;
}

export async function createAdminStaff(
  staff: CreateAdminStaff,
  citizenCard?: File
): Promise<AxiosResponse<Staff | Error>> {
  const formData = new FormData();
  formData.append("name", staff.name);
  formData.append("birth_date", staff.birth_date);
  formData.append("staff_type", staff.staff_type);
  formData.append("fiscal_number", staff.fiscal_number);
  formData.append("team_id", staff.team_id);
  formData.append("tournament_id", staff.tournament_id);
  formData.append("address", staff.address || "");
  formData.append("place_of_birth", staff.place_of_birth || "");
  
  if (citizenCard) {
    formData.append("citizen_card", citizenCard);
  }
  
  return await http.post("/staff/admin", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
}

export interface UpdateAdminStaff {
  name: string;
  birth_date: string;
  staff_type: "Coach" | "AssistantCoach" | "Physiotherapist" | "GameDeputy";
  fiscal_number: string;
  team_id?: string;
  address?: string;
  place_of_birth?: string;
}

export async function updateAdminStaff(
  staffId: string,
  staff: UpdateAdminStaff,
  citizenCard?: File
): Promise<AxiosResponse<Staff | Error>> {
  const formData = new FormData();
  formData.append("name", staff.name);
  formData.append("birth_date", staff.birth_date);
  formData.append("staff_type", staff.staff_type);
  formData.append("fiscal_number", staff.fiscal_number);
  if (staff.team_id) {
    formData.append("team_id", staff.team_id);
  }
  formData.append("address", staff.address || "");
  formData.append("place_of_birth", staff.place_of_birth || "");
  
  if (citizenCard) {
    formData.append("citizen_card", citizenCard);
  }
  
  return await http.put(`/staff/${staffId}`, formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
}
