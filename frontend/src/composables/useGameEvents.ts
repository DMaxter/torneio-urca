import { computed } from 'vue';

export function useGameEvents(gameRef: any) {
  const getEventIcon = (event: any) => {
    if (event.Goal) return 'pi pi-bullseye text-green-500';
    if (event.Foul) {
      if (event.Foul.card === 'Yellow') return 'pi pi-file text-yellow-500';
      if (event.Foul.card === 'Red') return 'pi pi-file text-red-500';
      return 'pi pi-exclamation-triangle text-orange-500';
    }
    if (event.PeriodStart) return 'pi pi-play text-blue-500';
    if (event.PeriodEnd) return 'pi pi-stop text-blue-500';
    if (event.PeriodPause) return 'pi pi-pause text-orange-500';
    if (event.PeriodResume) return 'pi pi-play text-green-500';
    if (event.Penalty) return 'pi pi-bullseye ' + (event.Penalty.scored ? 'text-green-500' : 'text-red-500');
    if (event.Manual) return 'pi pi-info-circle text-gray-500';
    return 'pi pi-circle-fill text-gray-500';
  };

  const getEventDescription = (event: any) => {
    if (event.Goal) {
      if (event.Goal.own_goal) {
        return `Auto-Golo: ${event.Goal.player_name || event.Goal.player_number || 'Desconhecido'} (${event.Goal.own_goal_committed_by})`;
      }
      return `Golo: ${event.Goal.player_name || event.Goal.player_number || 'Sem número'}`;
    }
    if (event.Foul) {
      const target = event.Foul.player_name || event.Foul.staff_name || 'Desconhecido';
      let desc = 'Falta';
      if (event.Foul.card === 'Yellow') desc = 'Cartão Amarelo';
      if (event.Foul.card === 'Red') desc = 'Cartão Vermelho';
      return `${desc}: ${target}`;
    }
    if (event.PeriodStart) return `Início da Parte ${event.PeriodStart.period}`;
    if (event.PeriodEnd) return `Fim da Parte ${event.PeriodEnd.period}`;
    if (event.PeriodPause) return `Pausa na Parte ${event.PeriodPause.period}`;
    if (event.PeriodResume) return `Retoma na Parte ${event.PeriodResume.period}`;
    if (event.Penalty) {
      return `Penálti (${event.Penalty.scored ? 'Marcado' : 'Falhado'}): ${event.Penalty.player_name || event.Penalty.player_number}`;
    }
    if (event.Manual) return event.Manual.description;
    return 'Evento Desconhecido';
  };

  const getEventTime = (event: any) => {
    const ev = Object.values(event)[0] as any;
    if (ev.minute !== undefined && ev.second !== undefined) {
      return `${ev.minute.toString().padStart(2, '0')}:${ev.second.toString().padStart(2, '0')}`;
    }
    if (ev.elapsed_seconds !== undefined) {
      const m = Math.floor(ev.elapsed_seconds / 60);
      const s = ev.elapsed_seconds % 60;
      return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return '--:--';
  };

  const getEventTeam = (event: any) => {
    if (event.Goal) return event.Goal.team_name;
    if (event.Foul) return event.Foul.team_name;
    if (event.Penalty) return event.Penalty.team_name;
    return '';
  };

  return {
    getEventIcon,
    getEventDescription,
    getEventTime,
    getEventTeam,
  };
}
