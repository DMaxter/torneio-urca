import { ref } from "vue";

export const TOURNAMENT_COLORS = [
  { value: "none",    label: "Nenhuma",  dot: "bg-transparent border border-stone-300", slot: "", chip: "border-stone-200" },
  { value: "rose",    label: "Rosa",     dot: "bg-pink-300",    slot: "border-l-2 border-l-pink-300",    chip: "border-pink-300" },
  { value: "blue",    label: "Azul",     dot: "bg-blue-400",    slot: "border-l-2 border-l-blue-400",    chip: "border-blue-400" },
  { value: "orange",  label: "Laranja",  dot: "bg-orange-400",  slot: "border-l-2 border-l-orange-400",  chip: "border-orange-400" },
  { value: "emerald", label: "Verde",    dot: "bg-emerald-400", slot: "border-l-2 border-l-emerald-400", chip: "border-emerald-400" },
  { value: "violet",  label: "Violeta",  dot: "bg-violet-400",  slot: "border-l-2 border-l-violet-400",  chip: "border-violet-400" },
  { value: "amber",   label: "Âmbar",    dot: "bg-amber-400",   slot: "border-l-2 border-l-amber-400",   chip: "border-amber-400" },
] as const;

export type TournamentColorValue = typeof TOURNAMENT_COLORS[number]["value"];

const STORAGE_KEY = "tournament_colors";

function load(): Record<string, TournamentColorValue> {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}");
  } catch {
    return {};
  }
}

const colors = ref<Record<string, TournamentColorValue>>(load());

export function useTournamentColors() {
  function getColor(tournamentId: string): typeof TOURNAMENT_COLORS[number] {
    const value = colors.value[tournamentId];
    return TOURNAMENT_COLORS.find(c => c.value === value) ?? TOURNAMENT_COLORS[0];
  }

  function setColor(tournamentId: string, value: TournamentColorValue) {
    colors.value = { ...colors.value, [tournamentId]: value };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(colors.value));
  }

  return { colors, getColor, setColor, TOURNAMENT_COLORS };
}
