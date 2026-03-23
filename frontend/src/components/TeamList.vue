<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Equipas" :style="{ width: '700px' }">
    <P-DataTable :value="teamStore.teams" striped-rows size="small">
      <P-Column field="name" header="Nome da Equipa">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <span>⚽</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Responsável">
        <template #body="{ data }">
          <span class="text-muted">{{ data.responsible_name }}</span>
        </template>
      </P-Column>
      <P-Column header="Jogadores">
        <template #body="{ data }">
          <P-Tag :value="`${data.players?.length || 0}`" severity="info" />
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button label="Atualizar" @click="teamStore.getTeams()">
        <span class="material-symbols-outlined">sync</span>
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTeamStore } from "@stores/teams";

const enabled = defineModel<boolean>();
const teamStore = useTeamStore();

onMounted(async () => {
  await teamStore.getTeams();
});
</script>
