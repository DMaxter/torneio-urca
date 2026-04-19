import { computed } from 'vue';
import type { Game } from '@router/backend/services/game/types';

export function useGameScore(gameRef: any) {
  const getPeriodGoals = (period: number) => {
    let home = 0;
    let away = 0;
    if (!gameRef.value || !gameRef.value.events) return { home, away };

    gameRef.value.events.forEach((event: any) => {
      if (event.Goal && event.Goal.period === period) {
        if (event.Goal.team_name === gameRef.value.home_team_name) {
          home++;
        } else if (event.Goal.team_name === gameRef.value.away_team_name) {
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
        if (event.Penalty.team_id === gameRef.value.home_team) {
          home++;
        } else if (event.Penalty.team_id === gameRef.value.away_team) {
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
