import { defineStore } from "pinia";
import { ref } from "vue";

import { type GameDay } from "@router/backend/services/game_day/types";
import * as gameDayService from "@router/backend/services/game_day";

export const useGameDayStore = defineStore("gameDaysStore", () => {
  const gameDays = ref<GameDay[]>([]);

  async function forceGetGameDays() {
    try {
      const { status, data } = await gameDayService.getGameDays();
      if (status === 200) {
        gameDays.value = data as GameDay[];
      }
    } catch {}
  }

  async function getGameDays() {
    if (gameDays.value.length > 0) return;
    await forceGetGameDays();
  }

  async function createGameDay(day: import("@router/backend/services/game_day/types").CreateGameDay) {
    try {
      const { status, data } = await gameDayService.createGameDay(day);
      if (status === 201) {
        gameDays.value.push(data as GameDay);
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  async function deleteGameDay(id: string) {
    try {
      const { status } = await gameDayService.deleteGameDay(id);
      if (status === 204) {
        gameDays.value = gameDays.value.filter(d => d.id !== id);
        return { success: true };
      }
      return { success: false };
    } catch {
      return { success: false };
    }
  }

  return { gameDays, getGameDays, forceGetGameDays, createGameDay, deleteGameDay };
});
