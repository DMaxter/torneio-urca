<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Anúncios" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-DataTable :value="announcements" striped-rows size="small">
      <P-Column field="title" header="Título">
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <span>📢</span>
            <span class="font-medium">{{ data.title }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column field="content" header="Conteúdo">
        <template #body="{ data }">
          <span class="text-stone-600">{{ data.content }}</span>
        </template>
      </P-Column>
      <P-Column header="Estado" class="w-24">
        <template #body="{ data }">
          <P-Tag :value="data.is_active ? 'Ativo' : 'Inativo'" :severity="data.is_active ? 'success' : 'secondary'" />
        </template>
      </P-Column>
      <P-Column header="Ações" class="w-5rem">
        <template #body="{ data }">
          <div class="flex items-center gap-1">
            <span
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-orange-500 hover:bg-orange-50"
              @click.stop="editAnnouncement(data)"
              v-tooltip.top="'Editar anúncio'"
            >edit</span>
            <span
              class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
              @click.stop="promptDelete(data)"
              v-tooltip.top="'Eliminar anúncio'"
            >delete</span>
          </div>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="refresh">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showDeleteConfirm" modal header="Confirmar Eliminação" class="w-11/12 md:w-6/12">
    <p>Tem a certeza que deseja eliminar o anúncio <strong>{{ announcementToDelete?.title }}</strong>?</p>
    <p class="text-red-600 mt-2 text-sm">Esta ação não pode ser desfeita.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showDeleteConfirm = false">Cancelar</P-Button>
      <P-Button severity="danger" :loading="deleting" @click="confirmDelete">Eliminar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";

import type { Announcement } from "@router/backend/services/announcement/types";
import * as announcementService from "@router/backend/services/announcement";

const emit = defineEmits<{
  (e: "edit-announcement", announcement: Announcement): void;
  (e: "saved"): void;
}>();

function editAnnouncement(announcement: Announcement) {
  emit("edit-announcement", announcement);
}

const enabled = defineModel<boolean>();
const toast = useToast();

const announcements = ref<Announcement[]>([]);

const showDeleteConfirm = ref(false);
const deleting = ref(false);
const announcementToDelete = ref<Announcement | null>(null);

async function refresh() {
  try {
    const response = await announcementService.getAnnouncements();
    if (response.status === 200 && Array.isArray(response.data)) {
      announcements.value = response.data as Announcement[];
    }
  } catch {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível carregar os anúncios", life: 3000 });
  }
}

function promptDelete(announcement: Announcement) {
  announcementToDelete.value = announcement;
  showDeleteConfirm.value = true;
}

async function confirmDelete() {
  if (!announcementToDelete.value) return;
  deleting.value = true;
  const result = await announcementService.deleteAnnouncement(announcementToDelete.value.id);
  deleting.value = false;
  showDeleteConfirm.value = false;
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Anúncio eliminado", life: 3000 });
    await refresh();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível eliminar o anúncio", life: 3000 });
  }
  announcementToDelete.value = null;
}

onMounted(async () => {
  await refresh();
});
</script>