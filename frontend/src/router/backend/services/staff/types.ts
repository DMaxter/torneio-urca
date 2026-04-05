export type StaffType = "main_coach" | "assistant_coach" | "physiotherapist" | "first_deputy" | "second_deputy";

export type Staff = {
  id: string;
  name: string;
  birth_date: string;
  address: string | null;
  place_of_birth: string | null;
  fiscal_number: string;
  staff_type: StaffType;
};
