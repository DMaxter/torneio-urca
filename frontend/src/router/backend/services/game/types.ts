export enum CardTypeEnum {
    Yellow = "Yellow",
    Red = "Red",
}

export type CardType = "Yellow" | "Red";

export type AssignGoalDto = {
  tournament: string;
  game: string;
  team: string;
  player_number?: number | null;
  own_goal: boolean;
  minute: number;
  second?: number;
};

export type AssignCardDto = {
  tournament: string;
  game: string;
  team: string;
  player_number?: number | null;
  staff_id?: string | null;
  card: CardType;
  minute: number;
  second?: number;
  is_direct_free_kick: boolean;
};

export type AssignFoulDto = {
  tournament: string;
  game: string;
  team: string;
  player_number?: number | null;
  minute: number;
  second?: number;
  is_direct_free_kick: boolean;
};

export type AssignPenaltyDto = {
  tournament: string;
  game: string;
  team: string;
  player_number: number;
  scored: boolean;
  minute: number;
  second?: number;
};

export type UpdatePeriodDto = {
  action: string;
  period?: number;
  seconds?: number;
};

export enum GameStatus {
  Scheduled = "Scheduled",
  CallsPending = "CallsPending",
  ReadyToStart = "ReadyToStart",
  InProgress = "InProgress",
  Finished = "Finished",
  Canceled = "Canceled",
}

export type GameCall = {
  id: string,
  game: string,
  team: string,
  players: { player: string; number: number | null }[],
  staff: string[],
  deputy: string | null,
}

export type GameEvent =
  { Goal: GoalEvent } |
  { Foul: FoulEvent } |
  { PeriodStart: PeriodEvent } |
  { PeriodEnd: PeriodEvent } |
  { PeriodPause: PeriodEvent } |
  { PeriodResume: PeriodEvent } |
  { Penalty: PenaltyEvent } |
  { GameEnd: GameEndEvent } |
  { PenaltyShootoutStart: PeriodEvent }

export type GameEndEvent = {
  home_score: number,
  away_score: number,
  home_penalty_score: number,
  away_penalty_score: number,
  winner_id: string | null,
  timestamp: string,
}

export type GoalEvent = {
  player_id: string,
  player_name: string,
  team_name: string,
  period: number,
  minute: number,
  second?: number,
  own_goal: boolean,
  timestamp: string,
  own_goal_committed_by?: string,
}

export type FoulEvent = {
  player_id: string,
  player_name: string,
  player_number?: number,
  team_name: string,
  period: number,
  minute: number,
  second?: number,
  card: CardType | null,
  staff_id?: string | null,
  staff_name?: string,
  staff_type?: string,
  is_direct_free_kick?: boolean,
  timestamp: string,
}

export type PeriodEvent = {
  period: number,
  timestamp: string,
}

export type PenaltyEvent = {
  player_id: string,
  player_name: string,
  player_number: number,
  team_id: string,
  team_name: string,
  scored: boolean,
  period: number,
  minute: number,
  second: number,
  timestamp: string,
}

export type GamePhase = "group" | "quarter_final" | "semi_final" | "final" | "third_place";

export type Game = {
  id: string,
  tournament: string,
  scheduled_date: Date | null,
  start_date: Date | null,
  finish_date: Date | null,
  status: GameStatus,
  phase: GamePhase,
  home_placeholder: string | null,
  away_placeholder: string | null,
  group: string | null,
  home_call: GameCall | null,
  away_call: GameCall | null,
  events: GameEvent[],
  current_period: number,
  period_elapsed_seconds: number,
  timer_active: boolean,
  timer_started_at: string | null,
}

export class CreateGameCall {
  team: string = "";
}

export class CreateGame {
  tournament: string = "";
  label: string | null = null;
  scheduled_date: Date | null = null;
  home_call: CreateGameCall | null = new CreateGameCall();
  away_call: CreateGameCall | null = new CreateGameCall();
  phase: GamePhase = "group";
  home_placeholder: string | null = null;
  away_placeholder: string | null = null;
  home_group_ref: string | null = null;
  home_group_position: number | null = null;
  away_group_ref: string | null = null;
  away_group_position: number | null = null;
  next_game_winner: string | null = null;
  next_game_loser: string | null = null;
  group: string | null = null;
}
