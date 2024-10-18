import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const useAdvanceRequestStore = defineStore('advanceRequest', {
  state: () => ({
    data: [],
  }),
  actions: {
    fetchAll() {
      const requestResource = createResource({
        url: 'smartoffice.api.advance.get_requests',
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
