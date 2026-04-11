<template>
  <P-Dialog v-model:visible="enabled" modal header="Gerir Funções de Utilizadores" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-6/5">
    <P-DataTable :value="userStore.users" striped-rows size="small" paginator :rows="10" dataKey="id">
      <P-Column field="username" header="Utilizador">
        <template #body="{ data }">
          <span class="font-medium">{{ data.username }}</span>
        </template>
      </P-Column>
      <P-Column header="Funções">
        <template #body="{ data }">
          <div class="flex flex-wrap gap-2">
            <P-Checkbox v-model="selectedRoles[data.id]" value="manage_players" :binary="false" inputId="mp_{{ data.id }}" />
            <label for="mp_{{ data.id }}" class="text-sm">Gerir Jogadores</label>
            <P-Checkbox v-model="selectedRoles[data.id]" value="manage_games" :binary="false" inputId="mg_{{ data.id }}" />
            <label for="mg_{{ data.id }}" class="text-sm">Gerir Jogos</label>
            <P-Checkbox v-model="selectedRoles[data.id]" value="manage_game_events" :binary="false" inputId="mge_{{ data.id }}" />
            <label for="mge_{{ data.id }}" class="text-sm">Eventos</label>
            <P-Checkbox v-model="selectedRoles[data.id]" value="fill_game_calls" :binary="false" inputId="fgc_{{ data.id }}" />
            <label for="fgc_{{ data.id }}" class="text-sm">Chamadas</label>
          </div>
        </template>
      </P-Column>
      <P-Column header="Jogos (Eventos)">
        <template #body="{ data }">
          <div v-if="selectedRoles[data.id]?.includes('manage_game_events') || data.assigned_games?.length">
            <P-MultiSelect
              v-model="selectedGames[data.id]"
              :options="gameOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecionar jogos"
              class="w-full"
              display="chip"
            />
          </div>
          <span v-else class="text-sm text-stone-400">-</span>
        </template>
      </P-Column>
      <P-Column header="Jogos (Chamadas)">
        <template #body="{ data }">
          <div v-if="selectedRoles[data.id]?.includes('fill_game_calls') || data.assigned_games_for_calls?.length">
            <P-MultiSelect
              v-model="selectedGamesForCalls[data.id]"
              :options="gameOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecionar jogos"
              class="w-full"
              display="chip"
            />
          </div>
          <span v-else class="text-sm text-stone-400">-</span>
        </template>
      </P-Column>
      <P-Column header="">
        <template #body="{ data }">
          <P-Button size="small" @click="saveUserRoles(data.id)" :disabled="!hasChanged(data.id)">
            <span class="material-symbols-outlined">save</span>
          </P-Button>
        </template>
      </P-Column>
    </P-DataTable>
  </P-Dialog>
</template>

<script setup lang="ts">
import { reactive, watch, computed } from "vue";
import { useToast } from "primevue/usetoast";
import { useUserStore } from "@stores/users";
import { useGameStore } from "@stores/games";
import { useTeamStore } from "@stores/teams";

const toast = useToast();
const enabled = defineModel<boolean>();

const userStore = useUserStore();
const gameStore = useGameStore();
const teamStore = useTeamStore();

const selectedRoles = reactive<Record<string, string[]>>({});
const selectedGames = reactive<Record<string, string[]>>({});
const selectedGamesForCalls = reactive<Record<string, string[]>>({});
const originalRoles = reactive<Record<string, string[]>>({});
const originalGames = reactive<Record<string, string[]>>({});
const originalGamesForCalls = reactive<Record<string, string[]>>({});

const gameOptions = computed(() => {
  // Separate active vs finished/canceled games
  const activeGames = gameStore.games.filter(g => 
    !["Finished", "Canceled"].includes(String(g.status))
  );
  const finishedGames = gameStore.games.filter(g => 
    ["Finished", "Canceled"].includes(String(g.status))
  );
  
  // Sort active games by date ascending
  const sortedActive = [...activeGames].sort((a, b) => {
    if (!a.scheduled_date) return 1;
    if (!b.scheduled_date) return -1;
    return new Date(a.scheduled_date).getTime() - new Date(b.scheduled_date).getTime();
  });
  
  // Sort finished games by date ascending
  const sortedFinished = [...finishedGames].sort((a, b) => {
    if (!a.scheduled_date) return 1;
    if (!b.scheduled_date) return -1;
    return new Date(a.scheduled_date).getTime() - new Date(b.scheduled_date).getTime();
  });
  
  // Combine: active first, then finished at the end
  const sortedGames = [...sortedActive, ...sortedFinished];
  
  return sortedGames.map(g => {
    const homeTeam = teamStore.teams.find(t => 
      t.id === g.home_placeholder || t.id === g.home_call?.team
    );
    const awayTeam = teamStore.teams.find(t => 
      t.id === g.away_placeholder || t.id === g.away_call?.team
    );
    return {
      label: `${homeTeam?.name || "Casa"} vs ${awayTeam?.name || "Fora"}`,
      value: g.id
    };
  });
});

watch(enabled, async (val) => {
  if (val) {
    await userStore.getUsers();
    await gameStore.getGames();
    await teamStore.getTeams();

    for (const user of userStore.users) {
      selectedRoles[user.id] = user.roles ? [...user.roles] : [];
      selectedGames[user.id] = user.assigned_games ? [...user.assigned_games] : [];
      selectedGamesForCalls[user.id] = user.assigned_games_for_calls ? [...user.assigned_games_for_calls] : [];
      originalRoles[user.id] = user.roles ? [...user.roles] : [];
      originalGames[user.id] = user.assigned_games ? [...user.assigned_games] : [];
      originalGamesForCalls[user.id] = user.assigned_games_for_calls ? [...user.assigned_games_for_calls] : [];
    }
  }
});

function hasChanged(userId: string): boolean {
  const rolesChanged = JSON.stringify(selectedRoles[userId]) !== JSON.stringify(originalRoles[userId]);
  const gamesChanged = JSON.stringify(selectedGames[userId] || []) !== JSON.stringify(originalGames[userId] || []);
  const gamesForCallsChanged = JSON.stringify(selectedGamesForCalls[userId] || []) !== JSON.stringify(originalGamesForCalls[userId] || []);
  return rolesChanged || gamesChanged || gamesForCallsChanged;
}

async function saveUserRoles(userId: string) {
  const result = await userStore.updateRoles(userId, selectedRoles[userId] || []);
  if (result.success) {
    const gameResult = await userStore.assignGames(userId, selectedGames[userId] || []);
    if (gameResult.success) {
      const callsResult = await userStore.assignGamesForCalls(userId, selectedGamesForCalls[userId] || []);
      if (callsResult.success) {
        toast.add({ severity: "success", summary: "Sucesso", detail: "Funções atualizadas", life: 3000 });
        originalRoles[userId] = [...(selectedRoles[userId] || [])];
        originalGames[userId] = [...(selectedGames[userId] || [])];
        originalGamesForCalls[userId] = [...(selectedGamesForCalls[userId] || [])];
      } else {
        toast.add({ severity: "error", summary: "Erro", detail: "Erro ao atribuir jogos para chamadas", life: 3000 });
      }
    } else {
      toast.add({ severity: "error", summary: "Erro", detail: "Erro ao atribuir jogos", life: 3000 });
    }
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Erro ao atualizar funções", life: 3000 });
  }
}
</script>
