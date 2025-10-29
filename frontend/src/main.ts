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
import DataTable from "primevue/datatable";
import DatePicker from "primevue/datepicker";
import Dialog from "primevue/dialog";
import Fieldset from "primevue/fieldset";
import FloatLabel from "primevue/floatlabel";
import InputText from "primevue/inputtext";
import Menubar from "primevue/menubar";
import MultiSelect from "primevue/multiselect";
import Select from "primevue/select";

app.component("P-Button", Button);
app.component("P-Column", Column);
app.component("P-DataTable", DataTable);
app.component("P-DatePicker", DatePicker);
app.component("P-Dialog", Dialog);
app.component("P-Fieldset", Fieldset);
app.component("P-FloatLabel", FloatLabel);
app.component("P-InputText", InputText);
app.component("P-Menubar", Menubar);
app.component("P-MultiSelect", MultiSelect);
app.component("P-Select", Select);

// Custom components

import GameList from "@components/GameList.vue";
import GameManagement from "@components/GameManagement.vue";
import TeamList from "@components/TeamList.vue";
import TeamManagement from "@components/TeamManagement.vue";
import TopBar from "@components/TopBar.vue";
import TournamentList from "@components/TournamentList.vue";
import TournamentManagement from "@components/TournamentManagement.vue";
import UserList from "@components/UserList.vue";
import UserManagement from "@components/UserManagement.vue";

app.component("GameList", GameList);
app.component("GameManagement", GameManagement);
app.component("TeamList", TeamList);
app.component("TeamManagement", TeamManagement);
app.component("TopBar", TopBar);
app.component("TournamentList", TournamentList);
app.component("TournamentManagement", TournamentManagement);
app.component("UserList", UserList);
app.component("UserManagement", UserManagement);

app.mount("#app");
