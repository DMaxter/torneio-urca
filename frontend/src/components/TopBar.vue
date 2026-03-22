<template>
  <header class="topbar">
    <div class="topbar-content">
      <router-link to="/" class="logo">
        <span class="logo-icon">⚽</span>
        <span class="logo-text">Torneio URCA</span>
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
        <router-link to="/register" class="nav-link cta-link" @click="menuOpen = false">
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

const menuOpen = ref(false);
</script>

<style scoped>
.topbar {
  background: #1c1917;
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
  color: #f97316;
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
  background: #d6d3d1;
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
  color: #d6d3d1;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.nav-link:hover {
  background: #292524;
  color: white;
}

.nav-link.router-link-active {
  background: #f97316;
  color: white;
  font-weight: 600;
}

  .cta-link {
    background: #f97316;
    color: white !important;
  }

  .cta-link:hover {
    background: #ea580c !important;
  }

  .admin-link {
    background: #44403c;
    color: white !important;
  }

  .admin-link:hover {
    background: #57534e !important;
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
    background: #1c1917;
    border: 1px solid #292524;
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
    color: #d6d3d1;
    margin: 0 0.5rem;
  }

  .nav-link:hover {
    background: #292524;
    color: white;
  }

  .nav-link.router-link-active {
    background: #f97316;
    color: white;
  }

  .cta-link,
  .admin-link {
    text-align: center;
  }
}
</style>
