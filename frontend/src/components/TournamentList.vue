<template>
  <P-Dialog v-model:visible="enabled" modal header="Lista de Torneios" class="w-11/12 md:w-10/12 lg:w-8/10 xl:w-4/5">
    <P-DataTable :value="tournamentStore.tournaments" striped-rows size="small">
      <P-Column field="name" header="Nome">
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <span>🏆</span>
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </P-Column>
      <P-Column header="Cor" class="w-24">
        <template #body="{ data }">
          <div class="flex items-center gap-1">
            <button
              v-for="c in TOURNAMENT_COLORS"
              :key="c.value"
              class="w-4 h-4 rounded-full border-2 transition-transform hover:scale-125 flex items-center justify-center"
              :class="[c.value !== 'none' ? c.dot : 'bg-white border-stone-400', getColor(data.id).value === c.value ? 'border-stone-700 scale-125' : c.value === 'none' ? 'border-stone-300' : 'border-transparent']"
              v-tooltip.top="c.label"
              @click="setColor(data.id, c.value)"
            >
              <span v-if="c.value === 'none'" class="text-stone-400 leading-none text-[9px]">✕</span>
            </button>
          </div>
        </template>
      </P-Column>
      <P-Column header="Equipas">
        <template #body="{ data }">
          <P-Tag :value="`${data.teams?.length || 0}`" severity="info" />
        </template>
      </P-Column>
      <P-Column header="Jogos">
        <template #body="{ data }">
          <P-Tag :value="`${data.games?.length || 0}`" severity="success" />
        </template>
      </P-Column>
      <P-Column header="Eliminatórias" class="w-5rem">
        <template #body="{ data }">
          <span
            v-if="canManageGames"
            class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-blue-600 hover:bg-blue-50"
            @click.stop="openKnockoutPreview(data)"
            v-tooltip.top="'Ver eliminatórias'"
          >sports_soccer</span>
        </template>
      </P-Column>
      <P-Column header="Eliminar" class="w-5rem">
        <template #body="{ data }">
          <span
            class="material-symbols-outlined cursor-pointer text-xl p-1 rounded text-red-600 hover:bg-red-50"
            @click.stop="promptDelete(data)"
            v-tooltip.top="'Eliminar torneio'"
          >delete</span>
        </template>
      </P-Column>
    </P-DataTable>
    <template #footer>
      <P-Button @click="tournamentStore.forceGetTournaments()">
        <span class="material-symbols-outlined">sync</span>
        Atualizar
      </P-Button>
    </template>
</P-Dialog>

  <P-Dialog v-model:visible="showDeleteConfirm" modal header="Confirmar Eliminação" class="w-11/12 md:w-6/12">
    <p>Tem a certeza que deseja eliminar o torneio <strong>{{ tournamentToDelete?.name }}</strong>?</p>
    <p class="text-red-600 mt-2 text-sm">Esta ação não pode ser desfeita.</p>
    <template #footer>
      <P-Button severity="secondary" @click="showDeleteConfirm = false">Cancelar</P-Button>
      <P-Button severity="danger" :loading="deleting" @click="confirmDelete">Eliminar</P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showKnockoutPreview" modal header="Fase de Eliminatórias" class="w-11/12 md:w-8/12">
    <div v-if="knockoutLoading" class="text-center py-8">
      <P-ProgressSpinner />
    </div>
    <div v-if="knockoutData?.remaining" class="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-md">
      <p class="text-orange-700">
        <i class="pi pi-exclamation-triangle mr-2" />
        Ainda faltam {{ knockoutData.remaining }} jogo(s) de grupo por completar
      </p>
    </div>
    <P-DataTable :value="knockoutData?.knockout || []" striped-rows size="small">
        <P-Column field="label" header="Jogo">
          <template #body="{ data }">
            <span class="font-medium">{{ data.label }}</span>
          </template>
        </P-Column>
        <P-Column header="Casa">
          <template #body="{ data }">
            <div class="flex flex-col">
              <span class="text-xs text-stone-500">{{ data.home_placeholder }}</span>
              <span class="font-medium text-green-700">{{ data.home_resolved || '-' }}</span>
            </div>
          </template>
        </P-Column>
        <P-Column header="Fora">
          <template #body="{ data }">
            <div class="flex flex-col">
              <span class="text-xs text-stone-500">{{ data.away_placeholder }}</span>
              <span class="font-medium text-green-700">{{ data.away_resolved || '-' }}</span>
            </div>
          </template>
        </P-Column>
      </P-DataTable>
    <template #footer>
      <P-Button severity="secondary" @click="showKnockoutPreview = false">Fechar</P-Button>
      <P-Button
        v-if="knockoutData?.canAdvance"
        severity="primary"
        :loading="advancing"
        @click="promptAdvance"
      >
        Avançar para Eliminatórias
      </P-Button>
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showAdvanceConfirm" modal header="Confirmar Avanço" class="w-11/12 md:w-6/12">
    <p>Isto vai avançar todas as equipas vencedoras dos grupos para a fase de eliminatórias.</p>
    <p class="mt-2 font-medium">Esta ação não pode ser desfeita. Continuar?</p>
    <template #footer>
      <P-Button severity="secondary" @click="showAdvanceConfirm = false">Cancelar</P-Button>
      <P-Button severity="primary" :loading="advancing" @click="confirmAdvance">Confirmar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { useTournamentStore } from "@stores/tournaments";
import { useTeamStore } from "@stores/teams";
import { useAuthStore } from "@stores/auth";
import { useTournamentColors } from "@/composables/useTournamentColors";
import { previewKnockout, advanceToKnockout, type PreviewKnockoutResponse } from "@router/backend/services/tournament";

const { getColor, setColor, TOURNAMENT_COLORS } = useTournamentColors();

const enabled = defineModel<boolean>();
const toast = useToast();
const tournamentStore = useTournamentStore();
const teamStore = useTeamStore();
const authStore = useAuthStore();

const showDeleteConfirm = ref(false);
const deleting = ref(false);
const tournamentToDelete = ref<{ id: string; name: string } | null>(null);

// Simple ref for role check (avoids reactive loop in DataTable)
const canManageGames = ref(false);

// Knockout preview state
const showKnockoutPreview = ref(false);
const knockoutLoading = ref(false);
const knockoutData = ref<PreviewKnockoutResponse | null>(null);
const advancing = ref(false);
const showAdvanceConfirm = ref(false);
const selectedTournamentId = ref<string | null>(null);

async function openKnockoutPreview(data: { id: string; name: string }) {
  selectedTournamentId.value = data.id;
  showKnockoutPreview.value = true;
  knockoutLoading.value = true;

  try {
    const response = await previewKnockout(data.id);
    knockoutData.value = response.data as PreviewKnockoutResponse;
  } catch (error) {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível carregar a pré-visualização", life: 3000 });
  } finally {
    knockoutLoading.value = false;
  }
}

function promptAdvance() {
  showAdvanceConfirm.value = true;
}

async function confirmAdvance() {
  if (!selectedTournamentId.value) return;
  advancing.value = true;
  showAdvanceConfirm.value = false;

  try {
    const response = await advanceToKnockout(selectedTournamentId.value);
    const data = response.data as { success: boolean; updated_games: number };
    if (data.success) {
      toast.add({ severity: "success", summary: "Sucesso", detail: `${data.updated_games} jogo(s) atualizado(s)`, life: 3000 });
      showKnockoutPreview.value = false;
      await tournamentStore.getTournaments();
    }
  } catch (error) {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível avançar para a fase de eliminatórias", life: 3000 });
  } finally {
    advancing.value = false;
  }
}

function promptDelete(data: { id: string; name: string }) {
  const hasPlayers = teamStore.teams
    .filter(t => t.tournament === data.id)
    .some(t => t.players.length > 0);

  if (hasPlayers) {
    toast.add({ severity: "warn", summary: "Não permitido", detail: "Não é possível eliminar um турни que já tem jogadores associados.", life: 4000 });
    return;
  }
  tournamentToDelete.value = data;
  showDeleteConfirm.value = true;
}

async function confirmDelete() {
  if (!tournamentToDelete.value) return;
  deleting.value = true;
  const result = await tournamentStore.deleteTournament(tournamentToDelete.value.id);
  deleting.value = false;
  showDeleteConfirm.value = false;
  tournamentToDelete.value = null;
  if (result.success) {
    toast.add({ severity: "success", summary: "Sucesso", detail: "Torneio eliminado", life: 3000 });
  } else {
    toast.add({ severity: "error", summary: "Erro", detail: "Não foi possível eliminar o torneio", life: 3000 });
  }
}

onMounted(async () => {
  // Set role once to avoid reactive loops in DataTable
  canManageGames.value = authStore.canManageGames;

  await Promise.all([
    tournamentStore.getTournaments(),
    teamStore.getTeams(),
  ]);
});
</script>
