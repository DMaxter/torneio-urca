<template>
  <P-Dialog v-model:visible="enabled" modal header="Criar Jogador" :style="{ width: '450px' }">
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="name" v-model="player.name" />
      <label for="name">Nome</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-DatePicker id="birthDate" v-model="player.birth_date" fluid dateFormat="dd/mm/yy" />
      <label for="birthDate">Data de Nascimento</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="tournament" v-model="player.tournament" :options="tournamentStore.tournaments"
        optionLabel="name" optionValue="id" @change="onTournamentChange" fluid />
      <label for="tournament">Torneio</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="team" v-model="player.team" :options="availableTeams" optionLabel="name" optionValue="id" fluid />
      <label for="team">Equipa</label>
    </P-FloatLabel>
    <div class="field">
      <P-Checkbox v-model="player.is_federated" :binary="true" inputId="federated" />
      <label for="federated" class="ml-2">É federado?</label>
    </div>
    <P-FloatLabel v-if="player.is_federated" class="field" variant="on">
      <P-InputText id="federationTeam" v-model="player.federation_team" />
      <label for="federationTeam">Equipa Federada</label>
    </P-FloatLabel>
    <template #footer>
      <P-Button label="Criar" icon="pi pi-check" @click="create" :loading="loading" />
      <P-Button label="Cancelar" severity="secondary" @click="close" />
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useToast } from "primevue/usetoast";

import { usePlayerStore } from "@stores/players";
import { useTournamentStore } from "@stores/tournaments";
import { useTeamStore } from "@stores/teams";
import { CreateAdminPlayer } from "@router/backend/services/player/types";

const toast = useToast();
const enabled = defineModel<boolean>();
const loading = ref(false);

const playerStore = usePlayerStore();
const tournamentStore = useTournamentStore();
const teamStore = useTeamStore();

const player = ref(new CreateAdminPlayer());

const availableTeams = computed(() => {
  if (!player.value.tournament) return [];
  return teamStore.teams.filter(t => t.tournament === player.value.tournament);
});

watch(enabled, async (newVal) => {
  if (newVal) {
    player.value = new CreateAdminPlayer();
    if (tournamentStore.tournaments.length === 0) {
      await tournamentStore.getTournaments();
    }
    if (teamStore.teams.length === 0) {
      await teamStore.getTeams();
    }
  }
});

function onTournamentChange() {
  player.value.team = "";
}

async function create() {
  if (!player.value.name || !player.value.birth_date || !player.value.team || !player.value.tournament) {
    toast.add({ severity: "warn", summary: "Campos obrigatórios", detail: "Preencha todos os campos", life: 3000 });
    return;
  }

  loading.value = true;
  const result = await playerStore.createAdminPlayer(player.value);
  loading.value = false;

  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogador criado com sucesso", life: 3000 });
    close();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: result.content || "Erro ao criar jogador", life: 3000 });
  }
}

function close() {
  enabled.value = false;
}
</script>

<style lang="scss" scoped>
.field {
  margin-top: 15px;
}

.ml-2 {
  margin-left: 8px;
}
</style>
