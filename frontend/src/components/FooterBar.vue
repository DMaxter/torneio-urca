<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-brand">
        <span class="footer-logo">⚽</span>
        <div class="footer-info">
          <span class="footer-title">Torneio de Futsal de São Pedro</span>
          <span class="footer-subtitle">Organizado por URCA - Porto de Mos</span>
        </div>
      </div>
      <div class="footer-contact">
        <span class="footer-year">2026</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
.footer {
  background: var(--p-surface-900);
  color: var(--p-surface-300);
  padding: 1rem 2rem;
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
