<template>
  <div class="max-w-[1200px] p-4 w-full mx-auto bg-stone-50 md:p-6">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-stone-900 mb-1 md:text-2xl">Gestão de Staff</h1>
        <p class="text-stone-500 text-sm">Adicionar, editar ou eliminar membros de staff</p>
      </div>
      <div class="flex gap-2">
        <P-Button text rounded @click="refreshStaff" v-tooltip.top="'Atualizar'">
          <span class="material-symbols-outlined text-orange-500">refresh</span>
        </P-Button>
        <P-Button label="Adicionar Staff" severity="success" @click="openCreateDialog" />
      </div>
    </div>

    <div class="bg-white border border-stone-300 rounded-xl overflow-hidden">
      <P-DataTable :value="staffStore.staff" striped-rows size="small" responsiveLayout="scroll">
        <P-Column header="Nome" field="name" />
        <P-Column header="Equipa" class="min-w-[150px]">
          <template #body="{ data }">
            {{ getTeamName(data) }}
          </template>
        </P-Column>
        <P-Column header="Tipo" field="staff_type">
          <template #body="{ data }">
            <P-Tag :value="getStaffTypeLabel(data.staff_type)" severity="info" />
          </template>
        </P-Column>
        <P-Column header="Data de Nascimento">
          <template #body="{ data }">
            {{ formatDate(data.birth_date) }}
          </template>
        </P-Column>
        <P-Column header="Nº Fiscal" field="fiscal_number" />
        <P-Column header="CC" class="w-[80px]">
          <template #body="{ data }">
            <P-Button v-if="data.citizen_card_file_id" size="small" severity="secondary" @click="viewFile(data.citizen_card_file_id)">
              <span class="material-symbols-outlined text-sm">picture_as_pdf</span>
            </P-Button>
            <span v-else class="text-stone-400">-</span>
          </template>
        </P-Column>
        <P-Column header="Ações" class="w-[120px]">
          <template #body="{ data }">
            <div class="flex gap-1">
              <P-Button text rounded size="small" @click="openEditDialog(data)" v-tooltip.top="'Editar'">
                <span class="material-symbols-outlined text-lg text-orange-500">edit</span>
              </P-Button>
              <P-Button text rounded size="small" @click="confirmDelete(data)" v-tooltip.top="'Eliminar'">
                <span class="material-symbols-outlined text-lg text-red-600">delete</span>
              </P-Button>
            </div>
          </template>
        </P-Column>
      </P-DataTable>
    </div>

    <!-- Create/Edit Dialog -->
    <P-Dialog v-model:visible="showFormDialog" modal :header="editingStaff ? 'Editar Staff' : 'Criar Staff'" class="w-11/12 md:w-6/12">
      <div class="space-y-3">
        <P-FloatLabel class="mt-3" variant="on">
          <P-Select id="staffTournament" v-model="staffForm.tournament_id" :options="tournamentOptions" optionLabel="label" optionValue="value" fluid @change="onTournamentChange" />
          <label for="staffTournament">Torneio *</label>
        </P-FloatLabel>
        <P-FloatLabel variant="on">
          <P-Select id="staffTeam" v-model="staffForm.team_id" :options="teamOptions" optionLabel="label" optionValue="value" fluid :disabled="!staffForm.tournament_id" />
          <label for="staffTeam">Equipa *</label>
        </P-FloatLabel>
        <P-FloatLabel variant="on">
          <P-Select id="staffType" v-model="staffForm.staff_type" :options="staffTypeOptions" optionLabel="label" optionValue="value" fluid />
          <label for="staffType">Tipo de Staff</label>
        </P-FloatLabel>
        <StaffMemberForm
          id="staff"
          legend="Dados Pessoais"
          v-model="staffForm.data"
          v-model:enabled="staffForm.enabled"
          v-model:files="staffForm.files"
        />
      </div>
      <template #footer>
        <P-Button severity="secondary" @click="showFormDialog = false">Cancelar</P-Button>
        <P-Button :loading="saving" @click="saveStaff">{{ editingStaff ? 'Atualizar' : 'Criar' }}</P-Button>
      </template>
    </P-Dialog>

    <!-- Delete Confirmation -->
    <P-Dialog v-model:visible="showDeleteDialog" modal header="Confirmar Eliminação" class="w-11/12 md:w-6/12">
      <p>Tem a certeza que deseja eliminar <strong>{{ deletingStaff?.name }}</strong>?</p>
      <template #footer>
        <P-Button severity="secondary" @click="showDeleteDialog = false">Cancelar</P-Button>
        <P-Button severity="danger" :loading="saving" @click="deleteStaff">Eliminar</P-Button>
      </template>
    </P-Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from "vue";
import { useToast } from "primevue/usetoast";
import { useStaffStore } from "@stores/staff";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { http } from "@router/backend/api";
import type { Staff } from "@router/backend/services/staff/types";
import { createAdminStaff, updateAdminStaff, type CreateAdminStaff } from "@router/backend/services/staff";
import { getFileUrl } from "@router/backend/services/file";
import { useDateFormatter } from "@/composables/useDateFormatter";
import { useApiErrorToast } from "@/composables/useApiErrorToast";
import { getStaffTypeLabel } from "@/utils";
import StaffMemberForm from "@components/forms/StaffMemberForm.vue";

const toast = useToast();
const staffStore = useStaffStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const { formatDate } = useDateFormatter();
const { handleApiError } = useApiErrorToast();

const showFormDialog = ref(false);
const showDeleteDialog = ref(false);
const editingStaff = ref<Staff | null>(null);
const deletingStaff = ref<Staff | null>(null);
const saving = ref(false);

const staffForm = reactive({
  team_id: null as string | null,
  tournament_id: null as string | null,
  staff_type: "Coach" as NonNullable<CreateAdminStaff["staff_type"]>,
  enabled: true,
  data: {
    name: "",
    birth_date: null as Date | null,
    address: "",
    place_of_birth: "",
    fiscal_number: "",
  },
  files: {
    citizenCard: null as File | null,
  },
});

const staffTypeOptions = [
  { label: "Treinador Principal", value: "Coach" },
  { label: "Treinador Adjunto", value: "AssistantCoach" },
  { label: "Fisioterapeuta", value: "Physiotherapist" },
  { label: "1º Delegado", value: "GameDeputy" },
];

const teamOptions = computed(() => {
  if (!staffForm.tournament_id) {
    return [{ label: "Selecione um torneio primeiro...", value: "" }];
  }
  return teamStore.teams
    .filter(t => t.tournament === staffForm.tournament_id)
    .map(t => ({ label: t.name, value: t.id }));
});

const tournamentOptions = computed(() => [
  { label: "Selecionar...", value: "" },
  ...tournamentStore.tournaments.map(t => ({ label: t.name, value: t.id })),
]);

function onTournamentChange() {
  staffForm.team_id = null;
}

function getTeamName(staff: Staff): string {
  return staff.team_name || "-";
}



async function refreshStaff() {
  await staffStore.forceGetStaff();
}

function openCreateDialog() {
  editingStaff.value = null;
  staffForm.team_id = null;
  staffForm.tournament_id = null;
  staffForm.staff_type = "Coach";
  staffForm.enabled = true;
  staffForm.data = {
    name: "",
    birth_date: null,
    address: "",
    place_of_birth: "",
    fiscal_number: "",
  };
  staffForm.files = { citizenCard: null };
  showFormDialog.value = true;
}

function openEditDialog(staff: Staff) {
  editingStaff.value = staff;
  const teamId = findTeamWithStaff(staff.id);
  const team = teamId ? teamStore.teams.find(t => t.id === teamId) : null;
  staffForm.team_id = teamId;
  staffForm.tournament_id = team?.tournament || "";
  staffForm.staff_type = staff.staff_type;
  staffForm.enabled = true;
  staffForm.data = {
    name: staff.name,
    birth_date: staff.birth_date ? new Date(staff.birth_date) : null,
    address: staff.address || "",
    place_of_birth: staff.place_of_birth || "",
    fiscal_number: staff.fiscal_number,
  };
  staffForm.files = { citizenCard: null };
  showFormDialog.value = true;
}

function findTeamWithStaff(staffId: string): string | null {
  const team = teamStore.teams.find(t =>
    t.main_coach === staffId ||
    t.assistant_coach === staffId ||
    t.physiotherapist === staffId ||
    t.first_deputy === staffId ||
    t.second_deputy === staffId
  );
  return team ? team.id : null;
}

function confirmDelete(staff: Staff) {
  deletingStaff.value = staff;
  showDeleteDialog.value = true;
}

function viewFile(fileId: string) {
  window.open(getFileUrl(fileId), "_blank");
}

function getStaffFieldForType(staffType: string): string | null {
  const mapping: Record<string, string> = {
    "Coach": "main_coach",
    "AssistantCoach": "assistant_coach",
    "Physiotherapist": "physiotherapist",
    "GameDeputy": "first_deputy",
  };
  return mapping[staffType] || null;
}

async function saveStaff() {
  if (!staffForm.team_id || !staffForm.tournament_id || !staffForm.data.name || !staffForm.data.birth_date) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Preencha os campos obrigatórios", life: 3000 });
    return;
  }

  if (!editingStaff.value && !staffForm.files.citizenCard) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Cartão de Cidadão é obrigatório", life: 3000 });
    return;
  }

  const staffField = getStaffFieldForType(staffForm.staff_type);
  if (staffField) {
    const team = teamStore.teams.find(t => t.id === staffForm.team_id);
    if (team) {
      const existingStaffId = team[staffField as keyof typeof team];
      if (existingStaffId && existingStaffId !== editingStaff.value?.id) {
        toast.add({ severity: "error", summary: "Erro", detail: `Esta função (${getStaffTypeLabel(staffForm.staff_type)}) já está atribuída na equipa`, life: 3000 });
        return;
      }
    }
  }

  saving.value = true;
  try {
    const staffData: CreateAdminStaff = {
      name: staffForm.data.name,
      birth_date: staffForm.data.birth_date?.toISOString() || "",
      staff_type: staffForm.staff_type,
      fiscal_number: staffForm.data.fiscal_number || "",
      team_id: staffForm.team_id,
      tournament_id: staffForm.tournament_id,
      address: staffForm.data.address,
      place_of_birth: staffForm.data.place_of_birth,
    };

    if (editingStaff.value) {
      const updateData = {
        name: staffData.name,
        birth_date: staffData.birth_date,
        staff_type: staffData.staff_type,
        fiscal_number: staffData.fiscal_number,
        team_id: staffForm.team_id || undefined,
        address: staffForm.data.address,
        place_of_birth: staffForm.data.place_of_birth,
      };
      await updateAdminStaff(editingStaff.value.id, updateData, staffForm.files.citizenCard || undefined);
      toast.add({ severity: "success", summary: "Sucesso", detail: "Staff atualizado", life: 3000 });
    } else {
      await createAdminStaff(staffData, staffForm.files.citizenCard || undefined);
      toast.add({ severity: "success", summary: "Sucesso", detail: "Staff criado", life: 3000 });
    }

    showFormDialog.value = false;
    await staffStore.getStaff();
    await teamStore.getTeams();
  } catch (e: unknown) {
    handleApiError(e, "Erro ao guardar staff");
  } finally {
    saving.value = false;
  }
}

async function deleteStaff() {
  if (!deletingStaff.value) return;
  saving.value = true;
  try {
    await http.delete(`/staff/${deletingStaff.value.id}`);
    toast.add({ severity: "success", summary: "Sucesso", detail: "Staff eliminado", life: 3000 });
    showDeleteDialog.value = false;
    await staffStore.getStaff();
  } catch (e: unknown) {
    handleApiError(e, "Erro ao eliminar staff");
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  await Promise.all([staffStore.getStaff(), teamStore.getTeams(), tournamentStore.getTournaments()]);
});
</script>

