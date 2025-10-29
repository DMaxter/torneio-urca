export enum Gender {
    Male = "Masculino",
    Female = "Feminino",
};

export const GENDERS = Object.entries(Gender).map(([key, value]) => ({"name": value, "value": key}));

export class CreateUser {
  name: string = "";
  gender: Gender | null = null;
  birth_date: Date | null = null;
  address: string = "";
  place_of_birth: string | null = null;
  fiscal_number: string = "";
  roles: Role[] = [];
};

export enum Role {
  Admin = "Administrador",
  Player = "Jogador",
  Coach = "Treinador",
  Physiotherapist = "Fisioterapeuta",
  GameDeputy = "Delegado de Jogo",
  Timekeeper = "Cronometrista",
  Organizer = "Organizador",
};

export const ROLES = Object.entries(Role).map(([key, value]) => ({"name": value, "value": key}));

export class User {
  id: string = "";
  name: string = "";
  gender: Gender = Gender.Male;
  birth_date: Date | null = null;
  address: string | null = null;
  place_of_birth: string | null = null;
  fiscal_number: string = "";
  confirmed: boolean = false;
  roles: Role[] = [];

  constructor(obj?: User) {
    if (obj) {
      this.id = obj.id;
      this.name = obj.name;
      this.gender = obj.gender as Gender;
      this.birth_date = obj.birth_date!;
      this.address = obj.address;
      this.place_of_birth = obj.place_of_birth;
      this.fiscal_number = obj.fiscal_number;
      this.confirmed = obj.confirmed;
      this.roles = obj.roles.map((r) => (r as Role));
    }
  }
};

import { getEnumKeyByValue } from "@/utils";

export function getRole(value: string): Role | undefined {
  return getEnumKeyByValue(Role, value) as Role;
}

export function getGender(value: string): Gender | undefined {
  return getEnumKeyByValue(Gender, value) as Gender;
}

