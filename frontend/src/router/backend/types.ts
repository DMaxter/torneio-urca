export type APIResponse<T, E = unknown> = {
  success: boolean,
  content: T,
  status?: number,
  entity?: E,
};

export type Error = {
  error: string,
  message: string,
};
