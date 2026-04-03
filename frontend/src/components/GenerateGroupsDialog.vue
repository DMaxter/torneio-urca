<template>
  <P-Dialog v-model:visible="enabled" modal header="Gerar Grupos" class="w-11/12 md:w-8/12 lg:w-6/12">
    <div class="flex flex-col gap-4">
      <template v-if="!finalGroups.length">
        <P-FloatLabel variant="on">
          <P-Select
            id="tournament"
            v-model="selectedTournament"
            :options="availableTournaments"
            optionLabel="name"
            optionValue="id"
            optionDisabled="disabled"
            fluid
            @change="onTournamentChange"
          />
          <label for="tournament">Torneio</label>
        </P-FloatLabel>

        <div class="flex items-center gap-3">
          <label for="numGroups" class="text-sm font-medium text-stone-700 whitespace-nowrap">Número de Grupos</label>
          <div class="flex items-center gap-1">
            <P-Button
              severity="secondary"
              size="small"
              :disabled="numGroups <= 1 || !selectedTournament"
              @click="numGroups--; computePreview()"
              outlined
            >
              <span class="material-symbols-outlined">remove</span>
            </P-Button>
            <P-InputText
              id="numGroups"
              v-model="numGroups"
              type="number"
              class="w-16 text-center num-input-no-spin"
              :min="1"
              :max="7"
              :disabled="!selectedTournament"
              @input="computePreview"
            />
            <P-Button
              severity="secondary"
              size="small"
              :disabled="numGroups >= 7 || !selectedTournament"
              @click="numGroups++; computePreview()"
              outlined
            >
              <span class="material-symbols-outlined">add</span>
            </P-Button>
          </div>
        </div>

        <div v-if="preview.length > 0" class="border border-stone-200 rounded-lg overflow-hidden">
          <div class="bg-stone-100 px-3 py-2 text-sm font-semibold text-stone-600">
            Pré-visualização — {{ tournamentTeams.length }} equipas distribuídas por {{ numGroups }} grupo{{ numGroups > 1 ? 's' : '' }}
          </div>
          <div class="grid gap-px bg-stone-200" :class="gridCols(preview.length)">
            <div v-for="group in preview" :key="group.name" class="bg-white p-3">
              <p class="font-semibold text-stone-800 mb-2 text-sm">{{ group.name }} <span class="text-stone-400 font-normal">({{ group.teams.length }})</span></p>
              <ul class="space-y-1">
                <li v-for="team in group.teams" :key="team.id" class="text-xs truncate flex items-center gap-1"
                  :class="getPlayerCount(team.id) < MIN_PLAYERS ? 'text-red-600' : 'text-stone-600'">
                  <span v-if="getPlayerCount(team.id) < MIN_PLAYERS" class="material-symbols-outlined text-xs leading-none">warning</span>
                  {{ team.name }}
                  <span class="opacity-60">({{ getPlayerCount(team.id) }} jog.)</span>
                </li>
              </ul>
            </div>
          </div>
          <div v-if="teamsWithoutMinPlayers.length > 0" class="bg-red-50 border-t border-red-200 px-3 py-2 text-xs text-red-700 flex items-start gap-2">
            <span class="material-symbols-outlined text-sm shrink-0 mt-0.5">error</span>
            <span>
              As seguintes equipas têm menos de {{ MIN_PLAYERS }} jogadores e não podem ser incluídas:
              <strong>{{ teamsWithoutMinPlayers.map(t => t.name).join(", ") }}</strong>.
              Adiciona jogadores antes de gerar os grupos.
            </span>
          </div>
        </div>

        <p v-if="selectedTournament && tournamentTeams.length === 0" class="text-sm text-stone-400 text-center py-2">
          Nenhuma equipa encontrada para este torneio.
        </p>
      </template>

      <template v-else>
        <div class="border border-green-200 rounded-lg overflow-hidden">
          <div class="bg-green-50 px-3 py-2 text-sm font-semibold text-green-700">
            {{ finalGroups.length }} grupos criados com sucesso
          </div>
          <div class="grid gap-px bg-stone-200" :class="gridCols(finalGroups.length)">
            <div v-for="group in finalGroups" :key="group.name" class="bg-white p-3">
              <p class="font-semibold text-stone-800 mb-2 text-sm">{{ group.name }} <span class="text-stone-400 font-normal">({{ group.teams.length }})</span></p>
              <ul class="space-y-1">
                <li v-for="team in group.teams" :key="team.id" class="text-xs text-stone-600 truncate">
                  {{ team.name }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </template>
    </div>

    <template #footer>
      <P-Button v-if="!finalGroups.length" severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
      <P-Button
        v-if="!finalGroups.length"
        :disabled="preview.length === 0 || loading || teamsWithoutMinPlayers.length > 0"
        :loading="loading"
        @click="generate"
      >
        <span class="material-symbols-outlined">auto_awesome</span>
        Gerar Grupos
      </P-Button>
      <P-Button v-else @click="close">
        <span class="material-symbols-outlined">check</span>
        Fechar
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useToast } from "primevue/usetoast";

import { CreateGroup } from "@router/backend/services/group/types";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";

const toast = useToast();
const enabled = defineModel<boolean>();

const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();

const selectedTournament = ref<string>("");
const numGroups = ref<number>(2);
const loading = ref(false);

const availableTournaments = computed(() =>
  tournamentStore.tournaments.map(t => ({
    ...t,
    disabled: groupStore.groups.some(g => g.tournament === t.id),
  }))
);

const GROUP_NAMES = ["Grupo A", "Grupo B", "Grupo C", "Grupo D", "Grupo E", "Grupo F", "Grupo G"];

const MIN_PLAYERS = 5;

const tournamentTeams = computed(() =>
  teamStore.teams.filter(t => t.tournament === selectedTournament.value)
);

function getPlayerCount(teamId: string): number {
  return teamStore.teams.find(t => t.id === teamId)?.players.length ?? 0;
}

const teamsWithoutMinPlayers = computed(() =>
  tournamentTeams.value.filter(t => t.players.length < MIN_PLAYERS)
);

interface PreviewGroup {
  name: string;
  teams: { id: string; name: string }[];
}

const preview = ref<PreviewGroup[]>([]);
const finalGroups = ref<PreviewGroup[]>([]);

function gridCols(n: number) {
  if (n <= 2) return "grid-cols-2";
  return "grid-cols-4";
}

function onTournamentChange() {
  computePreview();
}

function distribute(teams: { id: string; name: string }[], n: number): PreviewGroup[] {
  const base = Math.floor(teams.length / n);
  const extra = teams.length % n;
  const groups: PreviewGroup[] = [];
  let cursor = 0;

  for (let i = 0; i < n; i++) {
    const size = base + (i >= n - extra ? 1 : 0);
    groups.push({
      name: GROUP_NAMES[i],
      teams: teams.slice(cursor, cursor + size),
    });
    cursor += size;
  }

  return groups;
}

function computePreview() {
  const teams = tournamentTeams.value;
  if (!teams.length || !numGroups.value) {
    preview.value = [];
    return;
  }
  preview.value = distribute(
    teams.map(t => ({ id: t.id, name: t.name })),
    numGroups.value
  );
}

async function generate() {
  loading.value = true;
  let allOk = true;

  const shuffled = [...tournamentTeams.value].sort(() => Math.random() - 0.5);
  const groups = distribute(
    shuffled.map(t => ({ id: t.id, name: t.name })),
    numGroups.value
  );

  for (const group of groups) {
    const dto = new CreateGroup();
    dto.tournament = selectedTournament.value;
    dto.name = group.name;
    dto.teams = group.teams.map(t => t.id);

    const result = await groupStore.createGroup(dto);
    if (!result.success) {
      allOk = false;
      toast.add({ severity: "error", summary: "Erro", detail: `Falha ao criar ${group.name}`, life: 4000 });
    }
  }

  loading.value = false;

  if (allOk) {
    finalGroups.value = groups;
  }
}

function close() {
  enabled.value = false;
  preview.value = [];
  finalGroups.value = [];
  selectedTournament.value = "";
  numGroups.value = 2;
}
</script>

<style scoped>
.num-input-no-spin::-webkit-outer-spin-button,
.num-input-no-spin::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.num-input-no-spin[type="number"] {
  -moz-appearance: textfield;
}
</style>
