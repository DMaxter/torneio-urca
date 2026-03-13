<template>
  <TopBar />
  <RouterView />
  <P-Toast />
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
import { useToast } from "primevue/usetoast";
import { setToast } from "@router/backend/api";
import "@styles/global.css";

const toast = useToast();
setToast(toast);
</script>
