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
          @update:modelValue="onDatesChange"
        />

        <div v-if="pendingDays.length > 0" class="mt-3 border border-stone-200 rounded-lg overflow-hidden">
          <div class="bg-stone-100 px-3 py-2 text-sm font-semibold text-stone-600">
            {{ pendingDays.length }} dia{{ pendingDays.length > 1 ? 's' : '' }} selecionado{{ pendingDays.length > 1 ? 's' : '' }}
          </div>
          <ul class="divide-y divide-stone-100">
            <li v-for="day in sortedDays" :key="day.date" class="px-3 py-2">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-stone-700">{{ formatDate(day.date) }}</span>
                <span
                  class="material-symbols-outlined text-base cursor-pointer text-red-500 hover:text-red-700"
                  @click="removeDay(day.date)"
                >close</span>
              </div>
              <div class="flex gap-3">
                <P-FloatLabel variant="on" class="flex-1">
                  <P-InputText
                    :id="`games-${day.date}`"
                    v-model.number="day.numGames"
                    type="number"
                    min="1"
                    fluid
                  />
                  <label :for="`games-${day.date}`">Jogos por dia</label>
                </P-FloatLabel>
                <P-FloatLabel variant="on" class="flex-1">
                  <P-InputText
                    :id="`time-${day.date}`"
                    v-model="day.startTime"
                    type="time"
                    fluid
                  />
                  <label :for="`time-${day.date}`">Hora de início</label>
                </P-FloatLabel>
              </div>
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
      <P-Button :disabled="!selectedTournament || saving" :loading="saving" @click="save">
        <span class="material-symbols-outlined">save</span>
        Guardar
      </P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { useGameDayStore } from "@stores/game_days";
import { useTournamentStore } from "@stores/tournaments";
import { CreateGameDay } from "@router/backend/services/game_day/types";

const toast = useToast();
const enabled = defineModel<boolean>();
const gameDayStore = useGameDayStore();
const tournamentStore = useTournamentStore();

const selectedTournament = ref<string>("");
const selectedDates = ref<Date[]>([]);
const saving = ref(false);

interface PendingDay {
  date: string;      // "YYYY-MM-DD"
  numGames: number;
  startTime: string;
  existingId?: string; // set if already saved in backend
}

const pendingDays = ref<PendingDay[]>([]);

const sortedDays = computed(() =>
  [...pendingDays.value].sort((a, b) => a.date.localeCompare(b.date))
);

function onTournamentChange() {
  loadForTournament();
}

function loadForTournament() {
  const existing = gameDayStore.gameDays.filter(d => d.tournament === selectedTournament.value);
  pendingDays.value = existing.map(d => ({
    date: d.date,
    numGames: d.num_games,
    startTime: d.start_time,
    existingId: d.id,
  }));
  selectedDates.value = pendingDays.value.map(d => new Date(d.date + "T12:00:00"));
}

function onDatesChange() {
  const selectedKeys = selectedDates.value.map(d => toDateKey(d));
  // Remove deselected
  pendingDays.value = pendingDays.value.filter(d => selectedKeys.includes(d.date));
  // Add newly selected
  for (const key of selectedKeys) {
    if (!pendingDays.value.find(d => d.date === key)) {
      pendingDays.value.push({ date: key, numGames: 4, startTime: "20:00" });
    }
  }
}

function toDateKey(d: Date): string {
  return d.toISOString().slice(0, 10);
}

async function save() {
  saving.value = true;

  const existing = gameDayStore.gameDays.filter(d => d.tournament === selectedTournament.value);
  const pendingKeys = pendingDays.value.map(d => d.date);

  // Delete removed days
  for (const day of existing) {
    if (!pendingKeys.includes(day.date)) {
      await gameDayStore.deleteGameDay(day.id);
    }
  }

  // Create or update each pending day
  for (const day of pendingDays.value) {
    const existingDay = existing.find(e => e.date === day.date);
    if (existingDay) {
      // If config changed, delete and recreate
      if (existingDay.num_games !== day.numGames || existingDay.start_time !== day.startTime) {
        await gameDayStore.deleteGameDay(existingDay.id);
        const dto = new CreateGameDay();
        dto.tournament = selectedTournament.value;
        dto.date = day.date;
        dto.num_games = day.numGames;
        dto.start_time = day.startTime;
        await gameDayStore.createGameDay(dto);
      }
    } else {
      const dto = new CreateGameDay();
      dto.tournament = selectedTournament.value;
      dto.date = day.date;
      dto.num_games = day.numGames;
      dto.start_time = day.startTime;
      await gameDayStore.createGameDay(dto);
    }
  }

  saving.value = false;
  toast.add({ severity: "success", summary: "Guardado", detail: "Dias de jogo guardados", life: 3000 });
  close();
}

function removeDay(dateKey: string) {
  pendingDays.value = pendingDays.value.filter(d => d.date !== dateKey);
  selectedDates.value = pendingDays.value.map(d => new Date(d.date + "T12:00:00"));
}

function formatDate(dateKey: string): string {
  return new Date(dateKey + "T12:00:00").toLocaleDateString("pt-PT", {
    weekday: "long", day: "numeric", month: "long", year: "numeric",
  });
}

function close() {
  enabled.value = false;
  selectedTournament.value = "";
  selectedDates.value = [];
  pendingDays.value = [];
}

onMounted(async () => {
  await Promise.all([
    gameDayStore.getGameDays(),
    tournamentStore.getTournaments(),
  ]);
});
</script>
