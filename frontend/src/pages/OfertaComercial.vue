<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <PackageIcon class="h-5 w-5" />
        {{ __('Oferta Comercial') }}
      </div>
    </template>
    <template #right-header>
      <div class="flex items-center gap-2">
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
        <Button variant="solid" @click="openNew">
          <template #prefix>
            <FeatherIcon name="plus" class="h-4" />
          </template>
          {{ __('Nuevo') }}
        </Button>
      </div>
    </template>
  </LayoutHeader>

  <div class="flex h-full overflow-hidden">
    <!-- Menú lateral: categorías → grupos → subcategorías -->
    <div class="w-72 shrink-0 overflow-y-auto border-r p-2 text-sm">
      <button
        class="mb-1 flex w-full items-center justify-between rounded px-2 py-1.5 font-medium"
        :class="navClass(isAll)"
        @click="selectAll()"
      >
        <span>{{ __('Todo el catálogo') }}</span>
        <span class="text-ink-gray-5">{{ products.length }}</span>
      </button>

      <div v-for="cat in taxonomy" :key="cat.cat" class="mb-0.5">
        <button
          class="flex w-full items-center justify-between rounded px-2 py-1.5 text-left font-medium"
          :class="navClass(sel.level === 'cat' && sel.cat === cat.cat)"
          @click="selectCat(cat)"
        >
          <span class="flex items-center gap-1.5 truncate">
            <FeatherIcon
              v-if="cat.groups.length"
              :name="openCats[cat.cat] ? 'chevron-down' : 'chevron-right'"
              class="h-3.5 w-3.5 shrink-0 text-ink-gray-5"
              @click.stop="openCats[cat.cat] = !openCats[cat.cat]"
            />
            <span class="truncate">{{ cat.cat }}</span>
          </span>
          <span class="text-ink-gray-5">{{ countCat(cat.cat) }}</span>
        </button>

        <div v-if="openCats[cat.cat]" class="ml-3 mt-0.5">
          <div v-for="g in cat.groups" :key="g.name" class="mb-0.5">
            <button
              class="flex w-full items-center justify-between rounded px-2 py-1 text-left"
              :class="navClass(sel.level === 'group' && sel.key === g.name)"
              @click="selectGroup(cat, g)"
            >
              <span class="flex items-center gap-1.5 truncate">
                <FeatherIcon
                  v-if="g.items.length"
                  :name="openGroups[g.name] ? 'chevron-down' : 'chevron-right'"
                  class="h-3 w-3 shrink-0 text-ink-gray-4"
                  @click.stop="openGroups[g.name] = !openGroups[g.name]"
                />
                <span class="truncate">{{ g.name }}</span>
              </span>
              <span class="text-ink-gray-5">{{ countKey(g.name) }}</span>
            </button>

            <div v-if="openGroups[g.name]" class="ml-4 mt-0.5">
              <button
                v-for="leaf in g.items"
                :key="leaf"
                class="flex w-full items-center justify-between gap-2 rounded px-2 py-1 text-left text-xs"
                :class="navClass(sel.level === 'leaf' && sel.key === leaf)"
                @click="selectLeaf(cat, g, leaf)"
              >
                <span class="truncate">{{ leaf }}</span>
                <span class="shrink-0 text-ink-gray-5">{{ countKey(leaf) }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Panel principal -->
    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <!-- Barra: título del nodo + asignar -->
      <div
        class="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b px-4 py-2.5"
      >
        <div class="min-w-0">
          <div class="truncate text-base font-semibold text-ink-gray-8">
            {{ sel.title }}
          </div>
          <div class="text-xs text-ink-gray-5">
            {{ filteredProducts.length }} {{ __('productos') }}
          </div>
        </div>
        <div v-if="assignable" class="flex items-center gap-2">
          <Link
            class="w-56"
            :value="pickValue"
            doctype="CRM Product"
            :placeholder="__('Asignar producto...')"
            @change="(v) => onPick(v)"
          />
        </div>
      </div>

      <div class="flex-1 overflow-y-auto">
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
          <span>{{ __('Sin productos en esta selección') }}</span>
          <span v-if="assignable" class="text-xs">{{
            __('Usá "Asignar producto" para agregar')
          }}</span>
        </div>

        <table v-else class="w-full text-sm">
          <thead
            class="sticky top-0 z-10 border-b bg-surface-base text-xs text-ink-gray-5"
          >
            <tr>
              <th class="px-4 py-2 text-left font-medium">{{ __('Producto') }}</th>
              <th class="px-3 py-2 text-left font-medium">
                {{ __('Subcategorías') }}
              </th>
              <th class="px-3 py-2 text-right font-medium">{{ __('Precio') }}</th>
              <th class="px-3 py-2 text-right font-medium">{{ __('Oport.') }}</th>
              <th class="px-3 py-2 text-right font-medium">{{ __('Ganadas') }}</th>
              <th class="px-3 py-2 text-right font-medium">{{ __('Revenue') }}</th>
              <th class="px-3 py-2 text-left font-medium">{{ __('ERP') }}</th>
              <th v-if="assignable" class="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in filteredProducts"
              :key="p.name"
              class="border-b hover:bg-surface-gray-1"
            >
              <td class="px-4 py-2">
                <div class="flex items-center gap-2">
                  <IndicatorIcon
                    :class="colorClass(p.color)"
                    class="h-3 w-3 shrink-0"
                  />
                  <div class="min-w-0">
                    <div class="truncate font-medium text-ink-gray-9">
                      {{ p.product_name || p.name }}
                      <span
                        v-if="p.disabled"
                        class="ml-1 rounded bg-surface-gray-2 px-1 py-0.5 text-xs text-ink-gray-5"
                        >{{ __('Discont.') }}</span
                      >
                    </div>
                    <div class="truncate text-xs text-ink-gray-5">
                      {{ p.product_code }}
                    </div>
                  </div>
                  <button
                    class="ml-auto flex shrink-0 items-center gap-0.5 rounded p-1 text-ink-gray-4 hover:bg-surface-gray-2 hover:text-ink-gray-7"
                    :title="__('Adjuntos')"
                    @click="openFiles(p)"
                  >
                    <FeatherIcon name="paperclip" class="h-3.5 w-3.5" />
                    <span v-if="attachCount[p.name]" class="text-xs">{{
                      attachCount[p.name]
                    }}</span>
                  </button>
                </div>
              </td>
              <td class="px-3 py-2">
                <div class="flex max-w-xs flex-wrap gap-1">
                  <span
                    v-for="sc in productSubcats[p.name] || []"
                    :key="sc"
                    class="rounded bg-surface-gray-2 px-1.5 py-0.5 text-xs text-ink-gray-6"
                  >
                    {{ sc }}
                  </span>
                </div>
              </td>
              <td class="whitespace-nowrap px-3 py-2 text-right text-ink-gray-7">
                {{ p.standard_rate ? money(p.standard_rate) : '—' }}
              </td>
              <td class="px-3 py-2 text-right font-medium text-ink-gray-9">
                {{ sales(p.name).count }}
              </td>
              <td class="px-3 py-2 text-right font-medium text-green-700">
                {{ sales(p.name).won }}
              </td>
              <td
                class="whitespace-nowrap px-3 py-2 text-right font-medium text-ink-gray-9"
              >
                {{ money(sales(p.name).revenue) }}
              </td>
              <td class="px-3 py-2">
                <span
                  v-if="p.erpnext_item_code"
                  class="inline-flex items-center gap-1 rounded bg-blue-50 px-1.5 py-0.5 text-xs font-medium text-blue-700"
                  :title="__('Vinculado al ERP')"
                >
                  <FeatherIcon name="link" class="h-3 w-3" />
                  {{ p.erpnext_item_code }}
                </span>
                <span v-else class="text-xs text-ink-gray-4">{{
                  __('Sin ERP')
                }}</span>
              </td>
              <td v-if="assignable" class="px-3 py-2 text-right">
                <button
                  class="rounded p-1 text-ink-gray-5 hover:bg-surface-gray-3 hover:text-ink-red-6"
                  :title="__('Quitar de esta subcategoría')"
                  @click="unassign(p.name, sel.key)"
                >
                  <FeatherIcon name="x" class="h-3.5 w-3.5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Dialog: Nuevo producto -->
  <Dialog v-model="showNew" :options="{ title: __('Nuevo producto'), size: 'lg' }">
    <template #body-content>
      <div class="flex flex-col gap-3">
        <input
          v-model="nf.product_name"
          :placeholder="__('Nombre del producto *')"
          class="h-9 w-full rounded border border-outline-gray-2 bg-surface-base px-3 text-sm text-ink-gray-8 focus:outline-none"
        />
        <div class="grid grid-cols-2 gap-3">
          <input
            v-model="nf.product_code"
            :placeholder="__('Código')"
            class="h-9 rounded border border-outline-gray-2 bg-surface-base px-3 text-sm text-ink-gray-8 focus:outline-none"
          />
          <input
            v-model.number="nf.standard_rate"
            type="number"
            :placeholder="__('Precio')"
            class="h-9 rounded border border-outline-gray-2 bg-surface-base px-3 text-sm text-ink-gray-8 focus:outline-none"
          />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <select
            v-model="nf.custom_categoria"
            class="h-9 rounded border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
          >
            <option value="">{{ __('Categoría...') }}</option>
            <option v-for="c in taxonomy" :key="c.cat" :value="c.cat">
              {{ c.cat }}
            </option>
          </select>
          <select
            v-model="nf.color"
            class="h-9 rounded border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
          >
            <option value="">{{ __('Color...') }}</option>
            <option v-for="c in colorKeys" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">
            {{ __('Producto ERP (opcional)') }}
          </div>
          <Link
            class="form-control"
            doctype="Item"
            :value="nf.erpnext_item_code"
            :placeholder="__('Buscar producto del ERP...')"
            @change="(v) => (nf.erpnext_item_code = v)"
          />
        </div>
        <textarea
          v-model="nf.description"
          rows="3"
          :placeholder="__('Descripción')"
          class="w-full rounded border border-outline-gray-2 bg-surface-base p-3 text-sm text-ink-gray-8 focus:outline-none"
        />
        <div class="flex justify-end gap-2 pt-1">
          <Button @click="showNew = false">{{ __('Cancelar') }}</Button>
          <Button
            variant="solid"
            :loading="savingNew"
            :disabled="!nf.product_name.trim()"
            @click="saveNew"
          >
            {{ __('Crear') }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>

  <!-- Dialog: Adjuntos -->
  <Dialog
    v-model="showFiles"
    :options="{
      title: __('Adjuntos') + (filesProduct ? ' — ' + filesProduct : ''),
      size: 'lg',
    }"
  >
    <template #body-content>
      <input
        ref="fileInput"
        type="file"
        multiple
        class="hidden"
        @change="onFilePicked"
      />
      <Button variant="outline" :loading="uploading" @click="fileInput?.click()">
        <template #prefix>
          <FeatherIcon name="upload" class="h-4" />
        </template>
        {{ __('Subir archivo') }}
      </Button>
      <div v-if="filesList.length" class="mt-3 flex flex-col gap-2">
        <div
          v-for="f in filesList"
          :key="f.name"
          class="flex items-center justify-between gap-2 rounded border p-2"
        >
          <a
            :href="f.file_url"
            target="_blank"
            class="flex min-w-0 items-center gap-2 truncate text-sm text-blue-600 hover:underline"
          >
            <FeatherIcon name="file" class="h-4 w-4 shrink-0 text-ink-gray-5" />
            <span class="truncate">{{ f.file_name }}</span>
          </a>
          <button
            class="shrink-0 rounded p-1 text-ink-gray-5 hover:bg-surface-gray-2 hover:text-ink-red-6"
            :title="__('Eliminar')"
            @click="deleteFile(f.name)"
          >
            <FeatherIcon name="trash-2" class="h-4 w-4" />
          </button>
        </div>
      </div>
      <div
        v-else
        class="mt-3 flex h-20 items-center justify-center text-sm text-ink-gray-4"
      >
        {{ __('Sin adjuntos') }}
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import Link from '@/components/Controls/Link.vue'
import PackageIcon from '~icons/lucide/package'
import { FeatherIcon, createResource, call, toast, Dialog, Button } from 'frappe-ui'
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
          'Gestión de Calidad',
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
      { name: 'Mineria', items: ['Planificación Minera', 'Diseño de Minas'] },
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
const pickValue = ref('')
function onPick(v) {
  if (v && sel.key) assign(v, sel.key)
  pickValue.value = ''
}
const openCats = reactive({})
const openGroups = reactive({})
const sel = reactive({
  level: 'all',
  cat: null,
  key: null,
  title: 'Todo el catálogo',
})

const isAll = computed(() => sel.level === 'all')
function navClass(active) {
  return active
    ? 'bg-surface-gray-3 text-ink-gray-9'
    : 'text-ink-gray-7 hover:bg-surface-gray-2'
}
function selectAll() {
  sel.level = 'all'
  sel.cat = null
  sel.key = null
  sel.title = 'Todo el catálogo'
}
function selectCat(cat) {
  openCats[cat.cat] = true
  sel.level = 'cat'
  sel.cat = cat.cat
  sel.key = null
  sel.title = cat.cat
}
function selectGroup(cat, g) {
  openGroups[g.name] = true
  sel.level = 'group'
  sel.cat = cat.cat
  sel.key = g.name
  sel.title = cat.cat + ' › ' + g.name
}
function selectLeaf(cat, g, leaf) {
  sel.level = 'leaf'
  sel.cat = cat.cat
  sel.key = leaf
  sel.title = g.name + ' › ' + leaf
}

const assignable = computed(
  () => (sel.level === 'group' || sel.level === 'leaf') && !search.value.trim(),
)

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
      'erpnext_item_code',
    ],
    order_by: 'product_name asc',
    limit_page_length: 0,
  },
  auto: true,
})
const products = computed(() => productsRes.data || [])
const loading = computed(() => productsRes.loading)

const subcatRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Product Subcategoria',
    parent: 'CRM Product',
    filters: { parenttype: 'CRM Product' },
    fields: ['parent', 'subcategoria'],
    limit_page_length: 0,
  },
  auto: true,
})
const productSubcats = computed(() => {
  const m = {}
  for (const r of subcatRes.data || []) {
    if (!r.parent || !r.subcategoria) continue
    ;(m[r.parent] ||= []).push(r.subcategoria)
  }
  return m
})
const productsByKey = computed(() => {
  const m = {}
  for (const r of subcatRes.data || []) {
    if (!r.parent || !r.subcategoria) continue
    ;(m[r.subcategoria] ||= new Set()).add(r.parent)
  }
  return m
})

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
    m[r.custom_producto] = { count: r.count || 0, revenue: r.revenue || 0, won: 0 }
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
  const q = search.value.trim().toLowerCase()
  if (q) {
    return products.value.filter(
      (p) =>
        (p.product_name || p.name || '').toLowerCase().includes(q) ||
        (p.product_code || '').toLowerCase().includes(q),
    )
  }
  if (sel.level === 'all') return products.value
  if (sel.level === 'cat')
    return products.value.filter((p) => p.custom_categoria === sel.cat)
  // group o leaf → por clave en la tabla N:N
  const set = productsByKey.value[sel.key]
  if (!set) return []
  return products.value.filter((p) => set.has(p.name))
})

function countCat(cat) {
  return products.value.filter((p) => p.custom_categoria === cat).length
}
function countKey(key) {
  const set = productsByKey.value[key]
  return set ? set.size : 0
}

async function assign(product, key) {
  if (!product || !key) return
  const current = productSubcats.value[product] || []
  if (current.includes(key)) {
    toast.info(__('Ya estaba asignado'))
    return
  }
  try {
    const doc = await call('frappe.client.get', {
      doctype: 'CRM Product',
      name: product,
    })
    doc.custom_subcategorias = doc.custom_subcategorias || []
    doc.custom_subcategorias.push({ subcategoria: key })
    await call('frappe.client.save', { doc })
    toast.success(__('Producto asignado'))
    subcatRes.reload()
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo asignar'))
  }
}
async function unassign(product, key) {
  try {
    const doc = await call('frappe.client.get', {
      doctype: 'CRM Product',
      name: product,
    })
    doc.custom_subcategorias = (doc.custom_subcategorias || []).filter(
      (r) => r.subcategoria !== key,
    )
    await call('frappe.client.save', { doc })
    toast.success(__('Producto quitado'))
    subcatRes.reload()
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo quitar'))
  }
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
function money(n) {
  const v = Number(n) || 0
  if (!v) return '—'
  return '$' + Math.round(v).toLocaleString('es-AR')
}

const colorKeys = Object.keys(COLOR_MAP)

// --- Nuevo producto ---
const showNew = ref(false)
const savingNew = ref(false)
const nf = reactive({
  product_name: '',
  product_code: '',
  standard_rate: null,
  custom_categoria: '',
  color: '',
  erpnext_item_code: '',
  description: '',
})
function openNew() {
  Object.assign(nf, {
    product_name: '',
    product_code: '',
    standard_rate: null,
    custom_categoria: sel.level === 'cat' ? sel.cat : '',
    color: '',
    erpnext_item_code: '',
    description: '',
  })
  showNew.value = true
}
async function saveNew() {
  if (!nf.product_name.trim()) return
  savingNew.value = true
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'CRM Product',
        product_name: nf.product_name,
        product_code: nf.product_code || nf.product_name,
        standard_rate: nf.standard_rate || 0,
        custom_categoria: nf.custom_categoria || null,
        color: nf.color || null,
        erpnext_item_code: nf.erpnext_item_code || null,
        description: nf.description || null,
      },
    })
    toast.success(__('Producto creado'))
    showNew.value = false
    productsRes.reload()
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo crear el producto'))
  } finally {
    savingNew.value = false
  }
}

// --- Adjuntos por producto ---
const showFiles = ref(false)
const filesProduct = ref('')
const filesList = ref([])
const uploading = ref(false)
const fileInput = ref(null)
async function openFiles(p) {
  filesProduct.value = p.name
  showFiles.value = true
  await loadFiles()
}
async function loadFiles() {
  if (!filesProduct.value) return
  try {
    filesList.value = await call('frappe.client.get_list', {
      doctype: 'File',
      filters: {
        attached_to_doctype: 'CRM Product',
        attached_to_name: filesProduct.value,
      },
      fields: ['name', 'file_name', 'file_url', 'file_size'],
      order_by: 'creation desc',
      limit_page_length: 0,
    })
  } catch (e) {
    filesList.value = []
  }
}
async function onFilePicked(e) {
  const files = Array.from(e.target.files || [])
  if (!files.length) return
  uploading.value = true
  let ok = 0
  for (const file of files) {
    const fd = new FormData()
    fd.append('file', file, file.name)
    fd.append('is_private', '0')
    fd.append('folder', 'Home/Attachments')
    fd.append('doctype', 'CRM Product')
    fd.append('docname', filesProduct.value)
    try {
      const res = await fetch('/api/method/upload_file', {
        method: 'POST',
        headers: { 'X-Frappe-CSRF-Token': window.csrf_token },
        body: fd,
      })
      if (res.ok) ok++
    } catch (err) {
      // ignore
    }
  }
  e.target.value = ''
  uploading.value = false
  if (ok) toast.success(__('Archivo(s) subido(s)'))
  await loadFiles()
  attachCountRes.reload()
}
async function deleteFile(name) {
  try {
    await call('frappe.client.delete', { doctype: 'File', name })
    await loadFiles()
    attachCountRes.reload()
  } catch (e) {
    toast.error(__('No se pudo eliminar'))
  }
}

// contador de adjuntos por producto
const attachCountRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'File',
    filters: { attached_to_doctype: 'CRM Product' },
    fields: ['attached_to_name', 'count(name) as c'],
    group_by: 'attached_to_name',
    limit_page_length: 0,
  },
  auto: true,
})
const attachCount = computed(() => {
  const m = {}
  for (const r of attachCountRes.data || [])
    if (r.attached_to_name) m[r.attached_to_name] = r.c
  return m
})
</script>
