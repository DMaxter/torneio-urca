import { computed } from 'vue';

export function useGameEvents(gameRef: any) {
  const getEventIcon = (event: any) => {
    if (event.Goal) return 'sports_soccer';
    if (event.Foul) {
      if (event.Foul.card === 'Yellow' || event.Foul.card === 'Red') return 'style';
      return 'warning';
    }
    if (event.PeriodStart) return 'play_circle';
    if (event.PeriodEnd) return 'flag';
    if (event.PeriodPause) return 'pause_circle';
    if (event.PeriodResume) return 'play_circle';
    if (event.Penalty) return event.Penalty.scored ? 'sports_soccer' : 'close';
    if (event.Manual) return 'info';
    if (event.GameEnd) return 'emoji_events';
    if (event.PenaltyShootoutStart) return 'sports_and_outdoors';
    return 'circle';
  };

  const getEventIconColorClass = (event: any) => {
    if (event.Goal) return 'text-green-500';
    if (event.Foul) {
      if (event.Foul.card === 'Yellow') return 'text-yellow-500';
      if (event.Foul.card === 'Red') return 'text-red-500';
      return 'text-orange-500';
    }
    if (event.PeriodStart || event.PeriodEnd) return 'text-blue-500';
    if (event.PeriodPause) return 'text-orange-500';
    if (event.PeriodResume) return 'text-green-500';
    if (event.Penalty) return event.Penalty.scored ? 'text-green-500' : 'text-red-500';
    if (event.Manual) return 'text-gray-500';
    if (event.GameEnd) return 'text-amber-500';
    if (event.PenaltyShootoutStart) return 'text-purple-500';
    return 'text-gray-400';
  };

  const getEventDescription = (event: any) => {
    if (event.Goal) {
      const g = event.Goal;
      if (g.own_goal) {
        return `Auto-golo de ${g.own_goal_committed_by || 'Equipa desconhecida'}`;
      }
      return `Golo de ${g.player_name || g.player_number || 'Sem número'}`;
    }
    if (event.Foul) {
      const f = event.Foul;
      const target = f.player_name || f.staff_name || 'Desconhecido';
      if (f.card === 'Yellow') return `Cartão Amarelo para ${target}`;
      if (f.card === 'Red') return `Cartão Vermelho para ${target}`;
      return `Falta de ${target}`;
    }
    if (event.PeriodStart) {
      const p = event.PeriodStart.period;
      return `Início do ${p === 5 ? 'período de penalidades' : `${p}º período`}`;
    }
    if (event.PeriodEnd) {
      const p = event.PeriodEnd.period;
      return `Fim do ${p === 5 ? 'período de penalidades' : `${p}º período`}`;
    }
    if (event.PeriodPause) {
      const p = event.PeriodPause.period;
      return `Pausa no ${p === 5 ? 'período de penalidades' : `${p}º período`}`;
    }
    if (event.PeriodResume) {
      const p = event.PeriodResume.period;
      return `Retoma do ${p === 5 ? 'período de penalidades' : `${p}º período`}`;
    }
    if (event.Penalty) {
      return `Penálti (${event.Penalty.scored ? 'Marcado' : 'Falhado'}): ${event.Penalty.player_name || event.Penalty.player_number}`;
    }
    if (event.Manual) return event.Manual.description;
    if (event.GameEnd) {
      const g = event.GameEnd;
      let desc = `Fim do Jogo: ${g.home_score} - ${g.away_score}`;
      if (g.home_penalty_score > 0 || g.away_penalty_score > 0) {
        desc += ` (Pen: ${g.home_penalty_score} - ${g.away_penalty_score})`;
      }
      return desc;
    }
    if (event.PenaltyShootoutStart) return 'Início do Desempate por Grandes Penalidades';
    return 'Evento Desconhecido';
  };

  const getEventTime = (event: any) => {
    const ev = Object.values(event)[0] as any;
    if (ev.minute !== undefined) {
      return `${ev.minute}'`;
    }
    if (ev.elapsed_seconds !== undefined) {
      const m = Math.floor(ev.elapsed_seconds / 60);
      return `${m}'`;
    }
    if (event.GameEnd) return 'Fim';
    if (event.PenaltyShootoutStart) return 'P5';
    return '--\'';
  };

  const getEventTeam = (event: any) => {
    if (event.Goal) return event.Goal.team_name;
    if (event.Foul) return event.Foul.team_name;
    if (event.Penalty) return event.Penalty.team_name;
    return '';
  };

  return {
    getEventIcon,
    getEventIconColorClass,
    getEventDescription,
    getEventTime,
    getEventTeam,
  };
}
