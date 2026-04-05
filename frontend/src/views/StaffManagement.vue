<template>
  <div class="staff-management p-4 w-full mx-auto bg-stone-50 md:p-6">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-stone-900 mb-1 md:text-2xl">Gestão de Staff</h1>
        <p class="text-stone-500 text-sm">Adicionar, editar ou eliminar membros de staff</p>
      </div>
      <P-Button label="Adicionar Staff" icon="add" severity="success" @click="openCreateDialog" />
    </div>

    <div class="bg-white border border-stone-300 rounded-xl overflow-hidden">
      <P-DataTable :value="staffStore.staff" striped-rows size="small" responsiveLayout="scroll">
        <P-Column header="Nome" field="name" />
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
        <P-Column header="Ações" style="width: 120px">
          <template #body="{ data }">
            <div class="flex gap-1">
              <P-Button icon="edit" severity="info" text rounded size="small" @click="openEditDialog(data)" v-tooltip.top="'Editar'" />
              <P-Button icon="delete" severity="danger" text rounded size="small" @click="confirmDelete(data)" v-tooltip.top="'Eliminar'" />
            </div>
          </template>
        </P-Column>
      </P-DataTable>
    </div>

    <!-- Create/Edit Dialog -->
    <P-Dialog v-model:visible="showFormDialog" modal :header="editingStaff ? 'Editar Staff' : 'Criar Staff'" class="w-11/12 md:w-6/12">
      <div class="space-y-3">
        <P-FloatLabel variant="on">
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useStaffStore } from "@stores/staff";
import { http } from "@router/backend/api";

const router = useRouter();
const toast = useToast();
const staffStore = useStaffStore();

const showFormDialog = ref(false);
const showDeleteDialog = ref(false);
const editingStaff = ref<any>(null);
const deletingStaff = ref<any>(null);
const saving = ref(false);

const staffForm = ref({
  name: "",
  birth_date: null as Date | null,
  staff_type: "",
  fiscal_number: "",
});

const staffTypeOptions = [
  { label: "Treinador Principal", value: "main_coach" },
  { label: "Treinador Adjunto", value: "assistant_coach" },
  { label: "Fisioterapeuta", value: "physiotherapist" },
  { label: "1º Substituto", value: "first_deputy" },
  { label: "2º Substituto", value: "second_deputy" },
];

function getStaffTypeLabel(type: string): string {
  const opt = staffTypeOptions.find(o => o.value === type);
  return opt ? opt.label : type;
}

function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleDateString("pt-PT");
}

function openCreateDialog() {
  editingStaff.value = null;
  staffForm.value = { name: "", birth_date: null, staff_type: "", fiscal_number: "" };
  showFormDialog.value = true;
}

function openEditDialog(staff: any) {
  editingStaff.value = staff;
  staffForm.value = {
    name: staff.name,
    birth_date: staff.birth_date ? new Date(staff.birth_date) : null,
    staff_type: staff.staff_type,
    fiscal_number: staff.fiscal_number,
  };
  showFormDialog.value = true;
}

function confirmDelete(staff: any) {
  deletingStaff.value = staff;
  showDeleteDialog.value = true;
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
      // For now, delete and recreate since there's no PUT endpoint
      await http.delete(`/staff/${editingStaff.value.id}`);
    }
    await http.post("/staff", payload);

    toast.add({ severity: "success", summary: "Sucesso", detail: editingStaff.value ? "Staff atualizado" : "Staff criado", life: 3000 });
    showFormDialog.value = false;
    await staffStore.getStaff();
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao guardar staff";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
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
  } catch (e: any) {
    const msg = e.response?.data?.detail?.error || "Erro ao eliminar staff";
    toast.add({ severity: "error", summary: "Erro", detail: msg, life: 3000 });
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  await staffStore.getStaff();
});
</script>

<style lang="scss" scoped>
.staff-management {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
