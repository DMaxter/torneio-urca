import { ref, onMounted, onUnmounted, computed } from "vue";

export const REGISTRATION_DEADLINE = new Date("2026-05-10T23:59:59");

const now = ref(new Date());
let interval: ReturnType<typeof setInterval> | null = null;

function startInterval() {
  if (!interval) {
    interval = setInterval(() => {
      now.value = new Date();
    }, 1000);
  }
}

function stopInterval() {
  if (interval) {
    clearInterval(interval);
    interval = null;
  }
}

export function useRegistrationDeadline() {
  onMounted(() => {
    startInterval();
  });

  onUnmounted(() => {
    stopInterval();
  });

  const timeLeft = computed(() => {
    const diff = REGISTRATION_DEADLINE.getTime() - now.value.getTime();
    if (diff <= 0) return null;

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    return { days, hours, minutes, seconds };
  });

  const isOpen = computed(() => timeLeft.value !== null);

  return { timeLeft, isOpen };
}
