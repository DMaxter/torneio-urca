import { createApp } from "vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import { URCATheme } from "./theme";
import { pt } from "primelocale/js/pt.js";
import "material-symbols";

import App from "@/App.vue";
import router from "@router";

const app = createApp(App);

app.use(createPinia());
app.use(ToastService);
app.use(PrimeVue, {
  locale: pt,
  theme: {
    preset: URCATheme,
    options: {
      darkModeSelector: ".dark",
      cssLayer: false
    }
  }
});
app.use(router);

// PrimeVue components

import Button from "primevue/button";
import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";
import Checkbox from "primevue/checkbox";
import Column from 'primevue/column';
import DataTable from "primevue/datatable";
import DatePicker from "primevue/datepicker";
import Dialog from "primevue/dialog";
import Fieldset from "primevue/fieldset";
import FileUpload from "primevue/fileupload";
import FloatLabel from "primevue/floatlabel";
import InputText from "primevue/inputtext";
import Menubar from "primevue/menubar";
import MultiSelect from "primevue/multiselect";
import Select from "primevue/select";
import Steps from "primevue/steps";
import Tag from "primevue/tag";
import Toast from "primevue/toast";
import ToastService from "primevue/toastservice";
import Tooltip from "primevue/tooltip";

app.component("P-Accordion", Accordion);
app.component("P-AccordionTab", AccordionTab);
app.component("P-Button", Button);
app.component("P-Checkbox", Checkbox);
app.component("P-Column", Column);
app.component("P-DataTable", DataTable);
app.component("P-DatePicker", DatePicker);
app.component("P-Dialog", Dialog);
app.component("P-Fieldset", Fieldset);
app.component("P-FileUpload", FileUpload);
app.component("P-FloatLabel", FloatLabel);
app.component("P-InputText", InputText);
app.component("P-Menubar", Menubar);
app.component("P-MultiSelect", MultiSelect);
app.component("P-Select", Select);
app.component("P-Steps", Steps);
app.component("P-Tag", Tag);
app.component("P-Toast", Toast);

app.directive("tooltip", Tooltip);

// Custom components

import GameList from "@components/GameList.vue";
import GameManagement from "@components/GameManagement.vue";
import GroupList from "@components/GroupList.vue";
import GroupManagement from "@components/GroupManagement.vue";
import PlayerList from "@components/PlayerList.vue";
import TeamList from "@components/TeamList.vue";
import TeamManagement from "@components/TeamManagement.vue";
import TopBar from "@components/TopBar.vue";
import TournamentList from "@components/TournamentList.vue";
import TournamentManagement from "@components/TournamentManagement.vue";
import UserList from "@components/UserList.vue";
import UserManagement from "@components/UserManagement.vue";
import AdminPlayerForm from "@components/AdminPlayerForm.vue";

app.component("AdminPlayerForm", AdminPlayerForm);
app.component("GameList", GameList);
app.component("GameManagement", GameManagement);
app.component("GroupList", GroupList);
app.component("GroupManagement", GroupManagement);
app.component("PlayerList", PlayerList);
app.component("TeamList", TeamList);
app.component("TeamManagement", TeamManagement);
app.component("TopBar", TopBar);
app.component("TournamentList", TournamentList);
app.component("TournamentManagement", TournamentManagement);
app.component("UserList", UserList);
app.component("UserManagement", UserManagement);

app.mount("#app");
