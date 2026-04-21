<template>
  <header class="topbar">
    <div class="topbar-content">
      <router-link to="/" class="logo">
        <span class="logo-icon">⚽</span>
        <span class="logo-text">Torneio de Futsal de São Pedro</span>
      </router-link>

      <button class="menu-toggle" @click="menuOpen = !menuOpen" aria-label="Toggle menu">
        <span class="menu-icon" :class="{ open: menuOpen }">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>

      <nav class="nav-items" :class="{ open: menuOpen }">
        <router-link to="/" class="nav-link" @click="menuOpen = false">
          Início
        </router-link>
        <router-link to="/dashboard" class="nav-link" @click="menuOpen = false">
          Dashboard
        </router-link>
        <router-link to="/classifications" class="nav-link" @click="menuOpen = false">
          Classificações
        </router-link>
        <router-link to="/prizes" class="nav-link" @click="menuOpen = false">
          Prémios
        </router-link>
        <router-link to="/calendar" class="nav-link" @click="menuOpen = false">
          Calendário
        </router-link>
        <router-link to="/pinga" class="nav-link" @click="menuOpen = false">
          Taça da Pinga
        </router-link>
        <router-link v-if="isRegistrationOpen" to="/register" class="nav-link cta-link" @click="menuOpen = false">
          Registar Equipa
        </router-link>
        <router-link to="/admin" class="nav-link admin-link" @click="menuOpen = false">
          Administração
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRegistrationDeadline } from "@composables/useRegistrationDeadline";

const { isOpen: isRegistrationOpen } = useRegistrationDeadline();
const menuOpen = ref(false);
</script>

<style scoped>
.topbar {
  background: var(--color-stone-900);
  position: sticky;
  top: 0;
  z-index: 100;
}

.topbar-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  color: var(--color-orange-500);
}

.logo-icon {
  font-size: 1.5rem;
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
}

.menu-icon {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 24px;
}

.menu-icon span {
  display: block;
  height: 2px;
  background: var(--color-stone-300);
  border-radius: 2px;
  transition: all 0.2s ease;
}

.menu-icon.open span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.menu-icon.open span:nth-child(2) {
  opacity: 0;
}

.menu-icon.open span:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

.nav-items {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link {
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--color-stone-300);
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  transition: color 0.15s ease;
}

.nav-link.router-link-active {
  color: var(--color-orange-500);
  border-bottom-color: var(--color-orange-500);
  background: var(--color-stone-800);
}

  .cta-link,
  .admin-link {
    margin: 0 0.5rem;
  }

/* Mobile */
@media (max-width: 768px) {
  .menu-toggle {
    display: flex;
  }

  .topbar-content {
    position: relative;
    height: auto;
    min-height: 60px;
    padding: 0.75rem 1rem;
  }

  .logo {
    flex: 1;
  }

  .logo-text {
    font-size: 1.125rem;
  }

  .nav-items {
    display: none;
    position: absolute;
    top: 100%;
    left: 0.75rem;
    right: 0.75rem;
    flex-direction: column;
    background: var(--color-stone-900);
    border: 1px solid var(--color-stone-800);
    border-radius: 8px;
    padding: 0.5rem 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  .nav-items.open {
    display: flex;
  }

  .nav-link {
    padding: 1rem 1.25rem;
    border-radius: 6px;
    font-size: 1rem;
    color: var(--color-stone-300);
    margin: 0 0.5rem;
    border-bottom: 2px solid transparent;
  }

  .nav-link.router-link-active {
    color: var(--color-orange-500);
    border-bottom-color: var(--color-orange-500);
    background: var(--color-stone-800);
  }

  .cta-link,
  .admin-link {
    text-align: center;
  }
}
</style>
