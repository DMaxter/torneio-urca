<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Equipas" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
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
      <P-Column header="Guarda-Redes" class="w-5rem">
        <template #body="{ data }">
          <P-Tag :severity="hasGoalkeeper(data) ? 'success' : 'danger'" :value="hasGoalkeeper(data) ? 'Sim' : 'Não'" />
        </template>
      </P-Column>
      <P-Column header="Treinador" class="w-5rem">
        <template #body="{ data }">
          <P-Tag :severity="hasCoach(data) ? 'success' : 'danger'" :value="hasCoach(data) ? 'Sim' : 'Não'" />
        </template>
      </P-Column>
      <P-Column header="Jogadores" class="w-5rem md:w-auto">
        <template #body="{ data }">
          <P-Tag :value="`${data.players?.length || 0}`" :severity="(data.players?.length || 0) >= 5 ? 'success' : 'danger'" />
        </template>
      </P-Column>
      <P-Column header="Ações" class="w-[120px]">
        <template #body="{ data }">
          <div class="flex gap-1 items-center">
            <P-Button size="small" text @click.stop="viewTeam(data)">
              <span class="material-symbols-outlined text-orange-500" v-tooltip.top="'Ver detalhes'">visibility</span>
            </P-Button>
            <P-Button size="small" text @click.stop="openTeamPlayers(data.id)">
              <span class="material-symbols-outlined text-orange-500" v-tooltip.top="'Ver jogadores'">group</span>
            </P-Button>
            <span
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-orange-500 hover:bg-orange-50"
              @click.stop="promptEditTeam(data)"
              v-tooltip.top="'Editar equipa'"
            >
              edit
            </span>
            <span
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
              @click.stop="deleteTeam(data.id, data.name)"
              v-tooltip.top="'Eliminar equipa'"
            >
              delete
            </span>
          </div>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="teamStore.forceGetTeams()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showDeleteConfirm" modal header="Confirmar Eliminação" class="w-11/12 md:w-8/12">
    <p>Tem a certeza que deseja eliminar a equipa <strong>{{ teamToDelete?.name }}</strong>?</p>
    <p class="text-red-600 mt-2">Esta ação eliminará também todos os jogadores associados.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showDeleteConfirm = false">Cancelar</P-Button>
      <P-Button severity="danger" @click="confirmDeleteTeam">Eliminar</P-Button>
    </template>
  </P-Dialog>

  <TeamManagement v-model="showEditTeam" :team="editingTeam" :viewOnly="viewOnlyMode" />

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

  <P-Dialog v-model:visible="showTeamPlayers" modal :header="`Jogadores - ${selectedTeamName}`" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-DataTable :value="teamPlayers" striped-rows size="small">
      <P-Column field="name" header="Nome">
        <template #body="{ data }">
          <span class="font-semibold">{{ data.name }}</span>
        </template>
      </P-Column>
      <P-Column field="birth_date" header="Nascimento" class="w-24rem md:w-auto">
        <template #body="{ data }">
          {{ new Date(data.birth_date).toLocaleDateString('pt-PT') }}
        </template>
      </P-Column>
      <P-Column field="fiscal_number" header="NIF" class="w-20rem">
        <template #body="{ data }">
          {{ data.fiscal_number }}
        </template>
      </P-Column>
      <P-Column field="place_of_birth" header="Local Nascimento" class="w-24rem md:w-auto">
        <template #body="{ data }">
          {{ data.place_of_birth || '—' }}
        </template>
      </P-Column>
      <P-Column field="address" header="Morada" class="w-32rem md:w-auto">
        <template #body="{ data }">
          {{ data.address || '—' }}
        </template>
      </P-Column>
      <P-Column header="Federado" class="w-20rem">
        <template #body="{ data }">
          <div v-if="data.is_federated" class="flex flex-col gap-1">
            <P-Tag severity="info" :value='"Federado: " + data.federation_team' class="w-fit" />
          </div>
          <P-Tag v-else severity="secondary" value="Não" class="w-fit" />
        </template>
      </P-Column>
      <P-Column header="Exames" class="w-16rem">
        <template #body="{ data }">
          <P-Tag v-if="data.is_federated" :severity="data.federation_exams_up_to_date ? 'success' : 'danger'" :value="data.federation_exams_up_to_date ? 'OK' : 'Expirado'" />
          <span v-else class="text-muted">-</span>
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
      <P-Column header="GR" class="w-4rem">
        <template #body="{ data }">
          <P-Tag :severity="data.is_goalkeeper ? 'success' : 'secondary'" :value="data.is_goalkeeper ? 'Sim' : 'Não'" />
        </template>
      </P-Column>
      <P-Column header="Ações" class="w-6rem md:w-auto">
        <template #body="{ data }">
          <div class="flex gap-1">
            <span
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-orange-500 hover:bg-orange-50"
              @click="promptEditPlayer(data)"
              v-tooltip.top="'Editar jogador'"
            >
              edit
            </span>
            <span
              v-if="!data.is_confirmed"
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-orange-500 hover:bg-orange-50"
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

  <P-Dialog v-model:visible="showFileViewer" modal header="Documento" class="w-[80vw] h-[90vh]">
    <iframe v-if="fileUrl" :src="fileUrl" class="w-full h-[80vh] border-none"></iframe>
  </P-Dialog>

  <PlayerManagement v-model="showEditPlayer" :player="editingPlayer" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useToast } from "primevue/usetoast";
import { useTeamStore } from "@stores/teams";
import { usePlayerStore } from "@stores/players";
import { useGroupStore } from "@stores/groups";
import { useTournamentStore } from "@stores/tournaments";
import { getFileUrl } from "@router/backend/services/file";
import * as teamService from "@router/backend/services/team";
import type { Team } from "@router/backend/services/team/types";
import type { Player } from "@router/backend/services/player/types";
import PlayerManagement from "@components/PlayerManagement.vue";

const toast = useToast();
const enabled = defineModel<boolean>();
const teamStore = useTeamStore();
const playerStore = usePlayerStore();
const groupStore = useGroupStore();
const tournamentStore = useTournamentStore();

const showTeamPlayers = ref(false);
const showFileViewer = ref(false);
const showDeleteConfirm = ref(false);
const showConfirmPlayer = ref(false);
const showRemovePlayer = ref(false);
const showEditTeam = ref(false);
const showEditPlayer = ref(false);
const viewOnlyMode = ref(false);
const selectedTeamId = ref("");
const selectedTeamName = ref("");
const teamPlayers = ref<unknown[]>([]);
const fileUrl = ref("");
const teamToDelete = ref<{ id: string; name: string } | null>(null);
const playerToAction = ref<{ id: string; name: string } | null>(null);
const editingTeam = ref<Team | undefined>(undefined);
const editingPlayer = ref<Player | undefined>(undefined);

watch(showEditTeam, (val) => {
  if (!val) {
    viewOnlyMode.value = false;
  }
});

function getTournamentName(tournamentId: string): string {
  const tournament = tournamentStore.tournaments.find(t => t.id === tournamentId);
  return tournament?.name || "-";
}

function hasGoalkeeper(team: Team): boolean {
  if (!team.players || team.players.length === 0) return false;
  return playerStore.players.some(p => team.players.includes(p.id) && p.is_goalkeeper);
}

function hasCoach(team: Team): boolean {
  return !!(team.main_coach || team.assistant_coach);
}

function deleteTeam(teamId: string, teamName: string) {
  const team = teamStore.teams.find(t => t.id === teamId);
  if (team && groupStore.groups.some(g => g.tournament === team.tournament)) {
    toast.add({ severity: "warn", summary: "Não permitido", detail: "Não é possível eliminar equipas quando já existem grupos criados.", life: 4000 });
    return;
  }
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

function viewTeam(team: Team) {
  editingTeam.value = team;
  viewOnlyMode.value = true;
  showEditTeam.value = true;
}

function promptEditTeam(team: Team) {
  editingTeam.value = team;
  viewOnlyMode.value = false;
  showEditTeam.value = true;
}

function onTeamSelect(event: { data: { id: string } }) {
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
    teamPlayers.value = data as unknown[];
  }
}

function viewFile(fileId: string) {
  fileUrl.value = getFileUrl(fileId);
  showFileViewer.value = true;
}

function promptEditPlayer(player: Player) {
  editingPlayer.value = player;
  showEditPlayer.value = true;
}

async function handlePlayerSaved() {
  await loadTeamPlayers();
  await playerStore.forceGetPlayers();
}

watch(showEditPlayer, (val) => {
  if (!val) {
    editingPlayer.value = undefined;
    handlePlayerSaved();
  }
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
    await loadTeamPlayers();
  }
  showConfirmPlayer.value = false;
  playerToAction.value = null;
}

function promptRemovePlayer(playerId: string, playerName: string) {
  const team = teamStore.teams.find(t => t.players.includes(playerId));
  if (team && groupStore.groups.some(g => g.tournament === team.tournament)) {
    toast.add({ severity: "warn", summary: "Não permitido", detail: "Não é possível remover jogadores quando já existem grupos criados.", life: 4000 });
    return;
  }
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
  await Promise.all([
    teamStore.getTeams(),
    groupStore.getGroups(),
    tournamentStore.getTournaments(),
    playerStore.forceGetPlayers(),
  ]);
});
</script>
