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
      <P-Column header="Torneio" class="w-6rem md:w-auto">
        <template #body="{ data }">
          <span class="text-muted text-sm">{{ getTournamentName(data.tournament) }}</span>
        </template>
      </P-Column>
      <P-Column header="Responsável" class="w-6rem md:w-auto">
        <template #body="{ data }">
          <span class="text-muted">{{ data.responsible_name }}</span>
        </template>
      </P-Column>
      <P-Column header="Jogadores" class="w-5rem md:w-auto">
        <template #body="{ data }">
          <P-Tag :value="`${data.players?.length || 0}`" :severity="(data.players?.length || 0) >= 5 ? 'success' : 'danger'" />
        </template>
      </P-Column>
      <P-Column header="Ver Jogadores" class="w-8rem">
        <template #body="{ data }">
          <P-Button size="small" severity="info" @click.stop="openTeamPlayers(data.id)">
            <span class="material-symbols-outlined">visibility</span>
          </P-Button>
        </template>
      </P-Column>
      <P-Column header="Editar" class="w-3rem">
        <template #body="{ data }">
          <span
            class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-blue-600 hover:bg-blue-50"
            @click.stop="promptEditTeam(data)"
            v-tooltip.top="'Editar equipa'"
          >
            edit
          </span>
        </template>
      </P-Column>
      <P-Column header="Eliminar" class="w-5rem">
        <template #body="{ data }">
          <span
            class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
            @click.stop="deleteTeam(data.id, data.name)"
            v-tooltip.top="'Eliminar equipa'"
          >
            delete
          </span>
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

  <P-Dialog v-model:visible="showDeleteConfirm" modal header="Confirmar Eliminação" class="w-11/12 md:w-4/12">
    <p>Tem a certeza que deseja eliminar a equipa <strong>{{ teamToDelete?.name }}</strong>?</p>
    <p class="text-red-600 mt-2">Esta ação eliminará também todos os jogadores associados.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showDeleteConfirm = false">Cancelar</P-Button>
      <P-Button severity="danger" @click="confirmDeleteTeam">Eliminar</P-Button>
    </template>
  </P-Dialog>

  <TeamManagement v-model="showEditTeam" :team="editingTeam" />

  <P-Dialog v-model:visible="showConfirmPlayer" modal header="Confirmar Jogador" class="w-11/12 md:w-4/12">
    <p>Tem a certeza que deseja confirmar o jogador <strong>{{ playerToAction?.name }}</strong>?</p>
    <p class="text-orange-600 mt-2">Esta ação irá eliminar o Cartão de Cidadão, Comprovativo de Residência e o NIF do jogador.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showConfirmPlayer = false">Cancelar</P-Button>
      <P-Button severity="success" @click="confirmPlayerAction">Confirmar</P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showRemovePlayer" modal header="Remover Jogador" class="w-11/12 md:w-4/12">
    <p>Tem a certeza que deseja remover o jogador <strong>{{ playerToAction?.name }}</strong>?</p>
    <p class="text-red-600 mt-2">Esta ação não pode ser desfeita.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showRemovePlayer = false">Cancelar</P-Button>
      <P-Button severity="danger" @click="confirmRemovePlayerAction">Remover</P-Button>
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
              @click="promptConfirmPlayer(data.id, data.name)"
              v-tooltip.top="'Confirmar jogador'"
            >
              check
            </span>
            <span
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
              @click="promptRemovePlayer(data.id, data.name)"
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
import { useTournamentStore } from "@stores/tournaments";
import { getFileUrl } from "@router/backend/services/file";
import * as teamService from "@router/backend/services/team";

const toast = useToast();
const enabled = defineModel<boolean>();
const teamStore = useTeamStore();
const playerStore = usePlayerStore();
const tournamentStore = useTournamentStore();

const showTeamPlayers = ref(false);
const showFileViewer = ref(false);
const showDeleteConfirm = ref(false);
const showConfirmPlayer = ref(false);
const showRemovePlayer = ref(false);
const showEditTeam = ref(false);
const selectedTeamId = ref("");
const selectedTeamName = ref("");
const teamPlayers = ref<any[]>([]);
const fileUrl = ref("");
const teamToDelete = ref<{ id: string; name: string } | null>(null);
const playerToAction = ref<{ id: string; name: string } | null>(null);
const editingTeam = ref<{ id: string; name: string; tournament: string; responsible_name: string; responsible_email: string; responsible_phone: string }>({ id: "", name: "", tournament: "", responsible_name: "", responsible_email: "", responsible_phone: "" });

function getTournamentName(tournamentId: string): string {
  const tournament = tournamentStore.tournaments.find(t => t.id === tournamentId);
  return tournament?.name || "-";
}

function deleteTeam(teamId: string, teamName: string) {
  teamToDelete.value = { id: teamId, name: teamName };
  showDeleteConfirm.value = true;
}

async function confirmDeleteTeam() {
  if (!teamToDelete.value) return;
  const result = await teamStore.deleteTeam(teamToDelete.value.id);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Equipa eliminada", life: 3000 });
    showDeleteConfirm.value = false;
    teamToDelete.value = null;
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível eliminar a equipa", life: 3000 });
  }
}

function promptEditTeam(team: any) {
  editingTeam.value = team;
  showEditTeam.value = true;
}

async function saveEditTeam() {
  const result = await teamStore.updateTeam(editingTeam.value.id, {
    name: editingTeam.value.name,
    tournament: editingTeam.value.tournament,
    responsible_name: editingTeam.value.responsible_name,
    responsible_email: editingTeam.value.responsible_email,
    responsible_phone: editingTeam.value.responsible_phone,
    players: []
  } as any);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Equipa atualizada", life: 3000 });
    showEditTeam.value = false;
    await teamStore.getTeams();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível atualizar a equipa", life: 3000 });
  }
}

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

function promptConfirmPlayer(playerId: string, playerName: string) {
  playerToAction.value = { id: playerId, name: playerName };
  showConfirmPlayer.value = true;
}

async function confirmPlayerAction() {
  if (!playerToAction.value) return;
  const result = await playerStore.confirmPlayer(playerToAction.value.id);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador confirmado", life: 3000 });
    await loadTeamPlayers();
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
    await loadTeamPlayers();
    await teamStore.getTeams();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível remover o jogador", life: 3000 });
  }
  showRemovePlayer.value = false;
  playerToAction.value = null;
}

onMounted(async () => {
  await teamStore.getTeams();
  await tournamentStore.getTournaments();
});
</script>

<style scoped>
.file-viewer {
  width: 100%;
  height: 80vh;
  border: none;
}
</style>
