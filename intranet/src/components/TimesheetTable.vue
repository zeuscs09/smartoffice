<script setup lang="ts">
import { computed } from 'vue'
import { Clock } from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: Object,
    default: null
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
    default: false
  }
})

const emit = defineEmits(['sort', 'view'])

const handleSort = (field) => {
  if (props.sortable) {
    emit('sort', field)
  }
}

const getSortIcon = (field) => {
  if (props.sortField === field) {
    return props.sortOrder === 'asc' ? '↑' : '↓'
  }
  return ''
}

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'Draft':
      return 'badge-warning'
    case 'Submitted':
      return 'badge-success'
    case 'Cancelled':
      return 'badge-error'
    default:
      return 'badge-ghost'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>

<template>
  <div>
    <table class="table w-full">
      <thead>
        <tr>
          <th 
            @click="handleSort('name')" 
            :class="{ 'cursor-pointer': sortable }"
          >
            ID {{ getSortIcon('name') }}
          </th>
          <th 
            @click="handleSort('month')" 
            :class="{ 'cursor-pointer': sortable }"
          >
            Month {{ getSortIcon('month') }}
          </th>
          <th 
            @click="handleSort('year')" 
            :class="{ 'cursor-pointer': sortable }"
          >
            Year {{ getSortIcon('year') }}
          </th>
          <th 
            @click="handleSort('total_hours')" 
            :class="{ 'cursor-pointer': sortable }"
          >
            Working Hours {{ getSortIcon('total_hours') }}
          </th>
          <th 
            @click="handleSort('status')" 
            :class="{ 'cursor-pointer': sortable }"
          >
            Status {{ getSortIcon('status') }}
          </th>
          <th 
            @click="handleSort('creation')" 
            :class="{ 'cursor-pointer': sortable }"
          >
            Created {{ getSortIcon('creation') }}
          </th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <template v-if="loading">
          <tr v-for="i in 3" :key="i">
            <td colspan="7" class="text-center">
              <div class="skeleton h-4 w-full"></div>
            </td>
          </tr>
        </template>
        <template v-else-if="error">
          <tr>
            <td colspan="7" class="text-center text-error">
              {{ error.message || 'An error occurred while fetching data' }}
            </td>
          </tr>
        </template>
        <template v-else-if="data && data.length">
          <tr v-for="timesheet in data" :key="timesheet.name" class="hover">
            <td>{{ timesheet.name }}</td>
            <td>{{ timesheet.month }}</td>
            <td>{{ timesheet.year }}</td>
            <td>
              <div class="flex items-center">
                <Clock class="w-4 h-4 mr-1" />
                {{ timesheet.total_hours || 0 }} hrs
              </div>
            </td>
            <td>
              <div class="badge" :class="getStatusBadgeClass(timesheet.status)">
                {{ timesheet.status }}
              </div>
            </td>
            <td>{{ formatDate(timesheet.creation) }}</td>
            <td>
              <button 
                class="btn btn-ghost btn-xs"
                @click="emit('view', timesheet.name)"
              >
                View
              </button>
            </td>
          </tr>
        </template>
        <template v-else>
          <tr>
            <td colspan="7" class="text-center py-4">
              No timesheets found
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template> 