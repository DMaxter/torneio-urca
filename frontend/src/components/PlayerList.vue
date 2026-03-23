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
          <span class="material-symbols-outlined" :style="{ color: data.is_federated ? '#16a34a' : '#78716c' }">
            {{ data.is_federated ? 'check' : 'close' }}
          </span>
        </template>
      </P-Column>
      <P-Column header="Estado" style="width: 110px">
        <template #body="{ data }">
          <P-Tag :severity="data.is_confirmed ? 'success' : 'warning'" :value="data.is_confirmed ? 'Confirmado' : 'Pendente'" />
        </template>
      </P-Column>
      <P-Column header="Ações" style="width: 80px">
        <template #body="{ data }">
          <span
            v-if="!data.is_confirmed"
            class="material-symbols-outlined icon-btn success"
            @click="confirmPlayer(data.id)"
            v-tooltip.top="'Confirmar jogador'"
          >
            check
          </span>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button label="Atualizar" @click="playerStore.getPlayers()">
        <span class="material-symbols-outlined">sync</span>
      </P-Button>
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

<style scoped>
.icon-btn {
  cursor: pointer;
  font-size: 20px;
  padding: 4px;
  border-radius: 4px;
}

.icon-btn.success {
  color: #16a34a;
}

.icon-btn.success:hover {
  background-color: #f0fdf4;
}
</style>
