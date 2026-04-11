import { useToast } from "primevue/usetoast";

/**
 * Provides centralized error handling for Axios/API requests mapping error
 * codes and details to cleanly formatted UI Toasts.
 */
export function useApiErrorToast() {
  const toast = useToast();

  /**
   * Evaluates the standard backend HTTP error payload, formatting and broadcasting 
   * the message out using a PrimeVue Toast.
   * 
   * @param e - The unknown raw Axios exception caught from asynchronous requests.
   * @param fallbackMessage - Text to fallback to if the API object has no details.
   */
  function handleApiError(e: unknown, fallbackMessage = "Ocorreu um erro na plataforma") {
    const err = e as { response?: { data?: { detail?: { error?: string } } } };
    const msg = err.response?.data?.detail?.error || fallbackMessage;
    
    toast.add({ 
      severity: "error", 
      summary: "Erro", 
      detail: msg, 
      life: 3000 
    });
  }

  return { handleApiError };
}
