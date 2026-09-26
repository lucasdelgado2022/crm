<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucidePlane class="h-5 w-5" />
        {{ __('Planificación de Viajes') }}
      </div>
    </template>
    <template #right-header>
      <Button variant="solid" iconLeft="plus" :label="__('Nuevo plan')" @click="openNew" />
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <div class="mb-3 flex items-center justify-between gap-2">
      <div class="text-base text-ink-gray-6">{{ __('{0} planes', [planes.length]) }}</div>
      <FormControl class="w-64" type="text" :placeholder="__('Buscar...')" v-model="search">
        <template #prefix><FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" /></template>
      </FormControl>
    </div>

    <div v-if="filtered.length" class="overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-4 py-2 text-left font-medium">{{ __('Título') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Estado') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Semana') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Responsable') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('Visitas') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('Costo total') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="p in filtered"
            :key="p.name"
            class="cursor-pointer border-b last:border-0 hover:bg-surface-gray-1"
            @click="open(p)"
          >
            <td class="px-4 py-2 font-medium text-ink-gray-8">{{ p.titulo }}</td>
            <td class="px-3 py-2"><Badge variant="subtle" :theme="estadoTheme(p.estado)" size="sm">{{ p.estado }}</Badge></td>
            <td class="px-3 py-2 text-ink-gray-7">{{ p.fecha_desde || '—' }}</td>
            <td class="px-3 py-2 text-ink-gray-7">{{ p.responsable || '—' }}</td>
            <td class="px-3 py-2 text-right text-ink-gray-8">{{ counts[p.name]?.visitas ?? '·' }}</td>
            <td class="px-3 py-2 text-right text-ink-gray-9">{{ money(counts[p.name]?.costo || 0) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4">
      <LucidePlane class="h-10 w-10" />
      <div>{{ __('Sin planes de viaje') }}</div>
    </div>
  </div>

  <Dialog v-model="showNew" :options="{ title: __('Nuevo plan de viaje'), size: 'lg' }">
    <template #body-content>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <FormControl type="text" :label="__('Título')" v-model="form.titulo" class="sm:col-span-2" />
        <FormControl type="select" :label="__('Estado')" v-model="form.estado" :options="ESTADOS" />
        <FormControl type="date" :label="__('Semana desde')" v-model="form.fecha_desde" />
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Responsable') }}</div>
          <Link doctype="User" :value="form.responsable" @change="(v) => (form.responsable = v)" />
        </div>
        <FormControl type="textarea" :label="__('Descripción')" v-model="form.descripcion" class="sm:col-span-2" />
      </div>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button @click="showNew = false">{{ __('Cancelar') }}</Button>
        <Button variant="solid" :loading="saving" @click="createPlan">{{ __('Crear') }}</Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import LucidePlane from '~icons/lucide/plane'
import { FeatherIcon, FormControl, Button, Badge, Dialog, call, toast, usePageMeta } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const ESTADOS = ['Planificado', 'En curso', 'Realizado', 'Cancelado']
const planes = ref([])
const counts = ref({})
const search = ref('')

async function load() {
  planes.value = await call('frappe.client.get_list', {
    doctype: 'CRM Plan Viaje',
    fields: ['name', 'titulo', 'estado', 'fecha_desde', 'responsable'],
    order_by: 'modified desc',
    limit_page_length: 0,
  })
  await loadCounts()
}
async function loadCounts() {
  const m = {}
  try {
    const vis = await call('frappe.client.get_list', {
      doctype: 'CRM Plan Viaje Visita',
      filters: { parenttype: 'CRM Plan Viaje' },
      fields: ['parent'],
      limit_page_length: 0,
    })
    for (const v of vis) (m[v.parent] = m[v.parent] || { visitas: 0, costo: 0 }).visitas += 1
    const cos = await call('frappe.client.get_list', {
      doctype: 'CRM Plan Viaje Costo',
      filters: { parenttype: 'CRM Plan Viaje' },
      fields: ['parent', 'monto'],
      limit_page_length: 0,
    })
    for (const c of cos) (m[c.parent] = m[c.parent] || { visitas: 0, costo: 0 }).costo += Number(c.monto) || 0
  } catch (e) {
    // ignore
  }
  counts.value = m
}
load()

const filtered = computed(() => {
  let arr = planes.value
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    arr = arr.filter((p) => (p.titulo || '').toLowerCase().includes(q))
  }
  return arr
})

function estadoTheme(e) {
  return { Planificado: 'gray', 'En curso': 'blue', Realizado: 'green', Cancelado: 'red' }[e] || 'gray'
}
function money(v) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v || 0)
}
function open(p) {
  router.push({ name: 'PlanViajeDetalle', params: { planId: p.name } })
}

const showNew = ref(false)
const saving = ref(false)
const form = ref({})
function openNew() {
  form.value = { titulo: '', estado: 'Planificado', fecha_desde: '', responsable: '', descripcion: '' }
  showNew.value = true
}
async function createPlan() {
  if (!form.value.titulo?.trim()) {
    toast.error(__('El título es obligatorio'))
    return
  }
  saving.value = true
  try {
    const doc = await call('frappe.client.insert', { doc: { doctype: 'CRM Plan Viaje', ...form.value } })
    showNew.value = false
    router.push({ name: 'PlanViajeDetalle', params: { planId: doc.name } })
  } catch (e) {
    toast.error((e && e.messages && e.messages[0]) || __('No se pudo crear'))
  } finally {
    saving.value = false
  }
}

usePageMeta(() => ({ title: __('Planificación de Viajes') }))
</script>
