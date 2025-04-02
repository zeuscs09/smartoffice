import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

export const useTimesheetStore = defineStore('timesheet', () => {
  // State
  const data = ref([])
  const currentPage = ref(1)
  const pageSize = ref(10)
  const searchQuery = ref('')
  const statusFilter = ref('')
  const yearFilter = ref(new Date().getFullYear().toString())
  const monthFilter = ref((new Date().getMonth() + 1).toString().padStart(2, '0'))
  const sortField = ref('posting_date')
  const sortOrder = ref('desc')

  // Resource for fetching timesheets
  const documentsResource = createResource({
    url: 'smartoffice.api.timesheet.get_timesheets',
    auto: false,
    onSuccess(response) {
      data.value = response.data || []
    }
  })

  // Computed properties
  const isFirstPage = computed(() => currentPage.value === 1)
  const isLastPage = computed(() => {
    if (!documentsResource.data) return true
    const totalPages = Math.ceil(documentsResource.data.total / pageSize.value)
    return currentPage.value >= totalPages
  })

  // Methods
  const fetchAll = (page = currentPage.value) => {
    currentPage.value = page
    
    const filters = {
      year: yearFilter.value,
      month: monthFilter.value,
      status: statusFilter.value
    }

    documentsResource.submit({
      page: currentPage.value,
      page_size: pageSize.value,
      filters,
      search: searchQuery.value,
      sort_field: sortField.value,
      sort_order: sortOrder.value
    })
  }

  const nextPage = () => {
    if (!isLastPage.value) {
      currentPage.value++
      fetchAll(currentPage.value)
    }
  }

  const previousPage = () => {
    if (!isFirstPage.value) {
      currentPage.value--
      fetchAll(currentPage.value)
    }
  }

  const refresh = () => {
    fetchAll(currentPage.value)
  }

  return {
    // State
    data,
    currentPage,
    pageSize,
    searchQuery,
    statusFilter,
    yearFilter,
    monthFilter,
    sortField,
    sortOrder,
    documentsResource,

    // Computed
    isFirstPage,
    isLastPage,

    // Methods
    fetchAll,
    nextPage,
    previousPage,
    refresh
  }
}) 