import { ref, computed } from 'vue'
import { frappeService } from '~/services/frappe.service'
import type { SMOTimesheet, SMOTimesheetDetail } from '~/types/timesheet'

/**
 * Composable สำหรับการทำงานกับ SMO Timesheet แบบเดี่ยว
 */
export function useTimesheet(initialId?: string) {
  const timesheet = ref<SMOTimesheet | null>(null)
  const isLoading = ref(false)
  const error = ref<Error | null>(null)
  
  // Computed properties
  const isDraft = computed(() => timesheet.value?.status === 'Draft')
  const isSubmitted = computed(() => timesheet.value?.status === 'Submitted')
  const canEdit = computed(() => !timesheet.value?.name || isDraft.value)
  
  /**
   * โหลดข้อมูล timesheet ตาม ID
   */
  async function fetchTimesheet(id: string) {
    if (!id) return
    
    isLoading.value = true
    error.value = null
    
    try {
      timesheet.value = await frappeService.getDocument<SMOTimesheet>('SMO Timesheet', id)
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to fetch timesheet')
      console.error(error.value)
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * บันทึก timesheet (สร้างหรืออัปเดต)
   */
  async function saveTimesheet(data: Partial<SMOTimesheet> = {}) {
    isLoading.value = true
    error.value = null
    
    try {
      // ใช้ข้อมูลปัจจุบันร่วมกับข้อมูลใหม่
      const saveData = { 
        ...data,
        // หากไม่มีการส่ง timesheet_details มา ให้ใช้ของเดิม
        timesheet_details: data.timesheet_details || timesheet.value?.timesheet_details
      }
      
      if (timesheet.value?.name) {
        // อัปเดต
        timesheet.value = await frappeService.updateDocument<SMOTimesheet>(
          'SMO Timesheet', 
          timesheet.value.name, 
          saveData
        )
      } else {
        // สร้างใหม่
        timesheet.value = await frappeService.createDocument<SMOTimesheet>(
          'SMO Timesheet', 
          saveData
        )
      }
      
      return timesheet.value
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to save timesheet')
      console.error(error.value)
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Submit timesheet
   */
  async function submitTimesheet() {
    if (!timesheet.value?.name) {
      throw new Error('Cannot submit: No timesheet selected')
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      timesheet.value = await frappeService.submitDocument<SMOTimesheet>(
        'SMO Timesheet', 
        timesheet.value.name
      )
      return timesheet.value
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to submit timesheet')
      console.error(error.value)
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Cancel timesheet
   */
  async function cancelTimesheet() {
    if (!timesheet.value?.name) {
      throw new Error('Cannot cancel: No timesheet selected')
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      timesheet.value = await frappeService.cancelDocument<SMOTimesheet>(
        'SMO Timesheet', 
        timesheet.value.name
      )
      return timesheet.value
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to cancel timesheet')
      console.error(error.value)
      throw error.value
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * เพิ่มรายการ timesheet detail
   */
  function addTimesheetDetail() {
    if (!timesheet.value) {
      initEmptyTimesheet()
    }
    
    if (!timesheet.value) return null
    
    if (!timesheet.value.timesheet_details) {
      timesheet.value.timesheet_details = []
    }
    
    const newDetail: SMOTimesheetDetail = {
      name: `new-${Date.now()}`,
      idx: (timesheet.value.timesheet_details.length || 0) + 1,
      activity_type: '',
      from_time: '',
      to_time: '',
      hours: 0
    }
    
    timesheet.value.timesheet_details.push(newDetail)
    return newDetail
  }
  
  /**
   * ลบรายการ timesheet detail
   */
  function removeTimesheetDetail(index: number) {
    if (!timesheet.value?.timesheet_details) return
    
    timesheet.value.timesheet_details.splice(index, 1)
    
    // อัปเดต idx สำหรับทุกรายการที่เหลือ
    timesheet.value.timesheet_details.forEach((detail, i) => {
      detail.idx = i + 1
    })
    
    calculateTotalHours()
  }
  
  /**
   * คำนวณจำนวนชั่วโมงจาก from_time และ to_time
   */
  function calculateHours(fromTime: string, toTime: string): number {
    if (!fromTime || !toTime) return 0
    
    const from = new Date(fromTime)
    const to = new Date(toTime)
    
    if (isNaN(from.getTime()) || isNaN(to.getTime())) return 0
    
    // คำนวณผลต่างในหน่วยมิลลิวินาที และแปลงเป็นชั่วโมง
    return (to.getTime() - from.getTime()) / (1000 * 60 * 60)
  }
  
  /**
   * คำนวณชั่วโมงสำหรับรายการที่ระบุ
   */
  function calculateDetailHours(index: number) {
    if (!timesheet.value?.timesheet_details?.[index]) return 0
    
    const detail = timesheet.value.timesheet_details[index]
    if (!detail.from_time || !detail.to_time) return 0
    
    // คำนวณและบันทึกชั่วโมง
    detail.hours = calculateHours(detail.from_time, detail.to_time)
    
    // อัปเดตผลรวมชั่วโมง
    calculateTotalHours()
    
    return detail.hours
  }
  
  /**
   * คำนวณผลรวมชั่วโมงทั้งหมด
   */
  function calculateTotalHours() {
    if (!timesheet.value?.timesheet_details) return 0
    
    const total = timesheet.value.timesheet_details.reduce(
      (sum, detail) => sum + (detail.hours || 0), 
      0
    )
    
    if (timesheet.value) {
      timesheet.value.total_hours = total
    }
    
    return total
  }
  
  /**
   * สร้าง timesheet เปล่า
   */
  function initEmptyTimesheet() {
    timesheet.value = {
      name: '',
      employee: '',
      company: '',
      posting_date: new Date().toISOString().split('T')[0],
      total_hours: 0,
      status: 'Draft',
      timesheet_details: [],
      docstatus: 0
    }
  }
  
  // ถ้ามี ID ให้โหลดข้อมูล
  if (initialId) {
    fetchTimesheet(initialId)
  } else {
    initEmptyTimesheet()
  }
  
  return {
    // State
    timesheet,
    isLoading,
    error,
    
    // Computed
    isDraft,
    isSubmitted,
    canEdit,
    
    // Methods
    fetchTimesheet,
    saveTimesheet,
    submitTimesheet,
    cancelTimesheet,
    addTimesheetDetail,
    removeTimesheetDetail,
    calculateDetailHours,
    calculateTotalHours,
    initEmptyTimesheet
  }
} 