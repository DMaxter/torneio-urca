export type BestScorerResult = {
  position: number;
  player_id: string | null;
  player_name: string;
  team_name: string;
  goals: number;
  games: number;
};

export type BestDefenseResult = {
  position: number;
  team_id: string;
  team_name: string;
  goals_suffered: number;
  games: number;
};

export type FairPlayResult = {
  position: number;
  team_id: string;
  team_name: string;
  cards: number;
  games: number;
};

export type Prizes = {
  best_scorer: BestScorerResult[];
  best_defense: BestDefenseResult[];
  fair_play: FairPlayResult[];
};