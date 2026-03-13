export class CreateTeam {
  tournament: string = "";
  name: string = "";
  responsible_name: string = "";
  responsible_email: string = "";
  responsible_phone: string = "";
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
  responsible_name: string,
  responsible_email: string,
  responsible_phone: string,
  main_coach: string,
  assistant_coach: string | null,
  players: string[],
  physiotherapist: string,
  first_deputy: string,
  second_deputy: string | null,
};
