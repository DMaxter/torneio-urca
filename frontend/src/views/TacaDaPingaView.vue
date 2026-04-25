<template>
  <div class="pinga p-4 md:p-6">
    <div class="mb-6 md:mb-8">
      <h1 class="text-xl font-bold text-stone-900 mb-1 md:text-2xl">Taça da Pinga</h1>
      <p class="text-stone-500 text-sm md:text-base">Resultados da votação</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <h2 class="text-lg font-semibold mb-4">Distribuição</h2>
        <div v-if="loading" class="text-center text-stone-400">A carregar...</div>
        <div v-else-if="counts.length === 0" class="text-center text-stone-400">Sem votos registados</div>
        <div v-else>
          <P-Chart type="pie" :data="pieChartData" :options="pieChartOptions" class="w-full" />
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-4">
        <h2 class="text-lg font-semibold mb-4">Total de Votos</h2>
        <div v-if="loading" class="text-center text-stone-400">A carregar...</div>
        <div v-else-if="counts.length === 0" class="text-center text-stone-400">Sem votos registados</div>
        <P-DataTable v-else :value="teamTotals" size="small">
          <P-Column header="Equipa">
            <template #body="{ data }">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded" :style="{ backgroundColor: teamColor(data.team_name) }"></div>
                {{ data.team_name }}
              </div>
            </template>
          </P-Column>
          <P-Column header="Votos">
            <template #body="{ data }">
              {{ data.count }}
            </template>
          </P-Column>
          <P-Column header="%">
            <template #body="{ data }">
              {{ data.percentage }}%
            </template>
          </P-Column>
        </P-DataTable>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <h2 class="text-lg font-semibold mb-4">Evolução por Dia</h2>
      <div v-if="loading" class="text-center text-stone-400">A carregar...</div>
      <div v-else-if="history.length === 0" class="text-center text-stone-400">Sem histórico</div>
      <div v-else>
        <P-Chart type="line" :data="lineChartData" :options="lineChartOptions" class="w-full" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useToast } from "primevue/usetoast";
import type { TeamCount, DailyVoteHistory } from "@router/backend/services/pinga/types";
import * as pingaService from "@router/backend/services/pinga";
import { usePingaColors } from "@/utils/pingaColors";

const toast = useToast();
const { getColorForTeam } = usePingaColors();

const loading = ref(false);
const counts = ref<TeamCount[]>([]);
const history = ref<DailyVoteHistory[]>([]);

function teamColor(teamName: string): string {
  return getColorForTeam(teamName);
}

const totalVotes = computed(() => counts.value.reduce((sum, c) => sum + c.count, 0));

const teamTotals = computed(() =>
  counts.value.map(c => ({
    team_name: c.team_name,
    count: c.count,
    percentage: totalVotes.value === 0 ? "0" : ((c.count / totalVotes.value) * 100).toFixed(2)
  }))
);

const flattenHistory = computed(() => {
  const result = [];
  for (const day of history.value) {
    for (const team of day.teams) {
      result.push({ date: day.date, team_name: team.team_name, count: team.count });
    }
  }
  return result;
});

const pieChartData = computed(() => ({
  labels: counts.value.map(c => c.team_name),
  datasets: [{
    data: counts.value.map(c => c.count),
    backgroundColor: counts.value.map(c => teamColor(c.team_name)),
    hoverOffset: 4
  }]
}));

const pieChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 1.5,
  plugins: {
    legend: {
      display: false
    }
  }
};

const lineChartData = computed(() => {
  const dates = [...new Set(history.value.map(h => h.date))].sort();

  const teamNames = [...new Set(flattenHistory.value.map(h => h.team_name))];

  const cumulative = new Map<string, number>();
  const datasets = teamNames.map(teamName => {
    cumulative.set(teamName, 0);
    return {
      label: teamName,
      data: [] as number[],
      borderColor: teamColor(teamName),
      backgroundColor: teamColor(teamName),
      fill: false,
      tension: 0.3
    };
  });

  for (const date of dates) {
    const dayData = history.value.find(h => h.date === date);
    if (dayData) {
      for (const team of dayData.teams) {
        const current = cumulative.get(team.team_name) || 0;
        cumulative.set(team.team_name, current + team.count);
      }
    }
    for (let i = 0; i < teamNames.length; i++) {
      datasets[i].data.push(cumulative.get(teamNames[i]) || 0);
    }
  }

  return {
    labels: dates,
    datasets
  };
});

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "bottom" as const
    }
  },
  scales: {
    x: {
      offset: true,
      ticks: {
        maxRotation: 45,
        minRotation: 0
      }
    },
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1
      }
    }
  }
};

async function loadData() {
  loading.value = true;
  try {
    const [countsRes, historyRes] = await Promise.all([
      pingaService.getCounts(),
      pingaService.getHistory()
    ]);
    if (countsRes.status === 200) counts.value = countsRes.data;
    if (historyRes.status === 200) history.value = historyRes.data;
  } catch {
    toast.add({ severity: "error", summary: "Erro", detail: "Erro ao carregar dados", life: 3000 });
  } finally {
    loading.value = false;
  }
}

let refreshInterval: number | undefined;

onMounted(() => {
  loadData();
  refreshInterval = setInterval(loadData, 30000);
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>