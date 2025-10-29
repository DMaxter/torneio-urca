<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Equipa' : 'Editar Equipa'">
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="name" v-model="team.name" />
      <label for="name">Nome</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="tournament" v-model="team.tournament" :options="tournamentStore.tournaments"
        optionLabel="name" optionValue="id" fluid />
      <label for="tournament">Torneio</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="gender" v-model="team.gender" :options="GENDERS" optionLabel="name"
        optionValue="value" fluid />
      <label for="gender">Género</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="responsible" v-model="team.responsible" filter :options="userStore.users" optionLabel="name" optionValue="id"
      fluid />
      <label for="responsible">Responsável da Equipa</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="coach" v-model="team.main_coach" filter :options="coaches" optionLabel="name" optionValue="id" fluid />
      <label for="coach">Treinador Principal</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="secondcoach" v-model="team.assistant_coach" filter :options="coaches"
        optionLabel="name" optionValue="id" fluid />
      <label for="secondcoach">Treinador Adjunto</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-MultiSelect id="players" v-model="team.players" :showToggleAll="false" filter :options="players" optionLabel="name" optionValue="id" fluid />
      <label for="players">Jogadores</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="physiotherapist" v-model="team.physiotherapist" filter :options="physiotherapists"
        optionLabel="name" optionValue="id" fluid />
      <label for="physiotherapist">Fisioterapeuta</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="deputy" v-model="team.first_deputy" filter :options="deputies" optionLabel="name" optionValue="id" fluid />
      <label for="deputy">Primeiro Delegado</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="seconddeputy" v-model="team.second_deputy" filter :options="deputies"
        optionLabel="name" optionValue="id" fluid />
      <label for="seconddeputy">Segundo Delegado</label>
    </P-FloatLabel>
    <template #footer>
      <P-Button @click="createOrUpdate">{{ creating ? "Criar" : "Alterar" }}</P-Button>
      <P-Button @click="close">Cancelar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { CreateTeam, type Team } from "@router/backend/services/team/types";
import { GENDERS, getRole, Role } from "@router/backend/services/user/types";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { useUserStore } from "@stores/users";

const enabled = defineModel<boolean>();
const props = defineProps<{
  team?: Team
}>();

const creating = computed(() => props.team === undefined);

const team = ref<Team | CreateTeam>(new CreateTeam());

onMounted(() => {
  if (!creating.value) {
    team.value = props.team!
  }
});

const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const userStore = useUserStore();

const players = computed(() => userStore.users.filter((u) => u.roles.includes(getRole(Role.Player)!) && u.gender === team.value.gender!));
const coaches = computed(() => userStore.users.filter((u) => u.roles.includes(getRole(Role.Coach)!)));
const physiotherapists = computed(() => userStore.users.filter((u) =>
  u.roles.includes(getRole(Role.Physiotherapist)!)));
const deputies = computed(() => userStore.users.filter((u) =>
  u.roles.includes(getRole(Role.GameDeputy)!)));

async function createOrUpdate() {
  if (creating.value) {
    await create();
  } else {
    await update();
  }
}

async function create() {
  await teamStore.createTeam(team.value as CreateTeam);
}

async function update() {
  console.error("TODO");
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
