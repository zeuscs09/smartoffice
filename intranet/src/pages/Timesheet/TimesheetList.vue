<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { Plus } from 'lucide-vue-next'
import UserLayout from '@/layouts/userLayout.vue'
import Pagination from '@/components/Pagination.vue'
import TimesheetTable from '@/components/TimesheetTable.vue'
import { useTimesheetStore } from '@/stores/timesheetStore'


// Add years computed property
const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => (currentYear - 2 + i).toString())
})

const router = useRouter()

const timesheetStore = useTimesheetStore()
timesheetStore.pageSize = 10

// Storage key for criteria
const STORAGE_KEY = 'timesheet-criteria'

// UI state
const showFilter = ref(false)
const filterForm = reactive({
  year: new Date().getFullYear().toString(),
  month: '',
  status: '',
  employee: ''
})
const pageSize = ref(10)

// Computed properties for data access
const timesheets = computed(() => timesheetStore.data)
const isLoading = computed(() => timesheetStore.documentsResource.loading)
const error = computed(() => timesheetStore.documentsResource.error)
const displayedItemsCount = computed(() => timesheetStore.data.length)
const totalItems = computed(() => timesheetStore.documentsResource.data?.total || 0)

// Save and load criteria functions
const saveCriteria = () => {
  const criteria = {
    filterForm: { ...filterForm },
    pageSize: pageSize.value,
    showFilter: showFilter.value,
    currentPage: timesheetStore.currentPage,
    sortField: timesheetStore.sortField,
    sortOrder: timesheetStore.sortOrder
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(criteria))
}

const loadCriteria = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const criteria = JSON.parse(saved)
      
      // Set local state
      Object.assign(filterForm, criteria.filterForm)
      pageSize.value = criteria.pageSize || 10
      showFilter.value = criteria.showFilter || false
      
      // Set store state
      timesheetStore.yearFilter = filterForm.year
      timesheetStore.monthFilter = filterForm.month
      timesheetStore.statusFilter = filterForm.status
      timesheetStore.pageSize = pageSize.value
      timesheetStore.sortField = criteria.sortField || 'posting_date'
      timesheetStore.sortOrder = criteria.sortOrder || 'desc'
      
      // Fetch data with saved page
      timesheetStore.fetchAll(criteria.currentPage || 1)
    } else {
      // Use defaults if no saved criteria
      timesheetStore.pageSize = pageSize.value
      timesheetStore.fetchAll(1)
    }
  } catch (err) {
    console.error('Error loading criteria:', err)
    timesheetStore.pageSize = pageSize.value
    timesheetStore.fetchAll(1)
  }
}

// Filter actions
const applyFilters = () => {
  timesheetStore.yearFilter = filterForm.year
  timesheetStore.monthFilter = filterForm.month
  timesheetStore.statusFilter = filterForm.status
  timesheetStore.fetchAll(1)
  saveCriteria()
}

const clearFilters = () => {
  filterForm.year = new Date().getFullYear().toString()
  filterForm.month = ''
  filterForm.status = ''
  filterForm.employee = ''
  timesheetStore.yearFilter = filterForm.year
  timesheetStore.monthFilter = ''
  timesheetStore.statusFilter = ''
  timesheetStore.fetchAll(1)
  saveCriteria()
}

// Handle sorting
const handleSort = (field: string) => {
  if (timesheetStore.sortField === field) {
    timesheetStore.sortOrder = timesheetStore.sortOrder === 'asc' ? 'desc' : 'asc'
  } else {
    timesheetStore.sortField = field
    timesheetStore.sortOrder = 'asc'
  }
  timesheetStore.fetchAll(1)
  saveCriteria()
}

// Pagination handlers
const handlePageSizeChange = (newSize: number) => {
  pageSize.value = newSize
  timesheetStore.pageSize = newSize
  timesheetStore.fetchAll(1)
  saveCriteria()
}

// Navigation
const viewTimesheet = (name: string) => {
  saveCriteria()
  router.push({ name: 'TimesheetDetail', params: { id: name } })
}

const createTimesheet = () => {
  saveCriteria()
  router.push({ name: 'TimesheetDetail', params: { id: 'new' } })
}

// Toggle filter visibility
const toggleFilter = () => {
  showFilter.value = !showFilter.value
  saveCriteria()
}

// Initial data load
onMounted(() => {
  loadCriteria()
})

// External refresh function
window.refresh_timesheet_table = () => {
  timesheetStore.fetchAll(timesheetStore.currentPage)
  saveCriteria()
}

// Watch for changes to save criteria
watch(() => timesheetStore.currentPage, () => {
  saveCriteria()
})

watch(pageSize, (newSize) => {
  console.log('Page size changed to:', newSize)
  saveCriteria()
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

// Available months for filtering
const months = [
  { value: '1', label: 'January' },
  { value: '2', label: 'February' },
  { value: '3', label: 'March' },
  { value: '4', label: 'April' },
  { value: '5', label: 'May' },
  { value: '6', label: 'June' },
  { value: '7', label: 'July' },
  { value: '8', label: 'August' },
  { value: '9', label: 'September' },
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
      <div v-if="showFilter" class="flex items-center gap-2 mb-4">
        <input 
          type="text" 
          placeholder="Search..." 
          class="input input-bordered w-64" 
          v-model="filterForm.employee" 
          @input="applyFilters"
        />
        <select 
          class="select select-bordered w-32" 
          v-model="filterForm.status"
          @change="applyFilters"
        >
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <select 
          class="select select-bordered w-28" 
          v-model="filterForm.year"
          @change="applyFilters"
        >
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
        <select 
          class="select select-bordered w-36" 
          v-model="filterForm.month"
          @change="applyFilters"
        >
          <option value="">All Months</option>
          <option v-for="month in months" :key="month.value" :value="month.value">
            {{ month.label }}
          </option>
        </select>
      </div>

      <!-- Timesheets Table -->
      <div class="overflow-x-auto mt-4">
        <TimesheetTable
          :data="timesheets"
          :loading="isLoading"
          :error="error"
          :sort-field="timesheetStore.sortField"
          :sort-order="timesheetStore.sortOrder"
          :sortable="true"
          @sort="handleSort"
          @view="viewTimesheet"
        />
      </div>

      <!-- Pagination -->
      <Pagination 
        v-if="timesheets.length > 0" 
        :current-page="timesheetStore.currentPage"
        :is-first-page="timesheetStore.isFirstPage" 
        :is-last-page="timesheetStore.isLastPage"
        :page-size="pageSize" 
        :displayed-items-count="displayedItemsCount" 
        :total-items="totalItems"
        @previous="timesheetStore.previousPage()" 
        @next="timesheetStore.nextPage()"
        @update:page-size="handlePageSizeChange" 
      />

      <!-- No data message -->
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

      <!-- Error message -->
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 