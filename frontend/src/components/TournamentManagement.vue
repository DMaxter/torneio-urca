<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Torneio' : 'Editar Torneio'">
    <P-FloatLabel id="content" variant="on">
      <P-InputText id="name" v-model="name" />
      <label for="name">Nome</label>
    </P-FloatLabel>
    <template #footer>
      <P-Button @click="createOrUpdate">{{ creating ? "Criar" : "Alterar" }}</P-Button>
      <P-Button @click="close">Cancelar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import type { Tournament } from "@router/backend/services/tournament/types";
import { useTournamentStore } from "@stores/tournaments";

const enabled = defineModel<boolean>();
const props = defineProps<{
  tournament?: Tournament
}>();

const creating = computed(() => props.tournament === undefined);

const name = ref("");

onMounted(() => {
  if (!creating.value) {
    name.value = props.tournament!.name
  }
});

const tournamentStore = useTournamentStore();

async function createOrUpdate() {
  if (creating.value) {
    await create();
  } else {
    await update();
  }
}

async function create() {
  console.log(await tournamentStore.createTournament({ name: name.value }));
}

async function update() {
  console.error("TODO");
}

function close() {
  enabled.value = false;
}
</script>

<style lang="scss" scoped>
#content {
  margin-top: 10px;
}
</style>
