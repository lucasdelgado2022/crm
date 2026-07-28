<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <PackageIcon class="h-5 w-5" />
        {{ __('Oferta Comercial') }}
      </div>
    </template>
    <template #right-header>
      <div class="relative">
        <FeatherIcon
          name="search"
          class="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4"
        />
        <input
          v-model="search"
          type="text"
          :placeholder="__('Buscar producto...')"
          class="h-8 w-56 rounded-lg border border-outline-gray-2 bg-surface-base pl-8 pr-2 text-base text-ink-gray-8 focus:border-outline-gray-3 focus:outline-none focus:ring-0"
        />
      </div>
    </template>
  </LayoutHeader>

  <div class="flex h-full overflow-hidden">
    <!-- Árbol de categorías -->
    <div class="w-64 shrink-0 overflow-y-auto border-r p-2">
      <button
        class="mb-1 flex w-full items-center justify-between rounded px-2 py-1.5 text-sm font-medium"
        :class="
          !selCat
            ? 'bg-surface-gray-3 text-ink-gray-9'
            : 'text-ink-gray-7 hover:bg-surface-gray-2'
        "
        @click="selectNode(null, null)"
      >
        <span>{{ __('Todo el catálogo') }}</span>
        <span class="text-ink-gray-5">{{ products.length }}</span>
      </button>
      <div v-for="cat in taxonomy" :key="cat.cat" class="mb-0.5">
        <button
          class="flex w-full items-center justify-between rounded px-2 py-1.5 text-left text-sm font-medium"
          :class="
            selCat === cat.cat && !selGroup
              ? 'bg-surface-gray-3 text-ink-gray-9'
              : 'text-ink-gray-8 hover:bg-surface-gray-2'
          "
          @click="toggleCat(cat)"
        >
          <span class="flex items-center gap-1.5">
            <FeatherIcon
              v-if="cat.groups.length"
              :name="openCats[cat.cat] ? 'chevron-down' : 'chevron-right'"
              class="h-3.5 w-3.5 shrink-0 text-ink-gray-5"
            />
            <span class="truncate">{{ cat.cat }}</span>
          </span>
          <span class="text-ink-gray-5">{{ countByCat(cat.cat) }}</span>
        </button>
        <div v-if="openCats[cat.cat] && cat.groups.length" class="ml-3 mt-0.5">
          <button
            v-for="g in cat.groups"
            :key="g.name"
            class="flex w-full items-center justify-between rounded px-2 py-1 text-left text-sm"
            :class="
              selCat === cat.cat && selGroup === g.name
                ? 'bg-surface-gray-3 text-ink-gray-9'
                : 'text-ink-gray-6 hover:bg-surface-gray-2'
            "
            @click="selectNode(cat.cat, g.name)"
          >
            <span class="truncate">{{ g.name || __('General') }}</span>
            <span class="text-ink-gray-5">{{ countByGroup(cat.cat, g.name) }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Panel principal -->
    <div class="flex-1 overflow-y-auto p-4 sm:p-5">
      <!-- Ofertas de la subcategoría seleccionada (del árbol, informativo) -->
      <div v-if="currentGroupItems.length" class="mb-5">
        <div class="mb-2 text-sm font-semibold text-ink-gray-7">
          {{ __('Ofertas en') }} {{ selGroup }}
        </div>
        <div class="flex flex-wrap gap-1.5">
          <span
            v-for="it in currentGroupItems"
            :key="it"
            class="rounded-full border border-outline-gray-2 bg-surface-gray-1 px-2.5 py-1 text-xs text-ink-gray-7"
          >
            {{ it }}
          </span>
        </div>
      </div>

      <div
        v-if="loading"
        class="flex h-40 items-center justify-center text-ink-gray-4"
      >
        {{ __('Cargando...') }}
      </div>
      <div
        v-else-if="!filteredProducts.length"
        class="flex h-40 flex-col items-center justify-center gap-2 text-ink-gray-4"
      >
        <PackageIcon class="h-8 w-8" />
        <span>{{ __('No hay productos en esta selección') }}</span>
      </div>

      <div
        v-else
        class="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3"
      >
        <div
          v-for="p in filteredProducts"
          :key="p.name"
          class="flex flex-col rounded-lg border border-outline-gray-2 bg-surface-base p-3 hover:border-outline-gray-3"
        >
          <div class="flex items-start gap-3">
            <div
              class="flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded border bg-surface-gray-1"
            >
              <img
                v-if="p.image"
                :src="p.image"
                :alt="p.product_name || p.name"
                class="h-full w-full object-cover"
              />
              <IndicatorIcon v-else :class="colorClass(p.color)" class="h-4 w-4" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5">
                <IndicatorIcon
                  v-if="p.image"
                  :class="colorClass(p.color)"
                  class="h-3 w-3 shrink-0"
                />
                <span class="truncate font-medium text-ink-gray-9">{{
                  p.product_name || p.name
                }}</span>
              </div>
              <div class="truncate text-xs text-ink-gray-5">
                {{ p.product_code }}
              </div>
              <div
                v-if="p.custom_subcategoria"
                class="mt-0.5 inline-block rounded bg-surface-gray-2 px-1.5 py-0.5 text-xs text-ink-gray-6"
              >
                {{ p.custom_subcategoria }}
              </div>
            </div>
            <span
              v-if="p.disabled"
              class="rounded bg-surface-gray-2 px-1.5 py-0.5 text-xs text-ink-gray-5"
              >{{ __('Discontinuado') }}</span
            >
          </div>

          <div
            v-if="stripHtml(p.description)"
            class="mt-2 line-clamp-2 text-sm text-ink-gray-6"
          >
            {{ stripHtml(p.description) }}
          </div>

          <!-- Info de ventas -->
          <div
            class="mt-3 grid grid-cols-3 gap-2 rounded-md bg-surface-gray-1 p-2 text-center"
          >
            <div>
              <div class="text-sm font-semibold text-ink-gray-9">
                {{ sales(p.name).count }}
              </div>
              <div class="text-xs text-ink-gray-5">{{ __('Oport.') }}</div>
            </div>
            <div>
              <div class="text-sm font-semibold text-green-700">
                {{ sales(p.name).won }}
              </div>
              <div class="text-xs text-ink-gray-5">{{ __('Ganadas') }}</div>
            </div>
            <div>
              <div class="truncate text-sm font-semibold text-ink-gray-9">
                {{ money(sales(p.name).revenue) }}
              </div>
              <div class="text-xs text-ink-gray-5">{{ __('Revenue') }}</div>
            </div>
          </div>

          <div class="mt-2 flex items-center justify-between">
            <span v-if="p.standard_rate" class="text-sm text-ink-gray-7">
              {{ __('Precio') }}: {{ money(p.standard_rate) }}
            </span>
            <span v-else />
            <span
              v-if="p.erpnext_item_code"
              class="inline-flex items-center gap-1 rounded bg-blue-50 px-1.5 py-0.5 text-xs font-medium text-blue-700"
              :title="__('Vinculado al ERP')"
            >
              <FeatherIcon name="link" class="h-3 w-3" />
              ERP: {{ p.erpnext_item_code }}
            </span>
            <span
              v-else
              class="text-xs text-ink-gray-4"
              :title="__('Sin vincular al ERP')"
              >{{ __('Sin ERP') }}</span
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import PackageIcon from '~icons/lucide/package'
import { FeatherIcon, createResource } from 'frappe-ui'
import { ref, computed, reactive } from 'vue'

const taxonomy = [
  {
    cat: 'Licencias de Software',
    groups: [
      {
        name: 'Diseno',
        items: [
          'Diseño Mecánico (SOLIDWORKS)',
          'Diseño Mecánico Avanzado (CATIA)',
          'Diseño 2D (DraftSight)',
          'Diseño Eléctrico',
          'Diseño Electrónico (PCB)',
          'Diseño de Tuberías (Piping)',
          'Ingeniería Inversa',
        ],
      },
      {
        name: 'Simulacion',
        items: [
          'Estructural (SOLIDWORKS Simulation / Abaqus / SIMULIA)',
          'Electromagnetismo',
          'Fluidos (CFD)',
          'Dinámica Multicuerpo',
          'Durabilidad y Fatiga (Fe-Safe)',
          'Simulación de Inyección de Plásticos',
          'Ingeniería de Materiales Compuestos',
          'Simulación Térmica',
          'Acoplados Multiphysics',
          'Optimización (Isight / Process Composer)',
          'Gemelos Digitales (Digital Twin)',
        ],
      },
      {
        name: 'Gestion',
        items: [
          'Gestión de Documentación',
          'Gestión de Productos',
          'Colaboración MultiCAD',
          'Gestión de Calidad (No Conformidades, APQP, PPAP, FMEA, Safety, Planes de Control, Inspección, Auditorías, Riesgos, FTA)',
          'Gestión de Proyectos',
          'Gestión de Activos',
          'Dashboard de Performance',
          'Gestión de Procesos BPM',
        ],
      },
      {
        name: 'Manufactura',
        items: [
          'Planificación de Manufactura',
          'Manufactura Digital',
          'Instrucciones de Trabajo Digitales',
          'Simulación de Producción',
          'Gestión de Operaciones (MES)',
        ],
      },
      {
        name: 'Mineria',
        items: ['Planificación Minera', 'Diseño de Minas'],
      },
      {
        name: 'Ingenieria de Sistemas',
        items: [
          'MBSE',
          'Arquitectura de Sistemas',
          'Ingeniería de Requerimientos',
          'Validación y Verificación',
          'Trazabilidad',
        ],
      },
    ],
  },
  { cat: 'Servicios de Ingenieria', groups: [] },
  {
    cat: 'Capacitacion y Entrenamiento',
    groups: [
      {
        name: 'Capacitacion',
        items: [
          'Con Instructor In Company',
          'Workshops',
          'Certificación de Usuarios',
          'Plataforma de Cursos en Español',
          'Plataforma de Cursos Oficial',
        ],
      },
    ],
  },
  {
    cat: 'Servicios de Consultoria e Integracion',
    groups: [
      {
        name: 'Consultoria',
        items: [
          'Relevamiento y Diagnóstico de Procesos',
          'Definición de Arquitectura',
          'Roadmap de Transformación Digital',
        ],
      },
      {
        name: 'Implementacion',
        items: [
          'Implementación de Plataformas',
          'Proyectos Piloto',
          'Migración de Datos',
          'Desarrollo de Automatizaciones',
          'Configuración',
        ],
      },
      {
        name: 'Desarrollo de Software',
        items: [
          'Desarrollo de Aplicaciones',
          'APIs e Integraciones',
          'Desarrollo de Dashboards',
        ],
      },
      { name: 'Soporte', items: ['Soporte Extendido'] },
    ],
  },
]

const search = ref('')
const selCat = ref(null)
const selGroup = ref(null)
const openCats = reactive({})

function toggleCat(cat) {
  if (cat.groups.length) {
    openCats[cat.cat] = !openCats[cat.cat]
  }
  selectNode(cat.cat, null)
}
function selectNode(cat, group) {
  selCat.value = cat
  selGroup.value = group
}

const productsRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Product',
    fields: [
      'name',
      'product_name',
      'product_code',
      'description',
      'standard_rate',
      'image',
      'color',
      'disabled',
      'custom_categoria',
      'custom_subcategoria',
      'erpnext_item_code',
    ],
    order_by: 'product_name asc',
    limit_page_length: 0,
  },
  auto: true,
})
const products = computed(() => productsRes.data || [])
const loading = computed(() => productsRes.loading)

const salesAllRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Deal',
    fields: [
      'custom_producto',
      'count(name) as count',
      'sum(annual_revenue) as revenue',
    ],
    group_by: 'custom_producto',
    limit_page_length: 0,
  },
  auto: true,
})
const salesWonRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Deal',
    filters: { status: 'Won' },
    fields: ['custom_producto', 'count(name) as count'],
    group_by: 'custom_producto',
    limit_page_length: 0,
  },
  auto: true,
})

const salesMap = computed(() => {
  const m = {}
  for (const r of salesAllRes.data || []) {
    if (!r.custom_producto) continue
    m[r.custom_producto] = {
      count: r.count || 0,
      revenue: r.revenue || 0,
      won: 0,
    }
  }
  for (const r of salesWonRes.data || []) {
    if (!r.custom_producto) continue
    if (!m[r.custom_producto])
      m[r.custom_producto] = { count: 0, revenue: 0, won: 0 }
    m[r.custom_producto].won = r.count || 0
  }
  return m
})
function sales(name) {
  return salesMap.value[name] || { count: 0, revenue: 0, won: 0 }
}

const filteredProducts = computed(() => {
  let list = products.value
  const q = search.value.trim().toLowerCase()
  if (q) {
    list = list.filter(
      (p) =>
        (p.product_name || p.name || '').toLowerCase().includes(q) ||
        (p.product_code || '').toLowerCase().includes(q),
    )
    return list
  }
  if (selCat.value)
    list = list.filter((p) => p.custom_categoria === selCat.value)
  if (selGroup.value)
    list = list.filter((p) => p.custom_subcategoria === selGroup.value)
  return list
})

const currentGroupItems = computed(() => {
  if (!selCat.value || !selGroup.value) return []
  const cat = taxonomy.find((c) => c.cat === selCat.value)
  const g = cat?.groups.find((x) => x.name === selGroup.value)
  return g?.items || []
})

function countByCat(cat) {
  return products.value.filter((p) => p.custom_categoria === cat).length
}
function countByGroup(cat, group) {
  return products.value.filter(
    (p) => p.custom_categoria === cat && p.custom_subcategoria === group,
  ).length
}

const COLOR_MAP = {
  black: 'text-ink-gray-9',
  gray: 'text-gray-500',
  blue: 'text-blue-500',
  green: 'text-green-500',
  red: 'text-red-500',
  pink: 'text-pink-500',
  orange: 'text-orange-500',
  amber: 'text-amber-500',
  yellow: 'text-yellow-500',
  cyan: 'text-cyan-500',
  teal: 'text-teal-500',
  violet: 'text-violet-500',
  purple: 'text-purple-500',
}
function colorClass(c) {
  return COLOR_MAP[c] || 'text-gray-400'
}

function stripHtml(html) {
  if (!html) return ''
  const tmp = document.createElement('div')
  tmp.innerHTML = html
  return (tmp.textContent || tmp.innerText || '').trim()
}

function money(n) {
  const v = Number(n) || 0
  if (!v) return '—'
  if (Math.abs(v) >= 1000)
    return '$' + Math.round(v).toLocaleString('es-AR')
  return '$' + v.toLocaleString('es-AR')
}
</script>
