import { http } from "@router/backend/api";
import type { Announcement, CreateAnnouncement, UpdateAnnouncement } from "./types";

export async function getAnnouncements() {
  return await http.get("/announcements");
}

export async function createAnnouncement(
  announcement: CreateAnnouncement
) {
  try {
    const response = await http.post("/announcements", announcement);
    return { success: true, data: response.data as Announcement };
  } catch (error: unknown) {
    const axiosError = error as { response?: { status?: number } };
    return { success: false, content: `Erro ${axiosError.response?.status || 500}` };
  }
}

export async function updateAnnouncement(
  announcementId: string,
  announcement: UpdateAnnouncement
) {
  try {
    await http.put(`/announcements/${announcementId}`, announcement);
    return { success: true };
  } catch {
    return { success: false };
  }
}

export async function deleteAnnouncement(
  announcementId: string
) {
  try {
    await http.delete(`/announcements/${announcementId}`);
    return { success: true };
  } catch {
    return { success: false };
  }
}