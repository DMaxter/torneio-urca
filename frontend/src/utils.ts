export function getEnumKeyByValue(enumObj: object, value: string): string | undefined {
  const entries = Object.entries(enumObj).filter(([_, val]) => val === value);
  if (entries.length > 0) {
    return entries[0][0];
  } else {
    console.error(`Value "${value}" not found in ${enumObj}`);
  }
}
