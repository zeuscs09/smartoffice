<template>
  <div>
    <div class="hidden md:block">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th class="cursor-pointer w-32" @click="$emit('sort', 'name')" style="min-width: 252px;">
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
            <th class="cursor-pointer w-64" @click="$emit('sort', 'customer_name')">
              Customer
              <span class="ml-1" v-if="sortable">
                <span :class="{ 'text-primary': sortField === 'customer_name' }">
                  {{ sortField === 'customer_name' && sortOrder === 'asc' ? '▲' : '△' }}
                </span>
                <span :class="{ 'text-primary': sortField === 'customer_name' }">
                  {{ sortField === 'customer_name' && sortOrder === 'desc' ? '▼' : '▽' }}
                </span>
              </span>
            </th>
            <th class="w-64">Project</th>
            <th class="cursor-pointer w-48" @click="$emit('sort', 'workflow_state')">
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
            <th class="w-32">Responsible</th>
          </tr>
        </thead>
        <tbody v-if="loading">
          <tr>
            <td colspan="4">
              <SkeletonTable />
            </td>
          </tr>
        </tbody>
        <tbody v-else-if="sortedData.length > 0">
          <tr v-for="doc in sortedData" :key="doc.name">
            <td>
              <div class="cursor-pointer" @click="viewDocument(doc.name)">

                {{ doc.name }}
                <br />
                <span class="text-xs text-gray-500 "> {{ formatDate(doc.job_start_on) }}</span>
              </div>
            </td>
            <td>
              {{ doc.customer_name }}
              <br />
              <span class="text-xs text-gray-500 ">
                {{ doc.task_name }}
              </span>
            </td>
            <td>
              {{ doc.project_code }}
              <br />
              <span class="text-xs text-gray-500 ">
                {{ doc.project_name }}
              </span>
            </td>
            <td>
              <div class="flex items-center space-y-2 flex-col">
                <div class="flex items-center w-full">
                  <span class="w-2 h-6 block mr-2" :class="{
                    'bg-green-500': doc.workflow_state.toLowerCase() === 'customer approved',
                    'bg-yellow-500': doc.workflow_state.toLowerCase() === 'customer review',
                    'bg-red-500': ['customer reject', 'rejected'].includes(doc.workflow_state.toLowerCase()),
                    'bg-gray-500': doc.workflow_state.toLowerCase() === 'draft'
                  }"></span>
                  <span class="opacity-75" :class="{
                    'text-green-500': doc.workflow_state.toLowerCase() === 'customer approved',
                    'text-yellow-500': doc.workflow_state.toLowerCase() === 'customer review',
                    'text-red-500': ['customer reject', 'rejected'].includes(doc.workflow_state.toLowerCase()),
                    'text-gray-500': doc.workflow_state.toLowerCase() === 'draft'
                  }">{{ doc.workflow_state }}</span>
                </div>
                <button 
                  v-if="!['customer reject', 'rejected', 'draft'].includes(doc.workflow_state.toLowerCase())"
                  class="btn btn-ghost btn-xs text-primary hover:bg-primary/10" 
                  @click="openExpenseEntry(doc.name)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Expense
                </button>
              </div>
            </td>
            <td>
              <UserAvatar :email="doc.teams" />
            </td>

          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td colspan="4">
              <NoDataFoundTable />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="md:hidden space-y-4 mt-4">
      <div v-if="loading">
        <SkeletonCard />
      </div>
      <div v-else-if="sortedData.length > 0">
        <div v-for="doc in sortedData" :key="doc.name" 
          class="card bg-base-100 shadow-sm border border-base-200 mt-2">
          <div class="card-body">
            <div class="cursor-pointer" @click="viewDocument(doc.name)">
              <h2 class="card-title">
                {{ doc.customer_name }}
              </h2>
              <p class="text-sm text-gray-500">
                {{ doc.project_code }} - {{ doc.project_name }}
              </p>
              <p class="text-sm text-gray-500">
                {{ doc.task_name }}
                <br />
                # {{ doc.name }}
              </p>
              <p class="text-sm text-gray-500">
                {{ formatDate(doc.job_start_on) }}
                <span class="inline-flex border rounded-md px-2 py-1" :class="{
                  'bg-gray-100 border-gray-200 text-gray-700': doc.workflow_state.toLowerCase() === 'draft',
                  'bg-yellow-100 border-yellow-200 text-yellow-700': doc.workflow_state.toLowerCase() === 'customer review',
                  'bg-green-100 border-green-200 text-green-700': doc.workflow_state.toLowerCase() === 'customer approved',
                  'bg-red-100 border-red-200 text-red-700': ['customer reject', 'rejected'].includes(doc.workflow_state.toLowerCase())
                }">{{ doc.workflow_state }}</span>
              </p>
            </div>
            <div class="card-actions justify-end">
              <div class="flex justify-between items-center w-full">
                <button 
                  v-if="!['customer reject', 'rejected', 'draft'].includes(doc.workflow_state.toLowerCase())"
                  class="btn btn-ghost btn-sm text-primary hover:bg-primary/10" 
                  @click="openExpenseEntry(doc.name)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Expense
                </button>
                <UserAvatar :email="doc.teams" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <NoDataFoundCard />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, inject, computed } from 'vue'
import UserAvatar from './UserAvatar.vue';
import { useRouter } from 'vue-router';
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

const formatDate = inject('formatDate') as (date: string) => string
const router = useRouter()

const getStatusClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'customer review': return 'badge badge-xs badge-warning'
    case 'customer approved': return 'badge badge-xs badge-success'
    case 'rejected': return 'badge badge-xs badge-error'
    case 'customer reject': return 'badge badge-xs badge-error'
    default: return 'badge badge-xs'
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
  // window.open(`/app/smo-service-report/${docName}?from_page=/intranet`, '_blank')
  router.push(`/service-report/${docName}`)
}

const openExpenseEntry = (docName: string) => {
  window.open(`/app/smo-expense-entry/new?service_report=${docName}&from_page=/intranet/service-report`, '_blank')
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
