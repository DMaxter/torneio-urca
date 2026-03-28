<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Grupos" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-DataTable :value="groupStore.groups" striped-rows size="small" responsiveLayout="scroll" selectionMode="single" @rowSelect="viewGroupTeams">
      <P-Column field="name" header="Nome do Grupo">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>📋</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Torneio" class="w-6rem md:w-auto">
        <template #body="{ data }">
          <span class="text-sm text-muted">{{ getTournamentName(data.tournament) }}</span>
        </template>
      </P-Column>
      <P-Column header="Equipas" class="w-5rem md:w-auto">
        <template #body="{ data }">
          <P-Tag :value="`${data.teams?.length || 0}`" severity="info" />
        </template>
      </P-Column>
      <P-Column header="Editar" class="w-3rem">
        <template #body="{ data }">
          <span
            class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-blue-600 hover:bg-blue-50"
            @click.stop="promptEditGroup(data)"
            v-tooltip.top="'Editar grupo'"
          >
            edit
          </span>
        </template>
      </P-Column>
      <P-Column header="Eliminar" class="w-3rem">
        <template #body="{ data }">
          <span
            class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
            @click.stop="promptDeleteGroup(data.id, data.name)"
            v-tooltip.top="'Eliminar grupo'"
          >
            delete
          </span>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="groupStore.getGroups()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showViewTeams" modal :header="`Equipas - ${selectedGroupName}`" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-DataTable :value="groupTeams" striped-rows size="small" responsiveLayout="scroll">
      <P-Column field="name" header="Nome da Equipa">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>⚽</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Responsável" class="w-auto">
        <template #body="{ data }">
          <span class="text-muted text-sm">{{ data.responsible_name }}</span>
        </template>
      </P-Column>
      <P-Column header="Jogadores" class="w-5rem">
        <template #body="{ data }">
          <P-Tag :value="`${data.players?.length || 0}`" :severity="(data.players?.length || 0) >= 5 ? 'success' : 'danger'" />
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="showViewTeams = false">Fechar</P-Button>
    </template>
  </P-Dialog>

  <GroupManagement v-model="showEditDialog" :group="editingGroup" />

  <P-Dialog v-model:visible="showDeleteDialog" modal header="Confirmar Eliminação" class="w-11/12 md:w-8/12">
    <p>Tem a certeza que deseja eliminar o grupo <strong>{{ groupToDelete?.name }}</strong>?</p>
    <template #footer>
      <P-Button severity="secondary" @click="showDeleteDialog = false">Cancelar</P-Button>
      <P-Button severity="danger" @click="confirmDeleteGroup">Eliminar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import type { Group } from "@router/backend/services/group/types";

const toast = useToast();
const enabled = defineModel<boolean>();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const showEditDialog = ref(false);
const showDeleteDialog = ref(false);
const showViewTeams = ref(false);
const editingGroup = ref<Group | undefined>(undefined);
const groupToDelete = ref<{ id: string; name: string } | null>(null);
const selectedGroupName = ref("");
const groupTeams = ref<any[]>([]);

onMounted(async () => {
  await groupStore.getGroups();
  await teamStore.getTeams();
  await tournamentStore.getTournaments();
});

function getTournamentName(tournamentId: string): string {
  const tournament = tournamentStore.tournaments.find(t => t.id === tournamentId);
  return tournament?.name || "-";
}

function viewGroupTeams(event: any) {
  const group = event.data as Group;
  selectedGroupName.value = group.name;
  const teamIds = group.teams || [];
  groupTeams.value = teamStore.teams.filter(t => teamIds.includes(t.id));
  showViewTeams.value = true;
}

function promptEditGroup(group: Group) {
  editingGroup.value = group;
  showEditDialog.value = true;
}

function promptDeleteGroup(groupId: string, groupName: string) {
  groupToDelete.value = { id: groupId, name: groupName };
  showDeleteDialog.value = true;
}

async function confirmDeleteGroup() {
  if (!groupToDelete.value) return;
  const result = await groupStore.deleteGroup(groupToDelete.value.id);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Grupo eliminado", life: 3000 });
    showDeleteDialog.value = false;
    groupToDelete.value = null;
  }
}
</script>
