<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Jogos" :style="{ width: '800px' }">
    <P-DataTable :value="gameStore.games" striped-rows size="small">
      <P-Column header="Data" style="width: 150px">
        <template #body="{ data }">
          {{ new Date(data.scheduled_date).toLocaleDateString('pt-PT') }}
        </template>
      </P-Column>
      <P-Column header="Hora" style="width: 80px">
        <template #body="{ data }">
          {{ new Date(data.scheduled_date).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }) }}
        </template>
      </P-Column>
      <P-Column header="Equipa da Casa">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>🏠</span>
            <span class="font-medium">{{ data.home_call?.team || 'N/A' }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Equipa Visitante">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>✈️</span>
            <span class="font-medium">{{ data.away_call?.team || 'N/A' }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Estado" style="width: 120px">
        <template #body="{ data }">
          <P-Tag :severity="getStatusSeverity(data.status)" :value="getStatusLabel(data.status)" />
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button label="Atualizar" icon="pi pi-refresh" @click="gameStore.getGames()" />
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useGameStore } from "@stores/games";
import { GameStatus } from "@router/backend/services/game/types";

const enabled = defineModel<boolean>();
const gameStore = useGameStore();

onMounted(async () => {
  await gameStore.getGames();
});

function getStatusSeverity(status: number) {
  switch (status) {
    case GameStatus.NotStarted: return "secondary";
    case GameStatus.InProgress: return "info";
    case GameStatus.Finished: return "success";
    case GameStatus.Canceled: return "danger";
    default: return "secondary";
  }
}

function getStatusLabel(status: number) {
  switch (status) {
    case GameStatus.NotStarted: return "Por iniciar";
    case GameStatus.InProgress: return "Em progresso";
    case GameStatus.Finished: return "Terminado";
    case GameStatus.Canceled: return "Cancelado";
    default: return "Desconhecido";
  }
}
</script>
