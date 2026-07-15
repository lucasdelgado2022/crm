import { parseColor } from '@/utils'
import { defineStore } from 'pinia'
import { createListResource } from 'frappe-ui'
import { reactive } from 'vue'

export const industriesStore = defineStore('crm-industries', () => {
  let industriesByName = reactive({})

  const industries = createListResource({
    doctype: 'CRM Industry',
    fields: ['name', 'color', 'short_code'],
    orderBy: 'name asc',
    pageLength: 99999,
    cache: 'industries',
    initialData: [],
    auto: true,
    transform(industries) {
      for (let industry of industries) {
        industry.colorClass = parseColor(industry.color)
        industriesByName[industry.name] = industry
      }
      return industries
    },
  })

  function getIndustry(name) {
    return industriesByName[name]
  }

  return {
    industries,
    getIndustry,
  }
})
