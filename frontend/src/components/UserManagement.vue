<template>
  <P-Dialog v-model:visible="enabled" modal :header="creating ? 'Criar Utilizador' : 'Editar Utilizador'">
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="name" v-model="user.name" />
      <label for="name">Nome</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-Select id="gender" v-model="user.gender" :options="GENDERS" optionLabel="name"
        optionValue="value" fluid/>
      <label for="gender">Género</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-DatePicker id="birthdate" v-model="user.birth_date" />
      <label for="birthdate">Data de Nascimento</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="birthplace" v-model="user.place_of_birth" />
      <label for="birthplace">Local de Nascimento</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="address" v-model="user.address" />
      <label for="address">Morada</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-InputText id="fiscalnumber" v-model="user.fiscal_number" />
      <label for="fiscalnumber">NIF</label>
    </P-FloatLabel>
    <P-FloatLabel class="field" variant="on">
      <P-MultiSelect id="roles" v-model="user.roles" :showToggleAll="false" :options="ROLES" optionLabel="name"
        optionValue="value" fluid/>
      <label for="roles">Função</label>
    </P-FloatLabel>
    <template #footer>
      <P-Button @click="createOrUpdate">{{ creating ? "Criar" : "Alterar" }}</P-Button>
      <P-Button @click="close">Cancelar</P-Button>
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { GENDERS, ROLES, CreateUser, type User } from "@router/backend/services/user/types";
import { useUserStore } from "@stores/users";

const enabled = defineModel<boolean>();
const props = defineProps<{
  user?: User
}>();

const creating = computed(() => props.user === undefined);

const user = ref<User | CreateUser>(new CreateUser());
onMounted(() => {
  if (!creating.value) {
    user.value = props.user!
  }
});

const userStore = useUserStore();

async function createOrUpdate() {
  if (creating.value) {
    await create();
  } else {
    await update();
  }
}

async function create() {
  await userStore.createUser(user.value as CreateUser);
}

async function update() {
  console.error("TODO");
}

function close() {
  enabled.value = false;
}
</script>

<style lang="scss" scoped>
.field {
  margin-top: 10px;
}
</style>
