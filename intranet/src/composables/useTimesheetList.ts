import { ref, reactive, computed } from 'vue'
import { frappeService } from '@/services/frappe.service'

// ปรับปรุง interface ให้ตรงกับโครงสร้างจริง
export interface SMOTimesheet {
  name: string
  employee: string
  employee_name?: string
  year: string 
  month: string
  month_value?: string  // ฟิลด์ซ่อน
  total_hours: number
  approver?: string
  docstatus: number
  owner?: string
  creation?: string
  modified?: string
  modified_by?: string
  workflow_state?: string
}

// ปรับปรุง filter interface
export interface TimesheetFilters {
  employee?: string
  year?: string
  month?: string
  status?: '0' | '1' | '2'  // docstatus: 0=Draft, 1=Submitted, 2=Cancelled
}

/**
 * Composable สำหรับการทำงานกับรายการ SMO Timesheet
 */
export function useTimesheetList(initialFilters: TimesheetFilters = {}) {
  const timesheets = ref<SMOTimesheet[]>([])
  const isLoading = ref(false)
  const error = ref<Error | null>(null)
  
  // Filters
  const filters = reactive<TimesheetFilters>({ ...initialFilters })
  
  // Pagination
  const pagination = reactive({
    limit: 20,
    start: 0,
    total: 0,
    currentPage: computed(() => Math.floor(pagination.start / pagination.limit) + 1),
    totalPages: computed(() => Math.ceil(pagination.total / pagination.limit))
  })
  
  /**
   * โหลดรายการ timesheets ตาม filters
   */
  async function fetchTimesheets() {
    isLoading.value = true
    error.value = null
    
    try {
      // สร้าง filter array สำหรับ Frappe API
      const frappeFilters = []
      
      if (filters.employee) {
        frappeFilters.push(['employee', '=', filters.employee])
      }
      
      if (filters.year) {
        frappeFilters.push(['year', '=', filters.year])
      }
      
      if (filters.month) {
        frappeFilters.push(['month', '=', filters.month])
      }
      
      if (filters.status) {
        frappeFilters.push(['docstatus', '=', filters.status])
      }
      
      // ดึงข้อมูล
      const fields = [
        'name', 
        'employee', 
        
        'year', 
        'month', 
        'total_hours', 
        'approver',
        'docstatus',
        'owner',
        'creation', 
        'modified',
        'workflow_state'
      ]
      
      timesheets.value = await frappeService.getList<SMOTimesheet>('SMO Timesheet', {
        fields,
        filters: frappeFilters,
        orderBy: 'modified desc',
        limit: pagination.limit,
        start: pagination.start
      })
      
      // ดึงจำนวนทั้งหมดสำหรับการแบ่งหน้า
      fetchTotalCount(frappeFilters)
     
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to fetch timesheet list')
      console.error(error.value)
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * ดึงจำนวนรายการทั้งหมดสำหรับการแบ่งหน้า
   */
  async function fetchTotalCount(frappeFilters: any[]) {
    try {
      const total = await frappeService.getCount('SMO Timesheet', frappeFilters)
      console.log(total)
      pagination.total = total
    } catch (err) {
      console.error('Failed to fetch total count:', err)
    }
  }
  
  /**
   * อัปเดต filters และโหลดข้อมูลใหม่
   */
  function updateFilters(newFilters: Partial<TimesheetFilters>) {
    // อัปเดต filters
    Object.assign(filters, newFilters)
    
    // reset pagination
    pagination.start = 0
    
    // โหลดข้อมูลใหม่
    fetchTimesheets()
  }
  
  /**
   * ล้าง filters
   */
  function resetFilters() {
    // ล้าง filters ทั้งหมด
    Object.keys(filters).forEach(key => {
      delete filters[key as keyof TimesheetFilters]
    })
    
    // reset pagination
    pagination.start = 0
    
    // โหลดข้อมูลใหม่
    fetchTimesheets()
  }
  
  /**
   * ไปยังหน้าถัดไป
   */
  function nextPage() {
    if (pagination.start + pagination.limit < pagination.total) {
      pagination.start += pagination.limit
      fetchTimesheets()
    }
  }
  
  /**
   * ไปยังหน้าก่อนหน้า
   */
  function prevPage() {
    if (pagination.start - pagination.limit >= 0) {
      pagination.start -= pagination.limit
      fetchTimesheets()
    }
  }
  
  /**
   * ไปยังหน้าที่ระบุ
   */
  function goToPage(page: number) {
    const newStart = (page - 1) * pagination.limit
    
    if (newStart >= 0 && newStart < pagination.total) {
      pagination.start = newStart
      fetchTimesheets()
    }
  }
  
  // โหลดข้อมูลเริ่มต้น
  fetchTimesheets()
  
  return {
    // State
    timesheets,
    isLoading,
    error,
    filters,
    pagination,
    
    // Methods
    fetchTimesheets,
    updateFilters,
    resetFilters,
    nextPage,
    prevPage,
    goToPage
  }
} 