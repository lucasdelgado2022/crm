<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <BulbIcon class="h-5 w-5" />
        {{ __('Sugerencias') }}
      </div>
    </template>
    <template #right-header>
      <div v-if="isAdminUser" class="flex items-center gap-2">
        <select v-model="fEstado" class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none">
          <option value="">{{ __('Todos los estados') }}</option>
          <option v-for="e in ESTADOS" :key="e" :value="e">{{ e }}</option>
        </select>
        <Button variant="ghost" icon="refresh-cw" :loading="loading" :tooltip="__('Actualizar')" @click="load" />
      </div>
    </template>
  </LayoutHeader>

  <div v-if="!isAdminUser" class="flex h-full items-center justify-center p-10 text-center">
    <div>
      <LockIcon class="mx-auto h-8 w-8 text-ink-gray-4" />
      <div class="mt-3 text-base font-medium text-ink-gray-7">{{ __('Acceso restringido') }}</div>
      <div class="mt-1 text-sm text-ink-gray-5">{{ __('Solo administradores pueden ver todas las sugerencias.') }}</div>
    </div>
  </div>

  <div v-else class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <div class="mb-3 text-sm text-ink-gray-5">{{ filtered.length }} {{ __('sugerencias') }}</div>
    <div class="overflow-x-auto rounded-lg border">
      <table class="w-full min-w-[760px] text-sm">
        <thead>
          <tr class="border-b text-xs uppercase tracking-wide text-ink-gray-5">
            <th class="px-3 py-2 text-left">{{ __('Fecha') }}</th>
            <th class="px-3 py-2 text-left">{{ __('Autor') }}</th>
            <th class="px-3 py-2 text-left">{{ __('Página') }}</th>
            <th class="px-3 py-2 text-left">{{ __('Sugerencia') }}</th>
            <th class="px-3 py-2 text-left">{{ __('Estado') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filtered" :key="s.name" class="border-b align-top hover:bg-surface-gray-1">
            <td class="whitespace-nowrap px-3 py-2 text-xs text-ink-gray-6">{{ fmtDate(s.creation) }}</td>
            <td class="whitespace-nowrap px-3 py-2 text-ink-gray-7">{{ s.owner }}</td>
            <td class="whitespace-nowrap px-3 py-2 text-xs text-ink-gray-6">{{ s.pagina || '—' }}</td>
            <td class="px-3 py-2 text-ink-gray-8">{{ s.mensaje }}</td>
            <td class="whitespace-nowrap px-3 py-2">
              <select
                v-model="s.estado"
                class="rounded border bg-surface-white px-1.5 py-1 text-xs"
                :class="estadoClass(s.estado)"
                @change="saveEstado(s)"
              >
                <option v-for="e in ESTADOS" :key="e" :value="e">{{ e }}</option>
              </select>
            </td>
          </tr>
          <tr v-if="!filtered.length && !loading">
            <td colspan="5" class="px-3 py-8 text-center text-sm text-ink-gray-4">{{ __('Sin sugerencias.') }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, call, toast } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { usersStore } from '@/stores/users'
import BulbIcon from '~icons/lucide/lightbulb'
import LockIcon from '~icons/lucide/lock'

const { isAdmin } = usersStore()
const isAdminUser = computed(() => { try { return !!isAdmin() } catch (e) { return false } })

const ESTADOS = ['Nueva', 'En revision', 'Implementada', 'Descartada']
const rows = ref([])
const fEstado = ref('')
const loading = ref(false)

const filtered = computed(() => rows.value.filter(s => !fEstado.value || s.estado === fEstado.value))

function fmtDate(d) { return d ? String(d).slice(0, 16).replace('T', ' ') : '' }
function estadoClass(e) {
  return e === 'Implementada' ? 'text-green-700' : e === 'Descartada' ? 'text-ink-gray-5' : e === 'En revision' ? 'text-amber-700' : 'text-blue-700'
}

async function load() {
  if (!isAdminUser.value) return
  loading.value = true
  try {
    rows.value = await call('frappe.client.get_list', {
      doctype: 'CRM Sugerencia',
      fields: ['name', 'mensaje', 'pagina', 'estado', 'owner', 'creation'],
      order_by: 'creation desc',
      limit_page_length: 0,
    }) || []
  } catch (e) { toast.error(__('No se pudieron cargar las sugerencias')) } finally { loading.value = false }
}
async function saveEstado(s) {
  try { await call('frappe.client.set_value', { doctype: 'CRM Sugerencia', name: s.name, fieldname: 'estado', value: s.estado }) }
  catch (e) { toast.error(__('No se pudo actualizar')) }
}
onMounted(load)
</script>
