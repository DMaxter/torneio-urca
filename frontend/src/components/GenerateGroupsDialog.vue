<template>
  <P-Dialog v-model:visible="enabled" modal header="Gerar Grupos" class="w-11/12 md:w-8/12 lg:w-6/12">
    <div class="flex flex-col gap-4">
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

      <P-FloatLabel variant="on">
        <P-Select
          id="numGroups"
          v-model="numGroups"
          :options="groupOptions"
          optionLabel="label"
          optionValue="value"
          fluid
          :disabled="!selectedTournament"
          @change="computePreview"
        />
        <label for="numGroups">Número de Grupos</label>
      </P-FloatLabel>

      <div v-if="preview.length > 0" class="border border-stone-200 rounded-lg overflow-hidden">
        <div class="bg-stone-100 px-3 py-2 text-sm font-semibold text-stone-600">
          Pré-visualização — {{ tournamentTeams.length }} equipas distribuídas por {{ numGroups }} grupo{{ numGroups > 1 ? 's' : '' }}
        </div>
        <div class="grid gap-px bg-stone-200" :class="gridCols">
          <div v-for="group in preview" :key="group.name" class="bg-white p-3">
            <p class="font-semibold text-stone-800 mb-2 text-sm">{{ group.name }} <span class="text-stone-400 font-normal">({{ group.teams.length }})</span></p>
            <ul class="space-y-1">
              <li v-for="team in group.teams" :key="team.id" class="text-xs text-stone-600 truncate">
                {{ team.name }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <p v-if="selectedTournament && tournamentTeams.length === 0" class="text-sm text-stone-400 text-center py-2">
        Nenhuma equipa encontrada para este torneio.
      </p>
    </div>

    <template #footer>
      <P-Button severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
      <P-Button
        :disabled="preview.length === 0 || loading"
        :loading="loading"
        @click="generate"
      >
        <span class="material-symbols-outlined">auto_awesome</span>
        Gerar Grupos
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

const groupOptions = [
  { label: "1 Grupo", value: 1 },
  { label: "2 Grupos", value: 2 },
  { label: "3 Grupos", value: 3 },
  { label: "4 Grupos", value: 4 },
  { label: "5 Grupos", value: 5 },
  { label: "6 Grupos", value: 6 },
  { label: "7 Grupos", value: 7 },
];

const tournamentTeams = computed(() =>
  teamStore.teams.filter(t => t.tournament === selectedTournament.value)
);

interface PreviewGroup {
  name: string;
  teams: { id: string; name: string }[];
}

const preview = ref<PreviewGroup[]>([]);

const gridCols = computed(() => {
  const n = preview.value.length;
  if (n <= 2) return "grid-cols-2";
  if (n <= 4) return "grid-cols-4";
  return "grid-cols-4";
});

function onTournamentChange() {
  computePreview();
}

function computePreview() {
  const teams = tournamentTeams.value;
  if (!teams.length || !numGroups.value) {
    preview.value = [];
    return;
  }

  const n = numGroups.value;
  const base = Math.floor(teams.length / n);
  const extra = teams.length % n;

  const groups: PreviewGroup[] = [];
  let cursor = 0;

  for (let i = 0; i < n; i++) {
    const size = base + (i >= n - extra ? 1 : 0);
    groups.push({
      name: GROUP_NAMES[i],
      teams: teams.slice(cursor, cursor + size).map(t => ({ id: t.id, name: t.name })),
    });
    cursor += size;
  }

  preview.value = groups;
}

async function generate() {
  loading.value = true;
  let allOk = true;

  for (const group of preview.value) {
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
    toast.add({ severity: "success", summary: "Sucesso", detail: `${preview.value.length} grupos criados com sucesso`, life: 3000 });
    close();
  }
}

function close() {
  enabled.value = false;
  preview.value = [];
  selectedTournament.value = "";
  numGroups.value = 2;
}
</script>
