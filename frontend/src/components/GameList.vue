<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Jogos" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-DataTable :value="gameStore.games" striped-rows size="small" responsiveLayout="scroll">
      <P-Column header="Torneio">
        <template #body="{ data }">
          <span class="text-sm text-stone-500">{{ getTournamentName(data.tournament) }}</span>
        </template>
      </P-Column>
      <P-Column header="Equipa da Casa">
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <span>🏠</span>
            <span class="font-medium">{{ getTeamName(data.home_call?.team) }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Equipa Visitante">
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <span>✈️</span>
            <span class="font-medium">{{ getTeamName(data.away_call?.team) }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Fase" style="width: 100px">
        <template #body="{ data }">
          <span class="text-sm text-stone-500">{{ getPhaseLabel(data.phase) }}</span>
        </template>
      </P-Column>
      <P-Column header="Estado" style="width: 120px">
        <template #body="{ data }">
          <P-Tag :severity="getStatusSeverity(data.status)" :value="getStatusLabel(data.status)" />
        </template>
      </P-Column>
      <P-Column header="Ação" style="width: 150px">
        <template #body="{ data }">
           <div class="flex gap-1" v-if="data.status !== GameStatus.Finished">
             <P-Button 
               v-if="data.status === GameStatus.Scheduled" 
               label="Iniciar Chamadas" 
               size="small" 
               severity="info"
               @click="startCalls(data.id)" 
               v-tooltip.top="'Iniciar chamadas de jogadores'"
             />
             <P-Button 
               v-else-if="data.status === GameStatus.CallsPending" 
               label="Confirmar" 
               size="small" 
               severity="success"
               @click="confirmCalls(data.id)" 
               v-tooltip.top="'Confirmar chamadas (mín. 5 jogadores)'"
             />
             <P-Button 
               v-else-if="data.status === GameStatus.ReadyToStart" 
               label="Iniciar Jogo" 
               size="small" 
               severity="success"
               @click="startGame(data.id)" 
               v-tooltip.top="'Iniciar o jogo'"
             />
             <P-Button 
               v-else-if="data.status === GameStatus.InProgress" 
               label="Live" 
               size="small" 
               severity="warn"
               @click="goToLiveGame(data.id)" 
               v-tooltip.top="'Abrir vista de jogo ao vivo'"
             />
             <P-Button 
               v-if="data.status !== GameStatus.InProgress && data.status !== GameStatus.Finished" 
               icon="close" 
               size="small" 
               severity="danger"
               @click="cancelGame(data.id)" 
               v-tooltip.top="'Cancelar jogo'"
             />
           </div>
        </template>
      </P-Column>
      <P-Column header="Eliminar todos" style="width: 110px">
        <template #body="{ data }">
          <span
            v-if="!tournamentHasScheduledGames(data.tournament)"
            class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
            @click="promptDeleteTournamentGames(data.tournament)"
            v-tooltip.top="'Eliminar todos os jogos deste torneio'"
          >delete_sweep</span>
          <span
            v-else
            class="material-symbols-outlined text-xl p-1 text-stone-300 cursor-not-allowed"
            v-tooltip.top="'Não é possível eliminar jogos com agendamentos'"
          >delete_sweep</span>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="gameStore.getGames()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showDeleteConfirm" modal header="Confirmar Eliminação" class="w-11/12 md:w-6/12">
    <p>Tem a certeza que deseja eliminar <strong>todos os {{ tournamentGamesToDelete.length }} jogos</strong> do torneio <strong>{{ getTournamentName(tournamentToDelete) }}</strong>?</p>
    <p class="text-red-600 mt-2 text-sm">Esta ação não pode ser desfeita.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showDeleteConfirm = false">Cancelar</P-Button>
      <P-Button severity="danger" :loading="deleting" @click="confirmDeleteAll">Eliminar todos</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useGameStore } from "@stores/games";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { GameStatus } from "@router/backend/services/game/types";
import * as gameService from "@router/backend/services/game";

const router = useRouter();
const enabled = defineModel<boolean>();
const toast = useToast();
const gameStore = useGameStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const showDeleteConfirm = ref(false);
const tournamentToDelete = ref("");
const deleting = ref(false);

const tournamentGamesToDelete = computed(() =>
  gameStore.games.filter(g => g.tournament === tournamentToDelete.value)
);

function tournamentHasScheduledGames(tournamentId: string): boolean {
  return gameStore.games.some(g => g.tournament === tournamentId && g.scheduled_date);
}

function getTeamName(teamId: string): string {
  return teamStore.teams.find(t => t.id === teamId)?.name ?? "N/A";
}

function getTournamentName(tournamentId: string): string {
  return tournamentStore.tournaments.find(t => t.id === tournamentId)?.name ?? "-";
}

function promptDeleteTournamentGames(tournamentId: string) {
  tournamentToDelete.value = tournamentId;
  showDeleteConfirm.value = true;
}

async function confirmDeleteAll() {
  deleting.value = true;
  let allOk = true;

  for (const game of tournamentGamesToDelete.value) {
    const result = await gameStore.deleteGame(game.id);
    if (!result.success) allOk = false;
  }

  deleting.value = false;
  showDeleteConfirm.value = false;
  tournamentToDelete.value = "";

  if (allOk) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Todos os jogos eliminados", life: 3000 });
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Alguns jogos não foram eliminados", life: 3000 });
  }
}

async function startCalls(gameId: string) {
  try {
    const response = await gameService.updateGameStatus(gameId, GameStatus.CallsPending);
    if (response.status === 200) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Chamadas iniciadas", life: 3000 });
      await gameStore.getGames();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao iniciar chamadas";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  }
}

async function confirmCalls(gameId: string) {
  try {
    const response = await gameService.confirmGameCalls(gameId);
    if (response.status === 200) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Chamadas confirmadas", life: 3000 });
      await gameStore.getGames();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao confirmar chamadas";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  }
}

async function startGame(gameId: string) {
  try {
    const response = await gameService.updateGameStatus(gameId, GameStatus.InProgress);
    if (response.status === 200) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Jogo iniciado", life: 3000 });
      await gameStore.getGames();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao iniciar jogo";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  }
}

async function finishGame(gameId: string) {
  try {
    const response = await gameService.updateGameStatus(gameId, GameStatus.Finished);
    if (response.status === 200) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Jogo terminado", life: 3000 });
      await gameStore.getGames();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao terminar jogo";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  }
}

async function cancelGame(gameId: string) {
  try {
    const response = await gameService.updateGameStatus(gameId, GameStatus.Canceled);
    if (response.status === 200) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Jogo cancelado", life: 3000 });
      await gameStore.getGames();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao cancelar jogo";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  }
}

function goToLiveGame(gameId: string) {
  router.push(`/admin/live-game/${gameId}`);
}

function getStatusSeverity(status: number | string) {
  const s = String(status);
  switch (s) {
    case "0":
    case "Scheduled": return "secondary";
    case "1":
    case "CallsPending": return "warn";
    case "2":
    case "ReadyToStart": return "info";
    case "3":
    case "InProgress": return "success";
    case "4":
    case "Finished": return "contrast";
    case "5":
    case "Canceled": return "danger";
    default: return "secondary";
  }
}

function getPhaseLabel(phase: string) {
  switch (phase) {
    case "group": return "Grupos";
    case "quarter_final": return "Quartos";
    case "semi_final": return "Meias";
    case "final": return "Final";
    case "third_place": return "3º/4º";
    default: return phase;
  }
}

function getStatusLabel(status: number | string) {
  const s = String(status);
  switch (s) {
    case "0":
    case "Scheduled": return "Agendado";
    case "1":
    case "CallsPending": return "Chamadas Pendentes";
    case "2":
    case "ReadyToStart": return "Pronto";
    case "3":
    case "InProgress": return "Em Progresso";
    case "4":
    case "Finished": return "Terminado";
    case "5":
    case "Canceled": return "Cancelado";
    default: return "?" + s;
  }
}

onMounted(async () => {
  await gameStore.getGames();
  await teamStore.getTeams();
  await tournamentStore.getTournaments();
});
</script>
