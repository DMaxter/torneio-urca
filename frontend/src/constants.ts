export const TOURNAMENT = {
  MIN_PLAYERS: 5,
  MAX_PLAYERS: 14,
  MIN_AGE: 16,
  TOURNAMENT_START_DATE: new Date("2026-05-28"),
  AGE_FOR_ENROLLMENT: 16,
  AGE_REQUIRES_AUTHORIZATION: 18,
} as const;

export const FILE_PREFIXES = {
  staff: ["main_coach", "physiotherapist", "first_deputy", "second_deputy"],
  player: "player",
} as const;

export const URCA_EMAIL = "urca.1975@gmail.com";
