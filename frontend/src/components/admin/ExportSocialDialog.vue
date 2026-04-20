<template>
  <P-Dialog
    v-model:visible="visible"
    modal
    header="Exportar para Social & Impressão"
    class="w-full max-w-4xl"
    :breakpoints="{ '960px': '75vw', '640px': '95vw' }"
  >
    <P-Tabs value="0">
      <P-TabList>
        <P-Tab value="0">Resultados Diários</P-Tab>
        <P-Tab value="1">Classificações</P-Tab>
        <P-Tab value="2">Calendário</P-Tab>
        <P-Tab value="3">Eliminatórias</P-Tab>
      </P-TabList>
      
      <P-TabPanels>
        <!-- TAB 0: RESULTS -->
        <P-TabPanel value="0">
          <div class="space-y-4 pt-4">
            <div class="flex flex-col gap-2">
              <label class="text-sm font-bold text-stone-600">Selecionar Dia</label>
              <P-Select
                v-model="selectedDay"
                :options="gameDayStore.gameDays"
                optionLabel="date"
                placeholder="Escolha um dia"
                class="w-full"
              >
                <template #option="{ option }">
                  {{ formatDate(option.date) }}
                </template>
                <template #value="{ value }">
                  {{ value ? formatDate(value.date) : 'Escolha um dia' }}
                </template>
              </P-Select>
            </div>

            <div v-if="selectedDay" class="flex flex-col gap-4">
              <P-Button severity="secondary" @click="handlePrintDay" class="w-full">
                <span class="material-symbols-outlined">print</span>
                Imprimir Lista do Dia
              </P-Button>
              <P-Button severity="contrast" @click="exportResultsImage" :loading="exporting" class="w-full">
                <span class="material-symbols-outlined">image</span>
                Gerar Posts por Torneio ({{ tournamentsInDay }})
              </P-Button>
            </div>
            
            <div v-if="selectedDay && dayGames.length === 0" class="text-center py-4 text-stone-400 italic">
               Nenhum jogo registado para este dia.
            </div>
          </div>
        </P-TabPanel>

        <!-- TAB 1: CLASSIFICATIONS -->
        <P-TabPanel value="1">
          <div class="space-y-4 pt-4">
            <div class="flex flex-col gap-4">
               <P-Button severity="contrast" class="w-full" @click="exportAllClassifications" :loading="exporting">
                  <span class="material-symbols-outlined">analytics</span>
                  Gerar Post para Todos os Grupos ({{ groupStore.groups.length }})
               </P-Button>
               
               <P-Divider align="center">Ou individual</P-Divider>

               <div class="flex flex-col gap-2">
                 <label class="text-sm font-bold text-stone-600">Selecionar Grupo Específico</label>
                 <P-Select
                   v-model="selectedGroup"
                   :options="groupStore.groups"
                   optionLabel="name"
                   placeholder="Escolha um grupo"
                   class="w-full"
                 />
                 <P-Button v-if="selectedGroup" severity="secondary" @click="exportClassificationImage(selectedGroup)" :loading="exporting">
                   Exportar {{ selectedGroup.name }}
                 </P-Button>
               </div>
            </div>
          </div>
        </P-TabPanel>

        <!-- TAB 2: CALENDAR -->
        <P-TabPanel value="2">
          <div class="space-y-4 pt-4">
            <div class="flex flex-col gap-2">
              <label class="text-sm font-bold text-stone-600">Selecionar Dia para Calendário</label>
              <P-Select
                v-model="selectedCalendarDay"
                :options="gameDayStore.gameDays"
                optionLabel="date"
                placeholder="Escolha um dia"
                class="w-full"
              >
                <template #option="{ option }">
                  {{ formatDate(option.date) }}
                </template>
                <template #value="{ value }">
                  {{ value ? formatDate(value.date) : 'Escolha um dia' }}
                </template>
              </P-Select>
            </div>

            <div v-if="selectedCalendarDay">
               <P-Button severity="secondary" class="w-full" @click="exportCalendarImage" :loading="exporting">
                  <span class="material-symbols-outlined">today</span>
                  Gerar Post do Dia
               </P-Button>
            </div>

            <P-Divider align="center">Torneio Completo</P-Divider>

            <div class="flex flex-col gap-2">
              <label class="text-sm font-bold text-stone-600">Selecionar Torneio</label>
              <P-Select
                v-model="selectedFullTournament"
                :options="tournamentStore.tournaments"
                optionLabel="name"
                placeholder="Escolha um torneio"
                class="w-full"
              />
              <P-Button v-if="selectedFullTournament" severity="contrast" @click="exportFullTournamentCalendar" :loading="exporting">
                <span class="material-symbols-outlined">event_note</span>
                Gerar Calendário Completo (Multi-Post)
              </P-Button>
            </div>
          </div>
        </P-TabPanel>

        <!-- TAB 3: KNOCKOUT -->
        <P-TabPanel value="3">
          <div class="space-y-4 pt-4">
            <div class="flex flex-col gap-2">
              <label class="text-sm font-bold text-stone-600">Selecionar Torneio</label>
              <P-Select
                v-model="selectedKnockoutTournament"
                :options="tournamentStore.tournaments"
                optionLabel="name"
                placeholder="Escolha um torneio"
                class="w-full"
              />
            </div>

            <div v-if="selectedKnockoutTournament" class="flex flex-col gap-4">
               <P-Button severity="contrast" class="w-full" @click="exportKnockoutImage" :loading="exporting" :disabled="!knockoutAvailable" :title="!knockoutAvailable ? 'Este torneio ainda não entrou na fase de eliminatórias' : ''">
                  <span class="material-symbols-outlined">account_tree</span>
                  Gerar Post de Eliminatórias
               </P-Button>
               <p v-if="!knockoutAvailable" class="text-xs text-stone-500 text-center">Este torneio ainda não entrou na fase de eliminatórias</p>

               <div v-if="knockoutAvailable && finalStandings" class="flex gap-2">
                   <P-Button severity="help" class="flex-1" @click="triggerStandingsPrint">
                      <span class="material-symbols-outlined">celebration</span>
                      Imprimir Classificação Final
                   </P-Button>
                   <P-Button severity="help" class="flex-1" @click="exportStandingsImage" :loading="exporting">
                      <span class="material-symbols-outlined">image</span>
                      Gerar Post Final
                   </P-Button>
                </div>
            </div>
          </div>
        </P-TabPanel>
      </P-TabPanels>
    </P-Tabs>

    <!-- HIDDEN CANVAS FOR CAPTURE -->
    <div style="position: absolute; left: -9999px; top: -9999px;">
       <PostCanvas 
         v-if="renderCanvas"
         ref="canvasRef"
         :type="canvasType"
         :title="canvasTitle"
         :subtitle="canvasSubtitle"
         :date="canvasDate"
         :data="canvasData"
       />
    </div>

  </P-Dialog>

  <!-- PRINT SECTION (Hidden from UI, visible in Print) -->
  <div id="print-area" class="hidden-print">
    <div class="print-container-inner">
      <!-- Header with 3 Logos -->
      <div class="print-branding">
          <div class="logo-strip">
            <img src="/static/urca.jpg" alt="URCA" />
            <img src="/static/cmpm.jpg" alt="CMPM" />
            <img src="/static/nafpm.jpg" alt="NAFPM" />
          </div>
          <div class="branding-text">
            <div class="tournament-name-main">XII TORNEIO DE FUTSAL</div>
            <div class="tournament-name-sub">DE SÃO PEDRO</div>
          </div>
      </div>

      <div class="print-content">
          <!-- Mode: Daily Results -->
          <div v-if="printMode === 'daily' && dayGames.length > 0" class="print-results-section">
            <h2 class="print-section-title">Resultados do Dia · {{ selectedDay ? formatDate(selectedDay.date) : '' }}</h2>
            <div class="print-results-grid">
                <div v-for="g in dayGames" :key="g.id" class="print-game-card">
                  <div class="game-meta">
                    <span class="game-time">{{ getSlotTime(g) }}</span>
                    <span class="game-tag">{{ getTournamentName(g.tournament) }}</span>
                  </div>
                  <div class="game-main">
                    <div class="team home">{{ getHomeName(g) }}</div>
                    <div class="score-box">{{ getScoreDisplay(g) }}</div>
                    <div class="team away">{{ getAwayName(g) }}</div>
                  </div>
                </div>
            </div>
          </div>

          <!-- Mode: Final Standings -->
          <div v-if="printMode === 'standings' && finalStandings" class="print-final-standings">
            <h2 class="print-section-title text-center" style="border:none; text-align:center; padding-left:0">Classificação Final · {{ selectedKnockoutTournament?.name }}</h2>
            <div class="final-rankings">
              <div v-for="res in finalStandings" :key="res.pos" :class="['ranking-item', 'pos-' + res.pos[0]]">
                <span class="rank-pos">{{ res.pos }}</span>
                <span class="rank-team">{{ res.team }}</span>
              </div>
            </div>
          </div>
      </div>

      <div class="print-footer">
          #TorneioSaoPedro2026
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useGameStore } from "@stores/games";
import { useGameDayStore } from "@stores/game_days";
import { useGroupStore } from "@stores/groups";
import { useTeamStore } from "@stores/teams";
import { useTournamentStore } from "@stores/tournaments";
import { useDateFormatter } from "@/composables/useDateFormatter";
import { getClassification } from "@router/backend/services/group";
import { GameStatus } from "@router/backend/services/game/types";
import { TournamentPhase } from "@router/backend/services/tournament/types";
import { exportElementAsPng } from "@/utils/export_service";
import PostCanvas from "./PostCanvas.vue";

const toast = useToast();

const visible = defineModel<boolean>();

const gameStore = useGameStore();
const gameDayStore = useGameDayStore();
const groupStore = useGroupStore();
const teamStore = useTeamStore();
const tournamentStore = useTournamentStore();
const { formatDate, formatDateLong } = useDateFormatter();

// State
const selectedDay = ref<any>(null);
const selectedGroup = ref<any>(null);
const selectedCalendarDay = ref<any>(null);
const selectedKnockoutTournament = ref<any>(null);
const selectedFullTournament = ref<any>(null);
const exporting = ref(false);
const printMode = ref<'daily' | 'standings' | null>(null);

const dayGames = computed(() => {
  if (!selectedDay.value) return [];
  const date = selectedDay.value.date;
  return gameStore.games
    .filter(g => g.scheduled_date?.startsWith(date))
    .sort((a,b) => (a.scheduled_date||'').localeCompare(b.scheduled_date||''));
});

const tournamentsInDay = computed(() => {
  const tids = new Set(dayGames.value.map(g => g.tournament));
  return tids.size;
});

const knockoutAvailable = computed(() => {
  if (!selectedKnockoutTournament.value) return false;
  return selectedKnockoutTournament.value.phase === TournamentPhase.KNOCKOUT;
});

// Canvas Rendering State
const renderCanvas = ref(false);
const canvasRef = ref<any>(null);
const canvasType = ref<'results' | 'classification' | 'calendar'>('results');
const canvasTitle = ref('');
const canvasSubtitle = ref('');
const canvasDate = ref('');
const canvasData = ref<any[]>([]);

const finalStandings = computed(() => {
  if (!selectedKnockoutTournament.value) return null;
  const tid = selectedKnockoutTournament.value.id;
  const knockoutGames = gameStore.games.filter(g => g.tournament === tid && g.phase !== 'group');
  
  const final = knockoutGames.find(g => g.phase === 'final');
  if (!final || final.status !== GameStatus.Finished) return null;
  
  const thirdPlace = knockoutGames.find(g => g.phase === 'third_place');
  
  const results = [];
  
  // 1st and 2nd
  const finalScores = getScores(final);
  const homeWin = finalScores.home > finalScores.away || (finalScores.home === finalScores.away && finalScores.penalties.home > finalScores.penalties.away);
  
  if (homeWin) {
    results.push({ pos: '1º', team: getHomeName(final) });
    results.push({ pos: '2º', team: getAwayName(final) });
  } else {
    results.push({ pos: '1º', team: getAwayName(final) });
    results.push({ pos: '2º', team: getHomeName(final) });
  }
  
  // 3rd and 4th
  if (thirdPlace && thirdPlace.status === GameStatus.Finished) {
    const tpScores = getScores(thirdPlace);
    const tpHomeWin = tpScores.home > tpScores.away || (tpScores.home === tpScores.away && tpScores.penalties.home > tpScores.penalties.away);
    
    if (tpHomeWin) {
      results.push({ pos: '3º', team: getHomeName(thirdPlace) });
      results.push({ pos: '4º', team: getAwayName(thirdPlace) });
    } else {
      results.push({ pos: '3º', team: getAwayName(thirdPlace) });
      results.push({ pos: '4º', team: getHomeName(thirdPlace) });
    }
  }
  
  return results;
});

// Lifecycle
onMounted(async () => {
  await Promise.all([
    gameStore.getGames(),
    gameDayStore.getGameDays(),
    groupStore.getGroups(),
    teamStore.getTeams(),
    tournamentStore.getTournaments()
  ]);
});

// Helpers
function getTournamentName(id: string) {
  return tournamentStore.tournaments.find(t => t.id === id)?.name || id;
}

function getTeamName(id: string) {
  return teamStore.teams.find(t => t.id === id)?.name || id;
}

function getHomeName(game: any) {
  return getTeamName(game.home_call?.team) || game.home_placeholder || '?';
}

function getAwayName(game: any) {
  return getTeamName(game.away_call?.team) || game.away_placeholder || '?';
}

function getScores(game: any) {
  const homeN = getHomeName(game);
  const awayN = getAwayName(game);
  let home = 0, away = 0;
  let php = 0, pap = 0; // penalties
  
  (game.events || []).forEach((e: any) => {
    if ('Goal' in e) {
      if (e.Goal.team_name === homeN) home++;
      else if (e.Goal.team_name === awayN) away++;
    }
    if ('Penalty' in e && e.Penalty.scored) {
       // if period is shootout (usually period 5)
       if (e.Penalty.period === 5 || e.Penalty.is_shootout) {
         if (e.Penalty.team_id === game.home_call?.team) php++;
         else pap++;
       } else {
         // regular penalty goal
         if (e.Penalty.team_id === game.home_call?.team) home++;
         else away++;
       }
    }
  });
  return { home, away, penalties: { home: php, away: pap } };
}

function getScoreDisplay(game: any) {
  if (game.status === GameStatus.Scheduled) return '-';
  const { home, away, penalties } = getScores(game);
  let scoreStr = `${home} - ${away}`;
  if (penalties.home > 0 || penalties.away > 0) {
    scoreStr += `  (GP: ${penalties.home}-${penalties.away})`;
  }
  return scoreStr;
}

function getSlotTime(game: any) {
  if (!game.scheduled_date) return '--:--';
  const d = new Date(game.scheduled_date);
  return d.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });
}

// Actions
async function handlePrintDay() {
  if (!selectedDay.value) return;
  handlePrint('daily');
}

async function triggerStandingsPrint() {
  handlePrint('standings');
}

function handlePrint(mode: 'daily' | 'standings') {
  printMode.value = mode;
  nextTick(() => {
    window.print();
  });
}

async function exportResultsImage() {
  if (!selectedDay.value || dayGames.value.length === 0) return;
  
  exporting.value = true;
  const tGrouped = dayGames.value.reduce((acc: any, g) => {
    if (!acc[g.tournament]) acc[g.tournament] = [];
    acc[g.tournament].push(g);
    return acc;
  }, {});

  for (const tid in tGrouped) {
    const tName = getTournamentName(tid);
    const games = tGrouped[tid];
    
    canvasType.value = 'results';
    canvasTitle.value = 'Resultados';
    canvasSubtitle.value = tName;
    canvasDate.value = formatDateLong(selectedDay.value.date);
    canvasData.value = games.map(g => {
      const { home, away, penalties } = getScores(g);
      let hDisplay = String(home);
      let aDisplay = String(away);
      if (penalties.home > 0 || penalties.away > 0) {
        hDisplay += ` (${penalties.home})`;
        aDisplay = `(${penalties.away}) ${away}`;
      }
      return {
        id: g.id,
        home: getHomeName(g),
        away: getAwayName(g),
        homeScore: hDisplay,
        awayScore: aDisplay
      };
    });

    await renderAndDownload(`resultados_${tName.replace(/\s+/g, '_')}_${selectedDay.value.date}`);
  }
  
  exporting.value = false;
}

async function renderAndDownload(filename: string) {
  renderCanvas.value = true;
  await nextTick();
  // Wait for images/fonts
  await new Promise(resolve => setTimeout(resolve, 600));
  const el = canvasRef.value?.getCanvas();
  if (el) {
    await exportElementAsPng(el, filename);
  }
  renderCanvas.value = false;
}

async function exportAllClassifications() {
  exporting.value = true;
  for (const group of groupStore.groups) {
    await exportClassificationImage(group);
  }
  exporting.value = false;
}

async function exportClassificationImage(group: any) {
  try {
    const res = await getClassification(group.id);
    if (res.status === 200) {
      canvasType.value = 'classification';
      canvasTitle.value = group.name;
      canvasSubtitle.value = getTournamentName(group.tournament);
      canvasDate.value = 'Classificação Atual';
      canvasData.value = res.data.standings.map((s:any) => ({
        name: s.team_name,
        games: s.games,
        wins: s.wins,
        ties: s.ties,
        losses: s.losses,
        points: s.points
      }));

      await renderAndDownload(`classificacao_${group.name.replace(/\s+/g, '_')}`);
    }
  } catch (e) {
    console.error(e);
  }
}

async function exportCalendarImage() {
  if (!selectedCalendarDay.value) return;
  
  exporting.value = true;
  const date = selectedCalendarDay.value.date;
  const games = gameStore.games.filter(g => g.scheduled_date?.startsWith(date)).sort((a,b) => (a.scheduled_date||'').localeCompare(b.scheduled_date||''));
  
  canvasType.value = 'calendar';
  canvasTitle.value = 'Calendário';
  canvasSubtitle.value = 'Próximos Jogos';
  canvasDate.value = formatDateLong(date);
  
  // Grouping for the "Cell per day" structure
  canvasData.value = [{
    date: formatDate(date).split(',')[0], // Day name
    games: games.map(g => ({
      id: g.id,
      time: getSlotTime(g),
      home: getHomeName(g),
      away: getAwayName(g),
      tag: getTournamentName(g.tournament)
    }))
  }];

  await renderAndDownload(`calendario_${date}`);
  exporting.value = false;
}

async function exportFullTournamentCalendar() {
  if (!selectedFullTournament.value) return;
  
  exporting.value = true;
  const tid = selectedFullTournament.value.id;
  const tName = selectedFullTournament.value.name;
  const games = gameStore.games
    .filter(g => g.tournament === tid)
    .sort((a,b) => (a.scheduled_date||'').localeCompare(b.scheduled_date||''));

  const PAGE_SIZE = 6;
  const totalPages = Math.ceil(games.length / PAGE_SIZE);

  for (let i = 0; i < totalPages; i++) {
    const pageGames = games.slice(i * PAGE_SIZE, (i + 1) * PAGE_SIZE);
    
    // Group pageGames by date
    const groupedByDate: any = {};
    pageGames.forEach(g => {
      const gDate = g.scheduled_date?.split('T')[0] || 'TBD';
      if (!groupedByDate[gDate]) groupedByDate[gDate] = [];
      groupedByDate[gDate].push(g);
    });

    canvasType.value = 'calendar';
    canvasTitle.value = 'Calendário';
    canvasSubtitle.value = `${tName} ${totalPages > 1 ? `(${i+1}/${totalPages})` : ''}`;
    canvasDate.value = 'Torneio Completo';
    canvasData.value = Object.keys(groupedByDate).map(d => ({
      date: d === 'TBD' ? 'A Definir' : formatDate(d).split(',')[0],
      games: groupedByDate[d].map((g: any) => ({
        id: g.id,
        time: getSlotTime(g),
        home: getHomeName(g),
        away: getAwayName(g),
        tag: null // Don't need tournament tag in full tournament calendar
      }))
    }));

    await renderAndDownload(`calendario_${tName.replace(/\s+/g, '_')}_p${i+1}`);
  }
  
  exporting.value = false;
}

async function exportKnockoutImage() {
  if (!selectedKnockoutTournament.value) return;
  
  exporting.value = true;
  const tid = selectedKnockoutTournament.value.id;
  const tName = selectedKnockoutTournament.value.name;
  const games = gameStore.games
    .filter(g => g.tournament === tid && g.phase !== 'group' && g.status === GameStatus.Finished)
    .sort((a,b) => {
        const phases = ['quarter_final', 'semi_final', 'third_place', 'final'];
        return phases.indexOf(a.phase) - phases.indexOf(b.phase);
    });

  if (games.length === 0) {
    exporting.value = false;
    return;
  }

  canvasType.value = 'results';
  canvasTitle.value = 'Eliminatórias';
  canvasSubtitle.value = tName;
  canvasDate.value = 'Fase Final';
  canvasData.value = games.map(g => {
    const { home, away, penalties } = getScores(g);
    let hDisplay = String(home);
    let aDisplay = String(away);
    const phaseLabel: Record<string,string> = {
        quarter_final: '1/4',
        semi_final: '1/2',
        third_place: '3º lugar',
        final: 'Final'
    };
    if (penalties.home > 0 || penalties.away > 0) {
      hDisplay += ` (${penalties.home})`;
      aDisplay = `(${penalties.away}) ${away}`;
    }
    return {
      id: g.id,
      home: `${phaseLabel[g.phase] || ''} · ${getHomeName(g)}`,
      away: getAwayName(g),
      homeScore: hDisplay,
      awayScore: aDisplay
    };
  });

  await renderAndDownload(`eliminatorias_${tName.replace(/\s+/g, '_')}`);
  exporting.value = false;
}

async function exportStandingsImage() {
  if (!finalStandings.value || !selectedKnockoutTournament.value) return;
  
  exporting.value = true;
  canvasType.value = 'standings';
  canvasTitle.value = 'Classificação Final';
  canvasSubtitle.value = selectedKnockoutTournament.value.name;
  canvasDate.value = 'Pódio';
  canvasData.value = (finalStandings.value || []).filter(r => r.pos !== '4º');

  await renderAndDownload(`podio_${selectedKnockoutTournament.value.name.replace(/\s+/g, '_')}`);
  exporting.value = false;
}
</script>

<style>
@media print {
  @page {
    margin: 0;
    size: A4 portrait;
  }
  
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    height: 100% !important;
    overflow: hidden !important;
    background: white !important;
  }

  body {
    visibility: hidden !important;
  }

  .p-dialog-mask, .p-dialog {
    display: none !important;
  }

  #print-area {
    visibility: visible !important;
    display: flex !important;
    flex-direction: column;
    justify-content: center;
    position: fixed !important;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    padding: 10mm;
    box-sizing: border-box;
    background: white !important;
    color: black !important;
    margin: 0;
  }

  #print-area * {
    visibility: visible !important;
  }

  .print-container-inner {
    width: 100%;
    display: block;
  }

  .print-branding {
    margin-bottom: 10mm;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .print-content {
    width: 100%;
    margin-bottom: 10mm;
  }
  
  .score-box {
    border: 1px solid #ddd !important;
  }
}

#print-area {
  display: none;
  font-family: 'Inter', sans-serif;
  color: #1a1a1a;
}

.print-branding {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 4px solid #f97316;
  padding-bottom: 20px;
  margin-bottom: 40px;
}

.logo-strip {
  display: flex;
  gap: 15px;
}

.logo-strip img {
  height: 60px;
  width: auto;
  border-radius: 8px;
  filter: grayscale(0.2);
}

.branding-text {
  text-align: right;
}

.tournament-name-main {
  font-size: 24pt;
  font-weight: 900;
  font-style: italic;
  line-height: 1;
}

.tournament-name-sub {
  font-size: 18pt;
  font-weight: 700;
  color: #f97316;
}

.print-section-title {
  font-size: 20pt;
  font-weight: 800;
  margin-bottom: 30px;
  border-left: 8px solid #f97316;
  padding-left: 15px;
  text-transform: uppercase;
}

.print-results-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.print-game-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 15px;
  background: #fdfcfb;
}

.game-meta {
  display: flex;
  justify-content: space-between;
  font-size: 10pt;
  font-weight: 700;
  color: #6b7280;
  margin-bottom: 10px;
  text-transform: uppercase;
}

.game-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.team {
  flex: 1;
  font-size: 14pt;
  font-weight: 700;
}

.team.home { text-align: right; }
.team.away { text-align: left; }

.score-box {
  background: #1a1a1a;
  color: white;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12pt;
  font-weight: 900;
  white-space: nowrap;
}

.final-rankings {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 8px 20px;
  background: #f8fafc;
  border-radius: 10px;
  font-size: 14pt;
  font-weight: 700;
}

.rank-pos {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  color: white;
  border-radius: 50%;
  font-weight: 900;
  font-style: italic;
  font-size: 12pt;
}

.pos-1 .rank-pos { background: #fbbf24; color: #78350f; } /* Gold */
.pos-2 .rank-pos { background: #cbd5e1; color: #334155; } /* Silver */
.pos-3 .rank-pos { background: #d97706; color: white; }   /* Bronze */

.rank-team {
  flex: 1;
}

.print-footer {
  margin-top: 60px;
  border-top: 1px solid #e5e7eb;
  padding-top: 20px;
  text-align: center;
  font-size: 9pt;
  color: #9ca3af;
  font-weight: 600;
}
</style>
