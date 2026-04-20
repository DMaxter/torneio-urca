<template>
  <div
    ref="canvasRef"
    class="post-canvas-container"
    style="width: 1080px; height: 1080px; background: #000; color: #fff; overflow: hidden; position: relative; font-family: 'Inter', sans-serif;"
  >
    <!-- Background Accents -->
    <div class="absolute -top-40 -right-40 w-96 h-96 bg-orange-600/30 rounded-full blur-[100px]"></div>
    <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-orange-600/20 rounded-full blur-[100px]"></div>
    <div class="absolute inset-0 bg-gradient-to-tr from-black via-zinc-950 to-orange-950/20"></div>

    <div class="relative z-10 w-full h-full flex flex-col p-10">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-4 bg-white/10 p-3 rounded-2xl border border-white/5 shrink-0 flex-nowrap">
            <img src="/static/urca.jpg" alt="URCA" class="w-14 h-14 object-contain rounded-lg flex-none" @error="onLogoError" />
            <img src="/static/cmpm.jpg" alt="CMPM" class="w-14 h-14 object-contain rounded-lg flex-none" @error="onLogoError" />
            <img src="/static/nafpm.jpg" alt="NAFPM" class="w-14 h-14 object-contain rounded-lg flex-none" @error="onLogoError" />
          </div>
          <div class="h-16 w-1 bg-orange-500 rounded-full"></div>
          <div>
            <h1 class="text-3xl font-black italic tracking-tighter uppercase leading-none">
              XII Torneio de Futsal<br />
              <span class="text-orange-500 text-2xl">de São Pedro</span>
            </h1>
          </div>
        </div>
        <div class="text-right">
          <div class="text-orange-500 font-bold text-xl uppercase tracking-widest">{{ subtitle }}</div>
          <div class="text-zinc-500 font-semibold uppercase tracking-tight">{{ date }}</div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 flex flex-col justify-center min-h-0">
        <!-- TITLE (Only for non-standings) -->
        <h2 v-if="type !== 'standings'" class="text-5xl font-black italic uppercase mb-6 tracking-tighter leading-tight drop-shadow-lg">
          {{ title }}
        </h2>

        <!-- CONTENT SLOTS -->
        <div :class="['w-full min-h-0', type !== 'standings' ? 'bg-white/5 backdrop-blur-md rounded-3xl border border-white/10 p-6 shadow-2xl' : '']">
          
          <!-- TYPE: RESULTS -->
          <div v-if="type === 'results'" class="space-y-4">
            <div v-for="game in data" :key="game.id" class="flex items-center justify-between gap-4 py-4 px-6 bg-black/40 rounded-2xl border border-white/5">
               <div class="flex-1 text-right text-3xl font-black truncate text-white uppercase">{{ game.home }}</div>
               <div class="flex flex-col items-center gap-1 mx-4">
                 <span class="text-orange-500/50 font-black italic text-xs uppercase tracking-widest">VS</span>
                 <div class="flex items-center gap-3 bg-white text-black px-6 py-2 rounded-xl">
                   <span class="text-4xl font-black tabular-nums">{{ game.homeScore }}</span>
                   <span class="text-2xl font-bold opacity-30">-</span>
                   <span class="text-4xl font-black tabular-nums">{{ game.awayScore }}</span>
                 </div>
               </div>
               <div class="flex-1 text-left text-3xl font-black truncate text-white uppercase">{{ game.away }}</div>
            </div>
          </div>

          <!-- TYPE: STANDINGS (NEW) -->
          <div v-else-if="type === 'standings'" class="space-y-8">
            <h2 class="text-center text-7xl font-black text-white italic mb-12 uppercase tracking-tighter drop-shadow-2xl">
              Classificação <span class="text-orange-500">Final</span>
            </h2>
            <div class="grid grid-cols-1 gap-6 max-w-3xl mx-auto">
              <div 
                v-for="res in data"
                :key="res.pos"
                :class="[
                  'flex items-center gap-8 p-8 rounded-3xl border transition-all duration-500',
                  res.pos === '1º' ? 'bg-gradient-to-r from-amber-500/30 to-amber-900/20 border-amber-500/50 scale-105 shadow-2xl shadow-amber-500/20' : 'bg-zinc-900/80 border-white/10'
                ]"
              >
                <div :class="[
                  'w-24 h-24 rounded-2xl flex items-center justify-center text-4xl font-black italic shadow-lg',
                  res.pos === '1º' ? 'bg-amber-400 text-amber-950 rotate-3' : 
                  res.pos === '2º' ? 'bg-zinc-300 text-zinc-800' :
                  res.pos === '3º' ? 'bg-amber-700 text-white' : 'bg-zinc-800 text-zinc-500'
                ]">
                  {{ res.pos }}
                </div>
                <div class="flex-1">
                  <div class="text-zinc-500 text-sm font-black uppercase tracking-[0.2em] mb-1">
                    {{ res.pos === '1º' ? 'Grandes Campeões' : res.pos === '2º' ? 'Vice-Campeões' : 'Finalistas' }}
                  </div>
                  <div :class="['font-black uppercase tracking-tighter leading-none', res.pos === '1º' ? 'text-6xl text-amber-50' : 'text-5xl text-zinc-100']">
                    {{ res.team }}
                  </div>
                </div>
                <div v-if="res.pos === '1º'" class="scale-150 mr-4">
                  <svg width="56" height="56" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="#F59E0B"/>
                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- TYPE: CLASSIFICATION -->
          <div v-else-if="type === 'classification'" class="w-full">
            <table class="w-full border-collapse">
              <thead>
                <tr class="text-orange-500 text-2xl font-black uppercase tracking-wider text-left border-b-2 border-orange-500/30">
                  <th class="pb-6 px-4">#</th>
                  <th class="pb-6">Equipa</th>
                  <th class="pb-6 text-center px-4">J</th>
                  <th class="pb-6 text-center px-4">V</th>
                  <th class="pb-6 text-center px-4">E</th>
                  <th class="pb-6 text-center px-4">D</th>
                  <th class="pb-6 text-right px-4">Pts</th>
                </tr>
              </thead>
              <tbody class="text-3xl font-bold">
                <tr v-for="(team, index) in data" :key="team.name" class="border-b border-white/5 last:border-0 hover:bg-white/5 transition-colors">
                  <td class="py-4 px-4 text-zinc-500 italic">{{ index + 1 }}</td>
                  <td class="py-4 font-black text-zinc-100 uppercase tracking-tight">{{ team.name }}</td>
                  <td class="py-4 text-center text-zinc-400 bg-white/5">{{ team.games }}</td>
                  <td class="py-4 text-center text-zinc-400">{{ team.wins }}</td>
                  <td class="py-4 text-center text-zinc-400">{{ team.ties }}</td>
                  <td class="py-4 text-center text-zinc-400">{{ team.losses }}</td>
                  <td class="py-4 px-4 text-right text-orange-500 text-5xl font-black tabular-nums">{{ team.points }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- TYPE: CALENDAR -->
          <div v-else-if="type === 'calendar'" class="space-y-8 overflow-y-auto max-h-full pr-4">
            <div v-for="day in (data as any[])" :key="day.date" class="bg-black/40 border border-white/5 rounded-3xl p-8 shadow-xl">
              <!-- Day Header -->
              <div class="flex items-center gap-4 mb-6">
                <div class="bg-orange-500 text-black font-black px-8 py-3 rounded-2xl text-2xl italic uppercase tracking-tighter">
                  {{ day.date }}
                </div>
                <div class="h-1 flex-1 bg-white/10 rounded-full"></div>
              </div>

              <!-- Games List -->
              <div class="grid grid-cols-1 gap-4">
                <div v-for="game in day.games" :key="game.id" class="flex items-center gap-6">
                  <div class="text-orange-500 font-black text-3xl w-24 tabular-nums italic text-right">{{ game.time }}</div>
                  
                  <div class="flex-1 flex items-center justify-between gap-6 bg-white/5 p-5 rounded-2xl border border-white/5 overflow-hidden">
                    <span class="flex-1 font-black text-2xl truncate text-right text-zinc-100 uppercase tracking-tight">{{ game.home }}</span>
                    <span class="text-orange-500/50 font-black italic text-sm uppercase px-2 shrink-0">VS</span>
                    <span class="flex-1 font-black text-2xl truncate text-left text-zinc-100 uppercase tracking-tight">{{ game.away }}</span>
                  </div>

                  <div v-if="game.tag" class="bg-zinc-800 text-zinc-400 text-[12px] px-3 py-1.5 rounded-lg uppercase font-black shrink-0 border border-white/5">
                    {{ game.tag }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty state filler if needed -->
            <div v-if="data.length === 0" class="py-20 text-center text-zinc-500 italic text-2xl font-bold uppercase tracking-widest">
               Nenhum jogo agendado.
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-8 pt-8 border-t border-white/10 flex justify-between items-center text-zinc-500 font-black uppercase tracking-[0.3em] italic text-sm">
        <div>#TorneioSaoPedro2026</div>
        <div class="flex gap-6 items-center">
          <div class="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
          <span>Siga em direto na plataforma</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

defineProps<{
  type: 'results' | 'classification' | 'calendar' | 'standings';
  title: string;
  subtitle: string;
  date: string;
  data: any[];
}>();

const canvasRef = ref<HTMLElement | null>(null);

function onLogoError(e: Event) {
  (e.target as HTMLImageElement).style.visibility = 'hidden';
}

defineExpose({
  getCanvas: () => canvasRef.value
});
</script>

<style scoped>
.post-canvas-container {
  box-sizing: border-box;
}
.post-canvas-container * {
  box-sizing: border-box;
}

/* Custom scrollbar for calendar if needed */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}
.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(249, 115, 22, 0.3);
  border-radius: 4px;
}
</style>
