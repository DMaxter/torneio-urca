import { Gender } from "@router/backend/services/user/types";

export class CreateTeam {
  tournament: string = "";
  name: string = "";
  gender: Gender | null = null;
  responsible: string = "";
  main_coach: string = "";
  assistant_coach: string | null = null;
  players: string[] = [];
  physiotherapist: string = "";
  first_deputy: string = "";
  second_deputy: string | null = null;
};

export type Team = {
  id: string,
  tournament: string,
  name: string,
  gender: Gender,
  responsible: string,
  main_coach: string,
  assistant_coach: string | null,
  players: string[],
  physiotherapist: string,
  first_deputy: string,
  second_deputy: string | null,
};
