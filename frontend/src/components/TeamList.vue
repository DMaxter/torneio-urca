<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Equipas" class="w-11/12 md:w-8/12 lg:w-7/12 xl:w-6/12">
    <P-DataTable :value="teamStore.teams" striped-rows size="small" selectionMode="single" @rowSelect="onTeamSelect" responsiveLayout="scroll">
      <P-Column field="name" header="Nome da Equipa">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>⚽</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Responsável">
        <template #body="{ data }">
          <span class="text-muted">{{ data.responsible_name }}</span>
        </template>
      </P-Column>
      <P-Column header="Jogadores">
        <template #body="{ data }">
          <P-Tag :value="`${data.players?.length || 0}`" severity="info" />
        </template>
      </P-Column>
      <P-Column header="Ver Jogadores" class="w-8rem">
        <template #body="{ data }">
          <P-Button size="small" severity="info" @click.stop="openTeamPlayers(data.id)">
            <span class="material-symbols-outlined">visibility</span>
          </P-Button>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="teamStore.getTeams()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showTeamPlayers" modal :header="`Jogadores - ${selectedTeamName}`" class="w-11/12 md:w-10/12 lg:w-8/12 xl:w-7/12">
    <P-DataTable :value="teamPlayers" striped-rows size="small">
      <P-Column field="name" header="Nome">
        <template #body="{ data }">
          <span class="font-medium">{{ data.name }}</span>
        </template>
      </P-Column>
      <P-Column field="birth_date" header="Nascimento" class="w-24rem md:w-auto">
        <template #body="{ data }">
          {{ new Date(data.birth_date).toLocaleDateString('pt-PT') }}
        </template>
      </P-Column>
      <P-Column header="Cartão" class="w-6rem md:w-auto">
        <template #body="{ data }">
          <P-Button 
            v-if="data.citizen_card_file_id" 
            size="small" 
            severity="secondary" 
            @click="viewFile(data.citizen_card_file_id)"
          >
            <span class="material-symbols-outlined">picture_as_pdf</span>
            <span class="hidden md:inline">Ver</span>
          </P-Button>
          <span v-else class="text-muted">N/A</span>
        </template>
      </P-Column>
      <P-Column header="Residência" class="w-6rem md:w-auto">
        <template #body="{ data }">
          <P-Button 
            v-if="data.proof_of_residency_file_id" 
            size="small" 
            severity="secondary" 
            @click="viewFile(data.proof_of_residency_file_id)"
          >
            <span class="material-symbols-outlined">picture_as_pdf</span>
            <span class="hidden md:inline">Ver</span>
          </P-Button>
          <span v-else class="text-muted">N/A</span>
        </template>
      </P-Column>
      <P-Column header="Autoriz." class="w-5rem md:w-auto">
        <template #body="{ data }">
          <P-Button 
            v-if="data.authorization_file_id" 
            size="small" 
            severity="secondary" 
            @click="viewFile(data.authorization_file_id)"
          >
            <span class="material-symbols-outlined">picture_as_pdf</span>
            <span class="hidden md:inline">Ver</span>
          </P-Button>
          <span v-else class="text-muted">-</span>
        </template>
      </P-Column>
      <P-Column header="Estado" class="w-5rem md:w-auto">
        <template #body="{ data }">
          <P-Tag :severity="data.is_confirmed ? 'success' : 'warning'" :value="data.is_confirmed ? 'Confirmado' : 'Pendente'" />
        </template>
      </P-Column>
      <P-Column header="Ações" class="w-6rem md:w-auto">
        <template #body="{ data }">
          <div class="flex gap-1">
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
      <P-Button @click="loadTeamPlayers">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showFileViewer" modal header="Documento" :style="{ width: '80vw', height: '90vh' }">
    <iframe v-if="fileUrl" :src="fileUrl" class="file-viewer"></iframe>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { useTeamStore } from "@stores/teams";
import { usePlayerStore } from "@stores/players";
import { getFileUrl } from "@router/backend/services/file";
import * as teamService from "@router/backend/services/team";

const toast = useToast();
const enabled = defineModel<boolean>();
const teamStore = useTeamStore();
const playerStore = usePlayerStore();

const showTeamPlayers = ref(false);
const showFileViewer = ref(false);
const selectedTeamId = ref("");
const selectedTeamName = ref("");
const teamPlayers = ref<any[]>([]);
const fileUrl = ref("");

function onTeamSelect(event: any) {
  openTeamPlayers(event.data.id);
}

async function openTeamPlayers(teamId: string) {
  selectedTeamId.value = teamId;
  const team = teamStore.teams.find(t => t.id === teamId);
  selectedTeamName.value = team?.name || "";
  await loadTeamPlayers();
  showTeamPlayers.value = true;
}

async function loadTeamPlayers() {
  if (!selectedTeamId.value) return;
  const { data } = await teamService.getTeamPlayers(selectedTeamId.value);
  if (data) {
    teamPlayers.value = data as any[];
  }
}

function viewFile(fileId: string) {
  fileUrl.value = getFileUrl(fileId);
  showFileViewer.value = true;
}

async function confirmPlayer(playerId: string) {
  const result = await playerStore.confirmPlayer(playerId);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador confirmado", life: 3000 });
    await loadTeamPlayers();
  }
}

async function removePlayer(playerId: string) {
  console.log("Removing player:", playerId);
  const result = await playerStore.deletePlayer(playerId);
  console.log("Delete result:", result);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador removido", life: 3000 });
    await loadTeamPlayers();
    await teamStore.getTeams();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível remover o jogador", life: 3000 });
  }
}

onMounted(async () => {
  await teamStore.getTeams();
});
</script>

<style scoped>
.file-viewer {
  width: 100%;
  height: 80vh;
  border: none;
}
</style>
