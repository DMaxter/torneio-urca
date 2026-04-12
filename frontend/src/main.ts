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

import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";
import Button from "primevue/button";
import Checkbox from "primevue/checkbox";
import Column from 'primevue/column';
import DataTable from "primevue/datatable";
import DatePicker from "primevue/datepicker";
import Dialog from "primevue/dialog";
import Fieldset from "primevue/fieldset";
import FileUpload from "primevue/fileupload";
import FloatLabel from "primevue/floatlabel";
import InputNumber from "primevue/inputnumber";
import InputText from "primevue/inputtext";
import Menubar from "primevue/menubar";
import MultiSelect from "primevue/multiselect";
import ProgressBar from "primevue/progressbar";
import ProgressSpinner from "primevue/progressspinner";
import Select from "primevue/select";
import Steps from "primevue/steps";
import Tag from "primevue/tag";
import Toast from "primevue/toast";
import ToastService from "primevue/toastservice";
import ToggleSwitch from "primevue/toggleswitch";
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
app.component("P-InputNumber", InputNumber);
app.component("P-InputText", InputText);
app.component("P-Menubar", Menubar);
app.component("P-MultiSelect", MultiSelect);
app.component("P-ProgressBar", ProgressBar);
app.component("P-ProgressSpinner", ProgressSpinner);
app.component("P-Select", Select);
app.component("P-Steps", Steps);
app.component("P-Tag", Tag);
app.component("P-Toast", Toast);
app.component("P-ToggleSwitch", ToggleSwitch);

app.directive("tooltip", Tooltip);

// Custom components
import ChangePasswordDialog from "@components/ChangePasswordDialog.vue";
import CustomFileUpload from "@components/forms/FileUpload.vue";
import DistributeGamesDialog from "@components/DistributeGamesDialog.vue";
import FooterBar from "@components/FooterBar.vue";
import GameCalendarDialog from "@components/GameCalendarDialog.vue";
import GameDaysDialog from "@components/GameDaysDialog.vue";
import GameList from "@components/GameList.vue";
import GameManagement from "@components/GameManagement.vue";
import GameManagementDialog from "@components/GameManagementDialog.vue";
import GameResultDialog from "@components/GameResultDialog.vue";
import GenerateGamesDialog from "@components/GenerateGamesDialog.vue";
import GenerateGroupsDialog from "@components/GenerateGroupsDialog.vue";
import GroupList from "@components/GroupList.vue";
import GroupManagement from "@components/GroupManagement.vue";
import GroupView from "@components/GroupView.vue";
import PersonFields from "@components/forms/PersonFields.vue";
import PlayerForm from "@components/forms/PlayerForm.vue";
import PlayerList from "@components/PlayerList.vue";
import PlayerManagement from "@components/PlayerManagement.vue";
import StaffMemberForm from "@components/forms/StaffMemberForm.vue";
import TeamList from "@components/TeamList.vue";
import TeamManagement from "@components/TeamManagement.vue";
import TopBar from "@components/TopBar.vue";
import TournamentList from "@components/TournamentList.vue";
import TournamentManagement from "@components/TournamentManagement.vue";
import UserList from "@components/UserList.vue";
import UserManagement from "@components/UserManagement.vue";
import RoleManagement from "@components/RoleManagement.vue";
import ViewGamesDialog from "@components/ViewGamesDialog.vue";

app.component("ChangePasswordDialog", ChangePasswordDialog);
app.component("DistributeGamesDialog", DistributeGamesDialog);
app.component("FileUpload", CustomFileUpload);
app.component("FooterBar", FooterBar);
app.component("GameCalendarDialog", GameCalendarDialog);
app.component("GameDaysDialog", GameDaysDialog);
app.component("GameList", GameList);
app.component("GameManagement", GameManagement);
app.component("GameManagementDialog", GameManagementDialog);
app.component("GameResultDialog", GameResultDialog);
app.component("GenerateGamesDialog", GenerateGamesDialog);
app.component("GenerateGroupsDialog", GenerateGroupsDialog);
app.component("GroupList", GroupList);
app.component("GroupManagement", GroupManagement);
app.component("GroupView", GroupView);
app.component("PersonFields", PersonFields);
app.component("PlayerForm", PlayerForm);
app.component("PlayerList", PlayerList);
app.component("PlayerManagement", PlayerManagement);
app.component("StaffMemberForm", StaffMemberForm);
app.component("TeamList", TeamList);
app.component("TeamManagement", TeamManagement);
app.component("TopBar", TopBar);
app.component("TournamentList", TournamentList);
app.component("TournamentManagement", TournamentManagement);
app.component("UserList", UserList);
app.component("UserManagement", UserManagement);
app.component("RoleManagement", RoleManagement);
app.component("ViewGamesDialog", ViewGamesDialog);

app.mount("#app");
