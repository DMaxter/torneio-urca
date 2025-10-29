<template>
  <P-Fieldset legend="Torneios" :pt=ptFieldset>
    <P-Button @click="showTournamentManagement">Criar Torneio</P-Button>
    <P-Button @click="showTournamentsList">Lista de Torneios</P-Button>
  </P-Fieldset>
  <P-Fieldset legend="Utilizadores" :pt=ptFieldset>
    <P-Button @click="showUserManagement">Criar Utilizador</P-Button>
    <P-Button @click="showUsersList">Lista de Utilizadores</P-Button>
  </P-Fieldset>
  <P-Fieldset legend="Equipas" :pt=ptFieldset>
    <P-Button @click="showTeamManagement">Criar Equipa</P-Button>
    <P-Button @click="showTeamsList">Lista de Equipas</P-Button>
  </P-Fieldset>
  <P-Fieldset legend="Grupos" :pt=ptFieldset>
    <P-Button>Criar Grupo</P-Button>
    <P-Button>Lista de Grupos</P-Button>
  </P-Fieldset>
  <P-Fieldset legend="Jogos" :pt=ptFieldset>
    <P-Button @click="showGameManagement">Criar Jogo</P-Button>
    <P-Button @click="showGamesList">Lista de Jogos</P-Button>
  </P-Fieldset>
  <GameList v-model="listGames" />
  <GameManagement v-model="manageGame" />
  <TeamList v-model="listTeams" />
  <TeamManagement v-model="manageTeam" />
  <TournamentList v-model="listTournaments" />
  <TournamentManagement v-model="manageTournament" />
  <UserList v-model="listUsers" />
  <UserManagement v-model="manageUser" />
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

const manageUser = ref(false);
function showUserManagement() {
  manageUser.value = true;
}

const listUsers = ref(false);
function showUsersList() {
  listUsers.value = true;
}

const manageTeam = ref(false);
function showTeamManagement() {
  manageTeam.value = true;
}

const listTeams = ref(false);
function showTeamsList() {
  listTeams.value = true;
}

const manageGame = ref(false);
function showGameManagement() {
  manageGame.value = true;
}

const listGames = ref(false);
function showGamesList() {
  listGames.value = true;
}
</script>
