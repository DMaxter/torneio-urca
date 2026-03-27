import { http } from "@router/backend/api";

export function getFileUrl(fileId: string): string {
  return `/api/files/${fileId}`;
}

export async function downloadFile(fileId: string): Promise<Blob | null> {
  try {
    const response = await http.get(`/files/${fileId}`, {
      responseType: "blob",
    });
    return response.data;
  } catch {
    return null;
  }
}
