<template>
    <div>
      <!-- ตารางสำหรับหน้าจอขนาดกลางขึ้นไป -->
      <div class="hidden md:block overflow-x-auto mt-4">
        <table class="table table-zebra w-full">
          <thead>
            <tr>
              <th class="cursor-pointer" @click="$emit('sort', 'name')" style="min-width: 252px;">
                No.
                <span class="ml-1" v-if="sortable">
                  <span :class="{ 'text-primary': sortField === 'name' }">
                    {{ sortField === 'name' && sortOrder === 'asc' ? '▲' : '△' }}
                  </span>
                  <span :class="{ 'text-primary': sortField === 'name' }">
                    {{ sortField === 'name' && sortOrder === 'desc' ? '▼' : '▽' }}
                  </span>
                </span>
              </th>
            
              <th class="cursor-pointer" @click="$emit('sort', 'customer_name')">
               Customer Name
                <span class="ml-1" v-if="sortable">
                  <span :class="{ 'text-primary': sortField === 'customer_name' }">
                    {{ sortField === 'customer_name' && sortOrder === 'asc' ? '▲' : '△' }}
                  </span>
                  <span :class="{ 'text-primary': sortField === 'customer_name' }">
                    {{ sortField === 'customer_name' && sortOrder === 'desc' ? '▼' : '▽' }}
                  </span>
                </span>
              </th>
              <th class="cursor-pointer" @click="$emit('sort', 'workflow_state')">
                Status
                <span class="ml-1" v-if="sortable">
                  <span :class="{ 'text-primary': sortField === 'workflow_state' }">
                    {{ sortField === 'workflow_state' && sortOrder === 'asc' ? '▲' : '△' }}
                  </span>
                  <span :class="{ 'text-primary': sortField === 'workflow_state' }">
                    {{ sortField === 'workflow_state' && sortOrder === 'desc' ? '▼' : '▽' }}
                  </span>
                </span>
              </th>
              <th>Request By</th>
              <th>Next Action</th>
              <th>Approver</th>
            </tr>
          </thead>
          <tbody v-if="loading">
            <tr >
              <td colspan="5" >
                <SkeletonTable />
              </td>
            </tr>
          </tbody>
          <tbody v-else-if="data.length > 0">
            <tr v-for="report in data" :key="report.name">
              <td>
                <div class="cursor-pointer" @click="viewDocument(report.name)">
                  {{ report.name }}
                  <br/>
                 <span class="text-xs text-gray-500">Service Date: {{ formatDate(report.service_date)  }} - {{ formatDate(report.to) }}</span>
                </div>
                
              </td>
              <td>
                {{ report.customer_name }}
                <br/>
                <span class="text-xs text-gray-500">{{ formatCurrency(report.total_amount)}}</span>
              </td>
              <td>
                <div class="flex items-center">
                  <span class="w-2 h-6 block mr-2" :class="{
                    'bg-green-500': report.workflow_state === 'Approved',
                    'bg-yellow-500': report.workflow_state === 'Approval Review' || report.workflow_state === 'Pending Approval',
                    'bg-red-500': report.workflow_state === 'Rejected',
                    'bg-gray-500': report.workflow_state === 'Draft'
                  }"></span>
                  <span class="opacity-75" :class="{
                    'text-green-500': report.workflow_state === 'Approved',
                    'text-yellow-500': report.workflow_state === 'Approval Review' || report.workflow_state === 'Pending Approval',
                    'text-red-500': report.workflow_state === 'Rejected',
                    'text-gray-500': report.workflow_state === 'Draft'
                  }">{{ report.workflow_state }}</span>
                </div>
              </td>
              
              <td>
                <UserAvatar :email="report.owner" />
              </td>
              <td>
                <div v-if="report.next_action">
                <div class="flex items-center gap-2">
                  <UserAvatar :email="report.next_action" />
                  <span class="text-xs text-gray-500">{{ report.next_action }}</span>
                </div>
              </div>
              </td>
              <td>
                <div class="cursor-pointer" @click="showTimeline(report.name)">
                  <UserAvatar :email="report.approvers" />
                </div>
              </td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr >
              <td colspan="5" >
                <NoDataFoundTable />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- การ์ดสำหรับหน้าจอขนาดเล็ก -->
      <div class="md:hidden space-y-4 mt-4">
        <div v-if="loading">
          <SkeletonCard />
        </div>
        <div v-else-if="data.length > 0">
          <div v-for="report in data" :key="report.name" class="card bg-base-100 shadow-xl mt-2">
            <div class="card-body">
              <div class="cursor-pointer" @click="viewDocument(report.name)">
                <h2 class="card-title">
                  {{ report.customer_name }}
                </h2>
                <p class="text-sm text-gray-500">
                  Service Date: {{ formatDate(report.service_date) }} - {{ formatDate(report.to) }}
                  <br/>
                  # {{ report.name }}
                </p>
                <p class="text-sm text-gray-500">
                  {{ formatCurrency(report.total_amount) }}
                  <span class="inline-flex border rounded-md px-2 py-1" :class="{
                    'bg-gray-100 border-gray-200 text-gray-700': report.workflow_state === 'Draft',
                    'bg-yellow-100 border-yellow-200 text-yellow-700': report.workflow_state === 'Approval Review' || report.workflow_state === 'Pending Approval',
                    'bg-green-100 border-green-200 text-green-700': report.workflow_state === 'Approved',
                    'bg-red-100 border-red-200 text-red-700': report.workflow_state === 'Rejected'
                  }">{{ report.workflow_state }}</span>
                </p>
              </div>
              <div class="grid grid-cols-1 gap-2 mt-2">
                <div class="flex items-center gap-2 p-2 bg-gray-100 rounded-md">
                  <UserAvatar :email="report.owner" />
                  <span class="text-xs text-gray-500">Request Date: {{ formatDate(report.creation) }}</span>
                </div>
                <div class="grid grid-cols-2 gap-4 bg-gray-100 p-2 rounded-md">
                  <div class="space-y-1">
                    <p class="text-xs text-gray-600">Next Action:</p>
                    <div v-if="report.next_action">
                      <div class="flex items-center gap-2">
                        <UserAvatar :email="report.next_action" />
                        <span class="text-xs text-gray-500">{{ report.next_action }}</span>
                      </div>
                    </div>
                    <span v-else>-</span>
                  </div>
                  <div class="space-y-1">
                    <p class="text-xs text-gray-600">Approver:</p>
                    <div class="cursor-pointer" @click="showTimeline(report.name)">
                      <div class="flex items-center gap-2">
                        <UserAvatar :email="report.approvers" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <NoDataFoundCard />
        </div>
      </div>
  
      <!-- Modal for timeline -->
      <dialog id="timeline_modal" class="modal" ref="timelineModal">
        <div class="modal-box w-11/12 max-w-5xl">
          <h3 class="font-bold text-lg mb-4">ประวัติการอนุมัติ</h3>
          <Timeline :events="timelineEvents" />
          <div class="modal-action">
            <form method="dialog">
              <button class="btn">ปิด</button>
            </form>
          </div>
        </div>
      </dialog>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed } from 'vue'
  import { defineProps, defineEmits, inject } from 'vue'
  import UserAvatar from './UserAvatar.vue'
  import Timeline from './TimeLine.vue'
  import { createDocumentResource } from 'frappe-ui'
  import SkeletonTable from '@/components/SkeletonTable.vue'
  import NoDataFoundTable from '@/components/NoDataFoundTable.vue'
  import SkeletonCard from '@/components/SkeletonCard.vue'
  import NoDataFoundCard from '@/components/NoDataFoundCard.vue'
  import { useRouter } from 'vue-router'
  
  const router = useRouter()
  
  const props = defineProps({
    data: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    sortField: {
      type: String,
      default: ''
    },
    sortOrder: {
      type: String,
      default: 'asc'
    },
    sortable: {
      type: Boolean,
      default: true
    }
  })
  
  const emit = defineEmits(['sort'])
  
  const formatDate = inject('formatDate') as (date: string) => string
  const formatCurrency = inject('formatCurrency') as (amount: number) => string
  
  const timelineModal = ref<HTMLDialogElement | null>(null)
  const timelineEvents = ref([])
  
  const sortedData = computed(() => {
    if (!props.sortable) return props.data
    return [...props.data].sort((a, b) => {
      if (a[props.sortField] < b[props.sortField]) return props.sortOrder === 'asc' ? -1 : 1
      if (a[props.sortField] > b[props.sortField]) return props.sortOrder === 'asc' ? 1 : -1
      return 0
    })
  })
  
  const toggleSort = (field: string) => {
    if (!props.sortable) return
    emit('sort', field)
  }
  
  const viewDocument = (docName: string) => {
    // window.open(`/app/smo-advance-entry/${docName}?from_page=/intranet/advance-entry`, '_blank')

    router.push(`/advance-entry/${docName}`)

  }
  
  const showTimeline = async (docName: string) => {
  console.log(docName)
  const docData = createDocumentResource({
    doctype: 'SMO Advance Entry',
    name: docName,
    auto: false,
  })

  await docData.reload();
  
  // ตรวจสอบว่ามีรายการที่ rejected หรือไม่
  const hasRejected = docData.doc.approvers.some(approver => approver.status.toLowerCase() === 'rejected');

  timelineEvents.value = docData.doc.approvers
    .filter(approver => !hasRejected || approver.status.toLowerCase() !== 'pending')
    .map(approver => ({
      date:  approver.receive_date,
      status: approver.status,
      action: approver.status,
      approve_role: approver.approver_role,
      by: approver.user_id,
      remark: approver.comment,
      duration: approver.duration
    }));

  timelineEvents.value.unshift({
    date: docData.doc.creation,
    action: 'Submit Request',
    status: 'Approved',
    approve_role: 'Requestor',
    by: docData.doc.owner,
    remark: ""
  });

  timelineModal.value?.showModal();
}
  </script>
  
  <style scoped>
  .badge {
    @apply px-2 py-1 rounded-full text-xs font-semibold;
  }
  
  @media (max-width: 768px) {
    .card {
      @apply w-full;
    }
  }
  </style>
  