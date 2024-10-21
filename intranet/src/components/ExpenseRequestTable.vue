<template>
  <div>
    <!-- ตารางสำหรับหน้าจอขนาดกลางขึ้นไป -->
    <div class="hidden md:block overflow-x-auto mt-4">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th class="cursor-pointer" @click="toggleSort('name')">
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
            <th class="cursor-pointer" @click="toggleSort('creation')">
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
            <th class="cursor-pointer" @click="toggleSort('workflow_state')">
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
          <tr class="h-[300px]">
            <td colspan="5" class="text-center text-gray-500">
              <div class="flex justify-center items-center h-full">
                <div class="text-lg font-bold"> Loading...</div>
              </div>
            </td>
          </tr>
        </tbody>
        <tbody v-else-if="error">
          <tr class="h-[300px]">
            <td colspan="5" class="text-center text-gray-500">
              <div class="flex justify-center items-center h-full">
                <div class="text-lg font-bold">เกิดข้อผิดพลาดในการโหลดข้อมูล</div>
              </div>
            </td>
          </tr>
        </tbody>
        <tbody v-else-if="sortedData.length > 0">
          <tr v-for="doc in sortedData" :key="doc.name">
            <td @click="viewDocument(doc.name)" class="cursor-pointer">
              <span >{{ doc.name }}</span>
              <br>
              <span class="text-xs text-gray-500">{{ formatCurrency(doc.total) }}</span>
            </td>
            <td>{{ formatDate(doc.creation) }}</td>
            <td>
              <span :class="getStatusClass(doc.workflow_state)">{{ doc.workflow_state }}</span>
            </td>
            <td>
              <UserAvatar :email="doc.request_by" />
            </td>
            <td>
              <UserAvatar v-if="doc.next_action" :email="doc.next_action" />
            </td>
            <td>
              <div class="cursor-pointer" @click="showTimeline(doc.name)">
                <UserAvatar :email="doc.approvers" />
              </div>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr class="h-[300px]">
            <td colspan="5" class="text-center text-gray-500">
              <div class="flex justify-center items-center h-full">
                <div class="text-lg font-bold"> No Data Found</div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- การ์ดสำหรับหน้าจอขนาดเล็ก -->
    <div class="md:hidden space-y-4 mt-4">
      <div v-if="loading">
        <div class="card bg-base-100 shadow-xl animate-pulse">
          <div class="card-body">
            <div class="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
            <div class="h-4 bg-gray-300 rounded w-1/2 mb-2"></div>
            <div class="h-4 bg-gray-300 rounded w-1/4"></div>
          </div>
        </div>
      </div>
      <div v-else-if="error">
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <p class="text-center text-error">เกิดข้อผิดพลาดในการโหลดข้อมูล</p>
          </div>
        </div>
      </div>
      <div v-else-if="sortedData.length > 0">
        <div v-for="doc in sortedData" :key="doc.name" class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title cursor-pointer" @click="viewDocument(doc.name)">
              {{ doc.name }}
             
            </h2>
           
            <div class="grid grid-cols-2 gap-2 mt-2">
              <div>
                <p class="font-semibold">Amont</p>
                <p>{{ formatCurrency(doc.total) }}</p>

                <span  :class="getStatusClass(doc.workflow_state)">{{ doc.workflow_state }}</span>
              </div>
              <div class="flex flex-col items-center">
                <p class="font-semibold mb-2">Request By:</p>
                <UserAvatar :email="doc.request_by" class="mb-1" />
                <p class="text-xs text-gray-500 mt-1">
                 
                  {{ formatDate(doc.creation) }}
                </p>
              </div>
            </div>
            <div class="flex justify-between mt-2">
              <div>
                <p class="font-semibold">Next Action:</p>
                <UserAvatar v-if="doc.next_action" :email="doc.next_action" />
                <span v-else>-</span>
              </div>
              <div>
                <p class="font-semibold">Approver:</p>
                <div class="cursor-pointer" @click="showTimeline(doc.name)">
                  <UserAvatar :email="doc.approvers" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <p class="text-center">No Data Found</p>
          </div>
        </div>
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
import { defineProps, defineEmits, inject, ref, computed } from 'vue'
import UserAvatar from './UserAvatar.vue';
import { useRouter } from 'vue-router';
import { createDocumentResource } from 'frappe-ui'
import Timeline from './Timeline.vue'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
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

// ใช้ inject เพื่อเรียกใช้ formatDate
const formatDate = inject('formatDate') as (date: string) => string
const formatCurrency = inject('formatCurrency') as (amount: number) => string
const router = useRouter()

const getStatusClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'draft': return 'badge badge-ghost'
    case 'pending approval': return 'badge badge-warning'
    case 'approved': return 'badge badge-success'
    case 'rejected': return 'badge badge-error'
    default: return 'badge'
  }
}

const sortedData = computed(() => {
  if (!props.sortable || !props.sortField) return props.data
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
  location.href = `/app/smo-expense-request/${docName}?from=frontend`
}

const timelineModal = ref<HTMLDialogElement | null>(null)
const timelineEvents = ref([])

const showTimeline = async (docName: string) => {
  console.log(docName)
  const expenseRequest = createDocumentResource({
    doctype: 'SMO Expense Request',
    name: docName,
    auto: false,
  })

  await expenseRequest.reload();
  console.log(expenseRequest.doc.approvers);

  timelineEvents.value = expenseRequest.doc.approvers.map(approver => ({
    date: approver.action_date,
    status: approver.status,
    action: approver.status,
    approve_role: approver.approver_role,
    by: approver.user_id
  }));

  timelineEvents.value.unshift({
    date: expenseRequest.doc.creation,
    action: 'Submit Request',
    status: 'Approved',
    approve_role: 'Requestor',
    by: expenseRequest.doc.owner
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
    @apply w-full mt-2;
  }
}
</style>
