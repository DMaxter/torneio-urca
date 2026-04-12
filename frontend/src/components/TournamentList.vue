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
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { useTournamentStore } from "@stores/tournaments";
import { useTeamStore } from "@stores/teams";
import { useTournamentColors } from "@/composables/useTournamentColors";

const { getColor, setColor, TOURNAMENT_COLORS } = useTournamentColors();

const enabled = defineModel<boolean>();
const toast = useToast();
const tournamentStore = useTournamentStore();
const teamStore = useTeamStore();

const showDeleteConfirm = ref(false);
const deleting = ref(false);
const tournamentToDelete = ref<{ id: string; name: string } | null>(null);

function promptDelete(data: { id: string; name: string }) {
  const hasPlayers = teamStore.teams
    .filter(t => t.tournament === data.id)
    .some(t => t.players.length > 0);

  if (hasPlayers) {
    toast.add({ severity: "warn", summary: "Não permitido", detail: "Não é possível eliminar um torneio que já tem jogadores associados.", life: 4000 });
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
  await Promise.all([
    tournamentStore.getTournaments(),
    teamStore.getTeams(),
  ]);
});
</script>
