<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Equipa' : 'Editar Equipa'" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5" :style="{ maxHeight: '90vh' }">
    <div class="flex flex-col md:flex-row gap-4">
      <!-- Left: Basic Info -->
      <div class="w-full md:w-1/3 space-y-3">
        <h3 class="font-semibold text-stone-700">Informação Básica</h3>
        <P-FloatLabel class="field" variant="on">
          <P-InputText id="name" v-model="team.name" fluid />
          <label for="name">Nome</label>
        </P-FloatLabel>
        <P-FloatLabel class="field" variant="on">
          <P-Select id="tournament" v-model="team.tournament" :options="tournamentStore.tournaments"
            optionLabel="name" optionValue="id" fluid />
          <label for="tournament">Torneio</label>
        </P-FloatLabel>
        <P-FloatLabel class="field" variant="on">
          <P-InputText id="responsibleName" v-model="team.responsible_name" fluid />
          <label for="responsibleName">Nome do Responsável</label>
        </P-FloatLabel>
        <P-FloatLabel class="field" variant="on">
          <P-InputText id="responsibleEmail" v-model="team.responsible_email" type="email" fluid />
          <label for="responsibleEmail">Email do Responsável</label>
        </P-FloatLabel>
        <P-FloatLabel class="field" variant="on">
          <P-InputText id="responsiblePhone" v-model="team.responsible_phone" fluid />
          <label for="responsiblePhone">Telemóvel do Responsável</label>
        </P-FloatLabel>
      </div>

      <!-- Right: Staff & Players -->
      <div class="w-full md:w-2/3 space-y-4">
        <!-- Staff Section -->
        <div v-if="!creating" class="border border-stone-200 rounded-lg p-3">
          <h3 class="font-semibold text-stone-700 mb-2">Staff</h3>
          <div v-for="role in staffRoles" :key="role.field" class="flex items-center gap-2 mb-2">
            <span class="text-sm text-stone-600 w-32 shrink-0">{{ role.label }}</span>
            <P-Select v-model="(team as any)[role.field]" :options="staffOptions" optionLabel="name" optionValue="id"
              placeholder="Selecionar..." class="flex-1" showClear />
          </div>
        </div>

        <!-- Players Section -->
        <div v-if="!creating" class="border border-stone-200 rounded-lg p-3">
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold text-stone-700">Jogadores ({{ playerCount }})</h3>
            <P-Button label="Adicionar Jogador" icon="add" size="small" severity="info" @click="showAddPlayerDialog = true" />
          </div>
          <div class="max-h-48 overflow-y-auto space-y-1">
            <div v-for="player in teamPlayers" :key="player.id" 
                 class="flex items-center justify-between p-2 rounded bg-stone-50">
              <div class="flex items-center gap-2">
                <span class="text-sm">{{ player.name }}</span>
                <span class="text-xs text-stone-400">{{ player.age }} anos</span>
              </div>
              <P-Button icon="close" severity="danger" text rounded size="small" 
                @click="removePlayer(player.id)" v-tooltip.top="'Remover jogador'" />
            </div>
            <div v-if="teamPlayers.length === 0" class="text-sm text-stone-400 text-center py-4">
              Nenhum jogador atribuído
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <P-Button severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
      <P-Button @click="createOrUpdate">
        {{ creating ? "Criar" : "Alterar" }}
      </P-Button>
    </template>
  </P-Dialog>

  <!-- Add Player Dialog -->
  <P-Dialog v-model:visible="showAddPlayerDialog" modal header="Adicionar Jogador" class="w-11/12 md:w-6/12">
    <P-Select v-model="selectedPlayerId" :options="availablePlayers" optionLabel="name" optionValue="id"
      placeholder="Selecionar jogador..." fluid filter />
    <template #footer>
      <P-Button severity="secondary" @click="showAddPlayerDialog = false">Cancelar</P-Button>
      <P-Button :disabled="!selectedPlayerId" @click="addPlayer">Adicionar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useToast } from "primevue/usetoast";
import { CreateTeam, type Team } from "@router/backend/services/team/types";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { usePlayerStore } from "@stores/players";
import { useStaffStore } from "@stores/staff";
import { http } from "@router/backend/api";

const toast = useToast();
const enabled = defineModel<boolean>();
const props = defineProps<{
  team?: Team
}>();

const creating = computed(() => props.team === undefined);
const team = ref<Team | CreateTeam>(new CreateTeam());
const teamPlayers = ref<any[]>([]);
const showAddPlayerDialog = ref(false);
const selectedPlayerId = ref<string | null>(null);

const staffRoles = [
  { field: 'main_coach', label: 'Treinador Principal' },
  { field: 'assistant_coach', label: 'Treinador Adjunto' },
  { field: 'physiotherapist', label: 'Fisioterapeuta' },
  { field: 'first_deputy', label: '1º Substituto' },
  { field: 'second_deputy', label: '2º Substituto' },
];

const playerCount = computed(() => teamPlayers.value.length);

const playerStore = usePlayerStore();
const staffStore = useStaffStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const staffOptions = computed(() => staffStore.staff);

const availablePlayers = computed(() => {
  const currentIds = new Set(teamPlayers.value.map(p => p.id));
  return playerStore.players.filter(p => !currentIds.has(p.id));
});

watch(() => props.team, async (newTeam) => {
  if (newTeam) {
    team.value = newTeam;
    await loadTeamPlayers();
  } else {
    team.value = new CreateTeam();
    teamPlayers.value = [];
  }
});

onMounted(async () => {
  await Promise.all([
    playerStore.getPlayers(),
    staffStore.getStaff(),
  ]);
  if (!creating.value && props.team) {
    team.value = props.team;
    await loadTeamPlayers();
  }
});

async function loadTeamPlayers() {
  if (creating.value || !props.team?.id) return;
  try {
    const response = await http.get(`/teams/${props.team.id}/players`);
    if (response.status === 200) {
      teamPlayers.value = response.data;
    }
  } catch (e) {
    teamPlayers.value = [];
  }
}

async function addPlayer() {
  if (!selectedPlayerId.value || !props.team?.id) return;
  try {
    const response = await http.post(`/teams/${props.team.id}/players`, null, {
      params: { player_id: selectedPlayerId.value }
    });
    if (response.status === 200) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador adicionado", life: 3000 });
      await loadTeamPlayers();
      selectedPlayerId.value = null;
      showAddPlayerDialog.value = false;
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao adicionar jogador";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  }
}

async function removePlayer(playerId: string) {
  if (!props.team?.id) return;
  try {
    const response = await http.delete(`/teams/${props.team.id}/players/${playerId}`);
    if (response.status === 200) {
      toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador removido", life: 3000 });
      await loadTeamPlayers();
    }
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao remover jogador";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  }
}

async function createOrUpdate() {
  if (creating.value) {
    await create();
  } else {
    await update();
  }
}

async function create() {
  const result = await teamStore.createTeam(team.value as CreateTeam);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Equipa criada com sucesso", life: 3000 });
    close();
  }
}

async function update() {
  const result = await teamStore.updateTeam(props.team!.id, team.value as CreateTeam);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Equipa atualizada com sucesso", life: 3000 });
    close();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível atualizar a equipa", life: 3000 });
  }
}

function close() {
  enabled.value = false;
}
</script>

<style lang="scss" scoped>
.field {
  margin-top: 10px;
}
</style>
