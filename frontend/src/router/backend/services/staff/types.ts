export type StaffType = "Coach" | "AssistantCoach" | "Physiotherapist" | "GameDeputy";

export type Staff = {
  id: string;
  name: string;
  birth_date: string;
  address: string | null;
  place_of_birth: string | null;
  fiscal_number: string;
  staff_type: StaffType;
  citizen_card_file_id?: string;
  proof_of_residency_file_id?: string;
  authorization_file_id?: string;
  team_name?: string;
};
