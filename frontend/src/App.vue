<template>
  <div class="app-layout">
    <TopBar />
    <main class="main-content">
      <RouterView />
    </main>
    <FooterBar />
  </div>
  <P-Toast />
</template>

<script setup lang="ts">
import { useToast } from "primevue/usetoast";
import { setToast } from "@router/backend/api";
import "@styles/global.css";

const toast = useToast();
setToast(toast);
</script>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
}

.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
