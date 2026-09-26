<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <TrackIcon class="h-5 w-5" />
        {{ __('Seguimiento') }}
      </div>
    </template>
    <template #right-header>
      <Button
        variant="ghost"
        icon="refresh-cw"
        :loading="loading"
        @click="load"
      />
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-hidden">
    <!-- Filtros -->
    <div class="flex flex-wrap items-center gap-2 border-b border-outline-gray-modals px-4 py-2.5">
      <div class="relative">
        <FeatherIcon
          name="search"
          class="pointer-events-none absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4"
        />
        <input
          v-model="search"
          type="text"
          class="h-8 w-56 rounded border border-outline-gray-2 bg-surface-white pl-8 pr-2 text-base text-ink-gray-8 placeholder:text-ink-gray-4 focus:border-outline-gray-3 focus:outline-none"
          :placeholder="__('Buscar organización...')"
        />
      </div>
      <select
        v-model="kindFilter"
        class="h-8 rounded border border-outline-gray-2 bg-surface-white px-2 text-base text-ink-gray-8"
      >
        <option value="">{{ __('Todos') }}</option>
        <option value="Deal">{{ __('Oportunidades') }}</option>
        <option value="Lead">{{ __('Leads') }}</option>
      </select>
      <select
        v-model="statusFilter"
        class="h-8 max-w-[180px] rounded border border-outline-gray-2 bg-surface-white px-2 text-base text-ink-gray-8"
        :title="__('Filtrar por estado')"
      >
        <option value="">{{ __('Todos los estados') }}</option>
        <option v-for="s in statusList" :key="s" :value="s">{{ s }}</option>
      </select>
      <select
        v-model.number="diasFilter"
        class="h-8 rounded border border-outline-gray-2 bg-surface-white px-2 text-base text-ink-gray-8"
        :title="__('Días sin interacción')"
      >
        <option :value="0">{{ __('Sin interacción: todas') }}</option>
        <option :value="15">{{ __('+15 días sin interacción') }}</option>
        <option :value="30">{{ __('+1 mes sin interacción') }}</option>
        <option :value="90">{{ __('+3 meses sin interacción') }}</option>
      </select>
      <select
        v-model="selectedUser"
        class="h-8 rounded border border-outline-gray-2 bg-surface-white px-2 text-base text-ink-gray-8"
        :title="__('Ver seguimiento de (responsable o apoyo)')"
        @change="load"
      >
        <option
          v-for="u in userOptions"
          :key="u.user"
          :value="u.user"
        >
          {{ u.full_name }}
        </option>
      </select>
      <label class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7">
        <input
          type="checkbox"
          v-model="groupByOrg"
          class="h-3.5 w-3.5 rounded border-outline-gray-3"
        />
        {{ __('Agrupar por organización') }}
      </label>
      <Button
        variant="subtle"
        size="sm"
        :class="sortMode === 'inter' ? '!bg-surface-gray-3 !text-ink-gray-9' : ''"
        :tooltip="__('Ordenar por días sin interacción (más viejos primero)')"
        @click="toggleSort('inter')"
      >
        ↕ {{ __('Días s/ inter.') }}
      </Button>
      <Button
        variant="subtle"
        size="sm"
        :class="sortMode === 'cierre' ? '!bg-surface-gray-3 !text-ink-gray-9' : ''"
        :tooltip="__('Ordenar por días a cierre (más próximos primero)')"
        @click="toggleSort('cierre')"
      >
        ↕ {{ __('Días a cierre') }}
      </Button>
      <span class="ml-auto text-sm text-ink-gray-5">
        {{ filteredRows.length }} {{ __('interacciones') }} ·
        {{ groups.length }} {{ __('organizaciones') }}
      </span>
    </div>

    <!-- Tabla -->
    <div class="flex-1 overflow-auto px-4 py-3">
      <div
        v-if="!groups.length"
        class="flex h-full flex-col items-center justify-center gap-2 text-ink-gray-4"
      >
        <TrackIcon class="h-10 w-10" />
        <div class="text-base">{{ loading ? __('Cargando...') : __('Sin interacciones') }}</div>
      </div>

      <table
        v-else
        class="w-full table-fixed border-collapse text-sm"
      >
        <thead>
          <tr class="text-left text-ink-gray-6">
            <th class="w-56 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 font-medium">{{ __('Organización') }}</th>
            <th class="w-28 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 font-medium">{{ __('Oportunidad') }}</th>
            <th class="w-40 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 font-medium">{{ __('Título') }}</th>
            <th class="w-44 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 font-medium">{{ __('Estado') }}</th>
            <th class="w-36 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 font-medium">{{ __('Producto') }}</th>
            <th class="w-20 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 text-center font-medium" :title="__('Días desde la última interacción')">{{ __('Días s/ inter.') }}</th>
            <th class="w-20 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 text-center font-medium" :title="__('Días al Closed Date')">{{ __('Días a cierre') }}</th>
            <th class="w-20 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 font-medium">{{ __('Fecha') }}</th>
            <th class="border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 font-medium">{{ __('Interacción') }}</th>
            <th class="w-28 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 font-medium">{{ __('Contacto') }}</th>
            <th class="w-14 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 text-center font-medium">{{ __('Agente') }}</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(g, gi) in groups" :key="g.organization">
            <!-- Separador entre organizaciones -->
            <tr v-if="gi > 0 && groupByOrg" aria-hidden="true">
              <td colspan="11" class="h-2 bg-surface-gray-3 p-0"></td>
            </tr>
            <template v-for="(rf, ri) in g.refs" :key="rf.ref_docname">
              <tr
                v-for="(ln, li) in rf.lines"
                :key="ln.name"
                class="align-top hover:bg-surface-gray-1"
              >
                <!-- Organización (rowspan sobre todas sus líneas) -->
                <td
                  v-if="ri === 0 && li === 0"
                  :rowspan="g.orgRowspan"
                  class="border border-outline-gray-2 px-2 py-1.5 align-top font-medium text-ink-gray-8"
                >
                  <div
                    class="cursor-pointer break-words hover:text-ink-blue-link"
                    :title="__('Ver organización')"
                    @click="openOrg(g.organization)"
                  >
                    {{ g.organization }}
                  </div>
                </td>
                <!-- Oportunidad / Lead (rowspan sobre las líneas de ese ref) -->
                <td
                  v-if="li === 0"
                  :rowspan="rf.lines.length"
                  class="border border-outline-gray-2 px-2 py-1.5 text-ink-gray-8"
                >
                  <div
                    class="cursor-pointer hover:text-ink-blue-link"
                    @click="openRef(rf)"
                  >
                    <span v-if="rf.kind === 'Lead'" class="text-ink-gray-6">{{ __('Lead') }}</span>
                    <span v-else-if="esCodigo(rf.oportunidad)" class="text-ink-gray-4">{{ __('Sin numerar') }}</span>
                    <span v-else>{{ rf.oportunidad }}</span>
                  </div>
                </td>
                <!-- Título -->
                <td
                  v-if="li === 0"
                  :rowspan="rf.lines.length"
                  class="border border-outline-gray-2 px-2 py-1.5 text-ink-gray-7"
                >
                  <div class="line-clamp-2 max-w-[10rem]" :title="rf.titulo">
                    {{ rf.titulo }}
                  </div>
                </td>
                <!-- Estado -->
                <td
                  v-if="li === 0"
                  :rowspan="rf.lines.length"
                  class="border border-outline-gray-2 px-2 py-1.5 text-ink-gray-7"
                >
                  <div class="flex items-start gap-1">
                    <span
                      v-if="rf.status"
                      class="flex min-w-0 flex-1 items-start gap-1"
                    >
                      <IndicatorIcon
                        v-if="rf.kind === 'Deal'"
                        class="mt-1 shrink-0"
                        :class="getDealStatus(rf.status)?.color"
                      />
                      <span class="break-words">{{ rf.status }}</span>
                    </span>
                    <span v-else class="flex-1"></span>
                    <Dropdown :options="statusItems(rf)">
                      <button
                        type="button"
                        class="shrink-0 rounded p-0.5 hover:bg-surface-gray-2"
                        :title="__('Cambiar estado')"
                      >
                        <FeatherIcon
                          name="chevron-down"
                          class="h-4 w-4 text-ink-gray-5"
                        />
                      </button>
                    </Dropdown>
                  </div>
                </td>
                <!-- Producto (pill de color) -->
                <td
                  v-if="li === 0"
                  :rowspan="rf.lines.length"
                  class="border border-outline-gray-2 px-2 py-1.5"
                >
                  <span
                    v-if="rf.producto"
                    class="inline-block rounded px-1.5 py-0.5 text-xs font-medium"
                    :class="productoColor(rf.producto)"
                  >
                    {{ rf.producto }}
                  </span>
                </td>
                <!-- Días desde última interacción -->
                <td
                  v-if="li === 0"
                  :rowspan="rf.lines.length"
                  class="border border-outline-gray-2 px-2 py-1.5 text-center font-medium"
                  :class="
                    rf.dias == null
                      ? 'text-ink-gray-4'
                      : rf.dias > 60
                        ? 'text-red-600'
                        : rf.dias > 30
                          ? 'text-amber-600'
                          : 'text-ink-gray-7'
                  "
                >
                  {{ rf.dias == null ? '—' : rf.dias }}
                </td>
                <!-- Días a cierre (Closed Date) -->
                <td
                  v-if="li === 0"
                  :rowspan="rf.lines.length"
                  class="border border-outline-gray-2 px-2 py-1.5 text-center font-medium"
                  :class="
                    rf.diasCierre == null
                      ? 'text-ink-gray-4'
                      : rf.diasCierre < 0
                        ? 'text-red-600'
                        : rf.diasCierre <= 15
                          ? 'text-amber-600'
                          : 'text-ink-gray-7'
                  "
                >
                  {{ rf.diasCierre == null ? '—' : rf.diasCierre }}
                </td>
                <!-- Fecha -->
                <td class="whitespace-nowrap border border-outline-gray-2 px-2 py-1.5 text-right text-ink-gray-7">
                  {{ fmtDate(ln.fecha) }}
                </td>
                <!-- Interacción (clic para editar; "+" para agregar) -->
                <td class="border border-outline-gray-2 px-2 py-1.5 align-top text-ink-gray-8">
                  <div class="flex items-start gap-1">
                    <div class="min-w-0 flex-1">
                      <span
                        v-if="ln.sin_seguimiento"
                        class="text-sm italic text-ink-gray-4"
                      >
                        {{ __('— sin seguimiento —') }}
                      </span>
                      <template v-else>
                        <textarea
                          v-if="editing === ln.name"
                          :ref="(el) => el && el.focus()"
                          v-model="editText"
                          rows="3"
                          class="w-full rounded border border-outline-gray-3 bg-surface-white p-1.5 text-sm text-ink-gray-8 focus:outline-none"
                          @keydown.enter.exact.prevent="saveEdit(ln)"
                          @keydown.esc="editing = null"
                          @blur="saveEdit(ln)"
                        />
                        <div
                          v-else
                          class="line-clamp-2 w-full cursor-text whitespace-pre-line break-words rounded px-1 hover:bg-surface-gray-2"
                          :class="ln.es_proximo_paso ? 'font-medium text-purple-600' : ''"
                          :title="ln.interaccion"
                          @click="startEdit(ln)"
                        >
                          <span v-if="ln.es_proximo_paso" class="text-xs">▸ </span>{{ ln.interaccion }}
                        </div>
                      </template>
                    </div>
                    <Button
                      v-if="li === 0"
                      variant="ghost"
                      size="sm"
                      icon="plus"
                      class="shrink-0 text-ink-gray-6"
                      :tooltip="__('Agregar interacción')"
                      @click="openInteraction(rf)"
                    />
                  </div>
                </td>
                <!-- Contacto -->
                <td class="border border-outline-gray-2 px-2 py-1.5 text-ink-gray-7">
                  <div class="truncate" :title="ln.contacto">{{ ln.contacto }}</div>
                </td>
                <!-- Agente (avatar) -->
                <td class="border border-outline-gray-2 px-2 py-1.5 text-center">
                  <div class="flex justify-center">
                    <UserAvatar v-if="ln.agent" :user="ln.agent" size="sm" />
                  </div>
                </td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>
  </div>

  <Dialog
    v-model="showInteraction"
    :options="{ title: __('Interacciones'), size: '4xl' }"
    @close="load"
  >
    <template #body-content>
      <div v-if="currentRef" class="h-[60vh] overflow-hidden">
        <InteractionArea
          :doctype="currentRef.doctype"
          :docname="currentRef.docname"
        />
      </div>
    </template>
  </Dialog>

  <Dialog
    v-model="showOrg"
    :options="{ title: __('Organización'), size: 'lg' }"
  >
    <template #body-content>
      <div v-if="orgData" class="flex flex-col gap-4 text-sm">
        <div class="flex items-center gap-3">
          <Avatar
            size="2xl"
            :label="orgData.organization_name || orgName"
            :image="orgData.organization_logo"
          />
          <div class="min-w-0">
            <div class="truncate text-base font-semibold text-ink-gray-9">
              {{ orgData.organization_name || orgName }}
            </div>
            <a
              v-if="orgData.website"
              :href="orgData.website"
              target="_blank"
              class="truncate text-ink-blue-link"
            >{{ orgData.website }}</a>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-x-4 gap-y-2">
          <div><span class="text-ink-gray-5">{{ __('Industria') }}: </span>{{ orgData.industry || '—' }}</div>
          <div><span class="text-ink-gray-5">{{ __('País') }}: </span>{{ orgData.territory || '—' }}</div>
          <div><span class="text-ink-gray-5">{{ __('Empleados') }}: </span>{{ orgData.no_of_employees || '—' }}</div>
          <div><span class="text-ink-gray-5">{{ __('Ingresos anuales') }}: </span>{{ orgData.annual_revenue || '—' }}</div>
        </div>
      </div>
      <div v-else class="p-6 text-center text-ink-gray-4">{{ __('Cargando...') }}</div>
    </template>
    <template #actions>
      <div class="flex justify-end">
        <Button variant="solid" :label="__('Abrir organización')" @click="goOrg" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import InteractionArea from '@/components/Activities/InteractionArea.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import TrackIcon from '~icons/lucide/list-checks'
import { Button, FeatherIcon, Dropdown, Dialog, Avatar, call, toast, dayjs } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'
import { statusesStore } from '@/stores/statuses'

const router = useRouter()
const { user: sessionUser } = sessionStore()
const { statusOptions, getDealStatus } = statusesStore()

// --- Acciones por fila: cambiar estado / agregar interacción ---
const showInteraction = ref(false)
const currentRef = ref(null)

function statusItems(rf) {
  const dt = rf.ref_doctype === 'CRM Deal' ? 'deal' : 'lead'
  let opts = statusOptions(dt, [], (name) => changeStatus(rf, name))
  if (dt === 'deal') {
    // Won/Lost se cierran desde la oportunidad (requieren OC / motivo)
    opts = opts.filter((o) => {
      const t = getDealStatus(o.value)?.type
      return t !== 'Won' && t !== 'Lost'
    })
  }
  return opts
}

async function changeStatus(rf, name) {
  try {
    await call('frappe.client.set_value', {
      doctype: rf.ref_doctype,
      name: rf.ref_docname,
      fieldname: 'status',
      value: name,
    })
    toast.success(__('Estado actualizado'))
    load()
  } catch (e) {
    toast.error(__('No se pudo cambiar el estado'))
  }
}

function openInteraction(rf) {
  currentRef.value = { doctype: rf.ref_doctype, docname: rf.ref_docname }
  showInteraction.value = true
}

// --- Ver organización en ventana emergente ---
const showOrg = ref(false)
const orgData = ref(null)
const orgName = ref('')
async function openOrg(name) {
  if (!name || name === '(Sin organización)') return
  orgName.value = name
  orgData.value = null
  showOrg.value = true
  try {
    const d = await call('frappe.client.get_value', {
      doctype: 'CRM Organization',
      filters: name,
      fieldname: [
        'name',
        'organization_name',
        'organization_logo',
        'website',
        'industry',
        'territory',
        'no_of_employees',
        'annual_revenue',
      ],
    })
    orgData.value = d || { organization_name: name }
  } catch (e) {
    orgData.value = { organization_name: name }
  }
}
function goOrg() {
  showOrg.value = false
  router.push({ name: 'Organization', params: { organizationId: orgName.value } })
}

// --- Edición inline de la interacción (clic en la celda) ---
const editing = ref(null)
const editText = ref('')
function startEdit(ln) {
  editing.value = ln.name
  editText.value = ln.interaccion || ''
}
async function saveEdit(ln) {
  if (editing.value !== ln.name) return
  const val = editText.value
  editing.value = null
  if (val === (ln.interaccion || '')) return
  try {
    await call('frappe.client.set_value', {
      doctype: 'CRM Interaction',
      name: ln.name,
      fieldname: 'message',
      value: val,
    })
    ln.interaccion = val
    toast.success(__('Interacción actualizada'))
  } catch (e) {
    toast.error(__('No se pudo actualizar'))
  }
}

const rows = ref([])
const loading = ref(false)
const search = ref('')
const kindFilter = ref('')
const diasFilter = ref(0)
const statusFilter = ref('')
const selectedUser = ref(sessionUser)
const hierUsers = ref([])

// Estados presentes en los datos (para el filtro por status)
const statusList = computed(() => {
  const set = new Set()
  for (const r of rows.value) if (r.status) set.add(r.status)
  return [...set].sort((a, b) => a.localeCompare(b))
})

// Opciones del selector: usuarios de la jerarquía de ventas (+ el usuario actual)
const userOptions = computed(() => {
  const list = [...hierUsers.value]
  if (!list.some((u) => u.user === sessionUser)) {
    list.unshift({ user: sessionUser, full_name: __('Yo') })
  }
  return list
})

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sept', 'oct', 'nov', 'dic']
function fmtDate(s) {
  if (!s) return ''
  const d = dayjs(s)
  if (!d.isValid()) return ''
  return d.date() + '-' + MESES[d.month()]
}

// La oportunidad no tiene número real (viene el código CRM-DEAL/CRM-LEAD)
function esCodigo(v) {
  return !v || /^CRM-(DEAL|LEAD)/i.test(v)
}

// Color determinístico por producto
const PROD_COLORS = [
  'bg-blue-100 text-blue-700',
  'bg-green-100 text-green-700',
  'bg-purple-100 text-purple-700',
  'bg-amber-100 text-amber-700',
  'bg-pink-100 text-pink-700',
  'bg-cyan-100 text-cyan-700',
  'bg-indigo-100 text-indigo-700',
  'bg-rose-100 text-rose-700',
  'bg-teal-100 text-teal-700',
  'bg-orange-100 text-orange-700',
]
function productoColor(name) {
  if (!name) return 'bg-surface-gray-2 text-ink-gray-6'
  const n = name.toLowerCase()
  // Colores fijos por familia de producto
  if (n.includes('solidworks')) return 'bg-red-100 text-red-700'
  if (n.includes('geovia')) return 'bg-[#e9dccb] text-[#7a4a1e]'
  if (n.includes('3dexperience')) return 'bg-blue-100 text-blue-700'
  // Resto: color determinístico
  let h = 0
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0
  return PROD_COLORS[h % PROD_COLORS.length]
}

async function load() {
  loading.value = true
  try {
    const r = await call('seguimiento_data', { user: selectedUser.value })
    rows.value = Array.isArray(r) ? r : r?.message || []
  } catch (e) {
    rows.value = []
  } finally {
    loading.value = false
  }
}

async function loadHierarchy() {
  try {
    const r = await call('sales_hierarchy_users')
    hierUsers.value = Array.isArray(r) ? r : r?.message || []
  } catch (e) {
    hierUsers.value = []
  }
}

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  return rows.value.filter((r) => {
    if (kindFilter.value && r.kind !== kindFilter.value) return false
    if (statusFilter.value && r.status !== statusFilter.value) return false
    // Ocultar leads sin interés
    if (r.kind === 'Lead' && r.status === 'X. Sin Interés') return false
    if (q && !(r.organization || '').toLowerCase().includes(q)) return false
    return true
  })
})

// Agrupa: organización -> referencias (oportunidad/lead) -> líneas de interacción
const groups = computed(() => {
  const byOrg = new Map()
  for (const r of filteredRows.value) {
    const org = r.organization || '(Sin organización)'
    if (!byOrg.has(org)) byOrg.set(org, new Map())
    const refs = byOrg.get(org)
    const key = r.ref_docname || r.oportunidad || org
    if (!refs.has(key)) {
      refs.set(key, {
        ref_doctype: r.ref_doctype,
        ref_docname: r.ref_docname,
        oportunidad: r.oportunidad,
        titulo: r.titulo,
        producto: r.producto,
        status: r.status,
        kind: r.kind,
        ref_creation: r.ref_creation,
        closed_date: r.closed_date,
        lines: [],
      })
    }
    refs.get(key).lines.push(r)
  }
  const out = []
  const hoy = dayjs()
  for (const [org, refs] of byOrg) {
    const refList = [...refs.values()]
    // Días sin interacción: desde la última interacción, o desde la creación
    // del lead/oportunidad si nunca hubo interacción.
    for (const rf of refList) {
      let last = null
      for (const ln of rf.lines) {
        if (!ln.fecha) continue
        const d = dayjs(ln.fecha)
        if (d.isValid() && (!last || d.isAfter(last))) last = d
      }
      if (last) {
        rf.dias = hoy.diff(last, 'day')
        rf.nunca = false
      } else if (rf.ref_creation) {
        rf.dias = hoy.diff(dayjs(rf.ref_creation), 'day')
        rf.nunca = true
      } else {
        rf.dias = null
        rf.nunca = true
      }
      // Días a cierre (Closed Date): closed_date - hoy
      rf.diasCierre =
        rf.closed_date && dayjs(rf.closed_date).isValid()
          ? dayjs(rf.closed_date).diff(hoy, 'day')
          : null
    }
    // Filtro "días sin interacción"
    const shown = refList.filter(
      (rf) => !diasFilter.value || (rf.dias != null && rf.dias >= diasFilter.value),
    )
    if (!shown.length) continue
    const orgRowspan = shown.reduce((n, rf) => n + rf.lines.length, 0)
    out.push({ organization: org, orgRowspan, refs: shown })
  }
  // Con orden activo: lista plana GLOBAL monótona (una fila por ref).
  // La agrupación por organización no permite un orden global, así que al
  // ordenar se desagrupa automáticamente.
  if (sortMode.value === 'inter' || sortMode.value === 'cierre') {
    const allRefs = []
    for (const g of out) {
      for (const rf of g.refs) allRefs.push({ organization: g.organization, rf })
    }
    if (sortMode.value === 'inter') {
      // Más días sin interacción primero (descendente); sin dato al final
      allRefs.sort((a, b) => (b.rf.dias ?? -BIG) - (a.rf.dias ?? -BIG))
    } else {
      // Cierre más lejano primero (descendente); sin fecha de cierre al final
      allRefs.sort((a, b) => (b.rf.diasCierre ?? -BIG) - (a.rf.diasCierre ?? -BIG))
    }
    return allRefs.map((x) => ({
      organization: x.organization,
      orgRowspan: x.rf.lines.length,
      refs: [x.rf],
    }))
  }
  // Sin orden: alfabético por organización
  out.sort((a, b) => a.organization.localeCompare(b.organization))
  // Desagrupado: cada oportunidad/lead es su propia fila (la organización se repite)
  if (!groupByOrg.value) {
    const flat = []
    for (const g of out) {
      for (const rf of g.refs) {
        flat.push({
          organization: g.organization,
          orgRowspan: rf.lines.length,
          refs: [rf],
        })
      }
    }
    return flat
  }
  return out
})

// Agrupar por organización (tick)
const groupByOrg = ref(true)

// --- Orden por días sin interacción / días a cierre ---
const sortMode = ref('') // '' | 'inter' | 'cierre'
function toggleSort(mode) {
  sortMode.value = sortMode.value === mode ? '' : mode
}
const BIG = 1e9
function sortRefs(list) {
  if (sortMode.value === 'inter') {
    list.sort((a, b) => (b.dias ?? -BIG) - (a.dias ?? -BIG))
  } else if (sortMode.value === 'cierre') {
    list.sort((a, b) => (a.diasCierre ?? BIG) - (b.diasCierre ?? BIG))
  }
}
function orgMetricInter(g) {
  return g.refs.reduce((m, rf) => Math.max(m, rf.dias ?? -BIG), -BIG)
}
function orgMetricCierre(g) {
  return g.refs.reduce((m, rf) => Math.min(m, rf.diasCierre ?? BIG), BIG)
}

function openRef(rf) {
  if (!rf.ref_docname) return
  if (rf.ref_doctype === 'CRM Deal') router.push({ name: 'Deal', params: { dealId: rf.ref_docname } })
  else if (rf.ref_doctype === 'CRM Lead') router.push({ name: 'Lead', params: { leadId: rf.ref_docname } })
}

onMounted(load)
onMounted(loadHierarchy)
</script>
