<template>
  <P-Dialog v-model:visible="enabled" modal header="Dias de Jogo" class="w-11/12 md:w-8/12 lg:w-6/12">
    <div class="flex flex-col gap-4">
      <P-FloatLabel class="mt-3" variant="on">
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
                  v-if="scheduledCountForDay(day.date) === 0"
                  class="material-symbols-outlined text-base cursor-pointer text-red-500 hover:text-red-700"
                  v-tooltip.left="'Remover dia'"
                  @click="removeDay(day.date)"
                >close</span>
                <span
                  v-else
                  class="material-symbols-outlined text-base text-stone-300 cursor-not-allowed"
                  v-tooltip.left="`Não é possível remover — ${scheduledCountForDay(day.date)} jogo(s) agendado(s)`"
                >close</span>
              </div>
              <div class="flex gap-3">
                <div class="flex-1">
                  <P-FloatLabel variant="on">
                    <P-InputText
                      :id="`games-${day.date}`"
                      v-model.number="day.numGames"
                      type="number"
                      :min="scheduledCountForDay(day.date) || 1"
                      fluid
                      @change="validateNumGames(day)"
                    />
                    <label :for="`games-${day.date}`">Jogos por dia</label>
                  </P-FloatLabel>
                  <p v-if="day.validationError" class="text-xs text-red-500 mt-1">{{ day.validationError }}</p>
                </div>
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
      <P-Button :disabled="!selectedTournament || saving || hasValidationErrors" :loading="saving" @click="save">
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
import { useGameStore } from "@stores/games";
import { useTournamentStore } from "@stores/tournaments";
import { CreateGameDay } from "@router/backend/services/game_day/types";

const toast = useToast();
const enabled = defineModel<boolean>();
const gameDayStore = useGameDayStore();
const gameStore = useGameStore();
const tournamentStore = useTournamentStore();

const selectedTournament = ref<string>("");
const selectedDates = ref<Date[]>([]);
const saving = ref(false);

interface PendingDay {
  date: string;
  numGames: number;
  startTime: string;
  existingId?: string;
  validationError?: string;
}

const pendingDays = ref<PendingDay[]>([]);

const sortedDays = computed(() =>
  [...pendingDays.value].sort((a, b) => a.date.localeCompare(b.date))
);

const hasValidationErrors = computed(() =>
  pendingDays.value.some(d => !!d.validationError)
);

function scheduledCountForDay(dateKey: string): number {
  return gameStore.games.filter(g => {
    if (!g.scheduled_date || g.tournament !== selectedTournament.value) return false;
    const sd = new Date(g.scheduled_date);
    const key = `${sd.getFullYear()}-${String(sd.getMonth() + 1).padStart(2, "0")}-${String(sd.getDate()).padStart(2, "0")}`;
    return key === dateKey;
  }).length;
}

function validateNumGames(day: PendingDay) {
  const scheduled = scheduledCountForDay(day.date);
  if (day.numGames < scheduled) {
    day.validationError = `Já existem ${scheduled} jogo(s) agendado(s) neste dia. Retire um jogo do calendário antes de reduzir.`;
    day.numGames = scheduled;
  } else {
    day.validationError = undefined;
  }
}

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

  // Block removal of days with scheduled games
  const blocked = pendingDays.value.filter(
    d => !selectedKeys.includes(d.date) && scheduledCountForDay(d.date) > 0
  );
  if (blocked.length > 0) {
    toast.add({
      severity: "warn",
      summary: "Não permitido",
      detail: `Não é possível remover dias com jogos agendados: ${blocked.map(d => formatDate(d.date)).join(", ")}`,
      life: 4000,
    });
    // Re-add blocked days back to selection
    selectedDates.value = pendingDays.value.map(d => new Date(d.date + "T12:00:00"));
    return;
  }

  pendingDays.value = pendingDays.value.filter(d => selectedKeys.includes(d.date));
  for (const key of selectedKeys) {
    if (!pendingDays.value.find(d => d.date === key)) {
      pendingDays.value.push({ date: key, numGames: 4, startTime: "20:00" });
    }
  }
}

function toDateKey(d: Date): string {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function getSlotMinutes(startTime: string, numGames: number): number[] {
  const [h, m] = startTime.split(":").map(Number);
  const result: number[] = [];
  for (let i = 0; i < numGames; i++) {
    result.push(h * 60 + m + i * 60);
  }
  return result;
}

function checkOverlap(day: typeof pendingDays.value[0]): string | null {
  // Other tournaments' game days on the same date (excluding current tournament)
  const others = gameDayStore.gameDays.filter(
    d => d.tournament !== selectedTournament.value && d.date === day.date
  );
  if (others.length === 0) return null;

  const newSlots = new Set(getSlotMinutes(day.startTime, day.numGames));
  for (const other of others) {
    const otherSlots = getSlotMinutes(other.start_time, other.num_games);
    const conflict = otherSlots.find(s => newSlots.has(s));
    if (conflict !== undefined) {
      const hh = String(Math.floor(conflict / 60)).padStart(2, "0");
      const mm = String(conflict % 60).padStart(2, "0");
      const otherName = tournamentStore.tournaments.find(t => t.id === other.tournament)?.name ?? "outro torneio";
      return `Sobreposição no dia ${formatDate(day.date)} às ${hh}:${mm} com "${otherName}". Ajusta a hora de início ou o número de jogos.`;
    }
  }
  return null;
}

async function save() {
  // Validate overlaps before persisting anything
  for (const day of pendingDays.value) {
    const error = checkOverlap(day);
    if (error) {
      toast.add({ severity: "warn", summary: "Sobreposição de horários", detail: error, life: 6000 });
      return;
    }
  }

  saving.value = true;

  const existing = gameDayStore.gameDays.filter(d => d.tournament === selectedTournament.value);
  const pendingKeys = pendingDays.value.map(d => d.date);

  for (const day of existing) {
    if (!pendingKeys.includes(day.date)) {
      await gameDayStore.deleteGameDay(day.id);
    }
  }

  for (const day of pendingDays.value) {
    const existingDay = existing.find(e => e.date === day.date);
    if (existingDay) {
      if (existingDay.num_games !== day.numGames || existingDay.start_time !== day.startTime) {
        await gameDayStore.deleteGameDay(existingDay.id);
        const dto = new CreateGameDay();
        dto.tournament = selectedTournament.value;
        dto.date = day.date;
        dto.num_games = day.numGames;
        dto.start_time = day.startTime;
        await gameDayStore.createGameDay(dto);

        // If start time changed, reschedule games on this day from the new start time
        if (existingDay.start_time !== day.startTime) {
          const dayGames = gameStore.games.filter(g => {
            if (!g.scheduled_date || g.tournament !== selectedTournament.value) return false;
            const sd = new Date(g.scheduled_date);
            return toDateKey(sd) === day.date;
          }).sort((a, b) =>
            new Date(a.scheduled_date!).getTime() - new Date(b.scheduled_date!).getTime()
          );
          const [h, m] = day.startTime.split(":").map(Number);
          for (let i = 0; i < dayGames.length; i++) {
            const totalMin = h * 60 + m + i * 60;
            const hh = Math.floor(totalMin / 60) % 24;
            const mm = totalMin % 60;
            const dt = new Date(`${day.date}T${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:00`);
            await gameStore.updateGame(dayGames[i].id, dt);
          }
        }
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
    gameStore.getGames(),
    tournamentStore.getTournaments(),
  ]);
});
</script>
