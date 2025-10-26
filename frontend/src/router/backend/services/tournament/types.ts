export type Tournament = {
    id: string,
    name: string,
    teams: string[],
    games: string[],
    groups: string[],
    goals: string[],
    cards: string[],
};

export type CreateTournament = {
  name: string,
};
