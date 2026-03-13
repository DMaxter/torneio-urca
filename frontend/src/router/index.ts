import { createRouter, createWebHistory } from "vue-router"

const routes = [
  {
    path: "/",
    name: "home",
    component: () => import("@views/HomeView.vue"),
    meta: {
      title: import.meta.env.VUE_APP_NAME,
      requiresAuth: false,
    }
  },
  {
    path: "/register",
    name: "teamRegistration",
    component: () => import("@views/TeamRegistration.vue"),
    meta: {
      title: "Register Team | " + import.meta.env.VUE_APP_NAME,
      requiresAuth: false,
    }
  },
  {
    path: "/admin",
    name: "adminPanel",
    component: () => import("@views/AdminPanel.vue"),
    meta: {
      title: "Admin Panel | " + import.meta.env.VUE_APP_NAME,
      requiresAuth: false,
    }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router
