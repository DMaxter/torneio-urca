<template>
  <P-Dialog v-model:visible="visible" modal header="Chave API Taça da Pinga" class="w-11/12 md:w-6/12">
    <div class="mb-4">
      <p class="mb-2">Chave API para o sistema Taça da Pinga:</p>
      <P-InputText v-model="apiKey" readonly class="w-full" />
    </div>
    <template #footer>
      <P-Button severity="secondary" label="Fechar" @click="visible = false" />
      <P-Button severity="warn" label="Regenerar" :loading="rotating" @click="showConfirmRotate = true" class="ml-2" />
    </template>
  </P-Dialog>

  <P-Dialog v-model:visible="showConfirmRotate" modal header="Regenerar Chave API" class="w-11/12 md:w-6/12">
    <p>Isto irá gerar uma nova chave. O sistema POS terá que ser atualizado. Continuar?</p>
    <template #footer>
      <P-Button severity="secondary" label="Cancelar" @click="showConfirmRotate = false" />
      <P-Button severity="warn" label="Regenerar" :loading="rotating" @click="confirmRotate" class="ml-2" />
    </template>
  </P-Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import * as pingaService from "@router/backend/services/pinga";

const visible = defineModel<boolean>();
const apiKey = ref("");
const rotating = ref(false);
const showConfirmRotate = ref(false);
const toast = useToast();

onMounted(async () => {
  await loadApiKey();
});

async function loadApiKey() {
  try {
    const res = await pingaService.getApiKey();
    apiKey.value = res.data.api_key;
  } catch {
    toast.add({ severity: "error", summary: "Erro", detail: "Erro ao obter chave API", life: 3000 });
  }
}

async function confirmRotate() {
  showConfirmRotate.value = false;
  await rotateKey();
}

async function rotateKey() {
  rotating.value = true;
  try {
    const res = await pingaService.rotateApiKey();
    if (res.status === 200) {
      apiKey.value = res.data.api_key;
      toast.add({ severity: "success", summary: "Sucesso", detail: "Chave API regenerada", life: 3000 });
    }
  } catch {
    toast.add({ severity: "error", summary: "Erro", detail: "Erro ao regenerar chave API", life: 3000 });
  } finally {
    rotating.value = false;
  }
}
</script>