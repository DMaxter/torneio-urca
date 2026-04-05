<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Jogo' : 'Editar Jogo'" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-FloatLabel class="field" variant="on">
      <P-Select v-model="game.tournament" id="tournament" :options="tournamentStore.tournaments"
        optionLabel="name" optionValue="id" fluid />
      <label for="tournament">Torneio</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-DatePicker id="date" v-model="game.scheduled_date" showTime hourFormat="24" fluid />
      <label for="date">Data e Hora do Jogo</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="home" v-model="homeTeam" filter :options="teamStore.teams" optionLabel="name" optionValue="id"
      fluid />
      <label for="home">Equipa da Casa</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="away" v-model="awayTeam" filter :options="teamStore.teams" optionLabel="name" optionValue="id"
      fluid />
      <label for="away">Equipa Visitante</label>
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

import { CreateGame, type Game, type GameCall } from "@router/backend/services/game/types";
import { useGameStore } from "@stores/games";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";

const toast = useToast();
const enabled = defineModel<boolean>();
const props = defineProps<{
  game?: Game
}>();

const creating = computed(() => props.game === undefined);

// Use only CreateGame type for the form
const game = ref<CreateGame>(new CreateGame());

// Computed properties for v-model to handle optional calls
const homeTeam = computed({
  get: () => game.value.home_call?.team ?? '',
  set: (val: string) => {
    if (!game.value.home_call) {
      game.value.home_call = { team: val };
    } else {
      game.value.home_call.team = val;
    }
  }
});

const awayTeam = computed({
  get: () => game.value.away_call?.team ?? '',
  set: (val: string) => {
    if (!game.value.away_call) {
      game.value.away_call = { team: val };
    } else {
      game.value.away_call.team = val;
    }
  }
});

onMounted(() => {
  if (props.game) {
    const g = props.game;
    // Convert Game to CreateGame format for the form
    game.value = {
      tournament: g.tournament,
      scheduled_date: g.scheduled_date,
      home_call: g.home_call ? { team: g.home_call.team } : null,
      away_call: g.away_call ? { team: g.away_call.team } : null,
      phase: g.phase,
      home_placeholder: g.home_placeholder,
      away_placeholder: g.away_placeholder,
    };
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
