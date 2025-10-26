import { createRouter, createWebHistory } from "vue-router"

const routes = [{
    path: "/admin",
    name: "adminPanel",
    component: () => import("@views/AdminPanel.vue"),
    meta: {
      title: "Painel de Administração | " + import.meta.env.VUE_APP_NAME,
      requiresAuth: false,
    }
}];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router
