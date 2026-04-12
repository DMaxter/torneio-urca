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
    </P-DataTable>
    <template #footer>
      <div class="flex gap-2">
        <P-Button severity="danger" @click="promptDeleteAll" :disabled="groupStore.groups.length === 0 || deleting">
          <span class="material-symbols-outlined text-red-600">delete_sweep</span>
          Eliminar tudo
        </P-Button>
        <P-Button @click="groupStore.forceGetGroups()">
          <span class="material-symbols-outlined">sync</span>
          Atualizar
        </P-Button>
      </div>
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

  <P-Dialog v-model:visible="showDeleteAllDialog" modal header="Confirmar Eliminação" class="w-11/12 md:w-8/12">
    <p>Tem a certeza que deseja eliminar <strong>todos os grupos</strong> do sistema?</p>
    <p class="text-red-600 mt-2 text-sm">Esta ação não pode ser desfeita.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showDeleteAllDialog = false">Cancelar</P-Button>
      <P-Button severity="danger" :loading="deleting" @click="confirmDeleteAllGroups">Eliminar todos</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { useGameStore } from "@stores/games";
import type { Group } from "@router/backend/services/group/types";
import type { Team } from "@router/backend/services/team/types";

const toast = useToast();
const enabled = defineModel<boolean>();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const gameStore = useGameStore();


const showDeleteAllDialog = ref(false);
const showViewTeams = ref(false);

const deleting = ref(false);
const selectedGroupName = ref("");
const groupTeams = ref<Team[]>([]);

onMounted(async () => {
  await Promise.all([
    groupStore.getGroups(),
    teamStore.getTeams(),
    tournamentStore.getTournaments(),
    gameStore.getGames(),
  ]);
});

function getTournamentName(tournamentId: string): string {
  return tournamentStore.tournaments.find(t => t.id === tournamentId)?.name ?? "-";
}

function viewGroupTeams(event: { data: Group }) {
  const group = event.data;
  selectedGroupName.value = group.name;
  groupTeams.value = teamStore.teams.filter(t => group.teams.includes(t.id));
  showViewTeams.value = true;
}


function promptDeleteAll() {
  const tournamentIds = new Set(groupStore.groups.map(g => g.tournament));
  const hasGames = gameStore.games.some(g => tournamentIds.has(g.tournament));
  if (hasGames) {
    toast.add({ severity: "warn", summary: "Não permitido", detail: "Não é possível eliminar grupos quando já existem jogos gerados. Elimina primeiro os jogos.", life: 5000 });
    return;
  }
  showDeleteAllDialog.value = true;
}

async function confirmDeleteAllGroups() {
  deleting.value = true;
  let allOk = true;

  const groupsToDelete = [...groupStore.groups];
  for (const group of groupsToDelete) {
    const result = await groupStore.deleteGroup(group.id);
    if (!result.success) allOk = false;
  }

  deleting.value = false;
  showDeleteAllDialog.value = false;

  if (allOk) {
    await groupStore.getGroups();
    toast.add({ severity: "success", summary: "Sucesso", detail: "Todos os grupos eliminados", life: 3000 });
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Alguns grupos não foram eliminados", life: 3000 });
  }
}
</script>
