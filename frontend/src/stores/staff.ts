import { defineStore } from "pinia";
import * as staffService from "@router/backend/services/staff";
import type { Staff } from "@router/backend/services/staff/types";

export const useStaffStore = defineStore("staff", {
  state: () => ({
    staff: [] as Staff[],
  }),

  actions: {
    /** Fetches staff unconditionally from the backend. */
    async forceGetStaff() {
      const result = await staffService.getStaff();
      if (result.status === 200) {
        this.staff = result.data as Staff[];
      }
    },

    /** Fetches staff only if the store is empty. */
    async getStaff() {
      if (this.staff.length > 0) return;
      await this.forceGetStaff();
    },
  },
});
