import { computed } from 'vue';
import type { Game } from '@router/backend/services/game/types';

export function useGameScore(gameRef: any, homeTeamNameRef?: any, awayTeamNameRef?: any) {
  const getPeriodGoals = (period: number) => {
    let home = 0;
    let away = 0;
    if (!gameRef.value || !gameRef.value.events) return { home, away };

    const homeId = gameRef.value.home_call?.team;
    const awayId = gameRef.value.away_call?.team;

    gameRef.value.events.forEach((event: any) => {
      if (event.Goal && event.Goal.period === period) {
        const homeName = homeTeamNameRef?.value;
        const awayName = awayTeamNameRef?.value;

        if (event.Goal.team_name === homeName) {
          home++;
        } else if (event.Goal.team_name === awayName) {
          away++;
        }
      }
    });
    return { home, away };
  };

  const getPenaltiesScore = () => {
    let home = 0;
    let away = 0;
    if (!gameRef.value || !gameRef.value.events) return { home, away };

    gameRef.value.events.forEach((event: any) => {
      if (event.Penalty && event.Penalty.scored) {
        const homeId = gameRef.value.home_call?.team;
        const awayId = gameRef.value.away_call?.team;
        if (event.Penalty.team_id === homeId) {
          home++;
        } else if (event.Penalty.team_id === awayId) {
          away++;
        }
      }
    });

    return { home, away };
  };

  const totalScore = computed(() => {
    let home = 0;
    let away = 0;

    for (let i = 1; i <= (gameRef.value?.current_period || 2); i++) {
      const periodScore = getPeriodGoals(i);
      home += periodScore.home;
      away += periodScore.away;
    }

    return { home, away };
  });

  const displayScore = computed(() => {
    const { home, away } = totalScore.value;
    let scoreStr = `${home} - ${away}`;

    if (gameRef.value?.current_period === 4) {
      const penScore = getPenaltiesScore();
      if (penScore.home > 0 || penScore.away > 0) {
        scoreStr += ` (${penScore.home}-${penScore.away} gp)`;
      }
    }
    return scoreStr;
  });

  return {
    getPeriodGoals,
    getPenaltiesScore,
    totalScore,
    displayScore,
  };
}
