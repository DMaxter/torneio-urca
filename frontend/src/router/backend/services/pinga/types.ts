export type TeamCount = {
  team_name: string;
  count: number;
};

export type DailyVoteHistory = {
  date: string;
  teams: TeamCount[];
};

export type ApiKeyResponse = {
  api_key: string;
};