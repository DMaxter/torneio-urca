<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Equipa' : 'Editar Equipa'">
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
import { computed, onMounted, ref, watch } from "vue";
import { useToast } from "primevue/usetoast";

import { CreateTeam, type Team } from "@router/backend/services/team/types";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";

const toast = useToast();
const enabled = defineModel<boolean>();
const props = defineProps<{
  team?: Team
}>();

const creating = computed(() => props.team === undefined);

const team = ref<Team | CreateTeam>(new CreateTeam());

watch(() => props.team, (newTeam) => {
  if (newTeam) {
    team.value = newTeam;
  } else {
    team.value = new CreateTeam();
  }
});

onMounted(() => {
  if (!creating.value) {
    team.value = props.team!
  }
});

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
