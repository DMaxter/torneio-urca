export const TOURNAMENT = {
  MIN_PLAYERS: 5,
  MAX_PLAYERS: 14,
  MIN_AGE: 16,
} as const;

export const FILE_PREFIXES = {
  staff: ["main_coach", "physiotherapist", "first_deputy", "second_deputy"],
  player: "player",
} as const;
