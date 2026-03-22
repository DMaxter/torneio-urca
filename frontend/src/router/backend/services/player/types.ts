export class CreatePlayer {
  name: string = "";
  birth_date: Date | null = null;
  address: string = "";
  place_of_birth: string = "";
  fiscal_number: string = "";
  is_federated: boolean = false;
  federation_team: string = "";
  federation_exams_up_to_date: boolean = false;
};

export class CreateAdminPlayer {
  name: string = "";
  birth_date: Date | null = null;
  team: string = "";
  tournament: string = "";
  is_federated: boolean = false;
  federation_team: string = "";
};

export class Player {
  id: string = "";
  name: string = "";
  birth_date: Date | null = null;
  address: string | null = null;
  place_of_birth: string | null = null;
  fiscal_number: string = "";
  citizen_card_file_id: string | null = null;
  proof_of_residency_file_id: string | null = null;
  authorization_file_id: string | null = null;
  is_federated: boolean = false;
  federation_team: string | null = null;
  federation_exams_up_to_date: boolean = false;
  is_confirmed: boolean = false;
};
