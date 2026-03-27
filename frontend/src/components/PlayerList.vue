<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Jogadores" class="w-11/12 md:w-10/12 lg:w-8/12 xl:w-7/12">
    <P-DataTable :value="playerStore.players" striped-rows size="small" paginator :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]" responsiveLayout="scroll">
      <P-Column field="name" header="Nome">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>🧑</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column field="fiscal_number" header="NIF" class="w-6rem md:w-auto" />
      <P-Column field="birth_date" header="Nascimento" class="w-6rem md:w-auto">
        <template #body="{ data }">
          {{ new Date(data.birth_date).toLocaleDateString('pt-PT') }}
        </template>
      </P-Column>
      <P-Column header="Federado" class="w-4rem md:w-auto">
        <template #body="{ data }">
          <span class="material-symbols-outlined" :class="data.is_federated ? 'status-success' : 'status-muted'">
            {{ data.is_federated ? 'check' : 'close' }}
          </span>
        </template>
      </P-Column>
      <P-Column header="Estado" class="w-5rem md:w-auto">
        <template #body="{ data }">
          <P-Tag :severity="data.is_confirmed ? 'success' : 'warning'" :value="data.is_confirmed ? 'Confirmado' : 'Pendente'" />
        </template>
      </P-Column>
      <P-Column header="Ações" class="w-6rem md:w-auto">
        <template #body="{ data }">
          <div class="flex gap-2 items-center">
            <span
              v-if="!data.is_confirmed"
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-green-600 hover:bg-green-50"
              @click="confirmPlayer(data.id)"
              v-tooltip.top="'Confirmar jogador'"
            >
              check
            </span>
            <span
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
              @click="removePlayer(data.id)"
              v-tooltip.top="'Remover jogador'"
            >
              delete
            </span>
          </div>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="playerStore.getPlayers()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
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

async function removePlayer(playerId: string) {
  const result = await playerStore.deletePlayer(playerId);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador removido", life: 3000 });
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível remover o jogador", life: 3000 });
  }
}
</script>
