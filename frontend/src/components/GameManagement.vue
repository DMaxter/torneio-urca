<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Jogo' : 'Editar Jogo'">
    <P-FloatLabel class="field" variant="on">
      <P-Select v-model="game.tournament" id="tournament" :options="tournamentStore.tournaments"
        optionLabel="name" optionValue="id" fluid />
      <label for="tournament">Torneio</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-DatePicker id="date" v-model="game.scheduled_date" showTime hourFormat="24" />
      <label for="date">Data e Hora do Jogo</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="home" v-model="game.home_call.team" filter :options="teamStore.teams" optionLabel="name" optionValue="id"
      fluid />
      <label for="home">Equipa da Casa</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="away" v-model="game.away_call.team" filter :options="teamStore.teams" optionLabel="name" optionValue="id"
      fluid />
      <label for="away">Equipa Visitante</label>
    </P-FloatLabel>
    <template #footer>
      <P-Button @click="createOrUpdate">{{ creating ? "Criar" : "Alterar" }}</P-Button>
      <P-Button @click="close">Cancelar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useToast } from "primevue/usetoast";

import { CreateGame, type Game } from "@router/backend/services/game/types";
import { useGameStore } from "@stores/games";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";

const toast = useToast();
const enabled = defineModel<boolean>();
const props = defineProps<{
  game?: Game
}>();

const creating = computed(() => props.game === undefined);

const game = ref<Game | CreateGame>(new CreateGame());

onMounted(() => {
  if (!creating.value) {
    game.value = props.game!
  }
});

const gameStore = useGameStore();
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
  const result = await gameStore.createGame(game.value);
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Jogo criado com sucesso", life: 3000 });
    close();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: result.content || "Erro ao criar jogo", life: 3000 });
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
