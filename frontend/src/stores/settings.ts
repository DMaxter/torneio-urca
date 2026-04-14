import { defineStore } from "pinia";
import { ref } from "vue";
import * as settingsService from "@router/backend/services/settings";

export const useSettingsStore = defineStore("settingsStore", () => {
  const calendarLocked = ref(false);

  async function fetchSettings() {
    try {
      const { data } = await settingsService.getSettings();
      calendarLocked.value = data.calendar_locked;
    } catch {}
  }

  async function toggleCalendarLock(): Promise<boolean> {
    try {
      const { data } = await settingsService.toggleCalendarLock();
      calendarLocked.value = data.calendar_locked;
      return true;
    } catch {
      return false;
    }
  }

  return { calendarLocked, fetchSettings, toggleCalendarLock };
});
