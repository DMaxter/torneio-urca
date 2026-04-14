import { http } from "@router/backend/api";

export interface Settings {
  calendar_locked: boolean;
}

export async function getSettings() {
  return await http.get<Settings>("/settings");
}

export async function toggleCalendarLock() {
  return await http.patch<Settings>("/settings/calendar-lock");
}
