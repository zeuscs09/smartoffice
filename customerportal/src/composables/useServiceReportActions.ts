import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from '@/plugins/axios'

export const useServiceReportActions = () => {
  const isProcessing = ref(false)
  const error = ref<string | null>(null)

  const approveReports = async (reportNames: string[]) => {
    isProcessing.value = true
    error.value = null
    
    try {
      const results = await Promise.all(
        reportNames.map(name => 
          axios.post('/api/method/smartoffice.api.customerportal.approve_service_report', {
            report_name: name
          })
        )
      )
      
      // ตรวจสอบว่ามี error หรือไม่
      const hasError = results.some(r => r.message.status === 'error')
      if (hasError) {
        throw new Error('บางรายการไม่สามารถอนุมัติได้')
      }

      return true
    } catch (e) {
      error.value = e.message || 'เกิดข้อผิดพลาดในการอนุมัติ'
      return false
    } finally {
      isProcessing.value = false
    }
  }

  const rejectReports = async (reportNames: string[], reason: string) => {
    isProcessing.value = true
    error.value = null

    try {
      const results = await Promise.all(
        reportNames.map(name =>
          axios.post('/api/method/smartoffice.api.customerportal.reject_service_report', {
            report_name: name,
            reason
          })
        )
      )

      const hasError = results.some(r => r.message.status === 'error')
      if (hasError) {
        throw new Error('บางรายการไม่สามารถปฏิเสธได้')
      }

      return true
    } catch (e) {
      error.value = e.message || 'เกิดข้อผิดพลาดในการปฏิเสธ'
      return false
    } finally {
      isProcessing.value = false
    }
  }

  return {
    isProcessing,
    error,
    approveReports,
    rejectReports
  }
} 