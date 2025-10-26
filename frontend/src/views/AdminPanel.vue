<template>
  <P-Fieldset legend="Torneios" :pt=ptFieldset>
    <P-Button @click="showTournamentManagement">Criar Torneio</P-Button>
    <P-Button @click="showTournamentsList">Lista de Torneios</P-Button>
  </P-Fieldset>
  <P-Fieldset legend="Utilizadores" :pt=ptFieldset>
    <P-Button>Criar Utilizador</P-Button>
    <P-Button>Lista de Utilizadores</P-Button>
  </P-Fieldset>
  <P-Fieldset legend="Equipas" :pt=ptFieldset>
    <P-Button>Criar Equipa</P-Button>
    <P-Button>Lista de Equipas</P-Button>
  </P-Fieldset>
  <P-Fieldset legend="Grupos" :pt=ptFieldset>
    <P-Button>Criar Grupo</P-Button>
    <P-Button>Lista de Grupos</P-Button>
  </P-Fieldset>
  <P-Fieldset legend="Jogos" :pt=ptFieldset>
    <P-Button>Criar Jogo</P-Button>
    <P-Button>Lista de Jogos</P-Button>
  </P-Fieldset>
  <TournamentManagement v-model="manageTournament" />
  <TournamentList v-model="listTournaments" />
</template>

<script setup lang="ts">
import { ref } from "vue";

const ptFieldset = {
  content: {
    class: "flex justify-around"
  }
};

const manageTournament = ref(false);
function showTournamentManagement() {
  manageTournament.value = true;
}

const listTournaments = ref(false);
function showTournamentsList() {
  listTournaments.value = true;
}
</script>
