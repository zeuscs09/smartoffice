import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const useExpenseRequestStore = defineStore('expenseRequest', {
  state: () => ({
    data: [],
  }),
  actions: {
    fetchAll() {
      const requestResource = createResource({
        url: 'smartoffice.api.expense.get_requests',
        onSuccess: (data) => {
          this.data = data
        },
      })
      return requestResource
    },
    get(id) {
      return this.data.find(request => request.id === id)
    },
  },
})
