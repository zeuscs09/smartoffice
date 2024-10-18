import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const useUserStore = defineStore('user', {
  state: () => ({
    data: [],
    isLoggedIn: false,
  }),
  actions: {
    fetchAll() {
      const userResource = createResource({
        url: 'frappe.auth.get_users',
        onSuccess: (data) => {
          this.data = data
        },
      })
      return userResource
    },
    get(id) {
      return this.data.find(user => user.id === id)
    },
    fetchCurrentUser() {
      const userResource = createResource({
        url: 'frappe.auth.get_logged_user',
        onSuccess: (data) => {
          this.isLoggedIn = true
          if (!this.data.some(user => user.id === data.id)) {
            this.data.push(data)
          }
        },
        onError: () => {
          this.isLoggedIn = false
        },
      })
      return userResource
    },
    logout() {
      this.isLoggedIn = false
    },
  },
})
