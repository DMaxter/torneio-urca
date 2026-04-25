<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Anúncio' : 'Editar Anúncio'" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <div class="mt-3 flex flex-col gap-3">
      <P-FloatLabel id="titleLabel" variant="on">
        <P-InputText id="title" v-model="title" fluid />
        <label for="title">Título</label>
      </P-FloatLabel>
      <P-FloatLabel id="contentLabel" variant="on">
        <P-Textarea id="content" v-model="content" rows="3" fluid />
        <label for="content">Conteúdo</label>
      </P-FloatLabel>
      <div class="flex align-items-center gap-2">
        <P-Checkbox v-model="isActive" binary input-id="isActive" />
        <label for="isActive">Ativo</label>
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
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useToast } from "primevue/usetoast";

import type { Announcement } from "@router/backend/services/announcement/types";
import * as announcementService from "@router/backend/services/announcement";

const toast = useToast();
const enabled = defineModel<boolean>();
const props = defineProps<{
  announcement?: Announcement
}>();

const emit = defineEmits<{
  (e: "saved"): void;
}>();

const creating = computed(() => props.announcement === undefined);

const title = ref("");
const content = ref("");
const isActive = ref(true);

onMounted(() => {
  if (!creating.value) {
    title.value = props.announcement!.title;
    content.value = props.announcement!.content;
    isActive.value = props.announcement!.is_active;
  }
});

async function createOrUpdate() {
  if (creating.value) {
    await create();
  } else {
    await update();
  }
}

async function create() {
  const result = await announcementService.createAnnouncement({
    title: title.value,
    content: content.value,
    is_active: isActive.value,
  });
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Anúncio criado com sucesso", life: 3000 });
    emit("saved");
    close();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível criar o anúncio", life: 3000 });
  }
}

async function update() {
  const result = await announcementService.updateAnnouncement(props.announcement!.id, {
    title: title.value,
    content: content.value,
    is_active: isActive.value,
  });
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Anúncio atualizado com sucesso", life: 3000 });
    emit("saved");
    close();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível atualizar o anúncio", life: 3000 });
  }
}

function close() {
  enabled.value = false;
}
</script>
