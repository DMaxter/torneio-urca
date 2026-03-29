export class CreateGroup {
  tournament: string = "";
  name: string = "";
  teams: string[] = [];
}

export type Group = {
  id: string,
  tournament: string,
  name: string,
  teams: string[],
}

export type TeamStanding = {
  team_id: string,
  team_name: string,
  points: number,
  games: number,
  wins: number,
  ties: number,
  losses: number,
  goals_scored: number,
  goals_suffered: number,
  goal_difference: number,
}

export type Classification = {
  group_id: string,
  group_name: string,
  standings: TeamStanding[],
}
