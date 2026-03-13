<template>
  <div class="home">
    <div class="hero">
      <h1>Torneio de Futsal de São Pedro 2026</h1>
      <p class="organized-by">Organizado por URCA</p>
    </div>

    <div class="info-section">
      <div class="registration-info">
        <h3>Inscrições</h3>
        <p class="deadline">
          As inscrições estão abertas até <strong>8 de Maio de 2026</strong>
        </p>
        <router-link to="/register">
          <P-Button label="Registar Equipa" size="large" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style lang="scss" scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
}

.hero {
  text-align: center;
  margin-bottom: 60px;

  h1 {
    font-size: 3rem;
    margin-bottom: 10px;
    color: #4fc3f7;
  }

  h2 {
    font-size: 2rem;
    margin-bottom: 20px;
    font-weight: 400;
  }

  .organized-by {
    font-size: 1.2rem;
    opacity: 0.8;
  }
}

.info-section {
  text-align: center;

  .registration-info {
    background: rgba(255, 255, 255, 0.1);
    padding: 40px 60px;
    border-radius: 16px;
    backdrop-filter: blur(10px);

    h3 {
      font-size: 1.8rem;
      margin-bottom: 20px;
    }

    .deadline {
      font-size: 1.2rem;
      margin-bottom: 30px;

      strong {
        color: #ffeb3b;
      }
    }

    a {
      text-decoration: none;
    }
  }
}
</style>
