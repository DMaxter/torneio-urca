import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@stores/auth";

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
    path: "/calendario",
    name: "calendar",
    component: () => import("@views/CalendarView.vue"),
    meta: {
      title: "Calendário | " + import.meta.env.VUE_APP_NAME,
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
  },
   {
     path: "/game-calls",
     name: "gameCalls",
     component: () => import("@views/GameCallsView.vue"),
     meta: {
       title: "Chamada de Jogadores | " + import.meta.env.VUE_APP_NAME,
       requiresAuth: true,
     }
   },
   {
     path: "/admin/live-game/:gameId",
     name: "liveGame",
     component: () => import("@views/LiveGameManagement.vue"),
     meta: {
       title: "Jogo ao Vivo | " + import.meta.env.VUE_APP_NAME,
       requiresAuth: true,
     }
   },
   {
     path: "/admin/staff",
     name: "staffManagement",
     component: () => import("@views/StaffManagement.vue"),
     meta: {
       title: "Gestão de Staff | " + import.meta.env.VUE_APP_NAME,
       requiresAuth: true,
     }
   }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  await authStore.init();
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next("/login");
  }
  return next();
});

export default router
