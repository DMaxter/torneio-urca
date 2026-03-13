<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Jogadores" :style="{ width: '80vw' }">
    <P-DataTable :value="playerStore.players" paginator :rows="10">
      <P-Column field="name" header="Nome" />
      <P-Column field="fiscal_number" header="NIF" />
      <P-Column field="birth_date" header="Data de Nascimento">
        <template #body="{ data }">
          {{ new Date(data.birth_date).toLocaleDateString('pt-PT') }}
        </template>
      </P-Column>
      <P-Column field="is_federated" header="Federado">
        <template #body="{ data }">
          {{ data.is_federated ? 'Sim' : 'Não' }}
        </template>
      </P-Column>
      <P-Column field="federation_team" header="Equipa Federada" />
      <P-Column field="is_confirmed" header="Confirmado">
        <template #body="{ data }">
          <P-Tag :severity="data.is_confirmed ? 'success' : 'warning'" :value="data.is_confirmed ? 'Confirmado' : 'Pendente'" />
        </template>
      </P-Column>
      <P-Column header="Ações">
        <template #body="{ data }">
          <P-Button 
            v-if="!data.is_confirmed" 
            icon="pi pi-check" 
            severity="success" 
            text 
            rounded 
            @click="confirmPlayer(data.id)"
            title="Confirmar jogador"
          />
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="playerStore.getPlayers()">Atualizar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import { usePlayerStore } from "@stores/players";

const enabled = defineModel<boolean>();

const playerStore = usePlayerStore();

onMounted(async () => {
  await playerStore.getPlayers();
});

async function confirmPlayer(playerId: string) {
  await playerStore.confirmPlayer(playerId);
}
</script>
