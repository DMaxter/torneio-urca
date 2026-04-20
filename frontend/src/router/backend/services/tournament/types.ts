export enum TournamentPhase {
    GROUP = 'group',
    KNOCKOUT = 'knockout',
}

export type Tournament = {
    id: string,
    name: string,
    teams: string[],
    games: string[],
    groups: string[],
    goals: string[],
    cards: string[],
    phase: TournamentPhase,
};

export type CreateTournament = {
  name: string,
};
