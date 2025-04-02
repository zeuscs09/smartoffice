<script setup lang="ts">
import { ref, onMounted, computed, watch, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { Calendar, Clock, Save, ArrowLeft, Plus, Trash2, Check, X } from 'lucide-vue-next'
import UserLayout from '@/layouts/userLayout.vue'
import { session } from '@/data/session'

// Types
interface WorkflowTransition {
  name: string
  state: string
  action: string
  next_state: string
  allowed: string
  allow_self_approval: number
  condition: string
}

interface TimesheetEntry {
  from_time: string
  to_time: string
  working_hours: number
  link_from_doc: string
  doc_number: string
  project_code: string
  customer: string
  customer_name: string
}

interface Timesheet {
  name: string
  employee: string
  employee_name: string
  year: string
  month: string
  month_value: string
  time_sheets: TimesheetEntry[]
  docstatus: number
  workflow_state: string
  owner: string
  modified_by: string
}

interface Employee {
  name: string
  employee_name: string
}

interface Month {
  value: string
  label: string
  number: string
}

// Composables
const formatDuration = inject('formatDuration') as (duration: number, options?: { hourOnly?: boolean }) => string
const router = useRouter()
const route = useRoute()
const toast = useToast()

// State
const timesheetId = computed(() => route.params.id as string)
const isNewTimesheet = computed(() => timesheetId.value === 'new')

const employee = ref<Employee>({
  name: '',
  employee_name: ''
})

const timesheet = ref<Timesheet>({
  name: '',
  employee: '',
  employee_name: '',
  year: new Date().getFullYear().toString(),
  month: '',
  month_value: '',
  time_sheets: [],
  docstatus: 0,
  workflow_state: '',
  owner: '',
  modified_by: ''
})

const transitions = ref<WorkflowTransition[]>([])

// Constants
const months: Month[] = [
  { value: 'January', label: 'January', number: '01' },
  { value: 'February', label: 'February', number: '02' },
  { value: 'March', label: 'March', number: '03' },
  { value: 'April', label: 'April', number: '04' },
  { value: 'May', label: 'May', number: '05' },
  { value: 'June', label: 'June', number: '06' },
  { value: 'July', label: 'July', number: '07' },
  { value: 'August', label: 'August', number: '08' },
  { value: 'September', label: 'September', number: '09' },
  { value: 'October', label: 'October', number: '10' },
  { value: 'November', label: 'November', number: '11' },
  { value: 'December', label: 'December', number: '12' }
]

const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => (currentYear - 2 + i).toString())
})

// Computed
const totalHours = computed(() => {
  if (!timesheet.value.time_sheets?.length) return 0
  return timesheet.value.time_sheets.reduce((total, item) => {
    const hours = item.working_hours ? parseFloat(item.working_hours.toString()) : 0
    return total + hours
  }, 0)
})

// Add loading state for initial data fetch
const isInitialLoading = ref(true)

// Update isEditable computed property
const isEditable = computed(() => {
  // ถ้ายังโหลดข้อมูลครั้งแรกไม่เสร็จ ให้แสดงปุ่ม Save
  if (isInitialLoading.value) return true
  
  // ถ้าเป็นเอกสารใหม่ หรือ docstatus เป็น 0 (Draft) ให้แสดงปุ่ม Save
  if (isNewTimesheet.value || timesheet.value.docstatus === 0) return true
  
  // ถ้า workflow_state เป็น Rejected และ docstatus < 2 ให้แสดงปุ่ม Save
  if (timesheet.value.workflow_state === 'Rejected' && timesheet.value.docstatus < 2) return true
  
  return false
})


// Add loading states
const isLoading = ref({
  save: false,
  submit: false,
  cancel: false,
  fetch: false,
  cancelDocument: false
})

// Add new state for reject reason
const rejectReason = ref('')

// Methods
const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getEmployee = async (): Promise<void> => {
  try {
    const response = await fetch('/api/method/frappe.client.get_list', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctype: 'Employee',
        fields: ['name', 'employee_name'],
        filters: [['user_id', '=', session.user]],
        order_by: 'employee_name asc'
      })
    })

    const data = await response.json()
    employee.value = data.message[0] || { name: '', employee_name: '' }
  } catch (error) {
    console.error('Error fetching employee:', error)
    toast.error('Failed to fetch employee data')
  }
}

const fetchTimesheet = async (): Promise<void> => {
  if (isNewTimesheet.value) {
    isInitialLoading.value = false
    return
  }

  try {
    const response = await fetch('/api/method/frappe.client.get', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctype: 'SMO Timesheet',
        name: timesheetId.value
      })
    })

    if (!response.ok) throw new Error('Failed to fetch timesheet')
    const data = await response.json()
    
    // Get employee name
    const employeeResponse = await fetch('/api/method/frappe.client.get', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctype: 'Employee',
        name: data.message.employee
      })
    })

    if (!employeeResponse.ok) throw new Error('Failed to fetch employee data')
    const employeeData = await employeeResponse.json()

    // Set timesheet data with employee name
    timesheet.value = {
      ...data.message,
      employee_name: employeeData.message.employee_name
    }

    // Fetch workflow transitions after timesheet data is loaded
    await getWorkflowTransitions()
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to fetch timesheet')
  } finally {
    isInitialLoading.value = false
  }
}

const getTimesheetData = async (): Promise<void> => {
  if (!timesheet.value.employee || !timesheet.value.year || !timesheet.value.month) {
    toast.error('Please select employee, year and month')
    return
  }

  const selectedMonth = months.find(m => m.value === timesheet.value.month)
  if (!selectedMonth) {
    toast.error('Invalid month selected')
    return
  }

  timesheet.value.month_value = selectedMonth.number
  isLoading.value.fetch = true

  try {
    const response = await fetch('/api/method/smartoffice.smart_office.doctype.smo_timesheet.smo_timesheet.get_timesheets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        employee: timesheet.value.employee,
        year: timesheet.value.year,
        month: selectedMonth.value
      })
    })

    if (!response.ok) throw new Error('Failed to fetch timesheet data')
    const data = await response.json()
    timesheet.value.time_sheets = data.message || []
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to fetch timesheet data')
  } finally {
    isLoading.value.fetch = false
  }
}

const saveTimesheet = async (): Promise<void> => {
  if (!timesheet.value.employee || !timesheet.value.year || !timesheet.value.month) {
    toast.error('Please fill in all required fields')
    return
  }

  const selectedMonth = months.find(m => m.value === timesheet.value.month)
  if (!selectedMonth) {
    toast.error('Invalid month selected')
    return
  }

  timesheet.value.month_value = selectedMonth.number
  isLoading.value.save = true

  try {
    if (isNewTimesheet.value) {
      // For new timesheet, use insert
      const response = await fetch('/api/method/frappe.client.insert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doc: {
            doctype: 'SMO Timesheet',
            employee: timesheet.value.employee,
            year: timesheet.value.year,
            month: timesheet.value.month,
            month_value: timesheet.value.month_value,
            total_hours: totalHours.value,
            time_sheets: timesheet.value.time_sheets.map(item => ({
              doctype: 'SMO Timesheet Item',
              from_time: item.from_time,
              to_time: item.to_time,
              working_hours: item.working_hours,
              link_from_doc: item.link_from_doc,
              doc_number: item.doc_number,
              project_code: item.project_code,
              customer: item.customer,
              customer_name: item.customer_name
            }))
          }
        })
      })

      if (!response.ok) throw new Error('Failed to save timesheet')
      const data = await response.json()
      
      toast.success('Timesheet created successfully')
      // Use window.location.href instead of router.replace
      router.push(`/timesheet/${data.message.name}`)
    } else {
      // For existing timesheet, use set_value
      const response = await fetch('/api/method/frappe.client.set_value', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doctype: 'SMO Timesheet',
          name: timesheet.value.name,
          fieldname: {
            year: timesheet.value.year,
            month: timesheet.value.month,
            month_value: timesheet.value.month_value,
            total_hours: totalHours.value,
            time_sheets: timesheet.value.time_sheets.map(item => ({
              doctype: 'SMO Timesheet Item',
              from_time: item.from_time,
              to_time: item.to_time,
              working_hours: item.working_hours,
              link_from_doc: item.link_from_doc,
              doc_number: item.doc_number,
              project_code: item.project_code,
              customer: item.customer,
              customer_name: item.customer_name
            }))
          }
        })
      })

      if (!response.ok) throw new Error('Failed to update timesheet')
      
      toast.success('Timesheet updated successfully')
      // Reload the page to get fresh data
      window.location.reload()
    }
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to save timesheet')
  } finally {
    isLoading.value.save = false
  }
}

const submitTimesheet = async (): Promise<void> => {
  if (!timesheet.value.name) {
    toast.error('Please save the timesheet first')
    return
  }

  isLoading.value.submit = true
  try {
    const response = await fetch('/api/method/smartoffice.api.timesheet.submit_timesheet', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: timesheet.value.name })
    })

    if (!response.ok) throw new Error('Failed to submit timesheet')
    toast.success('Timesheet submitted successfully')
    await fetchTimesheet()
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to submit timesheet')
  } finally {
    isLoading.value.submit = false
  }
}

const cancelTimesheet = async (): Promise<void> => {
  if (!timesheet.value.name) {
    toast.error('Please save the timesheet first')
    return
  }

  isLoading.value.cancel = true
  try {
    const response = await fetch('/api/method/smartoffice.api.timesheet.cancel_timesheet', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: timesheet.value.name })
    })

    if (!response.ok) throw new Error('Failed to cancel timesheet')
    toast.success('Timesheet cancelled successfully')
    await fetchTimesheet()
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to cancel timesheet')
  } finally {
    isLoading.value.cancel = false
  }
}

const goBack = (): void => {
  router.push({ name: 'TimesheetList' })
}

const getWorkflowTransitions = async (): Promise<void> => {
  if (!timesheet.value.name) return

  try {
    const response = await fetch('/api/method/frappe.model.workflow.get_transitions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doc: {
          doctype: 'SMO Timesheet',
          name: timesheet.value.name,
          owner: timesheet.value.owner,
          modified_by: timesheet.value.modified_by,
          docstatus: timesheet.value.docstatus,
          workflow_state: timesheet.value.workflow_state
        }
      })
    })

    if (!response.ok) throw new Error('Failed to fetch workflow transitions')
    const data = await response.json()
    transitions.value = data.message || []
  } catch (error) {
    console.error('Error fetching workflow transitions:', error)
  }
}

const executeWorkflowAction = async (action: string): Promise<void> => {
  if (!timesheet.value.name) return

  try {
    if (action === 'Reject') {
      // First update the reject reason
      const updateResponse = await fetch('/api/method/frappe.client.set_value', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doctype: 'SMO Timesheet',
          name: timesheet.value.name,
          fieldname: 'reject_reason',
          value: rejectReason.value
        })
      })

      if (!updateResponse.ok) throw new Error('Failed to update reject reason')
    }

    // Then execute the workflow action
    const response = await fetch('/api/method/frappe.model.workflow.apply_workflow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doc: timesheet.value,
        action: action
      })
    })

    if (!response.ok) throw new Error('Failed to execute workflow action')
    toast.success('Action executed successfully')
    
    // Reload the page to get fresh data
    window.location.reload()
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to execute action')
  }
}

// Update workflow action handling
const handleTransition = (transition: WorkflowTransition) => {
  if (transition.action === 'Reject') {
    document.getElementById('reject-modal').checked = true
  } else {
    executeWorkflowAction(transition.action)
  }
}

const confirmReject = async () => {
  if (!rejectReason.value) {
    toast.error('Please enter rejection reason')
    return
  }
  
  await executeWorkflowAction('Reject')
  rejectReason.value = ''
}

// Add watch for workflow state changes
watch(() => timesheet.value.workflow_state, async () => {
  if (timesheet.value.name) {
    await getWorkflowTransitions()
  }
})

const cancelDocument = async (): Promise<void> => {
  if (!timesheet.value.name) return

  isLoading.value.cancelDocument = true
  try {
    const response = await fetch('/api/method/frappe.client.cancel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctype: 'SMO Timesheet',
        name: timesheet.value.name
      })
    })

    if (!response.ok) throw new Error('Failed to cancel document')
    toast.success('Document cancelled successfully')
    window.location.reload()
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to cancel document')
  } finally {
    isLoading.value.cancelDocument = false
  }
}

// Lifecycle hooks
onMounted(async () => {
  await Promise.all([
    fetchTimesheet(),
    getEmployee()
  ])

  if (isNewTimesheet.value) {
    const currentMonth = new Date().getMonth()
    timesheet.value.month = months[currentMonth].value
    timesheet.value.month_value = months[currentMonth].number
    timesheet.value.employee = employee.value.name
    timesheet.value.employee_name = employee.value.employee_name
  }
})
</script>

<template>
  <UserLayout>
    <div class="mx-auto p-4">
      <!-- Reject Modal -->
      <input type="checkbox" id="reject-modal" class="modal-toggle" />
      <div class="modal">
        <div class="modal-box">
          <h3 class="font-bold text-lg">Please enter rejection reason</h3>
          <textarea v-model="rejectReason" class="textarea textarea-bordered textarea-sm w-full mt-4" placeholder="Reason..."></textarea>
          <div class="modal-action">
            <label for="reject-modal" class="btn btn-sm" @click="confirmReject">Confirm</label>
            <label for="reject-modal" class="btn btn-sm">Cancel</label>
          </div>
        </div>
      </div>

      <!-- Workflow Transitions -->
      <div class="bg-white rounded-lg shadow p-4 mb-4">
        <div class="flex justify-between items-center">
          <div class="breadcrumbs text-sm">
            <ul>
              <li><a @click="router.push('/')">Home</a></li>
              <li><a @click="router.push({ name: 'TimesheetList' })">Timesheet</a></li>
              <li>{{ isNewTimesheet ? 'New Timesheet' : timesheet.name }}</li>
            </ul>
          </div>
          <div class="flex gap-2">
            <button 
              v-show="isEditable  && timesheet.docstatus == 0" 
              class="btn btn-sm bg-green-500 hover:bg-green-600 text-white"
              @click="saveTimesheet"
              :disabled="isLoading.save"
            >
              <Save class="w-4 h-4 mr-1" />
              Save
            </button>
          
            <button 
              v-if="timesheet.workflow_state === 'Rejected' && timesheet.docstatus < 2 && timesheet.emp_user_id == session.user"
              class="btn btn-sm bg-red-500 hover:bg-red-600 text-white"
              @click="cancelDocument"
              :disabled="isLoading.cancelDocument"
            >
              <X class="w-4 h-4 mr-1" />
              Cancel
            </button>
            <button 
              v-for="transition in transitions" 
              v-show= "timesheet.docstatus < 2"
              :key="transition.name"
              @click="handleTransition(transition)"
              :disabled="isLoading.submit"
              :class="{
                'btn btn-sm': true,
                'bg-blue-500 hover:bg-blue-600': transition.action === 'Request Approve',
                'bg-green-500 hover:bg-green-600': transition.action === 'Approve',
                'bg-red-500 hover:bg-red-600': transition.action === 'Reject',
                'opacity-50 cursor-not-allowed': isLoading.submit,
                'text-white': true
              }"
            >
              {{ transition.action }}
            </button>
          </div>
        </div>
      </div>

      <!-- Main content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left column - Timesheet Info -->
        <div class="lg:col-span-2">
          <div class="bg-base-100 p-6 rounded-lg shadow mb-6">
            <h2 class="text-lg font-semibold mb-4 flex items-center">
              <Clock class="w-5 h-5 mr-2" />
              Timesheet Information
            </h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="label">
                  <span class="label-text">Employee</span>
                </label>
                <input 
                  type="text" 
                  v-model="timesheet.employee_name"  
                  class="input input-bordered w-full" 
                  disabled
                  placeholder="Employee ID"
                />
              </div>
              
              <div>
                <label class="label">
                  <span class="label-text">Year</span>
                </label>
                <select 
                  v-model="timesheet.year" 
                  class="select select-bordered w-full"
                  :disabled="!isEditable || !isNewTimesheet"
                >
                  <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
                </select>
              </div>
              
              <div>
                <label class="label">
                  <span class="label-text">Month</span>
                </label>
                <select 
                  v-model="timesheet.month" 
                  class="select select-bordered w-full"
                  :disabled="!isEditable || !isNewTimesheet"
                >
                  <option v-for="month in months" :key="month.value" :value="month.value">
                    {{ month.label }}
                  </option>
                </select>
              </div>
              
              <div class="flex items-end">
                <button 
                  class="btn btn-primary btn-sm w-full"
                  @click="getTimesheetData"
                  :disabled="isLoading.fetch || !isEditable"
                >
                  <Calendar class="w-4 h-4 mr-1" />
                  Get Data
                </button>
              </div>
            </div>
          </div>
          
          <!-- Timesheet Items -->
          <div class="bg-base-100 p-6 rounded-lg shadow mb-6">
            <h2 class="text-lg font-semibold mb-4 flex items-center">
              <Calendar class="w-5 h-5 mr-2" />
              Timesheet Entries
            </h2>
            
            <div class="overflow-x-auto">
              <table class="table w-full">
                <thead>
                  <tr class="bg-base-200">
                    <th class="whitespace-nowrap">From Time</th>
                    <th class="whitespace-nowrap">To Time</th>
                    <th class="whitespace-nowrap text-center">Working Hours</th>
                    <th class="whitespace-nowrap">Project Code</th>
                    <th class="whitespace-nowrap">Customer</th>
                    <th class="whitespace-nowrap">From Doc</th>
                    <th class="whitespace-nowrap">Doc Number</th>
                   
                  </tr>
                </thead>
                <tbody>
                  <template v-if="isLoading.fetch">
                    <tr v-for="i in 3" :key="i">
                      <td colspan="7" class="text-center">
                        <div class="skeleton h-4 w-full"></div>
                      </td>
                    </tr>
                  </template>
                  <template v-else-if="timesheet.time_sheets && timesheet.time_sheets.length">
                    <tr v-for="(item, index) in timesheet.time_sheets" :key="index" class="hover border-b">
                      <td class="whitespace-nowrap text-sm">{{ formatDate(item.from_time) }}</td>
                      <td class="whitespace-nowrap text-sm">{{ formatDate(item.to_time) }}</td>
                      <td class="whitespace-nowrap text-sm text-center font-medium">{{ formatDuration(item.working_hours, { hourOnly: true }) }}</td>
                      <td class="whitespace-nowrap text-sm">
                        <span class="font-medium">{{ item.project_code }}</span>
                      </td>
                      <td class="whitespace-nowrap text-sm max-w-[200px] truncate">{{ item.customer_name }}</td>
                      <td class="whitespace-nowrap text-sm">{{ item.link_from_doc }}</td>
                      <td class="whitespace-nowrap text-sm">
                        <span class="font-medium text-blue-600">{{ item.doc_number }}</span>
                      </td>
                     
                    </tr>
                  </template>
                  <template v-else>
                    <tr>
                      <td colspan="7" class="text-center py-8 text-gray-500">
                        <div class="flex flex-col items-center gap-2">
                          <Calendar class="w-6 h-6" />
                          <p>No timesheet entries found.</p>
                          <p class="text-sm">Use the "Get Data" button to fetch entries.</p>
                        </div>
                      </td>
                    </tr>
                  </template>
                </tbody>
                <tfoot v-if="timesheet.time_sheets && timesheet.time_sheets.length">
                  <tr class="bg-base-200 font-medium">
                    <td colspan="2" class="text-right">Total Working Hours:</td>
                    <td class="text-center">{{ formatDuration(totalHours, { hourOnly: true }) }}</td>
                    <td colspan="4"></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
        
        <!-- Right column - Status Info -->
        <div class="lg:col-span-1">
          <div class="bg-base-100 p-6 rounded-lg shadow mb-6">
            <h2 class="text-lg font-semibold mb-4">Status Information</h2>
            
            <div class="stats stats-vertical shadow w-full">
              <div class="stat">
                <div class="stat-title">Status</div>
                <div class="stat-value text-sm">
                  <div 
                    class="badge badge-lg" 
                    :class="{
                      'badge-warning': timesheet.workflow_state === 'Draft',
                      'badge-success': timesheet.workflow_state === 'Approved',
                      'badge-error': timesheet.workflow_state === 'Rejected'
                    }"
                  >
                    {{ timesheet.workflow_state || 'Draft' }}
                  </div>
                </div>
              </div>
              
              <div class="stat">
                <div class="stat-title">Total Working Hours</div>
                <div class="stat-value text-primary flex items-center text-2xl">
                  <Clock class="w-5 h-5 mr-2" />
                  {{ formatDuration(totalHours, { hourOnly: true }) }} 
                </div>
              </div>
              
              <div class="stat" v-if="!isNewTimesheet">
                <div class="stat-title">Document ID</div>
                <div class="stat-value text-sm font-mono">{{ timesheet.name }}</div>
              </div>
            </div>
          </div>
          
          <!-- Remove Actions section and keep only Back button -->
          <div class="bg-base-100 p-6 rounded-lg shadow mb-6" v-if="!isNewTimesheet">
            <button 
              class="btn btn-ghost w-full" 
              @click="goBack"
            >
              <ArrowLeft class="w-4 h-4 mr-1" />
              Back to List
            </button>
          </div>
        </div>
      </div>
    </div>
  </UserLayout>
</template>

<style scoped>
.badge-lg {
  font-size: 0.875rem;
  height: 1.5rem;
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}
</style> 