<template>
  <P-Dialog v-model:visible="enabled" modal header="Dias de Jogo" class="w-11/12 md:w-8/12 lg:w-6/12">
    <div class="flex flex-col gap-4">
      <P-FloatLabel variant="on">
        <P-Select
          id="tournament"
          v-model="selectedTournament"
          :options="tournamentStore.tournaments"
          optionLabel="name"
          optionValue="id"
          fluid
          @change="onTournamentChange"
        />
        <label for="tournament">Torneio</label>
      </P-FloatLabel>

      <div v-if="selectedTournament">
        <P-DatePicker
          v-model="selectedDates"
          selectionMode="multiple"
          :manualInput="false"
          inline
          fluid
          showIcon
        />

        <div v-if="selectedDates.length > 0" class="mt-3 border border-stone-200 rounded-lg overflow-hidden">
          <div class="bg-stone-100 px-3 py-2 text-sm font-semibold text-stone-600">
            {{ selectedDates.length }} dia{{ selectedDates.length > 1 ? 's' : '' }} selecionado{{ selectedDates.length > 1 ? 's' : '' }}
          </div>
          <ul class="divide-y divide-stone-100">
            <li
              v-for="(date, i) in sortedDates"
              :key="i"
              class="flex items-center justify-between px-3 py-2 text-sm text-stone-700"
            >
              {{ formatDate(date) }}
              <span
                class="material-symbols-outlined text-base cursor-pointer text-red-500 hover:text-red-700"
                @click="removeDate(date)"
              >close</span>
            </li>
          </ul>
        </div>

        <p v-else class="text-sm text-stone-400 text-center py-2">
          Clique no calendário para selecionar os dias disponíveis.
        </p>
      </div>
    </div>

    <template #footer>
      <P-Button severity="secondary" @click="close">
        <span class="material-symbols-outlined">close</span>
        Cancelar
      </P-Button>
      <P-Button :disabled="!selectedTournament" @click="save">
        <span class="material-symbols-outlined">save</span>
        Guardar
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useToast } from "primevue/usetoast";
import { useTournamentStore } from "@stores/tournaments";

const STORAGE_KEY = "game_days";

const toast = useToast();
const enabled = defineModel<boolean>();
const tournamentStore = useTournamentStore();

const selectedTournament = ref<string>("");
const selectedDates = ref<Date[]>([]);

const sortedDates = computed(() =>
  [...selectedDates.value].sort((a, b) => a.getTime() - b.getTime())
);

function onTournamentChange() {
  loadFromStorage();
}

function loadFromStorage() {
  const stored = localStorage.getItem(STORAGE_KEY);
  const all: Record<string, string[]> = stored ? JSON.parse(stored) : {};
  const dates = all[selectedTournament.value] ?? [];
  selectedDates.value = dates.map(d => new Date(d));
}

function save() {
  const stored = localStorage.getItem(STORAGE_KEY);
  const all: Record<string, string[]> = stored ? JSON.parse(stored) : {};
  all[selectedTournament.value] = selectedDates.value.map(d => d.toISOString());
  localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  toast.add({ severity: "success", summary: "Guardado", detail: "Dias de jogo guardados", life: 3000 });
  close();
}

function removeDate(date: Date) {
  selectedDates.value = selectedDates.value.filter(
    d => d.toDateString() !== date.toDateString()
  );
}

function formatDate(date: Date): string {
  return date.toLocaleDateString("pt-PT", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
}

function close() {
  enabled.value = false;
  selectedTournament.value = "";
  selectedDates.value = [];
}
</script>
