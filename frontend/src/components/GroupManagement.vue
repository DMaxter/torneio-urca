<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Grupo' : 'Editar Grupo'">
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="name" v-model="group.name" />
      <label for="name">Nome</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select v-model="group.tournament" id="tournament" :options="tournamentStore.tournaments"
        optionLabel="name" optionValue="id" fluid />
      <label for="tournament">Torneio</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-MultiSelect id="teams" v-model="group.teams" :showToggleAll="false" filter
        :options="teamStore.teams" optionLabel="name" optionValue="id" fluid />
      <label for="teams">Equipas</label>
    </P-FloatLabel>
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

import { CreateGroup, type Group } from "@router/backend/services/group/types";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";

const toast = useToast();
const enabled = defineModel<boolean>();
const props = defineProps<{
  group?: Group
}>();

const creating = computed(() => props.group === undefined);

const group = ref<Group | CreateGroup>(new CreateGroup());

onMounted(() => {
  if (!creating.value) {
    group.value = props.group!
  }
});

const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

async function createOrUpdate() {
  if (creating.value) {
    await create();
  } else {
    await update();
  }
}

async function create() {
  const result = await groupStore.createGroup(group.value);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Grupo criado com sucesso", life: 3000 });
    close();
  }
}

async function update() {
  toast.add({ severity: "warn", summary: "Em desenvolvimento", detail: "Funcionalidade de edição ainda não disponível", life: 3000 });
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
