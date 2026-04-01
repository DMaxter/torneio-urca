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

export type Game = {
  id: string,
  tournament: string,
  scheduled_date: Date | null,
  start_date: Date | null,
  finish_date: Date | null,
  status: GameStatus,
  home_call: GameCall,
  away_call: GameCall,
  events: GameEvent[],
}

export class CreateGameCall {
  team: string = "";
}

export class CreateGame {
  tournament: string = "";
  scheduled_date: Date | null = null;
  home_call: CreateGameCall = new CreateGameCall();
  away_call: CreateGameCall = new CreateGameCall();
}
