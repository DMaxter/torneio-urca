import axios from "axios";

export const http = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
  withCredentials: true,
});

let toast: any = null;
let lastErrorMessage = "";
let lastErrorTime = 0;

export function setToast(toastInstance: any) {
  toast = toastInstance;
}

http.interceptors.response.use(
  (response) => response,
  (error) => {
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

    if (toast && (message !== lastErrorMessage || now - lastErrorTime > 500)) {
      lastErrorMessage = message;
      lastErrorTime = now;
      toast.add({ severity: "error", summary: "Erro", detail: message, life: 5000 });
    }
    return Promise.reject(error);
  }
);
