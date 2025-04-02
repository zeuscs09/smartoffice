<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { Calendar, Clock, Plus, Search, Filter } from 'lucide-vue-next'
import UserLayout from '@/layouts/userLayout.vue'
import Pagination from '@/components/Pagination.vue'
import TimesheetTable from '@/components/TimesheetTable.vue'
import { useTimesheetList } from '@/composables/useTimesheetList'
import type { TimesheetFilters } from '@/types/timesheet'

const router = useRouter()
const { showToast } = useToast()

// UI state
const showFilter = ref(false)

// ใช้ composable แทน store
const {
  timesheets,
  isLoading,
  error,
  filters,
  pagination,
  fetchTimesheets,
  updateFilters,
  resetFilters,
  nextPage,
  prevPage,
  goToPage
} = useTimesheetList()

// Sorting state
const sortState = reactive({
  field: 'posting_date',
  order: 'desc'
})

// Filter state สำหรับ UI
const filterForm = reactive({
  year: new Date().getFullYear().toString(),
  month: '',
  status: '',
  employee: ''
})

// ฟังก์ชันช่วยจัดรูปแบบต่างๆ - ย้ายจากบล็อก script ด้านล่าง
function getStatusText(workflow_state: string) {
  return workflow_state
}

function getStatusVariant(workflow_state: string) {
  switch(workflow_state) {
    case 'Draft': return 'warning'
    case 'Approval Review': return 'warning'
    case 'Rejected': return 'danger'
    case 'Approved': return 'success'
    default: return 'secondary'
  }
}

function formatHours(hours: number) {
  return `${hours} hrs`
}

// แปลงค่าจาก filter form เป็น TimesheetFilters
const convertToTimesheetFilters = () => {
  const newFilters: Partial<TimesheetFilters> = {}
  
  // ถ้ามีการเลือกทั้งปีและเดือน จะสร้าง from_date และ to_date
  if (filterForm.year && filterForm.month) {
    const year = parseInt(filterForm.year)
    const month = parseInt(filterForm.month) - 1 // JavaScript months are 0-11
    
    // สร้างวันแรกของเดือน
    const fromDate = new Date(year, month, 1)
    newFilters.from_date = fromDate.toISOString().split('T')[0]
    
    // สร้างวันสุดท้ายของเดือน
    const toDate = new Date(year, month + 1, 0)
    newFilters.to_date = toDate.toISOString().split('T')[0]
  } 
  // ถ้ามีแค่ปี จะกำหนดเป็นทั้งปี
  else if (filterForm.year) {
    const year = parseInt(filterForm.year)
    
    // วันแรกของปี
    newFilters.from_date = `${year}-01-01`
    
    // วันสุดท้ายของปี
    newFilters.to_date = `${year}-12-31`
  }
  
  // ถ้ามีการกรองตาม status
  if (filterForm.status) {
    // แปลงจากค่า docstatus (0, 1, 2) เป็น string enum ('Draft', 'Submitted', 'Cancelled')
    if (filterForm.status === '0') {
      newFilters.status = 'Draft'
    } else if (filterForm.status === '1') {
      newFilters.status = 'Submitted'
    } else if (filterForm.status === '2') {
      newFilters.status = 'Cancelled'
    }
  }
  
  // ถ้ามีการกรอง employee
  if (filterForm.employee) {
    newFilters.employee = filterForm.employee
  }
  
  return newFilters
}

// Available years for filtering
const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => (currentYear - 2 + i).toString())
})

// Available months for filtering
const months = [
  { value: '01', label: 'January' },
  { value: '02', label: 'February' },
  { value: '03', label: 'March' },
  { value: '04', label: 'April' },
  { value: '05', label: 'May' },
  { value: '06', label: 'June' },
  { value: '07', label: 'July' },
  { value: '08', label: 'August' },
  { value: '09', label: 'September' },
  { value: '10', label: 'October' },
  { value: '11', label: 'November' },
  { value: '12', label: 'December' }
]

// Status options for filtering
const statusOptions = [
  { value: '', label: 'All' },
  { value: '0', label: 'Draft' },
  { value: '1', label: 'Submitted' },
  { value: '2', label: 'Cancelled' }
]

// Toggle filter visibility
const toggleFilter = () => {
  showFilter.value = !showFilter.value
}

// Apply filters
const applyFilters = () => {
  const convertedFilters = convertToTimesheetFilters()
  updateFilters(convertedFilters)
}

// Reset filters
const clearFilters = () => {
  filterForm.year = new Date().getFullYear().toString()
  filterForm.month = ''
  filterForm.status = ''
  filterForm.employee = ''
  resetFilters()
}

// Navigate to timesheet detail page
const viewTimesheet = (name: string) => {
  router.push({ name: 'TimesheetDetail', params: { id: name } })
}

// Create new timesheet
const createTimesheet = () => {
  router.push({ name: 'TimesheetDetail', params: { id: 'new' } })
}

// Handle sorting
const handleSort = (field: string) => {
  if (sortState.field === field) {
    sortState.order = sortState.order === 'asc' ? 'desc' : 'asc'
  } else {
    sortState.field = field
    sortState.order = 'asc'
  }
  
  // อัปเดตการเรียงลำดับและโหลดข้อมูลใหม่
  updateFilters({
    ...convertToTimesheetFilters(),
    // สร้าง orderBy โดยใช้ค่าจาก sortState (ส่งเป็น option ไป)
    orderBy: `${sortState.field} ${sortState.order}`
  })
}

// Handle page size change
const handlePageSizeChange = (newSize: number) => {
  pagination.limit = newSize
  goToPage(1)
}

// Computed properties for pagination
const displayedItemsCount = computed(() => 
  timesheets.value.length || 0
)

const totalItems = computed(() => 
  pagination.total || 0
)

// Load data when component is mounted
onMounted(() => {
  // ตั้งค่า filter เริ่มต้นเป็นปีปัจจุบัน
  applyFilters()
})

// Add refresh function for external calls
window.refresh_timesheet_table = () => {
  fetchTimesheets()
}

// Watch for sorting changes
watch([sortState.field, sortState.order], () => {
  // อัปเดตการเรียงลำดับและโหลดข้อมูลใหม่
  updateFilters({
    ...convertToTimesheetFilters(),
    // สร้าง orderBy โดยใช้ค่าจาก sortState (ส่งเป็น option ไป)
    orderBy: `${sortState.field} ${sortState.order}`
  })
})
</script>

<template>
  <UserLayout>
    <div class="mx-auto p-4">
      <div class="flex justify-between items-center mb-4">
        <div class="breadcrumbs text-sm">
          <ul>
            <li><a @click="router.push('/')">Home</a></li>
            <li>Timesheet</li>
          </ul>
        </div>
        <div class="flex gap-2">
          <!-- Create button -->
          <button 
            class="btn btn-ghost btn-sm tooltip tooltip-bottom" 
            data-tip="Create Timesheet"
            @click="createTimesheet"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </button>

          <!-- Filter button -->
          <button 
            class="btn btn-sm" 
            :class="{ 'btn-ghost': !showFilter }" 
            @click="toggleFilter"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div v-if="showFilter" class="bg-base-200 p-4 rounded-lg mb-4 animate-fadeIn">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="label">
              <span class="label-text">Year</span>
            </label>
            <select 
              v-model="filterForm.year" 
              class="select select-bordered w-full"
            >
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
          <div>
            <label class="label">
              <span class="label-text">Month</span>
            </label>
            <select 
              v-model="filterForm.month" 
              class="select select-bordered w-full"
            >
              <option value="">All Months</option>
              <option v-for="month in months" :key="month.value" :value="month.value">
                {{ month.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">
              <span class="label-text">Status</span>
            </label>
            <select 
              v-model="filterForm.status" 
              class="select select-bordered w-full"
            >
              <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">
              <span class="label-text">Employee</span>
            </label>
            <input 
              v-model="filterForm.employee" 
              class="input input-bordered w-full"
              placeholder="Employee ID"
            />
          </div>
          <div class="md:col-span-4 flex gap-2">
            <button 
              class="btn btn-primary btn-sm"
              @click="applyFilters"
            >
              <Search class="w-4 h-4 mr-1" />
              Search
            </button>
            <button 
              class="btn btn-ghost btn-sm"
              @click="clearFilters"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      <!-- Timesheets Table -->
      <div class="overflow-x-auto bg-base-100 rounded-lg shadow mt-4">
        <TimesheetTable
          :data="timesheets"
          :loading="isLoading"
          :error="error"
          :sort-field="sortState.field"
          :sort-order="sortState.order"
          :sortable="true"
          @sort="handleSort"
          @view="viewTimesheet"
        >
       
        </TimesheetTable>
      </div>
{{ pagination }}
      <!-- Pagination -->
      <Pagination 
        v-if="timesheets.length > 0" 
        :current-page="pagination.currentPage"
        :is-first-page="pagination.start === 0" 
        :is-last-page="pagination.start + pagination.limit >= pagination.total"
        :page-size="pagination.limit" 
        :displayed-items-count="displayedItemsCount" 
        :total-items="totalItems"
        @previous="prevPage" 
        @next="nextPage"
        @update:page-size="handlePageSizeChange" 
      />

      <!-- ข้อความแสดงเมื่อไม่มีข้อมูล -->
      <div 
        v-if="!isLoading && !error && timesheets.length === 0" 
        class="text-center p-8 bg-base-100 rounded-lg shadow mt-4"
      >
        <div class="text-lg font-medium">No timesheets found</div>
        <p class="text-base-content/70 mt-2">Try adjusting your filters or create a new timesheet</p>
        <button 
          class="btn btn-primary mt-4"
          @click="createTimesheet"
        >
          <Plus class="w-4 h-4 mr-1" />
          Create Timesheet
        </button>
      </div>

      <!-- แสดงข้อผิดพลาด -->
      <div 
        v-if="error" 
        class="alert alert-error mt-4"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
            d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error.message }}</span>
      </div>
    </div>
  </UserLayout>
</template>

<style scoped>
.animate-fadeIn {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 