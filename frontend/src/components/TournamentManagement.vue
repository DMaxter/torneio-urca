<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Torneio' : 'Editar Torneio'" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-FloatLabel id="firstLabel" variant="on">
      <P-InputText id="name" v-model="name" fluid />
      <label for="name">Nome</label>
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

import type { Tournament } from "@router/backend/services/tournament/types";
import { useTournamentStore } from "@stores/tournaments";
import * as tournamentService from "@router/backend/services/tournament";

const toast = useToast();
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
  const result = await tournamentStore.createTournament({ name: name.value });
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Torneio criado com sucesso", life: 3000 });
    close();
  }
}

async function update() {
  const result = await tournamentService.updateTournament(props.tournament!.id, { name: name.value });
  if (result.success) {
    await tournamentStore.forceGetTournaments();
    toast.add({ severity: "success", summary: "Sucesso", detail: "Torneio atualizado com sucesso", life: 3000 });
    close();
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível atualizar o torneio", life: 3000 });
  }
}

function close() {
  enabled.value = false;
}
</script>

<style lang="scss" scoped>
#firstLabel {
  margin-top: 10px;
}
</style>
