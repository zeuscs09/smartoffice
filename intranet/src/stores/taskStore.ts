import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const useTaskStore = defineStore('task', {
  state: () => ({
    data: [],
  }),
  actions: {
    fetchAll() {
      const taskResource = createResource({
        url: 'smartoffice.api.task.get_todos_with_smo_tasks',
        onSuccess: (data) => {
          this.data = data
        },
      })
      return taskResource
    },
    get(id) {
      return this.data.find(task => task.id === id)
    },
  },
})
