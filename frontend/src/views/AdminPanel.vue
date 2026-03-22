<template>
  <div class="admin-panel">
    <div class="admin-header">
      <h1>Painel de Administração</h1>
      <p>Gerir torneios, equipas, jogadores e muito mais</p>
    </div>

    <div class="admin-grid">
      <div v-for="section in sections" :key="section.title" class="admin-card">
        <div class="card-header">
          <span class="card-icon">{{ section.icon }}</span>
          <h2>{{ section.title }}</h2>
        </div>
        <div class="card-actions">
          <P-Button
            v-for="action in section.actions"
            :key="action.label"
            :label="action.label"
            :icon="action.icon"
            :severity="action.severity || 'secondary'"
            outlined
            size="small"
            @click="action.handler"
          />
        </div>
      </div>
    </div>

    <GameList v-model="listGames" />
    <GameManagement v-model="manageGame" />
    <GroupList v-model="listGroups" />
    <GroupManagement v-model="manageGroup" />
    <TeamList v-model="listTeams" />
    <TeamManagement v-model="manageTeam" />
    <PlayerList v-model="listPlayers" />
    <TournamentList v-model="listTournaments" />
    <TournamentManagement v-model="manageTournament" />
    <UserList v-model="listUsers" />
    <UserManagement v-model="manageUser" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const listTournaments = ref(false);
const manageTournament = ref(false);
const listUsers = ref(false);
const manageUser = ref(false);
const listTeams = ref(false);
const manageTeam = ref(false);
const listPlayers = ref(false);
const listGroups = ref(false);
const manageGroup = ref(false);
const listGames = ref(false);
const manageGame = ref(false);

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
      { label: "Criar", icon: "pi pi-plus", severity: "success", handler: () => manageTournament.value = true },
      { label: "Listar", icon: "pi pi-list", handler: () => listTournaments.value = true }
    ]
  },
  {
    title: "Utilizadores",
    icon: "👥",
    actions: [
      { label: "Criar", icon: "pi pi-plus", severity: "success", handler: () => manageUser.value = true },
      { label: "Listar", icon: "pi pi-list", handler: () => listUsers.value = true }
    ]
  },
  {
    title: "Equipas",
    icon: "⚽",
    actions: [
      { label: "Criar", icon: "pi pi-plus", severity: "success", handler: () => manageTeam.value = true },
      { label: "Listar", icon: "pi pi-list", handler: () => listTeams.value = true }
    ]
  },
  {
    title: "Jogadores",
    icon: "🧑",
    actions: [
      { label: "Listar", icon: "pi pi-list", handler: () => listPlayers.value = true }
    ]
  },
  {
    title: "Grupos",
    icon: "📋",
    actions: [
      { label: "Criar", icon: "pi pi-plus", severity: "success", handler: () => manageGroup.value = true },
      { label: "Listar", icon: "pi pi-list", handler: () => listGroups.value = true }
    ]
  },
  {
    title: "Jogos",
    icon: "🎮",
    actions: [
      { label: "Criar", icon: "pi pi-plus", severity: "success", handler: () => manageGame.value = true },
      { label: "Listar", icon: "pi pi-list", handler: () => listGames.value = true }
    ]
  }
];
</script>

<style scoped>
.admin-panel {
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto;
  background: #fafaf9;
}

.admin-header {
  margin-bottom: 1.5rem;
}
  
.admin-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1c1917;
  margin: 0 0 0.25rem 0;
}

.admin-header p {
  color: #78716c;
  margin: 0;
  font-size: 0.875rem;
}

.admin-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.admin-card {
  background: white;
  border: 1px solid #d6d3d1;
  border-radius: 12px;
  padding: 1rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e7e5e4;
}

.card-icon {
  font-size: 1.25rem;
}

.card-header h2 {
  font-size: 0.9375rem;
  font-weight: 600;
  margin: 0;
  color: #1c1917;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.card-actions :deep(.p-button) {
  flex: 1;
  justify-content: center;
  font-weight: 600;
  font-size: 0.8125rem;
  background: #fff7ed;
  border-color: #f97316;
  color: #c2410c;
}

.card-actions :deep(.p-button:hover) {
  background: #f97316;
  color: white;
  border-color: #f97316;
}

.card-actions :deep(.p-button.p-button-success) {
  background: #f0fdf4;
  border-color: #16a34a;
  color: #15803d;
}

.card-actions :deep(.p-button.p-button-success:hover) {
  background: #16a34a;
  color: white;
  border-color: #16a34a;
}

/* Large phones */
@media (min-width: 480px) {
  .admin-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .admin-card {
    padding: 1.25rem;
  }
  
  .card-header {
    margin-bottom: 1rem;
    padding-bottom: 1rem;
  }
}

/* Tablets */
@media (min-width: 768px) {
  .admin-panel {
    padding: 1.5rem;
  }

  .admin-header {
    margin-bottom: 2rem;
  }

  .admin-header h1 {
    font-size: 1.5rem;
  }

  .admin-header p {
    font-size: 1rem;
  }

  .admin-card {
    padding: 1.5rem;
  }

  .card-icon {
    font-size: 1.5rem;
  }

  .card-header h2 {
    font-size: 1rem;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .admin-panel {
    padding: 2rem;
  }

  .admin-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }

  .admin-card {
    transition: all 0.2s ease;
  }

  .admin-card:hover {
    border-color: #fed7aa;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
  }
}
</style>
