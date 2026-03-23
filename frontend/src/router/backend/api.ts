import axios from "axios";

const TOKEN_KEY = "auth_token";

export const http = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL
});

let toast: any = null;

export function setToast(toastInstance: any) {
  toast = toastInstance;
}

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
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
    
    if (toast) {
      toast.add({ severity: "error", summary: "Erro", detail: message, life: 5000 });
    }
    return Promise.reject(error);
  }
);
