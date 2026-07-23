import { parseColor } from '@/utils'
import { defineStore } from 'pinia'
import { createListResource } from 'frappe-ui'
import { reactive } from 'vue'

export const productsStore = defineStore('crm-products', () => {
  let productsByName = reactive({})

  const products = createListResource({
    doctype: 'CRM Product',
    fields: ['name', 'color'],
    orderBy: 'name asc',
    pageLength: 99999,
    cache: 'products',
    initialData: [],
    auto: true,
    transform(products) {
      for (let product of products) {
        product.colorClass = parseColor(product.color)
        productsByName[product.name] = product
      }
      return products
    },
  })

  function getProduct(name) {
    return productsByName[name]
  }

  return {
    products,
    getProduct,
  }
})
