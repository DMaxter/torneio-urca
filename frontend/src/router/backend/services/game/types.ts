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
};

export type AssignCardDto = {
  tournament: string;
  game: string;
  team: string;
  player_number?: number | null;
  card: CardType;
  minute: number;
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
  deputy: string | null,
}

export type GameEvent =
  StartTime |
  EndTime |
  Foul |
  Goal |
  Break |
  Resume

export type StartTime = {
  period: number,
  timestamp: Date,
}

export type EndTime = {
  period: number,
  timestamp: Date,
}

export type Foul = {
  player_id: string,
  player_name: string,
  player_number?: number,
  team_name: string,
  period: number,
  minute: number,
  card: CardType,
  staff_id?: string | null,
  staff_name?: string,
  staff_type?: string,
  timestamp: Date,
}

export type Goal = {
  player_id: string,
  player_name: string,
  team_name: string,
  period: number,
  minute: number,
  own_goal: boolean,
  timestamp: Date,
}

export type Break = {
  team_id: string,
  team_name: string,
  timestamp: Date,
}

export type Resume = {
  timestamp: Date,
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
  home_call: GameCall | null,
  away_call: GameCall | null,
  events: GameEvent[],
}

export class CreateGameCall {
  team: string = "";
}

export class CreateGame {
  tournament: string = "";
  scheduled_date: Date | null = null;
  home_call: CreateGameCall | null = new CreateGameCall();
  away_call: CreateGameCall | null = new CreateGameCall();
  phase: GamePhase = "group";
  home_placeholder: string | null = null;
  away_placeholder: string | null = null;
}
