export enum CardType {
    Yellow,
    Red,
}

export enum GameStatus {
  NotStarted,
  InProgress,
  Finished,
  Canceled,
}

export type GameCall = {
  id: string,
  game: string,
  team: string,
  players: string[],
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
  team_name: string,
  period: number,
  minute: number,
  card: CardType,
  timestamp: Date,
}

export type Goal = {
  player_id: string,
  player_name: string,
  team_name: string,
  period: number,
  minute: number,
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
