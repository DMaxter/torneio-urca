<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Jogadores" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
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
      <P-Column header="Ações" class="w-8rem md:w-auto">
        <template #body="{ data }">
          <div class="flex gap-2 items-center">
            <span
              v-if="!data.is_confirmed"
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-green-600 hover:bg-green-50"
              @click.stop="promptConfirmPlayer(data.id, data.name)"
              v-tooltip.top="'Confirmar jogador'"
            >
              check
            </span>
            <span
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
              @click.stop="promptRemovePlayer(data.id, data.name)"
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

  <P-Dialog v-model:visible="showConfirmPlayer" modal header="Confirmar Jogador" class="w-11/12 md:w-8/12">
    <p>Tem a certeza que deseja confirmar o jogador <strong>{{ playerToAction?.name }}</strong>?</p>
    <p class="text-orange-600 mt-2">Esta ação irá eliminar o Cartão de Cidadão, Comprovativo de Residência e o NIF do jogador.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showConfirmPlayer = false">Cancelar</P-Button>
      <P-Button severity="success" @click="confirmPlayerAction">Confirmar</P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showRemovePlayer" modal header="Remover Jogador" class="w-11/12 md:w-8/12">
    <p>Tem a certeza que deseja remover o jogador <strong>{{ playerToAction?.name }}</strong>?</p>
    <p class="text-red-600 mt-2">Esta ação não pode ser desfeita.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showRemovePlayer = false">Cancelar</P-Button>
      <P-Button severity="danger" @click="confirmRemovePlayerAction">Remover</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { usePlayerStore } from "@stores/players";
import { useTeamStore } from "@stores/teams";

const toast = useToast();
const enabled = defineModel<boolean>();
const playerStore = usePlayerStore();
const teamStore = useTeamStore();

const showConfirmPlayer = ref(false);
const showRemovePlayer = ref(false);
const playerToAction = ref<{ id: string; name: string } | null>(null);

onMounted(async () => {
  await playerStore.getPlayers();
});

function promptConfirmPlayer(playerId: string, playerName: string) {
  playerToAction.value = { id: playerId, name: playerName };
  showConfirmPlayer.value = true;
}

async function confirmPlayerAction() {
  if (!playerToAction.value) return;
  const result = await playerStore.confirmPlayer(playerToAction.value.id);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador confirmado", life: 3000 });
  }
  showConfirmPlayer.value = false;
  playerToAction.value = null;
}

function promptRemovePlayer(playerId: string, playerName: string) {
  playerToAction.value = { id: playerId, name: playerName };
  showRemovePlayer.value = true;
}

async function confirmRemovePlayerAction() {
  if (!playerToAction.value) return;
  const result = await playerStore.deletePlayer(playerToAction.value.id);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador removido", life: 3000 });
    await teamStore.getTeams();
  }
  showRemovePlayer.value = false;
  playerToAction.value = null;
}
</script>
