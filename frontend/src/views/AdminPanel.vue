<template>
  <div class="admin-panel p-4 w-full mx-auto bg-stone-50 md:p-6">
    <div class="mb-6 md:mb-8">
      <div class="flex justify-between items-start gap-4">
        <div>
          <h1 class="text-xl font-bold text-stone-900 mb-1 md:text-2xl">Painel de Administração</h1>
          <p class="text-stone-500 text-sm md:text-base">Gerir torneios, equipas, jogadores e muito mais</p>
        </div>
        <P-Button severity="secondary" @click="changePassword = true">
          <span class="material-symbols-outlined">lock</span>
          <span class="hidden sm:inline">Alterar Palavra-passe</span>
        </P-Button>
        <P-Button severity="secondary" @click="handleLogout">
          <span class="material-symbols-outlined">logout</span>
          <span class="hidden sm:inline">Sair</span>
        </P-Button>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 lg:gap-6">
      <div v-for="section in sections" :key="section.title" class="admin-card bg-white border border-stone-300 rounded-xl p-4 md:p-5">
        <div class="card-header flex items-center gap-3 pb-3 mb-3 border-b border-stone-100">
          <span class="text-xl md:text-2xl">{{ section.icon }}</span>
          <h2 class="text-base font-semibold text-stone-900 m-0">{{ section.title }}</h2>
        </div>
        <div class="flex gap-2">
          <P-Button
            v-for="action in section.actions"
            :key="action.label"
            :severity="action.severity"
            size="small"
            class="flex-1 justify-center font-semibold text-sm"
            @click="action.handler"
          >
            <span class="material-symbols-outlined">{{ action.icon }}</span>
            {{ action.label }}
          </P-Button>
        </div>
      </div>
    </div>

    <GameDaysDialog v-model="gameDays" />
    <GenerateGamesDialog v-model="generateGames" />
    <GameCalendarDialog v-model="gameCalendar" @register-game="onRegisterGame" />
    <ViewGamesDialog v-model="viewGames" />
    <GameList v-model="listGames" />
    <GameManagement v-model="manageGame" />
    <GroupList v-model="listGroups" />
    <GroupManagement v-model="manageGroup" />
    <GenerateGroupsDialog v-model="generateGroups" />
    <GroupView v-model="viewGroups" />
    <TeamList v-model="listTeams" />
    <TeamManagement v-model="manageTeam" />
    <PlayerList v-model="listPlayers" />
    <AdminPlayerForm v-model="createPlayer" />
    <TournamentList v-model="listTournaments" />
    <TournamentManagement v-model="manageTournament" />
    <UserList v-model="listUsers" />
    <UserManagement v-model="manageUser" />
    <ChangePasswordDialog v-model="changePassword" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

import { useAuthStore } from "@stores/auth";
import type { Game } from "@router/backend/services/game/types";

const authStore = useAuthStore();

function handleLogout() {
  authStore.logout();
}

function onRegisterGame(_game: Game) {
  // TODO: abrir o diálogo de gestão do jogo ao vivo
}

const listTournaments = ref(false);
const manageTournament = ref(false);
const listUsers = ref(false);
const manageUser = ref(false);
const listTeams = ref(false);
const manageTeam = ref(false);
const changePassword = ref(false);
const listPlayers = ref(false);
const createPlayer = ref(false);
const listGroups = ref(false);
const manageGroup = ref(false);
const generateGroups = ref(false);
const viewGroups = ref(false);
const listGames = ref(false);
const manageGame = ref(false);
const gameDays = ref(false);
const generateGames = ref(false);
const gameCalendar = ref(false);
const viewGames = ref(false);

interface Action {
  label: string;
  icon: string;
  severity?: "secondary" | "success" | "info" | "warn" | "danger" | "help" | "contrast";
  handler: () => void;
}

interface Section {
  title: string;
  icon: string;
  actions: Action[];
}

const sections: Section[] = [
  {
    title: "Torneios",
    icon: "🏆",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => manageTournament.value = true },
      { label: "Listar", icon: "list", handler: () => listTournaments.value = true }
    ]
  },
  {
    title: "Utilizadores",
    icon: "👥",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => manageUser.value = true },
      { label: "Listar", icon: "list", handler: () => listUsers.value = true }
    ]
  },
  {
    title: "Equipas",
    icon: "⚽",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => manageTeam.value = true },
      { label: "Listar", icon: "list", handler: () => listTeams.value = true }
    ]
  },
  {
    title: "Jogadores",
    icon: "🧑",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => createPlayer.value = true },
      { label: "Listar", icon: "list", handler: () => listPlayers.value = true }
    ]
  },
  {
    title: "Grupos",
    icon: "📋",
    actions: [
      { label: "Gerar", icon: "auto_awesome", severity: "success", handler: () => generateGroups.value = true },
      { label: "Ver", icon: "grid_view", severity: "secondary", handler: () => viewGroups.value = true },
      { label: "Listar", icon: "list", handler: () => listGroups.value = true }
    ]
  },
  {
    title: "Jogos",
    icon: "🎮",
    actions: [
      { label: "Gerar", icon: "sports_soccer", severity: "success", handler: () => generateGames.value = true },
      { label: "Calendário", icon: "calendar_month", severity: "info", handler: () => gameCalendar.value = true },
      { label: "Ver", icon: "grid_view", severity: "secondary", handler: () => viewGames.value = true },
      { label: "Dias de Jogo", icon: "edit_calendar", severity: "secondary", handler: () => gameDays.value = true }
    ]
  }
];
</script>

<style scoped>
@media (min-width: 1024px) {
  .admin-card {
    transition: all 0.2s ease;
  }
  .admin-card:hover {
    border-color: var(--border-warning);
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    transform: translateY(-2px);
  }
}
</style>
