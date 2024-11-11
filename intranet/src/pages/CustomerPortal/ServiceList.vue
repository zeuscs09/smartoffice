<template>
  <div class="mx-auto p-4">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Service Reports</h2>
      <div class="flex gap-2">
        <div class="flex items-center gap-2">
          <span class="text-sm">{{ store.userEmail }}</span>
          <button 
            class="btn btn-sm btn-outline" 
            @click="handleLogout"
          >
            ออกจากระบบ
          </button>
        </div>
      </div>
    </div>

    <!-- Filter Section -->
    
    <!-- Table Section -->
    <div class="overflow-x-auto mt-4">
      <!-- Desktop View -->
      <div class="hidden md:block">
        <table class="table w-full">
          <thead>
            <tr>
              <!-- <th>
                <label>
                  <input type="checkbox" class="checkbox" v-model="selectAll" @change="toggleSelectAll"/>
                </label>
              </th> -->
              <th>Service Report No.</th>
              <th>Date</th>
              <th>Working Hours</th>
              <th>Project</th>
              <th>Owner</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody v-if="store.data.length > 0">
            <tr v-for="report in store.data" :key="report.name">
              <!-- <td>
                <label>
                  <input type="checkbox" class="checkbox" v-model="selectedItems" :value="report.name"/>
                </label>
              </td> -->
              <td>{{ report.name }}</td>
              <td>{{ formatDate(report.start_date_input) }}</td>
              <td>{{ report.duration }}</td>
              <td>{{ report.project_code }}-{{ report.project_name }}</td>
              <td>
                {{report.owner}}
              </td>
              <td>
                <div class="flex gap-2">
                  <button 
                    class="btn btn-sm btn-success" 
                    @click="showApproveModal(report.name)"
                  >
                    Approve
                  </button>
                  <button 
                    class="btn btn-sm btn-error" 
                    @click="showRejectModal(report.name)"
                   
                  >
                    Reject
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr>
              <td colspan="6" class="text-center py-4">
                No data found
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile View -->
      <div class="md:hidden space-y-4">
        <div v-for="report in store.data" :key="report.name" 
          class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <div class="flex items-center justify-between">
              <h2 class="card-title">{{ report.name }}</h2>
             
            </div>
            <p class="text-sm text-gray-500">
              Date: {{ formatDate(report.start_date_input) }} 
              <br/>
              Working Hours: {{ report.duration }}
              <br/>
              Project: {{ report.project_code }}-{{ report.project_name }}
              <br/>
              Owner: {{ report.owner }}
            </p>
            <div class="flex justify-between items-center mt-2">
             
              <div class="flex gap-2">
                <button 
                  class="btn btn-sm btn-success" 
                  @click="showApproveModal(report.name)"
                 
                >
                  Approve
                </button>
                <button 
                  class="btn btn-sm btn-error" 
                  @click="showRejectModal(report.name)"
                 
                >
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <dialog ref="rejectModal" class="modal">
      <div class="modal-box">
        <h3 class="font-bold text-lg">Reject Service Report</h3>
        <div class="py-4">
          <textarea 
            v-model="rejectReason"
            class="textarea textarea-bordered w-full"
            placeholder="Enter reason for rejection"
            rows="4"
          ></textarea>
        </div>
        <div class="modal-action">
          <button class="btn btn-error" @click="rejectReport" :disabled="!rejectReason">Reject</button>
          <button class="btn" @click="closeRejectModal">Cancel</button>
        </div>
      </div>
    </dialog>

    <!-- Approve Modal -->
    <dialog ref="approveModal" class="modal">
      <div class="modal-box">
        <h3 class="font-bold text-lg">ยืนยันการอนุมัติ</h3>
        <p class="py-4">คุณต้องการอนุมัติรายงานนี้ใช่หรือไม่?</p>
        <div class="modal-action">
          <button class="btn btn-success" @click="confirmApprove">ยืนยัน</button>
          <button class="btn" @click="closeApproveModal">ยกเลิก</button>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useCustomerPortalStore } from '@/stores/customerPortalStore'
import axios from 'axios'
import { useRouter } from 'vue-router'

const store = useCustomerPortalStore()
const selectedItems = ref([])
const rejectModal = ref<HTMLDialogElement | null>(null)
const rejectReason = ref('')
const currentReportId = ref('')

const formatDate = inject('formatDate') as (date: string) => string

const selectAll = computed({
  get: () => {
    return store.data.length > 0 && selectedItems.value.length === store.data.length
  },
  set: (value) => {
    selectedItems.value = value ? store.data.map(item => item.name) : []
  }
})

onMounted(() => {
  store.fetchServiceReports()
})

const toggleFilter = () => {
  store.showFilter = !store.showFilter
}

const handleSearch = () => {
  store.searchQuery = store.searchQuery
  store.fetchServiceReports()
}

const handleFilter = () => {
  store.statusFilter = store.statusFilter
  store.startDate = store.startDate
  store.endDate = store.endDate
  store.fetchServiceReports()
}

const getStatusClass = (status: string) => {
  const classes = {
    'Customer Review': 'badge badge-warning',
    'Customer Approve': 'badge badge-success',
    'Customer Reject': 'badge badge-error'
  }
  return classes[status] || 'badge'
}

const approveModal = ref<HTMLDialogElement | null>(null)
const reportToApprove = ref('')

const showApproveModal = (reportId: string) => {
  reportToApprove.value = reportId
  approveModal.value?.showModal()
}

const closeApproveModal = () => {
  approveModal.value?.close()
}

const confirmApprove = async () => {
  try {
    const response = await store.approveReport(reportToApprove.value)
    if (response) {
      closeApproveModal()
      store.fetchServiceReports()
    }
  } catch (error) {
    console.error('Failed to approve report:', error)
  }
}

const showRejectModal = (reportId: string) => {
  currentReportId.value = reportId
  rejectReason.value = ''
  rejectModal.value?.showModal()
}

const closeRejectModal = () => {
  rejectModal.value?.close()
}

const rejectReport = async () => {
  try {
    const response = await store.rejectReport(currentReportId.value, rejectReason.value)
    if (response) {
      closeRejectModal()
      store.fetchServiceReports()
    }
  } catch (error) {
    console.error('Failed to reject report:', error)
  }
}

// กำหนด types
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

// ปรับปรุง store หรือ composable
const fetchServiceReports = async () => {
  try {
    const { data } = await axios.get<APIResponse>('/api/method/smartoffice.api.service_report.get_service_reports')
    
    if (data.message.status === 'success') {
      store.data = data.message.data
    }
  } catch (error) {
    console.error('Failed to fetch service reports:', error)
  }
}

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('customerToken')
  router.push({ name: 'CustomerLogin' })
}
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
