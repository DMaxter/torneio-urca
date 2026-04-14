export function getEnumKeyByValue(enumObj: object, value: string): string | undefined {
  const entries = Object.entries(enumObj).filter(([, val]) => val === value);
  if (entries.length > 0) {
    return entries[0][0];
  } else {
    console.error(`Value "${value}" not found in ${enumObj}`);
  }
}

export function calculateAge(birthDate: Date | null, referenceDate?: Date): number {
  if (!birthDate) return 0;
  const refDate = referenceDate || new Date();
  const birth = new Date(birthDate);
  let age = refDate.getFullYear() - birth.getFullYear();
  const monthDiff = refDate.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && refDate.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

export function isUnderAge(birthDate: Date | null, minAge: number, referenceDate?: Date): boolean {
  return calculateAge(birthDate, referenceDate) < minAge;
}

export function getStaffTypeLabel(type: string | undefined): string {
  const labels: Record<string, string> = {
    'Coach': 'Treinador Principal',
    'AssistantCoach': 'Treinador Adjunto',
    'Physiotherapist': 'Fisioterapeuta',
    'GameDeputy': 'Delegado',
  };
  return type ? (labels[type] || type) : '';
}
