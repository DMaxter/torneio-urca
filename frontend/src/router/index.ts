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
    path: "/login",
    name: "login",
    component: () => import("@views/LoginView.vue"),
    meta: {
      title: "Login | " + import.meta.env.VUE_APP_NAME,
      requiresAuth: false,
    }
  },
  {
    path: "/admin",
    name: "adminPanel",
    component: () => import("@views/AdminPanel.vue"),
    meta: {
      title: "Admin Panel | " + import.meta.env.VUE_APP_NAME,
      requiresAuth: true,
    }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem("auth_token");
  if (to.meta.requiresAuth && !token) {
    next("/login");
  } else {
    next();
  }
});

export default router
