export function getEnumKeyByValue(enumObj: object, value: string): string | undefined {
  const entries = Object.entries(enumObj).filter(([, val]) => val === value);
  if (entries.length > 0) {
    return entries[0][0];
  } else {
    console.error(`Value "${value}" not found in ${enumObj}`);
  }
}

export function calculateAge(birthDate: Date | null): number {
  if (!birthDate) return 0;
  const today = new Date();
  const birth = new Date(birthDate);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

export function isUnderAge(birthDate: Date | null, minAge: number): boolean {
  return calculateAge(birthDate) < minAge;
}
