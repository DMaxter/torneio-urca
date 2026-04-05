export type Goal = {
  id: string;
  tournament: string;
  team_id: string;
  team_name: string;
  player_id: string | null;
  player_name: string;
  player_number: number | null;
  staff_id: string | null;
  staff_name: string;
  staff_type: string | null;
  game_id: string;
  period: number;
  minute: number;
  timestamp: Date;
};

export type Card = {
  id: string;
  tournament: string;
  team_id: string;
  team_name: string;
  card: "Yellow" | "Red";
  game_id: string;
  player_id: string | null;
  player_name: string;
  player_number: number | null;
  staff_id: string | null;
  staff_name: string;
  staff_type: string | null;
  period: number;
  minute: number;
  timestamp: Date;
};
