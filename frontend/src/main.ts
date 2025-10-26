import { createApp } from "vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import Aura from "@primeuix/themes/aura";


import App from "@/App.vue";
import router from "@router";

const app = createApp(App);

app.use(createPinia());
app.use(PrimeVue, {
  theme: {
    preset: Aura
  }
});
app.use(router);

// PrimeVue components

import Button from "primevue/button";
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from "primevue/dialog";
import Fieldset from "primevue/fieldset";
import FloatLabel from 'primevue/floatlabel';
import InputText from 'primevue/inputtext';
import Menubar from "primevue/menubar";

app.component("P-Button", Button);
app.component("P-Column", Column);
app.component("P-DataTable", DataTable);
app.component("P-Dialog", Dialog);
app.component("P-Fieldset", Fieldset);
app.component("P-FloatLabel", FloatLabel);
app.component("P-InputText", InputText);
app.component("P-Menubar", Menubar);

// Custom components

import TournamentManagement from "@components/TournamentManagement.vue";
import TournamentList from "@components/TournamentList.vue";
import TopBar from "@components/TopBar.vue";

app.component("TournamentManagement", TournamentManagement);
app.component("TournamentList", TournamentList);
app.component("TopBar", TopBar);

app.mount("#app");
