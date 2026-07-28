<template>
  <Dialog v-model="show" :options="{ size: '2xl' }">
    <template #body>
      <div class="p-1">
        <div class="flex items-center gap-2 border-b border-outline-gray-modals px-4 py-3">
          <FeatherIcon name="search" class="h-4 w-4 shrink-0 text-ink-gray-5" />
          <input
            ref="inputRef"
            v-model="query"
            type="text"
            :placeholder="__('Buscar organizaciones, contactos, deals, leads...')"
            class="w-full border-0 bg-transparent p-0 text-base text-ink-gray-8 placeholder:text-ink-gray-4 focus:outline-none focus:ring-0"
            @keydown.esc="show = false"
          />
          <LoadingIndicator v-if="loading" class="h-4 w-4 text-ink-gray-4" />
        </div>
        <div class="max-h-[60vh] min-h-[120px] overflow-y-auto p-2">
          <template v-if="hasResults">
            <div
              v-for="g in groups.filter((x) => x.items.length)"
              :key="g.label"
              class="mb-2"
            >
              <div class="px-2 py-1 text-xs font-medium uppercase text-ink-gray-4">
                {{ __(g.label) }}
              </div>
              <button
                v-for="it in g.items"
                :key="g.doctype + it.name"
                class="flex w-full items-center gap-2 rounded px-2 py-2 text-left text-base hover:bg-surface-gray-2"
                @click="goTo(g, it)"
              >
                <component :is="g.icon" class="h-4 w-4 shrink-0 text-ink-gray-6" />
                <span class="truncate text-ink-gray-8">{{ it.label }}</span>
                <span v-if="it.sub" class="ml-auto truncate pl-2 text-sm text-ink-gray-4">
                  {{ it.sub }}
                </span>
              </button>
            </div>
          </template>
          <div
            v-else-if="query.length >= 2 && !loading"
            class="px-3 py-8 text-center text-sm text-ink-gray-4"
          >
            {{ __('Sin resultados') }}
          </div>
          <div v-else class="px-3 py-8 text-center text-sm text-ink-gray-4">
            {{ __('Escribí al menos 2 caracteres para buscar…') }}
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { call, FeatherIcon, Dialog, LoadingIndicator } from 'frappe-ui'
import { watchDebounced } from '@vueuse/core'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'

const show = defineModel({ type: Boolean, default: false })
const router = useRouter()
const query = ref('')
const loading = ref(false)
const inputRef = ref(null)

const groups = reactive([
  { label: 'Organizaciones', doctype: 'CRM Organization', route: 'Organization', param: 'organizationId', icon: OrganizationsIcon, items: [] },
  { label: 'Contactos', doctype: 'Contact', route: 'Contact', param: 'contactId', icon: ContactsIcon, items: [] },
  { label: 'Deals', doctype: 'CRM Deal', route: 'Deal', param: 'dealId', icon: DealsIcon, items: [] },
  { label: 'Leads', doctype: 'CRM Lead', route: 'Lead', param: 'leadId', icon: LeadsIcon, items: [] },
])

const CFG = {
  'CRM Organization': {
    fields: ['name'],
    or: ['name'],
    label: (r) => r.name,
    sub: () => '',
  },
  Contact: {
    fields: ['name', 'full_name', 'company_name'],
    or: ['name', 'first_name', 'last_name', 'email_id'],
    label: (r) => r.full_name || r.name,
    sub: (r) => r.company_name || '',
  },
  'CRM Deal': {
    fields: ['name', 'organization', 'custom_numero_solaer'],
    or: ['name', 'organization', 'custom_numero_solaer'],
    label: (r) => r.custom_numero_solaer || r.organization || r.name,
    sub: (r) => r.organization || '',
  },
  'CRM Lead': {
    fields: ['name', 'lead_name', 'organization'],
    or: ['lead_name', 'organization', 'name'],
    label: (r) => r.lead_name || r.name,
    sub: (r) => r.organization || '',
  },
}

const hasResults = computed(() => groups.some((g) => g.items.length))

async function runSearch(q) {
  loading.value = true
  await Promise.all(
    groups.map(async (g) => {
      const cfg = CFG[g.doctype]
      try {
        const rows = await call('frappe.client.get_list', {
          doctype: g.doctype,
          fields: cfg.fields,
          or_filters: cfg.or.map((f) => [f, 'like', '%' + q + '%']),
          limit_page_length: 6,
        })
        g.items = (rows || []).map((r) => ({
          name: r.name,
          label: cfg.label(r),
          sub: cfg.sub(r),
        }))
      } catch (e) {
        g.items = []
      }
    }),
  )
  loading.value = false
}

watchDebounced(
  query,
  (q) => {
    if (!q || q.trim().length < 2) {
      groups.forEach((g) => (g.items = []))
      loading.value = false
      return
    }
    runSearch(q.trim())
  },
  { debounce: 300 },
)

watch(show, (v) => {
  if (v) {
    query.value = ''
    groups.forEach((g) => (g.items = []))
    nextTick(() => inputRef.value?.focus())
  }
})

function goTo(g, it) {
  show.value = false
  router.push({ name: g.route, params: { [g.param]: it.name } })
}
</script>
