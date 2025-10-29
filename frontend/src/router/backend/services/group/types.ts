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
