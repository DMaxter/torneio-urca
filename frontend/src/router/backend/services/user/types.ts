export class CreateUser {
  username: string = "";
  password: string = "";
};

export class ChangePassword {
  current_password: string = "";
  new_password: string = "";
};

export const USER_ROLES = {
  MANAGE_PLAYERS: "manage_players",
  MANAGE_GAMES: "manage_games",
  MANAGE_GAME_EVENTS: "manage_game_events",
  FILL_GAME_CALLS: "fill_game_calls",
  OPEN_CALENDAR: "open_calendar",
} as const;

export class User {
  id: string = "";
  username: string = "";
  roles: string[] = [];
  assigned_games: string[] = [];
  assigned_games_for_calls: string[] = [];

  constructor(obj?: User) {
    if (obj) {
      this.id = obj.id;
      this.username = obj.username;
      this.roles = obj.roles;
      this.assigned_games = obj.assigned_games;
      this.assigned_games_for_calls = obj.assigned_games_for_calls;
    }
  }
};

export class UpdateUserRoles {
  roles: string[] = [];
};

export class AssignUserGames {
  assigned_games: string[] = [];
};

export class AssignUserGamesForCalls {
  assigned_games_for_calls: string[] = [];
};
