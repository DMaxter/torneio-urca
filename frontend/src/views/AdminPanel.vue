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
      <div v-for="section in sections.filter(s => s.show())" :key="section.title" class="admin-card bg-white border border-stone-300 rounded-xl p-4 md:p-5">
        <div class="card-header flex items-center gap-3 pb-3 mb-3 border-b border-stone-100">
          <span class="text-xl md:text-2xl">{{ section.icon }}</span>
          <h2 class="text-base font-semibold text-stone-900 m-0">{{ section.title }}</h2>
        </div>
        <div class="flex gap-2">
          <P-Button
            v-for="action in section.actions.filter(a => !a.requiredRole || a.requiredRole())"
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

    <GameDaysDialog v-if="gameDays" v-model="gameDays" />
    <GenerateGamesDialog v-if="generateGames" v-model="generateGames" />
    <GameCalendarDialog v-if="gameCalendar" v-model="gameCalendar" @register-game="onRegisterGame" />
    <ViewGamesDialog v-if="viewGames" v-model="viewGames" />
    <GameList v-if="listGames" v-model="listGames" />
    <GameManagement v-if="manageGame" v-model="manageGame" />
    <GameManagementDialog v-if="manageGames" v-model="manageGames" />
    <GroupList v-if="listGroups" v-model="listGroups" @edit-group="(group: Group) => { selectedGroup = group; manageGroup = true; }" />
    <GroupManagement v-if="manageGroup" v-model="manageGroup" :group="selectedGroup" />
    <GenerateGroupsDialog v-if="generateGroups" v-model="generateGroups" />
    <GroupView v-if="viewGroups" v-model="viewGroups" />
    <TeamList v-if="listTeams" v-model="listTeams" />
    <TeamManagement v-if="manageTeam" v-model="manageTeam" />
    <PlayerList v-if="listPlayers" v-model="listPlayers" />
    <PlayerManagement v-if="createPlayer" v-model="createPlayer" />
    <TournamentList v-if="listTournaments" v-model="listTournaments" @edit-tournament="(t: Tournament) => { selectedTournament = t; manageTournament = true; }" />
    <TournamentManagement v-if="manageTournament" v-model="manageTournament" :tournament="selectedTournament" />
    <UserList v-if="listUsers" v-model="listUsers" />
    <UserManagement v-if="manageUser" v-model="manageUser" />
    <RoleManagement v-if="manageRoles" v-model="manageRoles" />
    <ChangePasswordDialog v-if="changePassword" v-model="changePassword" />
    <ExportSocialDialog v-if="exportSocial" v-model="exportSocial" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@stores/auth";
import type { Game } from "@router/backend/services/game/types";
import type { Group } from "@router/backend/services/group/types";
import type { Tournament } from "@router/backend/services/tournament/types";
import ExportSocialDialog from "@/components/admin/ExportSocialDialog.vue";

const router = useRouter();
const authStore = useAuthStore();

function handleLogout() {
  authStore.logout(router);
}

function onRegisterGame(_game: Game) {
  // TODO: abrir o diálogo de gestão do jogo ao vivo
  console.info("Register game:", _game);
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
const selectedGroup = ref<Group | undefined>(undefined);
const selectedTournament = ref<Tournament | undefined>(undefined);
const generateGroups = ref(false);
const viewGroups = ref(false);
const listGames = ref(false);
const manageGame = ref(false);
const manageGames = ref(false);
const gameDays = ref(false);
const generateGames = ref(false);
const gameCalendar = ref(false);
const viewGames = ref(false);
const manageRoles = ref(false);
const exportSocial = ref(false);

interface Action {
  label: string;
  icon: string;
  severity?: "secondary" | "success" | "info" | "warn" | "danger" | "help" | "contrast";
  handler: () => void;
  requiredRole?: () => boolean;
}

interface Section {
  title: string;
  icon: string;
  actions: Action[];
  show: () => boolean;
}

const sections: Section[] = [
  {
    title: "Torneios",
    icon: "🏆",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => { selectedTournament.value = undefined; manageTournament.value = true; } },
      { label: "Listar", icon: "list", handler: () => listTournaments.value = true }
    ],
    show: () => authStore.canManagePlayers
  },
  {
    title: "Utilizadores",
    icon: "👥",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => manageUser.value = true },
      { label: "Listar", icon: "list", handler: () => listUsers.value = true },
      { label: "Funções", icon: "admin_panel_settings", severity: "info", handler: () => manageRoles.value = true }
    ],
    show: () => authStore.isAdmin
  },
  {
    title: "Equipas",
    icon: "⚽",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => manageTeam.value = true },
      { label: "Listar", icon: "list", handler: () => listTeams.value = true }
    ],
    show: () => authStore.canManagePlayers
  },
  {
    title: "Jogadores",
    icon: "🧑",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => createPlayer.value = true },
      { label: "Listar", icon: "list", handler: () => listPlayers.value = true }
    ],
    show: () => authStore.canManagePlayers
  },
  {
    title: "Grupos",
    icon: "📋",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => { selectedGroup.value = undefined; manageGroup.value = true; } },
      { label: "Gerar", icon: "auto_awesome", severity: "success", handler: () => generateGroups.value = true },
      { label: "Ver", icon: "grid_view", severity: "secondary", handler: () => viewGroups.value = true },
      { label: "Listar", icon: "list", handler: () => listGroups.value = true }
    ],
    show: () => authStore.canManageGames
  },
  {
    title: "Calendário",
    icon: "📅",
    actions: [
      { label: "Calendário", icon: "calendar_month", severity: "info", handler: () => gameCalendar.value = true },
      { label: "Dias de Jogo", icon: "edit_calendar", severity: "secondary", handler: () => gameDays.value = true }
    ],
    show: () => authStore.canManageGames
  },
   {
    title: "Gestão de Jogos",
    icon: "🎮",
    actions: [
      { label: "Criar", icon: "add", severity: "success", handler: () => manageGame.value = true, requiredRole: () => authStore.canManageGames },
      { label: "Gerir", icon: "manage_search", severity: "info", handler: () => manageGames.value = true, requiredRole: () => authStore.canManageGames || authStore.canManageGameEvents || authStore.canFillGameCalls },
      { label: "Gerar", icon: "sports_soccer", severity: "secondary", handler: () => generateGames.value = true, requiredRole: () => authStore.canManageGames },
      { label: "Ver", icon: "grid_view", severity: "secondary", handler: () => viewGames.value = true, requiredRole: () => authStore.canManageGames }
    ],
    show: () => authStore.canManageGames || authStore.canManageGameEvents || authStore.canFillGameCalls
   },
   {
    title: "Gestão de Staff de Equipas",
    icon: "👥",
    actions: [
      { label: "Gerir", icon: "manage_accounts", severity: "info", handler: () => router.push('/admin/staff') }
    ],
    show: () => authStore.canManagePlayers
   },
   {
    title: "Comunicação",
    icon: "📣",
    actions: [
      { label: "Exportar", icon: "share", severity: "contrast", handler: () => exportSocial.value = true, requiredRole: () => authStore.canManageGames }
    ],
    show: () => authStore.canManageGames
   }
];
</script>

<style scoped>
@media (min-width: 1024px) {
  .admin-card {
    transition: all 0.2s ease;
  }
  .admin-card:hover {
    border-color: var(--color-orange-200);
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    transform: translateY(-2px);
  }
}
</style>
