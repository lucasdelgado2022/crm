<template>
  <div class="grid h-full grid-cols-1 gap-4 overflow-hidden p-4 lg:grid-cols-2">
    <!-- Datos / Hechos -->
    <div class="flex min-h-0 flex-col overflow-hidden rounded-lg border">
      <div
        class="flex shrink-0 items-center justify-between gap-2 border-b px-4 py-3"
      >
        <div
          class="flex items-center gap-2 text-base font-semibold text-ink-gray-8"
        >
          <FeatherIcon name="file-text" class="h-5" />
          {{ __('Datos / Hechos') }}
          <Badge variant="subtle" theme="gray" size="sm">
            {{ facts.data?.length || 0 }}
          </Badge>
        </div>
        <Button variant="outline" @click="showAdd = !showAdd">
          <template #prefix>
            <FeatherIcon name="plus" class="h-4" />
          </template>
          {{ __('Agregar') }}
        </Button>
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto p-4">
        <div v-if="showAdd" class="mb-3 rounded-lg border p-3">
          <textarea
            v-model="nf.hecho"
            :placeholder="__('Hecho / dato...')"
            rows="2"
            class="w-full rounded border border-outline-gray-2 bg-surface-base p-2 text-sm text-ink-gray-8 focus:outline-none"
          />
          <input
            v-model="nf.fuente"
            :placeholder="__('Fuente (URL o descripción)')"
            class="mt-2 w-full rounded border border-outline-gray-2 bg-surface-base p-2 text-sm text-ink-gray-8 focus:outline-none"
          />
          <div class="mt-2 flex justify-end gap-2">
            <Button variant="ghost" @click="showAdd = false">
              {{ __('Cancelar') }}
            </Button>
            <Button
              variant="solid"
              :disabled="!nf.hecho.trim()"
              @click="addFact"
            >
              {{ __('Guardar') }}
            </Button>
          </div>
        </div>
        <div v-if="facts.data?.length" class="flex flex-col gap-2">
          <div
            v-for="f in facts.data"
            :key="f.name"
            class="group flex items-start gap-2 rounded-lg border p-2.5"
          >
            <span
              class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 text-xs font-medium"
              :class="
                f.origen === 'IA'
                  ? 'bg-violet-100 text-violet-700'
                  : 'bg-surface-gray-2 text-ink-gray-6'
              "
              >{{ f.origen === 'IA' ? 'IA' : 'Manual' }}</span
            >
            <div class="min-w-0 flex-1">
              <div class="whitespace-pre-line text-sm text-ink-gray-8">
                {{ f.hecho }}
              </div>
              <a
                v-if="f.fuente && /^https?:/.test(f.fuente)"
                :href="f.fuente"
                target="_blank"
                class="block truncate text-xs text-blue-600 hover:underline"
                >{{ f.fuente }}</a
              >
              <div
                v-else-if="f.fuente"
                class="truncate text-xs text-ink-gray-5"
              >
                {{ f.fuente }}
              </div>
            </div>
            <button
              class="shrink-0 rounded p-1 text-ink-gray-4 opacity-0 hover:bg-surface-gray-2 hover:text-ink-red-6 group-hover:opacity-100"
              @click="delFact(f.name)"
            >
              <FeatherIcon name="x" class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
        <div
          v-else
          class="flex h-24 items-center justify-center px-4 text-center text-sm text-ink-gray-4"
        >
          {{ __('Sin datos aún. Usá "Agregar".') }}
        </div>
      </div>
    </div>

    <!-- Ubicación -->
    <div class="flex min-h-0 flex-col overflow-hidden rounded-lg border">
      <div
        class="flex shrink-0 items-center gap-2 border-b px-4 py-3 text-base font-semibold text-ink-gray-8"
      >
        <FeatherIcon name="map-pin" class="h-5" />
        {{ __('Ubicación') }}
      </div>
      <div class="min-h-[16rem] flex-1">
        <iframe
          v-if="mapQuery"
          :src="mapUrl"
          class="h-full w-full border-0"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
        />
        <div
          v-else
          class="flex h-full items-center justify-center px-4 text-center text-sm text-ink-gray-4"
        >
          {{ __('Sin ubicación') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  FeatherIcon,
  Badge,
  Button,
  createListResource,
  call,
  toast,
} from 'frappe-ui'
import { ref, computed } from 'vue'

const props = defineProps({
  refField: { type: String, required: true },
  refValue: { type: String, required: true },
  mapQuery: { type: String, default: '' },
})

const facts = createListResource({
  type: 'list',
  doctype: 'CRM Fact',
  cache: ['facts', props.refField, props.refValue],
  fields: ['name', 'hecho', 'fuente', 'origen', 'modified'],
  filters: { [props.refField]: props.refValue },
  orderBy: 'modified desc',
  pageLength: 100,
  auto: true,
})

const showAdd = ref(false)
const nf = ref({ hecho: '', fuente: '' })

async function addFact() {
  if (!nf.value.hecho.trim()) return
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'CRM Fact',
        [props.refField]: props.refValue,
        hecho: nf.value.hecho,
        fuente: nf.value.fuente,
        origen: 'Manual',
      },
    })
    nf.value = { hecho: '', fuente: '' }
    showAdd.value = false
    facts.reload()
    toast.success(__('Dato agregado'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo guardar'))
  }
}
async function delFact(name) {
  try {
    await call('frappe.client.delete', { doctype: 'CRM Fact', name })
    facts.reload()
  } catch (e) {
    toast.error(__('No se pudo eliminar'))
  }
}

const mapUrl = computed(
  () =>
    'https://maps.google.com/maps?q=' +
    encodeURIComponent(props.mapQuery) +
    '&output=embed&z=6',
)
</script>
