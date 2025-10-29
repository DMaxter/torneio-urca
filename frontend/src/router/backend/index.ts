import * as gameController from "@router/backend/services/game";
import * as groupController from "@router/backend/services/group";
import * as teamController from "@router/backend/services/team";
import * as tournamentController from "@router/backend/services/tournament";
import * as userController from "@router/backend/services/user";

export const API = {
  games: gameController,
  groups: groupController,
  teams: teamController,
  tournaments: tournamentController,
  users: userController,
};
