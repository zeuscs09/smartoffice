import axios from 'axios'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Define types
type ServiceReport = {
  name: string
  project_code: string
  project_name: string
  start_date_input: string
  duration: string
  owner: string
  creation: string
  modified: string
}

type APIResponse = {
  message: {
    status: string
    is_authenticated: boolean
    email: string
    data: ServiceReport[]
  }
}

// Create axios instance for Customer Portal
const customerAxios = axios.create()

customerAxios.interceptors.request.use((config) => {
  const token = localStorage.getItem('customerToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const useCustomerPortalStore = defineStore('customerPortal', () => {
  const data = ref<ServiceReport[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // filters
  const searchQuery = ref('')
  const statusFilter = ref('')
  const startDate = ref('')
  const endDate = ref('')

  const fetchServiceReports = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await customerAxios.get<APIResponse>('/api/method/smartoffice.api.customerportal.check_auth_and_get_reports')
      
      if (response.data.message.status === 'success') {
        data.value = response.data.message.data
      } else {
        error.value = 'Failed to fetch data'
      }
    } catch (err) {
      error.value = err.response?.data?.message || 'Error fetching service reports'
    } finally {
      loading.value = false
    }
  }

  const approveReport = async (reportId: string) => {
    try {
      const response = await customerAxios.post('/api/method/smartoffice.api.customerportal.approve_service_report', {
        report_name: reportId
      })
      
      if (response.data.message.status === 'success') {
        await fetchServiceReports() // refresh data
        return true
      }
      return false
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to approve report'
      return false
    }
  }

  const rejectReport = async (reportId: string, reason: string) => {
    try {
      const response = await customerAxios.post('/api/method/smartoffice.api.customerportal.reject_service_report', {
        report_name: reportId,
        reason: reason
      })
      
      if (response.data.message.status === 'success') {
        await fetchServiceReports() // refresh data
        return true
      }
      return false
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to reject report'
      return false
    }
  }

  return {
    data,
    loading,
    error,
    searchQuery,
    statusFilter,
    startDate,
    endDate,
    fetchServiceReports,
    approveReport,
    rejectReport
  }
})
