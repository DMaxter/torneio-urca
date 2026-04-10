<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-brand">
        <span class="footer-logo">⚽</span>
        <div class="footer-info">
          <span class="footer-title">Torneio de Futsal de São Pedro</span>
          <span class="footer-subtitle">Organizado by URCA - Porto de Mós</span>
        </div>
      </div>
      <div class="footer-contact">
        <P-Button 
          label="Política de Privacidade" 
          link 
          class="privacy-link"
          @click="goToPrivacy"
        />
        <span class="footer-year">2026</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

function goToPrivacy() {
  router.push("/privacidade");
}
</script>

<style scoped>
.footer {
  background: var(--p-surface-900);
  color: var(--p-surface-300);
  padding: 1rem 2rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.footer-logo {
  font-size: 1.5rem;
}

.footer-info {
  display: flex;
  flex-direction: column;
}

.footer-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--p-surface-100);
}

.footer-subtitle {
  font-size: 0.75rem;
  opacity: 0.7;
}

.footer-year {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--p-primary-400);
}

.privacy-link {
  font-size: 0.875rem;
  color: var(--p-surface-300);
  text-decoration: underline;
  margin-right: 1rem;
}

.privacy-link:hover {
  color: var(--p-primary-400);
}

@media (max-width: 640px) {
  .footer-content {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .footer-brand {
    flex-direction: column;
  }
}
</style>
