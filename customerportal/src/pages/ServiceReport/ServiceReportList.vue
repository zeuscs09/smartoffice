<template>
  <CustomerLayout>
    <div class="mx-auto p-4">
      <!-- Header -->
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-2xl font-bold">Service Report</h1>
        <div class="flex gap-2">
          <button 
            class="btn btn-sm btn-success" 
            @click="handleApprove" 
            :disabled="!selectedReports.length || isProcessing"
          >
            <span v-if="isProcessing" class="loading loading-spinner loading-xs"></span>
            Approve
          </button>
          <button class="btn btn-sm btn-error" @click="openRejectModal" :disabled="!selectedReports.length">
            Reject
          </button>
          <button class="btn btn-sm" :class="{ 'btn-ghost': !showFilter }" @click="toggleFilter">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Filter Section -->
      <div v-if="showFilter" class="mb-4 p-4 bg-base-200 rounded-lg">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Search</span>
            </label>
            <input type="text" v-model="serviceReportStore.searchQuery" @input="handleSearchChange($event.target.value)"
              placeholder="Search..." class="input input-bordered w-full" />
          </div>
          <div class="form-control">
            <label class="label">
              <span class="label-text">Start Date</span>
            </label>
            <input type="date" v-model="serviceReportStore.startDate" @change="handleDateRangeChange"
              class="input input-bordered w-full" />
          </div>
          <div class="form-control">
            <label class="label">
              <span class="label-text">End Date</span>
            </label>
            <input type="date" v-model="serviceReportStore.endDate" @change="handleDateRangeChange"
              class="input input-bordered w-full" />
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button class="btn btn-primary" @click="applyFiltersAndRefresh">Search</button>
        </div>
      </div>

      <!-- Table Section -->
      <div class="overflow-x-auto mt-4">
        <table class="table w-full">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox"
                  class="checkbox" 
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th>Document No.</th>
              <th>Project Code</th>
              <th>Project Name</th>
              <th>WorkDate</th>
              <th>Duration</th>
              <th>Owner</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="serviceReportStore.isLoading">
              <td colspan="8" class="text-center">
                <span class="loading loading-spinner loading-md"></span>
              </td>
            </tr>
            <tr v-else v-for="report in serviceReportStore.reports" :key="report.name">
              <td>
                <input 
                  type="checkbox"
                  class="checkbox"
                  :checked="selectedReports.includes(report.name)"
                  @change="(e) => toggleReport(report.name)"
                />
              </td>
              <td>{{ report.name }}</td>
              <td>{{ report.project_code }}</td>
              <td>{{ report.project_name }}</td>
              <td>{{ formatDate(report.start_date_input) }}</td>
              <td>{{ report.duration }}</td>
              <td>{{ report.owner }}</td>
            </tr>
          </tbody>
        </table>
      </div>

     
    </div>

    <!-- Reject Modal -->
    <dialog id="reject_modal" class="modal">
      <div class="modal-box">
        <h3 class="font-bold text-lg">Reason for rejection</h3>
        <div class="py-4">
          <textarea 
            v-model="rejectReason" 
            class="textarea textarea-bordered w-full h-24" 
            placeholder="Please enter reason for rejection"
            :disabled="isProcessing"
          ></textarea>
        </div>
        <div class="modal-action">
          <form method="dialog">
            <button 
              class="btn btn-ghost mr-2" 
              @click="closeRejectModal"
              :disabled="isProcessing"
            >
              Cancel
            </button>
            <button 
              class="btn btn-error" 
              @click="handleReject" 
              :disabled="!rejectReason || isProcessing"
            >
              <span v-if="isProcessing" class="loading loading-spinner loading-xs"></span>
              Confirm Reject
            </button>
          </form>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button @click="closeRejectModal">close</button>
      </form>
    </dialog>
  </CustomerLayout>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import CustomerLayout from '@/layouts/CustomerLayout.vue'
import { useServiceReportStore } from '@/stores/serviceReport'
import { useServiceReportActions } from '@/composables/useServiceReportActions'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const serviceReportStore = useServiceReportStore()
const { isProcessing, error, approveReports, rejectReports } = useServiceReportActions()
const toast = useToast()

// State
const showFilter = ref(false)
const selectedReports = ref<string[]>([])
const showRejectModal = ref(false)
const rejectReason = ref('')

// Computed
const isAllSelected = computed(() => {
  return serviceReportStore.reports.length > 0 && 
         selectedReports.value.length === serviceReportStore.reports.length
})

// Methods
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedReports.value = []
  } else {
    selectedReports.value = serviceReportStore.reports.map(report => report.name)
  }
}

const toggleReport = (reportName: string) => {
  const index = selectedReports.value.indexOf(reportName)
  if (index === -1) {
    selectedReports.value.push(reportName)
  } else {
    selectedReports.value.splice(index, 1)
  }
}

const toggleFilter = () => {
  showFilter.value = !showFilter.value
}

const applyFiltersAndRefresh = () => {
  serviceReportStore.fetchAll(1)
}

const handleSearchChange = (query: string) => {
  serviceReportStore.setSearchQuery(query)
}

const handleDateRangeChange = () => {
  serviceReportStore.setDateRange(
    serviceReportStore.startDate,
    serviceReportStore.endDate
  )
}

const handlePageSizeChange = () => {
  serviceReportStore.fetchAll(1)
}

const viewDocument = (docName: string) => {
  router.push(`/service-report/${docName}`)
}

const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('th-TH')
}

const getStatusClass = (status: string) => {
  const classes = {
    'Customer Review': 'badge badge-warning',
    'Approved': 'badge badge-success',
    'Rejected': 'badge badge-error'
  }
  return classes[status] || 'badge'
}

const handleApprove = async () => {
  if (!selectedReports.value.length) return
  
  const confirmed = await window.confirm('Are you sure you want to approve the selected reports?')
  if (!confirmed) return

  const success = await approveReports(selectedReports.value)
  
  if (success) {
    toast.success('Reports approved successfully')
    selectedReports.value = [] // clear selection
    await serviceReportStore.fetchAll(serviceReportStore.currentPage) // reload current page
  } else {
    toast.error(error.value || 'Failed to approve reports')
  }
}

const openRejectModal = () => {
  rejectReason.value = '' // Clear reason when opening modal
  const modal = document.getElementById('reject_modal') as HTMLDialogElement
  modal.showModal()
}

const closeRejectModal = () => {
  rejectReason.value = '' // Clear reason
  const modal = document.getElementById('reject_modal') as HTMLDialogElement
  if (modal) {
    modal.close()
  }
}

const handleReject = async () => {
  if (!selectedReports.value.length || !rejectReason.value) return
  
  const success = await rejectReports(selectedReports.value, rejectReason.value)
  
  if (success) {
    toast.success('Reports rejected successfully')
    selectedReports.value = [] // clear selection
    closeRejectModal() // ปิด modal
    await serviceReportStore.fetchAll(serviceReportStore.currentPage) // reload current page
  } else {
    toast.error(error.value || 'Failed to reject reports')
  }
}

// เพิ่มฟังก์ชันสำหรับ refresh table
const refreshTable = async () => {
  await serviceReportStore.fetchAll(serviceReportStore.currentPage)
}

// เพิ่ม watch สำหรับ error เพื่อแสดง toast
watch(error, (newError) => {
  if (newError) {
    toast.error(newError)
  }
})

// เพิ่ม onMounted เพื่อโหลดข้อมูลครั้งแรก
onMounted(async () => {
  await refreshTable()
})
</script>
