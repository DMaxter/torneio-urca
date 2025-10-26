export type APIResponse<T> = {
  success: boolean,
  content: T,
  status?: number,
};

export type Error = {
  error: string,
  message: string,
};
