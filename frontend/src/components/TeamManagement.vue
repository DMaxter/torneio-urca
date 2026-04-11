<template>
  <P-Dialog v-model:visible="enabled" modal :header="viewMode ? 'Ver Equipa' : (creating ? 'Criar Equipa' : 'Editar Equipa')" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5" :style="{ maxHeight: '90vh' }">
    <div class="flex flex-col md:flex-row gap-4">
      <!-- Left: Basic Info -->
      <div class="w-full md:w-1/3 space-y-3">
        <h3 class="font-semibold text-stone-700">Informação Básica</h3>
        <P-FloatLabel class="field" variant="on">
          <P-InputText id="name" v-model="teamForm.name" :disabled="viewMode" fluid />
          <label for="name">Nome</label>
        </P-FloatLabel>
        <P-FloatLabel class="field" variant="on">
          <P-Select id="tournament" v-model="teamForm.tournament" :options="tournamentStore.tournaments"
            optionLabel="name" optionValue="id" :disabled="viewMode" fluid />
          <label for="tournament">Torneio</label>
        </P-FloatLabel>
        
        <h3 class="font-semibold text-stone-700 mt-4">Responsável</h3>
        <P-FloatLabel class="field" variant="on">
          <P-InputText id="responsibleName" v-model="teamForm.responsible_name" :disabled="viewMode" fluid />
          <label for="responsibleName">Nome do Responsável</label>
        </P-FloatLabel>
        <P-FloatLabel class="field" variant="on">
          <P-InputText id="responsibleEmail" v-model="teamForm.responsible_email" type="email" :disabled="viewMode" fluid />
          <label for="responsibleEmail">Email do Responsável</label>
        </P-FloatLabel>
        <P-FloatLabel class="field" variant="on">
          <P-InputText id="responsiblePhone" v-model="teamForm.responsible_phone" :disabled="viewMode" fluid />
          <label for="responsiblePhone">Telemóvel do Responsável</label>
        </P-FloatLabel>
      </div>

      <!-- Right: Staff & Players -->
      <div class="w-full md:w-2/3 space-y-4">
        <!-- Staff Section -->
        <div v-if="!creating" class="border border-stone-200 rounded-lg p-3">
          <h3 class="font-semibold text-stone-700 mb-2">Staff</h3>
          <div v-if="viewMode" class="space-y-2">
            <div v-for="staff in teamStaffDetails" :key="staff.id" class="flex items-center justify-between p-2 rounded bg-stone-50">
              <div class="flex-1">
                <span class="text-sm font-medium">{{ staff.name }}</span>
                <span class="text-xs text-stone-400 ml-2">({{ getStaffTypeLabel(staff.staff_type) }})</span>
              </div>
              <div class="flex gap-2">
                <P-Button v-if="staff.citizen_card_file_id" size="small" severity="secondary" @click="viewFile(staff.citizen_card_file_id)">
                  <span class="material-symbols-outlined text-sm">picture_as_pdf</span>
                  CC
                </P-Button>
                <P-Button v-if="staff.proof_of_residency_file_id" size="small" severity="secondary" @click="viewFile(staff.proof_of_residency_file_id)">
                  <span class="material-symbols-outlined text-sm">picture_as_pdf</span>
                  Morada
                </P-Button>
              </div>
            </div>
            <div v-if="teamStaffDetails.length === 0" class="text-sm text-stone-400">
              Nenhum staff atribuído
            </div>
          </div>
          <div v-else>
            <div v-for="role in staffRoles" :key="role.field" class="flex items-center gap-2 mb-2">
              <span class="text-sm text-stone-600 w-32 shrink-0">{{ role.label }}</span>
              <P-Select v-model="(teamForm as unknown as Record<string, unknown>)[role.field]" :options="staffOptions" optionLabel="name" optionValue="id"
                placeholder="Selecionar..." class="flex-1" showClear />
            </div>
          </div>
        </div>

        <!-- Players Section -->
        <div v-if="!creating" class="border border-stone-200 rounded-lg p-3">
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold text-stone-700">Jogadores ({{ playerCount }})</h3>
            <P-Button v-if="!viewMode" label="Adicionar Jogador" size="small" severity="info" @click="showAddPlayerDialog = true">
              <span class="material-symbols-outlined">person_add</span>
            </P-Button>
          </div>
          <div class="max-h-48 overflow-y-auto space-y-1">
            <div v-for="player in teamPlayers" :key="player.id" 
                 class="flex items-center justify-between p-2 rounded bg-stone-50">
              <div class="flex items-center gap-2 flex-1">
                <span class="text-sm">{{ player.name }}</span>
                <span class="text-xs text-stone-400">{{ calculateAge(player.birth_date) }} anos</span>
              </div>
              <div class="flex gap-1 text-xs text-stone-500">
                <span v-if="player.address" class="text-xs text-stone-400">📍</span>
                <span v-if="player.place_of_birth" class="text-xs text-stone-400">🏠</span>
              </div>
              <div v-if="viewMode" class="flex gap-1">
                <P-Button v-if="player.citizen_card_file_id" size="small" severity="secondary" @click="viewFile(player.citizen_card_file_id)">
                  <span class="material-symbols-outlined text-sm">picture_as_pdf</span>
                  CC
                </P-Button>
                <P-Button v-if="player.proof_of_residency_file_id" size="small" severity="secondary" @click="viewFile(player.proof_of_residency_file_id)">
                  <span class="material-symbols-outlined text-sm">picture_as_pdf</span>
                  Morada
                </P-Button>
                <P-Button v-if="player.authorization_file_id" size="small" severity="secondary" @click="viewFile(player.authorization_file_id)">
                  <span class="material-symbols-outlined text-sm">picture_as_pdf</span>
                  Auth
                </P-Button>
              </div>
              <P-Button v-else severity="danger" text rounded size="small" @click="removePlayer(player.id)" v-tooltip.top="'Remover jogador'">
                <span class="material-symbols-outlined text-base text-red-600">close</span>
              </P-Button>
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
        Fechar
      </P-Button>
      <P-Button v-if="!viewMode" @click="createOrUpdate">
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
import { type Player } from "@router/backend/services/player/types";
import { type Staff } from "@router/backend/services/staff/types";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { usePlayerStore } from "@stores/players";
import { useStaffStore } from "@stores/staff";
import { http } from "@router/backend/api";
import { calculateAge } from "@/utils";

const toast = useToast();
const enabled = defineModel<boolean>();
const props = defineProps<{
  team?: Team
  viewOnly?: boolean
}>();

const creating = computed(() => props.team === undefined);
const viewMode = computed(() => props.viewOnly === true);
const teamForm = ref<Team | CreateTeam>(new CreateTeam());
const teamPlayers = ref<Player[]>([]);
const showAddPlayerDialog = ref(false);
const selectedPlayerId = ref<string | null>(null);

const staffRoles = [
  { field: 'main_coach', label: 'Treinador Principal' },
  { field: 'assistant_coach', label: 'Treinador Adjunto' },
  { field: 'physiotherapist', label: 'Fisioterapeuta' },
  { field: 'first_deputy', label: '1º Substituto' },
  { field: 'second_deputy', label: '2º Substituto' },
];

function getStaffTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    'Coach': 'Treinador Principal',
    'AssistantCoach': 'Treinador Adjunto',
    'Physiotherapist': 'Fisioterapeuta',
    'GameDeputy': 'Delegado',
  };
  return labels[type] || type;
}

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

const teamStaffDetails = computed(() => {
  if (!props.team) return [];
  const staff: Staff[] = [];
  const fields = ['main_coach', 'assistant_coach', 'physiotherapist', 'first_deputy', 'second_deputy'];
  for (const field of fields) {
    const staffId = (props.team as unknown as Record<string, string>)[field];
    if (staffId) {
      const found = staffStore.staff.find(s => s.id === staffId);
      if (found) staff.push(found);
    }
  }
  return staff;
});

watch(() => props.team, async (newTeam) => {
  if (newTeam) {
    teamForm.value = newTeam;
    await loadTeamPlayers();
  } else {
    teamForm.value = new CreateTeam();
    teamPlayers.value = [];
  }
});

onMounted(async () => {
  await Promise.all([
    playerStore.getPlayers(),
    staffStore.getStaff(),
  ]);
  if (!creating.value && props.team) {
    teamForm.value = props.team;
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
  } catch {
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
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: { error?: string } } } };
    const msg = err.response?.data?.detail?.error || "Erro ao adicionar jogador";
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
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: { error?: string } } } };
    const msg = err.response?.data?.detail?.error || "Erro ao remover jogador";
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
  const result = await teamStore.createTeam(teamForm.value as CreateTeam);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Equipa criada com sucesso", life: 3000 });
    close();
  }
}

async function update() {
  const result = await teamStore.updateTeam(props.team!.id, teamForm.value as CreateTeam);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Equipa atualizada com sucesso", life: 3000 });
    close();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível atualizar a equipa", life: 3000 });
  }
}

async function viewFile(fileId: string) {
  try {
    const response = await http.get(`/files/${fileId}`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `file_${fileId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível descargar o ficheiro", life: 3000 });
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
