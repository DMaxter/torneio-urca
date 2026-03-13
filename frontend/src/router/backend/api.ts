import axios from "axios";

export const http = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL
});

let toast: any = null;

export function setToast(toastInstance: any) {
  toast = toastInstance;
}

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || "Erro ao comunicar com o servidor";
    if (toast) {
      toast.add({ severity: "error", summary: "Erro", detail: message, life: 3000 });
    }
    return Promise.reject(error);
  }
);
