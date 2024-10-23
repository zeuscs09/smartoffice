<template>
  <div>
    <div class="hidden md:block">
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
            <th class="cursor-pointer" @click="$emit('sort', 'job_start_on')">
              Date
              <span class="ml-1" v-if="sortable">
                <span :class="{ 'text-primary': sortField === 'job_start_on' }">
                  {{ sortField === 'job_start_on' && sortOrder === 'asc' ? '▲' : '△' }}
                </span>
                <span :class="{ 'text-primary': sortField === 'job_start_on' }">
                  {{ sortField === 'job_start_on' && sortOrder === 'desc' ? '▼' : '▽' }}
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
            <th>Responsible</th>
          </tr>
        </thead>
        <tbody v-if="loading">
          <tr >
            <td colspan="4" >
              <SkeletonTable />
            </td>
          </tr>
        </tbody>
        <tbody v-else-if="sortedData.length > 0">
          <tr v-for="doc in sortedData" :key="doc.name">
            <td>
              <div class="cursor-pointer" @click="viewDocument(doc.name)">

                {{ doc.name }}
                <br/>
                <span class="text-xs text-gray-500 " > {{ doc.task_name
                  }}</span>
                  </div>
            </td>
            <td>{{ formatDate(doc.job_start_on) }}</td>
            <td>
              <div :class="getStatusClass(doc.workflow_state)">{{ doc.workflow_state }}</div>
              <br/>
              <button class="btn btn-neutral btn-xs mt-1" @click="openExpenseEntry(doc.name)">
                + Expense
              </button>
            </td>
            <td>
              <UserAvatar :email="doc.teams" />
            </td>
            
          </tr>
        </tbody>
        <tbody v-else>
          <tr >
            <td colspan="4" >
              <NoDataFoundTable />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="md:hidden">
      <div v-if="loading">
        <SkeletonCard />
      </div>
      <div v-else-if="sortedData.length > 0" class="space-y-4">
        <div v-for="doc in sortedData" :key="doc.name" class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title cursor-pointer" @click="viewDocument(doc.name)">
              {{ doc.name }}
            </h2>
            <p class="text-sm text-gray-500">{{ doc.task_name }}</p>
            <p>Date: {{ formatDate(doc.job_start_on) }}</p>
            <p>Status: <span :class="getStatusClass(doc.workflow_state)">{{ doc.workflow_state }}</span></p>
            <div class="card-actions justify-end">
              <div class="flex justify-between items-center w-full">
                <button class="btn btn-neutral btn-sm" @click="openExpenseEntry(doc.name)">
                  
               
                  <span class="ml-1 text-xs">+ Expense</span>
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
    case 'customer review': return 'badge badge-warning'
    case 'customer approve': return 'badge badge-success'
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
  location.href = `/app/smo-service-report/${docName}`
}

const openExpenseEntry = (docName: string) => {
  window.open(`/app/smo-expense-entry/new?service_report=${docName}`, '_blank')
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
