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
    path: "/classifications",
    name: "classifications",
    component: () => import("@views/ClassificationsView.vue"),
    meta: {
      title: "Classifications | " + import.meta.env.VUE_APP_NAME,
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

function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return true;
    const payload = JSON.parse(atob(parts[1]));
    if (!payload.exp) return true;
    return Date.now() >= payload.exp * 1000;
  } catch {
    return true;
  }
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? match[2] : null;
}

router.beforeEach((to, _from, next) => {
  const token = getCookie("auth_token");
  if (to.meta.requiresAuth && (!token || isTokenExpired(token))) {
    next("/login");
  } else {
    next();
  }
});

export default router
