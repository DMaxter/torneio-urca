import { computed } from 'vue';
import type { Game } from '@router/backend/services/game/types';
import type { Team } from '@router/backend/services/team/types';

export function useGameHelpers(gameRef: any, tournamentTeamsRef: any) {
  const getTeamName = (teamId?: string | null) => {
    if (!tournamentTeamsRef.value || !teamId) return 'Unknown';
    const team = tournamentTeamsRef.value.find((t: Team) => t.id === teamId);
    return team ? team.name : 'Unknown';
  };

  const homeTeamName = computed(() => {
    return gameRef.value?.home_call?.team ? getTeamName(gameRef.value.home_call.team) : 'Equipa Casa';
  });

  const awayTeamName = computed(() => {
    return gameRef.value?.away_call?.team ? getTeamName(gameRef.value.away_call.team) : 'Equipa Fora';
  });

  return {
    getTeamName,
    homeTeamName,
    awayTeamName,
  };
}
