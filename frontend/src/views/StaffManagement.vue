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
          <P-InputText id="staffName" v-model="staffForm.name" fluid />
          <label for="staffName">Nome</label>
        </P-FloatLabel>
        <P-FloatLabel variant="on">
          <P-DatePicker id="staffBirth" v-model="staffForm.birth_date" dateFormat="yy-mm-dd" fluid />
          <label for="staffBirth">Data de Nascimento</label>
        </P-FloatLabel>
        <P-FloatLabel variant="on">
          <P-Select id="staffType" v-model="staffForm.staff_type" :options="staffTypeOptions" optionLabel="label" optionValue="value" fluid />
          <label for="staffType">Tipo de Staff</label>
        </P-FloatLabel>
        <P-FloatLabel variant="on">
          <P-InputText id="staffFiscal" v-model="staffForm.fiscal_number" fluid />
          <label for="staffFiscal">Nº Fiscal</label>
        </P-FloatLabel>
        <P-FloatLabel variant="on">
          <P-Select id="staffTeam" v-model="staffForm.selected_team_id" :options="teamOptions" optionLabel="label" optionValue="value" fluid />
          <label for="staffTeam">Equipa</label>
        </P-FloatLabel>
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
import { ref, onMounted, computed } from "vue";
import { useToast } from "primevue/usetoast";
import { useStaffStore } from "@stores/staff";
import { useTeamStore } from "@stores/teams";
import { http } from "@router/backend/api";
import type { Staff } from "@router/backend/services/staff/types";
import { useDateFormatter } from "@/composables/useDateFormatter";
import { useApiErrorToast } from "@/composables/useApiErrorToast";
import { getStaffTypeLabel } from "@/utils";

const toast = useToast();
const staffStore = useStaffStore();
const teamStore = useTeamStore();
const { formatDate } = useDateFormatter();
const { handleApiError } = useApiErrorToast();

const showFormDialog = ref(false);
const showDeleteDialog = ref(false);
const editingStaff = ref<Staff | null>(null);
const deletingStaff = ref<Staff | null>(null);
const saving = ref(false);

const staffForm = ref({
  name: "",
  birth_date: null as Date | null,
  staff_type: "",
  fiscal_number: "",
  selected_team_id: null as string | null,
});

const staffTypeOptions = [
  { label: "Treinador Principal", value: "Coach" },
  { label: "Treinador Adjunto", value: "AssistantCoach" },
  { label: "Fisioterapeuta", value: "Physiotherapist" },
  { label: "1º Delegado", value: "GameDeputy" },
];

const teamOptions = computed(() => [
  { label: "Sem Equipa", value: "" },
  ...teamStore.teams.map(t => ({ label: t.name, value: t.id }))
]);


function getTeamName(staff: Staff): string {
  return staff.team_name || "-";
}



async function refreshStaff() {
  await staffStore.forceGetStaff();
}

function openCreateDialog() {
  editingStaff.value = null;
  staffForm.value = { name: "", birth_date: null, staff_type: "", fiscal_number: "", selected_team_id: null };
  showFormDialog.value = true;
}

function openEditDialog(staff: Staff) {
  editingStaff.value = staff;
  const teamId = findTeamWithStaff(staff.id);
  staffForm.value = {
    name: staff.name,
    birth_date: staff.birth_date ? new Date(staff.birth_date) : null,
    staff_type: staff.staff_type,
    fiscal_number: staff.fiscal_number,
    selected_team_id: teamId,
  };
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
  if (!staffForm.value.name || !staffForm.value.staff_type) {
    toast.add({ severity: "warn", summary: "Aviso", detail: "Preencha os campos obrigatórios", life: 3000 });
    return;
  }

  saving.value = true;
  try {
    const payload = {
      name: staffForm.value.name,
      birth_date: staffForm.value.birth_date?.toISOString() || new Date().toISOString(),
      staff_type: staffForm.value.staff_type,
      fiscal_number: staffForm.value.fiscal_number || "",
    };

    if (editingStaff.value) {
      await http.put(`/staff/${editingStaff.value.id}`, payload);

      const staffField = getStaffFieldForType(editingStaff.value.staff_type);
      if (staffField) {
        const oldTeam = teamStore.teams.find(t => t[staffField as keyof typeof t] === editingStaff.value!.id);
        if (oldTeam && oldTeam.id !== staffForm.value.selected_team_id) {
          await http.patch(`/teams/${oldTeam.id}/staff/${staffField}?staff_id=`);
        }
      }

      if (staffForm.value.selected_team_id) {
        const staffField = getStaffFieldForType(staffForm.value.staff_type);
        if (staffField) {
          await http.patch(`/teams/${staffForm.value.selected_team_id}/staff/${staffField}?staff_id=${editingStaff.value.id}`);
        }
      }

      toast.add({ severity: "success", summary: "Sucesso", detail: "Staff atualizado", life: 3000 });
    } else {
      const { data } = await http.post("/staff", payload);
      const newStaffId = (data as { id: string }).id;

      if (staffForm.value.selected_team_id) {
        const staffField = getStaffFieldForType(staffForm.value.staff_type);
        if (staffField) {
          await http.patch(`/teams/${staffForm.value.selected_team_id}/staff/${staffField}?staff_id=${newStaffId}`);
        }
      }

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
  await Promise.all([staffStore.getStaff(), teamStore.getTeams()]);
});
</script>

