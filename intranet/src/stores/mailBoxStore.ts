import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
// smartoffice.api.task.get_todos_with_smo_tasks
// smartoffice.api.servicereport.get_user_service_reports
export const useMailBoxStore = defineStore('mailBoxStore', {
  state: () => ({
    currentPage: 1,
    pageSize: 10,
   
    documentsResource: createResource({
      url: 'smartoffice.api.mailbox.get_mail_box',
      auto: false,
    }),
    searchQuery: '',
    statusFilter: '',
    startDate: '',
    endDate: '',
    sortField: '',
    sortOrder: 'asc',
  }),
  actions: {
     fetchAll(page: number) {
      this.currentPage = page
      
       this.documentsResource.fetch({
        page: this.currentPage,
        page_size: this.pageSize,
        search: this.searchQuery,
        status: this.statusFilter,
        start_date: this.startDate,
        end_date: this.endDate,
        sort_field: this.sortField,
        sort_order: this.sortOrder,
      })

      //this.totalPages = this.documentsResource.data?.total_pages || 1
      return this.documentsResource
    },
    setSearchQuery(query: string) {
      this.searchQuery = query
      this.fetchAll(1)
    },
    setStatusFilter(status: string) {
      this.statusFilter = status
      this.fetchAll(1)
    },
    setDateRange(start: string, end: string) {
      this.startDate = start
      this.endDate = end
      this.fetchAll(1)
    },
    setSorting(field: string) {
      if (this.sortField === field) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortField = field
        this.sortOrder = 'asc'
      }
      this.fetchAll(this.currentPage)
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.fetchAll(this.currentPage + 1)
      }
    },
    previousPage() {
      if (this.currentPage > 1) {
        this.fetchAll(this.currentPage - 1)
      }
    },
    goToPage(page: number) {
      if (page >= 1 && page <= this.totalPages) {
        this.fetchAll(page)
      }
    },
    get(id: string) {
      return this.data.find((report) => report.id === id)
    },
  },
  getters: {
    data(): any[] {
      return this.documentsResource.data?.data || []
    },
    isFirstPage(): boolean {
      return this.currentPage === 1
    },
    isLastPage(): boolean {
      return this.currentPage === this.totalPages
    },
    totalRecords(): number {
      return this.documentsResource.data?.total || 0
    },
    totalPages(): number {
      return this.documentsResource.data?.total_pages || 1
    }

  }
})
