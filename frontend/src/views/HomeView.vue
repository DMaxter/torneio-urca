<template>
  <div class="home">
    <div class="hero">
      <div class="hero-badge">São Pedro 2026</div>
      <h1>Torneio de Futsal</h1>
      <p class="subtitle">Organizado por URCA - Porto de Mos</p>
    </div>

    <div class="content">
      <div class="info-card">
        <div class="card-icon">📅</div>
        <h3>Inscrições Abertas</h3>
        <p class="deadline">
          Até <strong>8 de Maio de 2026</strong>
        </p>
        <router-link to="/register" class="cta-button">
          <P-Button size="large">
          <span class="material-symbols-outlined">how_to_reg</span>
          Registar Equipa
        </P-Button>
        </router-link>
      </div>

      <div class="features">
        <div class="feature">
          <span class="feature-icon">⚽</span>
          <span class="feature-text">Equipas de Futsal</span>
        </div>
        <div class="feature">
          <span class="feature-icon">🏆</span>
          <span class="feature-text">Torneio Competitivo</span>
        </div>
        <div class="feature">
          <span class="feature-icon">📋</span>
          <span class="feature-text">Gestão Integrada</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  background: #fafaf9;
}

.hero {
  text-align: center;
  margin-bottom: 2rem;
}

.hero-badge {
  display: inline-block;
  padding: 4px 12px;
  background: #fff7ed;
  color: #c2410c;
  border-radius: 50px;
  font-size: 0.6875rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hero h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1c1917;
  margin: 0 0 0.5rem 0;
  line-height: 1.2;
}

.subtitle {
  font-size: 0.9375rem;
  color: #78716c;
  margin: 0;
}

.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
  max-width: 400px;
}

.info-card {
  background: white;
  border: 1px solid #e7e5e4;
  border-radius: 16px;
  padding: 1.5rem;
  text-align: center;
  width: 100%;
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.info-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #292524;
  margin: 0 0 0.5rem 0;
}

.deadline {
  font-size: 0.875rem;
  color: #78716c;
  margin: 0 0 1.25rem 0;
}

.deadline strong {
  color: #f97316;
}

.cta-button {
  text-decoration: none;
  display: block;
  width: 100%;
}

.cta-button :deep(.p-button) {
  width: 100%;
  font-size: 0.9375rem;
}

.features {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: #78716c;
  font-size: 0.8125rem;
}

.feature-icon {
  font-size: 1rem;
}

.feature-text {
  font-weight: 500;
}

/* Large phones */
@media (min-width: 480px) {
  .hero h1 {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .info-card {
    padding: 2rem;
  }

  .card-icon {
    font-size: 3rem;
  }

  .info-card h3 {
    font-size: 1.25rem;
  }

  .deadline {
    font-size: 0.9375rem;
  }
}

/* Tablets */
@media (min-width: 768px) {
  .home {
    padding: 3rem 2rem;
  }

  .hero {
    margin-bottom: 3rem;
  }

  .hero-badge {
    padding: 6px 16px;
    font-size: 0.75rem;
    margin-bottom: 1rem;
  }

  .hero h1 {
    font-size: 2.5rem;
  }

  .subtitle {
    font-size: 1.125rem;
  }

  .content {
    gap: 2rem;
    max-width: 500px;
  }

  .info-card {
    padding: 2.5rem;
    border-radius: 20px;
  }

  .card-icon {
    font-size: 3.5rem;
    margin-bottom: 0.75rem;
  }

  .info-card h3 {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
  }

  .deadline {
    font-size: 1rem;
    margin-bottom: 1.5rem;
  }

  .cta-button :deep(.p-button) {
    font-size: 1rem;
  }

  .features {
    gap: 1.5rem;
  }

  .feature {
    font-size: 0.9375rem;
  }

  .feature-icon {
    font-size: 1.25rem;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .hero h1 {
    font-size: 3rem;
  }

  .content {
    max-width: 560px;
  }
}
</style>
