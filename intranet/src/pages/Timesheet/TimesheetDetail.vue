<script setup lang="ts">
import { ref, onMounted, computed, watch, inject } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { Calendar, Clock, Save, ArrowLeft, Plus, Trash2, Check, X } from 'lucide-vue-next'
import UserLayout from '@/layouts/userLayout.vue'
import { session } from '@/data/session'

const formatDuration = inject('formatDuration') as (duration: number, options?: { hourOnly?: boolean }) => string
const router = useRouter()
const route = useRoute()

// เปลี่ยนวิธีการใช้งาน toast ตามตัวอย่างใน AdvanceEntryDetail.vue
const toast = useToast()

// Get timesheet ID from route params
const timesheetId = computed(() => route.params.id as string)
const isNewTimesheet = computed(() => timesheetId.value === 'new')
const employee = ref({
  name: '',
  employee_name: ''
})
// Timesheet data
const timesheet = ref({
  name: '',
  employee: '',
  employee_name: '',
  year: new Date().getFullYear().toString(),
  month: '',
  month_value: '',
  time_sheets: [],
  docstatus: 0
})

// Available years for selection
const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => (currentYear - 2 + i).toString())
})

// Available months for selection
const months = [
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

// Resource for fetching timesheet data
const timesheetResource = createResource({
  url: 'smartoffice.api.timesheet.get_timesheet',
  auto: false,
  onSuccess(data) {
    if (data) {
      timesheet.value = data
    }
  },
  onError(error) {
    // เปลี่ยนจาก showToast() เป็นการใช้ toast.error()
    toast.error(error.message || 'Failed to fetch timesheet')
  }
})

// Resource for saving timesheet
const saveTimesheetResource = createResource({
  url: 'smartoffice.api.timesheet.save_timesheet',
  onSuccess(data) {
    // เปลี่ยนจาก showToast() เป็นการใช้ toast.success()
    toast.success('Timesheet saved successfully')
    if (isNewTimesheet.value) {
      router.replace({ name: 'TimesheetDetail', params: { id: data.name } })
    } else {
      fetchTimesheet()
    }
  },
  onError(error) {
    // เปลี่ยนจาก showToast() เป็นการใช้ toast.error()
    toast.error(error.message || 'Failed to save timesheet')
  }
})

// Resource for submitting timesheet
const submitTimesheetResource = createResource({
  url: 'smartoffice.api.timesheet.submit_timesheet',
  onSuccess() {
    toast.success('Timesheet submitted successfully')
    fetchTimesheet()
  },
  onError(error) {
    toast.error(error.message || 'Failed to submit timesheet')
  }
})

// Resource for cancelling timesheet
const cancelTimesheetResource = createResource({
  url: 'smartoffice.api.timesheet.cancel_timesheet',
  onSuccess() {
    toast.success('Timesheet cancelled successfully')
    fetchTimesheet()
  },
  onError(error) {
    toast.error(error.message || 'Failed to cancel timesheet')
  }
})

// Resource for fetching timesheet data
const fetchDataResource = createResource({
  url: 'smartoffice.smart_office.doctype.smo_timesheet.smo_timesheet.get_timesheets',
  onSuccess(data) {
    console.log(data)
    if (data) {
      timesheet.value.time_sheets = data
      console.log(timesheet.value.time_sheets)
    }
  },
  onError(error) {
    toast.error(error.message || 'Failed to fetch timesheet data')
  }
})

// Fetch timesheet data
const fetchTimesheet = () => {
  if (!isNewTimesheet.value) {
    timesheetResource.submit({ name: timesheetId.value })
  }
}

// Save timesheet
const saveTimesheet = () => {
  if (!timesheet.value.employee) {
    toast.error('Please select an employee')
    return
  }

  if (!timesheet.value.year) {
    toast.error('Please select a year')
    return
  }

  if (!timesheet.value.month) {
    toast.error('Please select a month')
    return
  }

  // Set month_value based on selected month
  const selectedMonth = months.find(m => m.value === timesheet.value.month)
  if (selectedMonth) {
    timesheet.value.month_value = selectedMonth.number
  }

  saveTimesheetResource.submit({
    timesheet: timesheet.value
  })
}

// Submit timesheet
const submitTimesheet = () => {
  if (!timesheet.value.name) {
    toast.error('Please save the timesheet first')
    return
  }

  submitTimesheetResource.submit({
    name: timesheet.value.name
  })
}

// Cancel timesheet
const cancelTimesheet = () => {
  if (!timesheet.value.name) {
    toast.error('Please save the timesheet first')
    return
  }

  cancelTimesheetResource.submit({
    name: timesheet.value.name
  })
}

// Get timesheet data
const getTimesheetData = () => {
  if (!timesheet.value.employee || !timesheet.value.year || !timesheet.value.month) {
    toast.error('Please select employee, year and month')
    return
  }

  // Set month_value based on selected month
  const selectedMonth = months.find(m => m.value === timesheet.value.month)
  if (selectedMonth) {
    timesheet.value.month_value = selectedMonth.number
  }

  fetchDataResource.submit({
    employee: timesheet.value.employee,
    year: timesheet.value.year,
    month: selectedMonth.value
  })
}

// Format date for display
const formatDate = (dateString: string) => {
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
const getEmployee = async () => {
    
    try {
      const response = await fetch('/api/method/frappe.client.get_list', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          doctype: 'Employee',
          fields: ['name', 'employee_name'],
          filters: [['user_id', '=', session.user]],
          order_by: 'employee_name asc'
        })
      })

      const data = await response.json()
      
      employee.value = data.message[0] || []
      console.log(employee.value)
    } catch (err) {
      console.error('Error fetching expense types:', err)
    }
  }

// Calculate total hours
const totalHours = computed(() => {
  if (!timesheet.value.time_sheets || !timesheet.value.time_sheets.length) return 0
  
  return timesheet.value.time_sheets.reduce((total, item: any) => {
    const hours = item.working_hours ? parseFloat(item.working_hours) : 0
    return total + hours
  }, 0)
})

// Check if timesheet is editable
const isEditable = computed(() => {
  return isNewTimesheet.value || timesheet.value.docstatus === 0
})

// Get status text
const statusText = computed(() => {
  switch (timesheet.value.docstatus) {
    case 0: return 'Draft'
    case 1: return 'Submitted'
    case 2: return 'Cancelled'
    default: return 'Unknown'
  }
})

// Go back to timesheet list
const goBack = () => {
  router.push({ name: 'TimesheetList' })
}

onMounted(async () => {
  fetchTimesheet()
  await getEmployee()
  // Set current month as default for new timesheet
  if (isNewTimesheet.value) {
    console.log(employee.value)
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
      <!-- Breadcrumbs and actions -->
      <div class="flex justify-between items-center mb-4">
        <div class="breadcrumbs text-sm">
          <ul>
            <li><a @click="router.push('/')">Home</a></li>
            <li><a @click="router.push({ name: 'TimesheetList' })">Timesheet</a></li>
            <li>{{ isNewTimesheet ? 'New Timesheet' : timesheet.name }}</li>
          </ul>
        </div>
        
        <div class="flex gap-2">
          <button 
            v-if="isEditable" 
            class="btn btn-primary btn-sm" 
            @click="saveTimesheet"
            :disabled="saveTimesheetResource.loading"
          >
            <Save class="w-4 h-4 mr-1" />
            Save
          </button>
          
          <button 
            v-if="!isNewTimesheet && timesheet.docstatus === 0" 
            class="btn btn-success btn-sm" 
            @click="submitTimesheet"
            :disabled="submitTimesheetResource.loading"
          >
            <Check class="w-4 h-4 mr-1" />
            Submit
          </button>
          
          <button 
            v-if="!isNewTimesheet && timesheet.docstatus === 1" 
            class="btn btn-error btn-sm" 
            @click="cancelTimesheet"
            :disabled="cancelTimesheetResource.loading"
          >
            <X class="w-4 h-4 mr-1" />
            Cancel
          </button>
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
                  :disabled="!isEditable || isNewTimesheet"
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
                  :disabled="fetchDataResource.loading || !isEditable"
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
                  <tr>
                    <th>From Time</th>
                    <th>To Time</th>
                    <th>Working Hours</th>
                    <th>From Doc</th>
                    <th>Doc Number</th>
                    <th>Project Code</th>
                    <th>Customer</th>
                  </tr>
                </thead>
                <tbody>
                  <template v-if="fetchDataResource.loading">
                    <tr v-for="i in 3" :key="i">
                      <td colspan="7" class="text-center">
                        <div class="skeleton h-4 w-full"></div>
                      </td>
                    </tr>
                  </template>
                  <template v-else-if="timesheet.time_sheets && timesheet.time_sheets.length">
                    <tr v-for="(item, index) in timesheet.time_sheets" :key="index" class="hover">
                      <td>{{ formatDate(item.from_time) }}</td>
                      <td>{{ formatDate(item.to_time) }}</td>
                      <td>{{ formatDuration(item.working_hours, { hourOnly: true }) }} </td>
                      <td>{{ item.link_from_doc }}</td>
                      <td>{{ item.doc_number }}</td>
                      <td>{{ item.project_code }}</td>
                      <td>{{ item.customer_name }}</td>
                    </tr>
                  </template>
                  <template v-else>
                    <tr>
                      <td colspan="7" class="text-center py-4">
                        No timesheet entries found. Use the "Get Data" button to fetch entries.
                      </td>
                    </tr>
                  </template>
                </tbody>
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
                      'badge-warning': timesheet.docstatus === 0,
                      'badge-success': timesheet.docstatus === 1,
                      'badge-error': timesheet.docstatus === 2
                    }"
                  >
                    {{ statusText }}
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
          
          <div class="bg-base-100 p-6 rounded-lg shadow mb-6" v-if="!isNewTimesheet">
            <h2 class="text-lg font-semibold mb-4">Actions</h2>
            
            <div class="flex flex-col gap-2">
              <button 
                v-if="isEditable" 
                class="btn btn-primary btn-sm w-full" 
                @click="saveTimesheet"
                :disabled="saveTimesheetResource.loading"
              >
                <Save class="w-4 h-4 mr-1" />
                Save
              </button>
              
              <button 
                v-if="timesheet.docstatus === 0" 
                class="btn btn-success btn-sm w-full" 
                @click="submitTimesheet"
                :disabled="submitTimesheetResource.loading"
              >
                <Check class="w-4 h-4 mr-1" />
                Submit
              </button>
              
              <button 
                v-if="timesheet.docstatus === 1" 
                class="btn btn-error btn-sm w-full" 
                @click="cancelTimesheet"
                :disabled="cancelTimesheetResource.loading"
              >
                <X class="w-4 h-4 mr-1" />
                Cancel
              </button>
              
              <button 
                class="btn btn-ghost btn-sm w-full" 
                @click="goBack"
              >
                <ArrowLeft class="w-4 h-4 mr-1" />
                Back to List
              </button>
            </div>
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