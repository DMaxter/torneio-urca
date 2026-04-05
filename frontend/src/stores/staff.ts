import { defineStore } from "pinia";
import * as staffService from "@router/backend/services/staff";
import type { Staff } from "@router/backend/services/staff/types";

export const useStaffStore = defineStore("staff", {
  state: () => ({
    staff: [] as Staff[],
  }),

  actions: {
    async getStaff() {
      const result = await staffService.getStaff();
      if (result.status === 200) {
        this.staff = result.data as Staff[];
      }
    },
  },
});
