<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Jogadores" :style="{ width: '900px' }">
    <P-DataTable :value="playerStore.players" striped-rows size="small" paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]">
      <P-Column field="name" header="Nome">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>🧑</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column field="fiscal_number" header="NIF" style="width: 100px" />
      <P-Column field="birth_date" header="Nascimento" style="width: 110px">
        <template #body="{ data }">
          {{ new Date(data.birth_date).toLocaleDateString('pt-PT') }}
        </template>
      </P-Column>
      <P-Column header="Federado" style="width: 90px">
        <template #body="{ data }">
          <i :class="data.is_federated ? 'pi pi-check text-green-600' : 'pi pi-times text-gray-400'" />
        </template>
      </P-Column>
      <P-Column header="Estado" style="width: 110px">
        <template #body="{ data }">
          <P-Tag :severity="data.is_confirmed ? 'success' : 'warning'" :value="data.is_confirmed ? 'Confirmado' : 'Pendente'" />
        </template>
      </P-Column>
      <P-Column header="Ações" style="width: 80px">
        <template #body="{ data }">
          <P-Button 
            v-if="!data.is_confirmed" 
            icon="pi pi-check" 
            severity="success" 
            text 
            rounded 
            @click="confirmPlayer(data.id)"
            v-tooltip.top="'Confirmar jogador'"
          />
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button label="Atualizar" icon="pi pi-refresh" @click="playerStore.getPlayers()" />
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { usePlayerStore } from "@stores/players";

const toast = useToast();
const enabled = defineModel<boolean>();
const playerStore = usePlayerStore();

onMounted(async () => {
  await playerStore.getPlayers();
});

async function confirmPlayer(playerId: string) {
  const result = await playerStore.confirmPlayer(playerId);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador confirmado", life: 3000 });
  }
}
</script>
