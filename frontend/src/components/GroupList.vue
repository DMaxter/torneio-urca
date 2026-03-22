<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Grupos" :style="{ width: '600px' }">
    <P-DataTable :value="groupStore.groups" striped-rows size="small">
      <P-Column field="name" header="Nome do Grupo">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>📋</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Equipas">
        <template #body="{ data }">
          <P-Tag :value="`${data.teams?.length || 0}`" severity="info" />
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button label="Atualizar" icon="pi pi-refresh" @click="groupStore.getGroups()" />
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useGroupStore } from "@stores/groups";

const enabled = defineModel<boolean>();
const groupStore = useGroupStore();

onMounted(async () => {
  await groupStore.getGroups();
});
</script>
