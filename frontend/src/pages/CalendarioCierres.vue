<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucideCalendarClock class="h-5 w-5" />
        {{ __('Calendario de Cierres') }}
      </div>
    </template>
  </LayoutHeader>
  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Navegación de mes -->
    <div class="mb-4 flex items-center justify-between gap-2">
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="prevMonth">
          <template #icon><FeatherIcon name="chevron-left" class="h-4 w-4" /></template>
        </Button>
        <div class="min-w-44 text-center text-base font-semibold text-ink-gray-8">
          {{ monthLabel }}
        </div>
        <Button variant="outline" @click="nextMonth">
          <template #icon><FeatherIcon name="chevron-right" class="h-4 w-4" /></template>
        </Button>
        <Button variant="subtle" @click="goToday">{{ __('Hoy') }}</Button>
      </div>
      <div class="flex flex-wrap items-center gap-2 text-xs text-ink-gray-6">
        <button
          type="button"
          class="flex items-center gap-1 rounded px-1.5 py-0.5 transition-colors"
          :class="tipoFilter === 'renov' ? 'bg-amber-100 ring-1 ring-amber-400' : 'hover:bg-surface-gray-2'"
          :title="__('Filtrar renovaciones')"
          @click="toggleTipo('renov')"
        >
          <span class="rounded bg-amber-300 px-1 text-[9px] font-bold text-amber-900">RN</span>
          {{ __('Renovación') }}
        </button>
        <button
          type="button"
          class="flex items-center gap-1 rounded px-1.5 py-0.5 transition-colors"
          :class="tipoFilter === 'nueva' ? 'bg-surface-gray-3 ring-1 ring-ink-gray-4' : 'hover:bg-surface-gray-2'"
          :title="__('Filtrar nuevas')"
          @click="toggleTipo('nueva')"
        >
          <span class="rounded bg-ink-gray-3 px-1 text-[9px] font-bold text-ink-gray-8">NW</span>
          {{ __('Nueva') }}
        </button>
        <span class="flex items-center gap-1">
          <span class="h-2.5 w-2.5 rounded-full bg-green-500"></span>{{ __('Ganada') }}
        </span>
        <span class="flex items-center gap-1">
          <span class="h-2.5 w-2.5 rounded-full bg-red-500"></span>{{ __('Perdida') }}
        </span>
        <span class="flex items-center gap-1">
          <span class="h-2.5 w-2.5 rounded-full bg-violet-500"></span>{{ __('Listo para cerrar') }}
        </span>
        <span class="flex items-center gap-1">
          <span class="h-2.5 w-2.5 rounded-full bg-blue-500"></span>{{ __('En curso') }}
        </span>
      </div>
    </div>

    <!-- Filtro de visualización de monto -->
    <div class="mb-4 flex flex-wrap items-center gap-2">
      <span class="text-xs text-ink-gray-5">{{ __('Monto a visualizar') }}:</span>
      <div class="flex overflow-hidden rounded-lg border border-outline-gray-2">
        <button
          v-for="opt in AMOUNT_OPTIONS"
          :key="opt.key"
          class="border-r px-3 py-1 text-xs last:border-r-0"
          :class="
            amountType === opt.key
              ? 'bg-surface-gray-3 font-medium text-ink-gray-9'
              : 'bg-surface-white text-ink-gray-6 hover:text-ink-gray-9'
          "
          @click="amountType = opt.key"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Resumen del mes -->
    <div class="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Cierres del mes') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">{{ monthSummary.count }}</div>
      </div>
      <div class="rounded-lg border border-green-200 bg-green-50 p-3">
        <div class="text-xs text-green-700">
          {{ __('Ganado') }}
          <span class="text-green-600">· {{ monthSummary.wonN }}</span>
        </div>
        <div class="mt-0.5 text-xl font-semibold text-green-800">{{ money(monthSummary.won) }}</div>
      </div>
      <div class="rounded-lg border border-blue-200 bg-blue-50 p-3">
        <div class="text-xs text-blue-700">
          {{ __('En curso') }}
          <span class="text-blue-600">· {{ monthSummary.openN }}</span>
        </div>
        <div class="mt-0.5 text-xl font-semibold text-blue-800">{{ money(monthSummary.open) }}</div>
      </div>
      <div class="rounded-lg border border-red-200 bg-red-50 p-3">
        <div class="text-xs text-red-700">
          {{ __('Perdido') }}
          <span class="text-red-600">· {{ monthSummary.lostN }}</span>
        </div>
        <div class="mt-0.5 text-xl font-semibold text-red-800">{{ money(monthSummary.lost) }}</div>
      </div>
    </div>

    <!-- Cabecera días -->
    <div class="grid grid-cols-7 gap-0.5 overflow-hidden rounded-t-lg border border-b-0 border-ink-gray-4 bg-ink-gray-4 text-center text-xs font-medium text-ink-gray-5">
      <div v-for="d in weekDays" :key="d" class="bg-surface-gray-2 py-2">{{ d }}</div>
    </div>
    <!-- Celdas -->
    <div class="grid grid-cols-7 gap-0.5 overflow-hidden rounded-b-lg border border-ink-gray-4 bg-ink-gray-4">
      <div
        v-for="(cell, idx) in cells"
        :key="idx"
        class="min-h-28 bg-surface-white p-1.5 align-top transition-colors"
        :class="[
          cell.inMonth ? '' : 'bg-surface-gray-2/60',
          dragOverKey === cell.key ? 'bg-blue-50 ring-2 ring-inset ring-blue-400' : '',
        ]"
        @dragover.prevent="dragOverKey = cell.key"
        @dragleave="onDragLeave(cell)"
        @drop="onDrop($event, cell)"
      >
        <div
          class="mb-1 flex items-center justify-between text-xs"
          :class="cell.isToday ? 'font-bold text-blue-600' : 'text-ink-gray-5'"
        >
          <span
            :class="
              cell.isToday
                ? 'flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-white'
                : ''
            "
          >
            {{ cell.day }}
          </span>
          <span v-if="cell.deals.length" class="text-ink-gray-4">
            {{ cell.deals.length }}
          </span>
        </div>
        <div class="flex flex-col gap-1">
          <div
            v-for="d in visibleDeals(cell)"
            :key="d.name"
            :draggable="!isRenov(d)"
            class="block rounded px-1.5 py-1 text-xs text-white"
            :class="[statusBg(d.status), isRenov(d) ? 'cursor-pointer' : 'cursor-grab active:cursor-grabbing']"
            :title="(d.organization || d.name) + ' · ' + money(dealVal(d)) + (isRenov(d) ? ' · ' + __('Renovación (no se mueve)') : '')"
            @click="openDeal(d.name)"
            @dragstart="onDragStart($event, d)"
          >
            <div class="flex items-center gap-1 leading-tight">
              <span
                class="shrink-0 rounded px-1 text-[9px] font-bold"
                :class="isRenov(d) ? 'bg-amber-300 text-amber-900' : 'bg-white/30 text-white'"
              >
                {{ isRenov(d) ? 'RN' : 'NW' }}
              </span>
              <span class="truncate font-medium">{{ d.organization || d.name }}</span>
            </div>
            <div class="mt-0.5 flex items-center justify-between gap-1">
              <span class="truncate opacity-90">{{ moneyShort(dealVal(d)) }}</span>
              <div class="flex shrink-0 items-center -space-x-1.5">
                <Avatar
                  v-for="p in dealPeople(d)"
                  :key="p.email"
                  size="sm"
                  :label="p.label"
                  :image="p.image"
                  :title="p.title"
                  class="ring-1 ring-white"
                />
              </div>
            </div>
          </div>
          <button
            v-if="cell.deals.length > 2"
            class="rounded px-1.5 py-0.5 text-[10px] font-medium text-ink-gray-6 hover:bg-surface-gray-3"
            @click.stop="toggleExpand(cell)"
          >
            {{ isExpanded(cell) ? __('Ver menos') : '+' + (cell.deals.length - 2) + ' ' + __('más') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideCalendarClock from '~icons/lucide/calendar-clock'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'
import { FeatherIcon, Button, Avatar, call, toast, createResource, usePageMeta } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { getUser, isAdmin } = usersStore()
const { user: sessionUser } = sessionStore()
function openDeal(name) {
  router.push({ name: 'Deal', params: { dealId: name } })
}

// Expandir días con más de 2 cierres
const expandedDays = ref(new Set())
function isExpanded(cell) {
  return expandedDays.value.has(cell.key)
}
function toggleExpand(cell) {
  const s = new Set(expandedDays.value)
  if (s.has(cell.key)) s.delete(cell.key)
  else s.add(cell.key)
  expandedDays.value = s
}
function visibleDeals(cell) {
  if (cell.deals.length <= 2 || isExpanded(cell)) return cell.deals
  return cell.deals.slice(0, 2)
}

const weekDays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const MONTHS = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

const AMOUNT_OPTIONS = [
  { key: 'deal_value', label: __('Valor oportunidad') },
  { key: 'custom_ds_revenue', label: __('DS Revenue') },
  { key: 'custom_solaer_revenue', label: __('Solaer Revenue') },
]
const amountType = ref('deal_value')

const today = new Date()
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth())
const dragOverKey = ref(null)
const tipoFilter = ref(null) // null | 'renov' | 'nueva'
function toggleTipo(t) {
  tipoFilter.value = tipoFilter.value === t ? null : t
}

const dealsRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Deal',
    filters: { closed_date: ['is', 'set'] },
    fields: [
      'name',
      'organization',
      'closed_date',
      'status',
      'deal_owner',
      'deal_value',
      'custom_ds_revenue',
      'custom_solaer_revenue',
      'custom_tipo_oportunidad',
    ],
    limit_page_length: 0,
  },
  auto: true,
})
const deals = computed(() => {
  const all = dealsRes.data || []
  try { if (isAdmin()) return all } catch (e) {}
  return all.filter((d) => d.deal_owner === sessionUser)
})

// Deals filtrados por tipo (RN / NW) según las referencias clickeables
const filteredDeals = computed(() => {
  if (!tipoFilter.value) return deals.value
  return deals.value.filter((d) =>
    tipoFilter.value === 'renov' ? isRenov(d) : !isRenov(d),
  )
})

// Apoyo comercial (tabla hija: varios usuarios por oportunidad)
const apoyoRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Apoyo Comercial User',
    filters: { parenttype: 'CRM Deal', parentfield: 'custom_apoyo_comercial' },
    fields: ['parent', 'user'],
    limit_page_length: 0,
  },
  auto: true,
})
const apoyoByDeal = computed(() => {
  const m = {}
  for (const r of apoyoRes.data || []) {
    if (!r.user) continue
    ;(m[r.parent] = m[r.parent] || []).push(r.user)
  }
  return m
})

// Mapa fecha 'YYYY-MM-DD' -> [deals]
const byDate = computed(() => {
  const m = {}
  for (const d of filteredDeals.value) {
    const key = String(d.closed_date).slice(0, 10)
    ;(m[key] = m[key] || []).push(d)
  }
  return m
})

const monthLabel = computed(() => `${MONTHS[viewMonth.value]} ${viewYear.value}`)

const monthSummary = computed(() => {
  const s = { count: 0, won: 0, open: 0, lost: 0, wonN: 0, openN: 0, lostN: 0 }
  for (const d of filteredDeals.value) {
    const dt = String(d.closed_date).slice(0, 10)
    if (Number(dt.slice(0, 4)) !== viewYear.value) continue
    if (Number(dt.slice(5, 7)) - 1 !== viewMonth.value) continue
    s.count += 1
    const v = dealVal(d)
    if (d.status === 'Won') {
      s.won += v
      s.wonN += 1
    } else if (d.status === 'Lost') {
      s.lost += v
      s.lostN += 1
    } else {
      s.open += v
      s.openN += 1
    }
  }
  return s
})

function pad(n) {
  return String(n).padStart(2, '0')
}

const cells = computed(() => {
  const y = viewYear.value
  const mo = viewMonth.value
  const first = new Date(y, mo, 1)
  let startOffset = (first.getDay() + 6) % 7
  const start = new Date(y, mo, 1 - startOffset)
  const todayKey = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`
  const out = []
  for (let i = 0; i < 42; i++) {
    const dt = new Date(start.getFullYear(), start.getMonth(), start.getDate() + i)
    const key = `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}`
    out.push({
      key,
      day: dt.getDate(),
      inMonth: dt.getMonth() === mo,
      isToday: key === todayKey,
      deals: byDate.value[key] || [],
    })
  }
  return out
})

function prevMonth() {
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value -= 1
  } else viewMonth.value -= 1
}
function nextMonth() {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value += 1
  } else viewMonth.value += 1
}
function goToday() {
  viewYear.value = today.getFullYear()
  viewMonth.value = today.getMonth()
}

function statusBg(status) {
  if (status === 'Won') return 'bg-green-500 hover:bg-green-600'
  if (status === 'Lost') return 'bg-red-500 hover:bg-red-600'
  if (/listo para cerrar/i.test(status || '')) return 'bg-violet-500 hover:bg-violet-600'
  return 'bg-blue-500 hover:bg-blue-600'
}
function isRenov(d) {
  return /^renovaci/i.test(d.custom_tipo_oportunidad || '')
}
function dealVal(d) {
  return Number(d[amountType.value]) || 0
}
function dealPeople(d) {
  const people = []
  if (d.deal_owner) {
    const u = getUser(d.deal_owner)
    people.push({
      email: d.deal_owner,
      label: u?.full_name || d.deal_owner,
      image: u?.user_image,
      title: __('Responsable') + ': ' + (u?.full_name || d.deal_owner),
    })
  }
  for (const email of apoyoByDeal.value[d.name] || []) {
    const u = getUser(email)
    people.push({
      email: 'apoyo-' + email,
      label: u?.full_name || email,
      image: u?.user_image,
      title: __('Apoyo') + ': ' + (u?.full_name || email),
    })
  }
  return people
}
function money(v) {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(v || 0)
}
function moneyShort(v) {
  const n = Number(v) || 0
  const a = Math.abs(n)
  if (a >= 1e6) return '$' + (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M'
  if (a >= 1e3) return '$' + Math.round(n / 1e3) + 'k'
  return '$' + n
}

// --- Drag & drop: cambiar fecha de cierre ---
function onDragStart(e, d) {
  if (isRenov(d)) {
    e.preventDefault()
    return
  }
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', d.name)
}
function onDragLeave(cell) {
  if (dragOverKey.value === cell.key) dragOverKey.value = null
}
async function onDrop(e, cell) {
  e.preventDefault()
  dragOverKey.value = null
  const name = e.dataTransfer.getData('text/plain')
  if (!name) return
  const d = deals.value.find((x) => x.name === name)
  if (!d) return
  if (String(d.closed_date).slice(0, 10) === cell.key) return
  const prev = d.closed_date
  d.closed_date = cell.key // optimista
  try {
    await call('frappe.client.set_value', {
      doctype: 'CRM Deal',
      name,
      fieldname: 'closed_date',
      value: cell.key,
    })
    toast.success(__('Fecha de cierre actualizada'))
    dealsRes.reload()
  } catch (err) {
    d.closed_date = prev
    toast.error((err && err.messages && err.messages[0]) || __('No se pudo mover'))
    dealsRes.reload()
  }
}

usePageMeta(() => ({ title: __('Calendario de Cierres') }))
</script>
