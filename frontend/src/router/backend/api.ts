import axios from "axios";
import type { ToastServiceMethods } from "primevue/toastservice";

export const http = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
  withCredentials: true,
});

let toast: ToastServiceMethods | null = null;
let lastErrorMessage = "";
let lastErrorTime = 0;

export function setToast(toastInstance: ToastServiceMethods) {
  toast = toastInstance;
}

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error.config?.url || "";
    const status = error.response?.status;
    const now = Date.now();
    let message = "Erro ao comunicar com o servidor";
    
    const responseData = error.response?.data;
    if (responseData) {
      const data = typeof responseData === "string" ? JSON.parse(responseData) : responseData;
      if (data?.error) {
        message = data.error;
      } else if (data?.message) {
        message = data.message;
      }
    }

    const isAuthEndpoint = url.includes("/auth/me");
    if (isAuthEndpoint && status === 200 && !responseData) {
      return Promise.resolve({ data: null });
    }

    if (toast && (message !== lastErrorMessage || now - lastErrorTime > 500)) {
      lastErrorMessage = message;
      lastErrorTime = now;
      toast.add({ severity: "error", summary: "Erro", detail: message, life: 5000 });
    }
    return Promise.reject(error);
  }
);
