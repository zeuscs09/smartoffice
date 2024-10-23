<template>
  <div>
    <!-- ตารางสำหรับหน้าจอขนาดกลางขึ้นไป -->
    <div class="hidden md:block overflow-x-auto mt-4">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th class="cursor-pointer" @click="$emit('sort', 'name')">
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
          
            <th class="cursor-pointer" @click="$emit('sort', 'creation')">
              Request Date
              <span class="ml-1" v-if="sortable">
                <span :class="{ 'text-primary': sortField === 'creation' }">
                  {{ sortField === 'creation' && sortOrder === 'asc' ? '▲' : '△' }}
                </span>
                <span :class="{ 'text-primary': sortField === 'creation' }">
                  {{ sortField === 'creation' && sortOrder === 'desc' ? '▼' : '▽' }}
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
               <span class="text-xs text-gray-500">{{ formatCurrency(report.total_amount) }}</span>
              </div>
              
            </td>
            <td>{{ formatDate(report.creation) }}</td>
            <td>
              <div class="badge badge-sm" :class="{
                'badge-primary': report.workflow_state === 'Approved',
                'badge-warning': report.workflow_state === 'Approval Review',
                'badge-error': report.workflow_state === 'Rejected'
              }">{{ report.workflow_state }}</div>
            </td>
            
            <td>
              <UserAvatar :email="report.owner" />
            </td>
            <td>
              <div class="cursor-pointer" @click="showTimeline(report.name)">
                <UserAvatar :email="report.approver" />
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
        <div v-for="report in data" :key="report.name" class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title cursor-pointer" @click="viewDocument(report.name)">
              No. {{ report.name }}
            </h2>
            <p class="text-sm text-gray-500">{{ formatCurrency(report.total_amount) }}   <span class="badge badge-sm" :class="{
                  'badge-primary': report.workflow_state === 'Approved',
                  'badge-warning': report.workflow_state === 'Approval Review',
                  'badge-error': report.workflow_state === 'Rejected'
                }">{{ report.workflow_state }}</span></p>
           
            <div class="grid grid-cols-1 gap-2 mt-2">
             
              <div class="flex items-center gap-2">
                <UserAvatar :email="report.owner" />
               <span class="text-xs text-gray-500"> Request Date {{ formatDate(report.creation) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <p class="font-semibold">Approver:</p>
                <div class="cursor-pointer" @click="showTimeline(report.name)">
                  <UserAvatar :email="report.approver" />
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
  location.href = `/app/smo-expense-entry/${docName}?from=frontend`
}

const showTimeline = async (docName: string) => {
  const expenseRequest = createDocumentResource({
    doctype: 'SMO Expense Entry',
    name: docName,
    auto: false,
  })
  timelineEvents.value = []

  await expenseRequest.reload();
  console.log(expenseRequest.doc);

  // เพิ่มเหตุการณ์ "สร้างคำขอ" ที่ด้านบนสุดของ timeline
  timelineEvents.value.push({
    date: expenseRequest.doc.creation,
    action: 'Submit Request',
    status: 'Approved',
    approve_role: 'Requestor',
    by: expenseRequest.doc.owner
  });

  timelineEvents.value.push({
    date: expenseRequest.doc.creation,
    action: expenseRequest.doc.workflow_state,
    status: expenseRequest.doc.workflow_state,
    approve_role: 'Vice President',
    by: expenseRequest.doc.approver
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
