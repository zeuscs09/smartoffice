<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { Calendar, Clock, Plus, Search, Filter } from 'lucide-vue-next'
import UserLayout from '@/layouts/userLayout.vue'
import Pagination from '@/components/Pagination.vue'
import TimesheetTable from '@/components/TimesheetTable.vue'
import { useTimesheetStore } from '@/stores/timesheetStore'

const router = useRouter()
const { showToast } = useToast()
const timesheetStore = useTimesheetStore()

// UI state
const showFilter = ref(false)

// Filter state
const filters = ref({
  year: timesheetStore.yearFilter,
  month: timesheetStore.monthFilter,
  status: timesheetStore.statusFilter
})

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
  timesheetStore.yearFilter = filters.value.year
  timesheetStore.monthFilter = filters.value.month
  timesheetStore.statusFilter = filters.value.status
  timesheetStore.fetchAll(1)
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
  if (timesheetStore.sortField === field) {
    timesheetStore.sortOrder = timesheetStore.sortOrder === 'asc' ? 'desc' : 'asc'
  } else {
    timesheetStore.sortField = field
    timesheetStore.sortOrder = 'asc'
  }
  timesheetStore.fetchAll(1)
}

// Handle page size change
const handlePageSizeChange = (newSize: number) => {
  timesheetStore.pageSize = newSize
  timesheetStore.fetchAll(1)
}

// Computed properties for pagination
const displayedItemsCount = computed(() => 
  timesheetStore.data.length || 0
)

const totalItems = computed(() => 
  timesheetStore.documentsResource.data?.total || 0
)

onMounted(() => {
  timesheetStore.fetchAll()
})

// Add refresh function for external calls
window.refresh_timesheet_table = () => {
  timesheetStore.refresh()
}
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
              v-model="filters.year" 
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
              v-model="filters.month" 
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
              v-model="filters.status" 
              class="select select-bordered w-full"
            >
              <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <div class="flex items-end">
            <button 
              class="btn btn-primary btn-sm w-full"
              @click="applyFilters"
            >
              <Search class="w-4 h-4 mr-1" />
              Search
            </button>
          </div>
        </div>
      </div>

      <!-- Timesheets Table -->
      <div class="overflow-x-auto bg-base-100 rounded-lg shadow mt-4">
        <TimesheetTable
          :data="timesheetStore.data"
          :loading="timesheetStore.documentsResource.loading"
          :error="timesheetStore.documentsResource.error"
          :sort-field="timesheetStore.sortField"
          :sort-order="timesheetStore.sortOrder"
          :sortable="true"
          @sort="handleSort"
          @view="viewTimesheet"
        />
      </div>

      <!-- Pagination -->
      <Pagination 
        v-if="timesheetStore.data.length > 0" 
        :current-page="timesheetStore.currentPage"
        :is-first-page="timesheetStore.isFirstPage" 
        :is-last-page="timesheetStore.isLastPage"
        :page-size="timesheetStore.pageSize" 
        :displayed-items-count="displayedItemsCount" 
        :total-items="totalItems"
        @previous="timesheetStore.previousPage" 
        @next="timesheetStore.nextPage"
        @update:page-size="handlePageSizeChange" 
      />
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