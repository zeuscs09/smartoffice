import { defineStore } from 'pinia'


export const useServiceReportStore = defineStore('serviceReport', {
  state: () => ({
    currentPage: 1,
    pageSize: 10,
    reports: [],
    isLoading: false,
    error: '',
    searchQuery: '',
    statusFilter: '',
    startDate: '',
    endDate: '',
    sortField: '',
    sortOrder: 'asc',
  }),

  actions: {
    async fetchAll(page: number) {
      this.currentPage = page
      this.isLoading = true
      
      try {
        const token = localStorage.getItem('customer_token')
        if (!token) {
          throw new Error('Unauthorized')
        }

        const response = await fetch('/api/method/smartoffice.api.customerportal.check_auth_and_get_reports', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            page: this.currentPage,
            page_size: this.pageSize,
            search: this.searchQuery,
            status: this.statusFilter,
            start_date: this.startDate,
            end_date: this.endDate,
            sort_field: this.sortField,
            sort_order: this.sortOrder,
          })
        })

        const data = await response.json()
        console.log('API Response:', data.message)
        const message = data.message
        if (message.status === 'success') {
          this.reports = message.data
          this.error = ''
          return true
        } else {
          this.error = message.message || 'ไม่สามารถดึงข้อมูลได้'
          return false
        }
      } catch (err) {
        console.error('Fetch error:', err)
        this.error = err.message || 'เกิดข้อผิดพลาด กรุณาลองใหม่'
        return false
      } finally {
        this.isLoading = false
      }
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
      return this.reports.find((report) => report.id === id)
    }
  },

  getters: {
    data(): any[] {
      return this.reports || []
    },
    isFirstPage(): boolean {
      return this.currentPage === 1
    },
    isLastPage(): boolean {
      return this.currentPage === this.totalPages
    },
    totalPages(): number {
      return this.reports.length / this.pageSize + (this.reports.length % this.pageSize > 0 ? 1 : 0)
    }
  }
})
