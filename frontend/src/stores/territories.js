import { parseColor } from '@/utils'
import { defineStore } from 'pinia'
import { createListResource } from 'frappe-ui'
import { reactive } from 'vue'

export const territoriesStore = defineStore('crm-territories', () => {
  let territoriesByName = reactive({})

  const territories = createListResource({
    doctype: 'CRM Territory',
    fields: ['name', 'color'],
    orderBy: 'name asc',
    pageLength: 99999,
    cache: 'territories',
    initialData: [],
    auto: true,
    transform(territories) {
      for (let territory of territories) {
        territory.colorClass = parseColor(territory.color)
        territoriesByName[territory.name] = territory
      }
      return territories
    },
  })

  function getTerritory(name) {
    return territoriesByName[name]
  }

  return {
    territories,
    getTerritory,
  }
})
