<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <BellIcon class="h-5 w-5" />
        {{ __('Alertas') }}
      </div>
    </template>
    <template #right-header>
      <label
        class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
      >
        <input v-model="soloMias" type="checkbox" class="rounded" />
        {{ __('Solo míos') }}
      </label>
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Resumen closed-won -->
    <div class="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
      <div class="rounded-lg border border-green-200 bg-green-50 p-3">
        <div class="text-xs text-green-700">{{ __('Ganado este mes') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-green-800">
          {{ money(won.mes.monto) }}
        </div>
        <div class="text-xs text-green-700">
          {{ won.mes.count }} {{ __('oportunidades') }}
        </div>
      </div>
      <div class="rounded-lg border border-green-200 bg-green-50 p-3">
        <div class="text-xs text-green-700">{{ __('Ganado este año') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-green-800">
          {{ money(won.anio.monto) }}
        </div>
        <div class="text-xs text-green-700">
          {{ won.anio.count }} {{ __('oportunidades') }}
        </div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Por cerrar este mes') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">
          {{ money(porCerrar.monto) }}
        </div>
        <div class="text-xs text-ink-gray-5">
          {{ porCerrar.count }} {{ __('oportunidades') }}
        </div>
      </div>
      <div
        class="rounded-lg border p-3"
        :class="overdue.length ? 'border-red-200 bg-red-50' : ''"
      >
        <div class="text-xs" :class="overdue.length ? 'text-red-700' : 'text-ink-gray-5'">
          {{ __('Tareas vencidas') }}
        </div>
        <div
          class="mt-0.5 text-xl font-semibold"
          :class="overdue.length ? 'text-red-700' : 'text-ink-gray-9'"
        >
          {{ overdue.length }}
        </div>
      </div>
    </div>

    <!-- Tareas vencidas -->
    <div class="rounded-lg border">
      <div class="flex items-center gap-2 border-b px-4 py-3 text-base font-semibold text-ink-gray-8">
        <FeatherIcon name="alert-triangle" class="h-4 w-4 text-red-500" />
        {{ __('Tareas vencidas') }}
        <span class="text-ink-gray-5">{{ overdue.length }}</span>
      </div>
      <div v-if="loading" class="flex h-32 items-center justify-center text-ink-gray-4">
        {{ __('Cargando...') }}
      </div>
      <div
        v-else-if="!overdue.length"
        class="flex h-32 flex-col items-center justify-center gap-2 text-ink-gray-4"
      >
        <FeatherIcon name="check-circle" class="h-7 w-7 text-green-500" />
        {{ __('Sin tareas vencidas 🎉') }}
      </div>
      <table v-else class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-4 py-2 text-left font-medium">{{ __('Tarea') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Vencimiento') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Prioridad') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Responsable') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Vinculado a') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="t in overdue"
            :key="t.name"
            class="cursor-pointer border-b last:border-0 hover:bg-surface-gray-1"
            @click="openRef(t)"
          >
            <td class="px-4 py-2 text-ink-gray-8">{{ t.title || '—' }}</td>
            <td class="whitespace-nowrap px-3 py-2 text-red-600">
              {{ diasVencida(t.due_date) }}
            </td>
            <td class="px-3 py-2">
              <span
                class="rounded px-1.5 py-0.5 text-xs font-medium"
                :class="prioClass(t.priority)"
                >{{ t.priority || '—' }}</span
              >
            </td>
            <td class="px-3 py-2 text-ink-gray-7">
              {{ userLabel(t.assigned_to) }}
            </td>
            <td class="px-3 py-2 text-ink-gray-6">
              <span v-if="t.reference_docname" class="text-blue-600 hover:underline">
                {{ refLabel(t) }}
              </span>
              <span v-else>—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import BellIcon from '~icons/lucide/bell'
import { FeatherIcon, createResource } from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { user } = sessionStore()
const { getUser } = usersStore()

const soloMias = ref(true)

function nowStr() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

const tasksRes = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    const filters = {
      status: ['not in', ['Done', 'Canceled']],
      due_date: ['<', nowStr()],
    }
    if (soloMias.value) filters.assigned_to = user
    return {
      doctype: 'CRM Task',
      filters,
      fields: [
        'name',
        'title',
        'due_date',
        'priority',
        'status',
        'assigned_to',
        'reference_doctype',
        'reference_docname',
      ],
      order_by: 'due_date asc',
      limit_page_length: 0,
    }
  },
  auto: true,
})

const dealsRes = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    const filters = {}
    if (soloMias.value) filters.deal_owner = user
    return {
      doctype: 'CRM Deal',
      filters,
      fields: [
        'name',
        'status',
        'deal_owner',
        'custom_solaer_revenue',
        'expected_closure_date',
      ],
      limit_page_length: 0,
    }
  },
  auto: true,
})

watch(soloMias, () => {
  tasksRes.reload()
  dealsRes.reload()
})

const loading = computed(() => tasksRes.loading || dealsRes.loading)
const overdue = computed(() => tasksRes.data || [])
const deals = computed(() => dealsRes.data || [])

const now = new Date()
const curMonth = now.getMonth()
const curYear = now.getFullYear()

const won = computed(() => {
  const res = { mes: { count: 0, monto: 0 }, anio: { count: 0, monto: 0 } }
  for (const d of deals.value) {
    if (d.status !== 'Won') continue
    const amt = Number(d.custom_solaer_revenue) || 0
    if (!d.expected_closure_date) continue
    const y = Number(d.expected_closure_date.slice(0, 4))
    const m = Number(d.expected_closure_date.slice(5, 7)) - 1
    if (y === curYear) {
      res.anio.count++
      res.anio.monto += amt
      if (m === curMonth) {
        res.mes.count++
        res.mes.monto += amt
      }
    }
  }
  return res
})

const porCerrar = computed(() => {
  const res = { count: 0, monto: 0 }
  for (const d of deals.value) {
    if (d.status === 'Won' || d.status === 'Lost') continue
    if (!d.expected_closure_date) continue
    const y = Number(d.expected_closure_date.slice(0, 4))
    const m = Number(d.expected_closure_date.slice(5, 7)) - 1
    if (y === curYear && m === curMonth) {
      res.count++
      res.monto += Number(d.custom_solaer_revenue) || 0
    }
  }
  return res
})

function diasVencida(due) {
  if (!due) return ''
  const d = new Date(String(due).replace(' ', 'T'))
  const dias = Math.floor((Date.now() - d.getTime()) / 86400000)
  if (dias <= 0) return __('hoy')
  return __('hace {0}d', [dias])
}
function prioClass(p) {
  if (p === 'High') return 'bg-red-100 text-red-700'
  if (p === 'Medium') return 'bg-amber-100 text-amber-700'
  return 'bg-surface-gray-2 text-ink-gray-6'
}
function userLabel(u) {
  if (!u) return '—'
  return getUser(u)?.full_name || u
}
function refLabel(t) {
  const dt = (t.reference_doctype || '').replace('CRM ', '')
  return dt + ': ' + t.reference_docname
}
function openRef(t) {
  if (!t.reference_docname) return
  const map = {
    'CRM Deal': { name: 'Deal', param: 'dealId' },
    'CRM Lead': { name: 'Lead', param: 'leadId' },
  }
  const r = map[t.reference_doctype]
  if (r) router.push({ name: r.name, params: { [r.param]: t.reference_docname } })
}
function money(n) {
  const v = Number(n) || 0
  if (!v) return '$0'
  return '$' + Math.round(v).toLocaleString('es-AR')
}
</script>
