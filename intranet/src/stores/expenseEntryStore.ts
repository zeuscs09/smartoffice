import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const useExpenseEntryStore = defineStore('expenseEntry', {
  state: () => ({
    data: [],
    currentPage: 1,
    pageSize: 20,
    totalPages: 1,
    documentsResource: createResource({
      url: 'smartoffice.api.expense.get_user_expense_entries',
      auto: false,
    }),
  }),
  actions: {
    fetchAll(page) {
      this.currentPage = page

      this.documentsResource.fetch({
        page: this.currentPage,
        page_size: this.pageSize,
      })

      this.data = this.documentsResource.data?.data || []
      this.totalPages = this.documentsResource.data?.total_pages || 1
      return this.documentsResource
    },
    get(id) {
      return this.data.find((report) => report.id === id)
    },
  },
})
