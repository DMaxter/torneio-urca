export type GameDay = {
  id: string;
  tournament: string;
  date: string;       // "YYYY-MM-DD"
  num_games: number;
  start_time: string; // "HH:MM"
}

export class CreateGameDay {
  tournament: string = "";
  date: string = "";
  num_games: number = 2;
  start_time: string = "09:00";
}
