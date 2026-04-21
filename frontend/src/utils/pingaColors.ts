import { ref } from 'vue';

const COLOR_SHADES = [
  'emerald', 'green', 'lime',
  'red', 'rose', 'pink',
  'blue', 'indigo', 'cyan', 'sky',
  'violet', 'purple', 'fuchsia',
  'yellow', 'amber'
];

const SHADES = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900', '950'];

const THEME_COMBINATIONS: { color: string; shade: string }[] = [];
for (const color of COLOR_SHADES) {
  for (const shade of SHADES) {
    THEME_COMBINATIONS.push({ color, shade });
  }
}

function seededRandom(seed: number): () => number {
  return function() {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  };
}

function shuffleArray<T>(array: T[], randomFn: () => number): T[] {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(randomFn() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

const SHUFFLED_COMBINATIONS = shuffleArray(THEME_COMBINATIONS, seededRandom(11));

const FNV_PRIME = 2166136261;
const FNV_OFFSET = 16777619;

function fnv1a(str: string): number {
  let hash = FNV_PRIME;
  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
    hash *= FNV_OFFSET;
    hash = hash >>> 0;
  }
  return hash >>> 0;
}

export function usePingaColors() {
  const colorCache = ref<Map<string, string>>(new Map());

  function loadColor(color: string, shade: string): string {
    const key = `${color}-${shade}`;
    if (colorCache.value.has(key)) {
      return colorCache.value.get(key)!;
    }
    const computedStyle = getComputedStyle(document.documentElement);
    const value = computedStyle.getPropertyValue(`--p-${color}-${shade}`).trim();
    const result = value || '#6b7280';
    colorCache.value.set(key, result);
    return result;
  }

  function getColorForTeam(teamName: string): string {
    const hash = fnv1a(teamName);
    const index = hash % SHUFFLED_COMBINATIONS.length;
    const { color, shade } = SHUFFLED_COMBINATIONS[index];
    return loadColor(color, shade);
  }

  return { getColorForTeam };
}
