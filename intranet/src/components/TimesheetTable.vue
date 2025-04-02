<script setup lang="ts">
import { computed, inject, ref } from 'vue'
import { Clock } from 'lucide-vue-next'
import UserAvatar from './UserAvatar.vue'
import Timeline from './TimeLine.vue'
import { createDocumentResource, createListResource, frappe } from 'frappe-ui'

interface TimelineEvent {
  date: string
  status: string
  action: string
  approve_role: string
  by: string
  remark: string
}

interface WorkflowComment {
  action_by: string
  content: string
  creation: string
}

interface Timesheet {
  name: string
  year: string
  month: string
  month_value: string
  workflow_state: string
  total_hours: number
  user_id: string
  approver: string
  creation: string
  workflow_history?: Array<{
    creation: string
    status: string
    role: string
    owner: string
    comment?: string
  }>
  owner: string
}

interface DocumentResource<T> {
  reload: () => Promise<void>
  doc: T
  list?: T[]
}

const formatDuration = inject('formatDuration') as (duration: number, options?: { hourOnly?: boolean }) => string

const props = defineProps({
  data: {
    type: Array as () => Timesheet[],
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

const timelineModal = ref<HTMLDialogElement | null>(null)
const timelineEvents = ref<TimelineEvent[]>([])

const showTimeline = async (docName: string) => {
  try {
    // Fetch timesheet data and comments
    const [timesheetResponse, commentsResponse] = await Promise.all([
      fetch(`/api/method/frappe.client.get`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          doctype: 'SMO Timesheet',
          name: docName
        })
      }),
      fetch(`/api/method/smartoffice.api.util.get_comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: docName,
          comment_type: 'Workflow',
          reference_doctype: 'SMO Timesheet'
        })
      })
    ])

    if (!timesheetResponse.ok || !commentsResponse.ok) {
      throw new Error('Failed to fetch data')
    }

    const [timesheetData, commentsData] = await Promise.all([
      timesheetResponse.json(),
      commentsResponse.json()
    ])

    const timesheet = timesheetData.message
    const comments: WorkflowComment[] = commentsData.message || []
    
    // Map workflow history to timeline events
    timelineEvents.value = timesheet.workflow_history?.map(history => {
      // Find matching comment for this workflow transition
      const comment = comments.find(c => 
        c.creation === history.creation && 
        c.action_by === history.owner
      )

      return {
        date: history.creation,
        status: history.status,
        action: history.status,
        approve_role: history.role,
        by: history.owner,
        remark: comment?.content || history.comment || ""
      }
    }) || []

    timelineEvents.value.push({
      date: timesheet.creation,
      action: 'Created',
      status: 'Draft',
      approve_role: 'Requestor',
      by: timesheet.owner,
      remark: ""
    })
   
   for (const comment of comments) {
    const action_text = comment.content == "Approval Review" ? "Request Approve" : comment.content  
    const status = comment.content == "Approval Review" ? "Pending Approval" : comment.content
    timelineEvents.value.push({
      date: comment.creation,
      action: action_text,
      status: status,
      approve_role: comment.content == "Approval Review" ? "Approver" : '',
      by: comment.action_by,
      remark: comment.content == "Rejected" ? timesheet.reject_reason : ""
    })
   }

    timelineModal.value?.showModal()
  } catch (error) {
    console.error('Error showing timeline:', error)
  }
}

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
  <div class="bg-base-100 rounded-lg shadow">
    <table class="table w-full">
      <thead>
        <tr>
          <th @click="handleSort('name')" :class="{ 'cursor-pointer': sortable }">
            ID {{ getSortIcon('name') }}
          </th>
          <th @click="handleSort('total_hours')" :class="{ 'cursor-pointer': sortable }">
            Working Hours {{ getSortIcon('total_hours') }}
          </th>
          <th @click="handleSort('status')" :class="{ 'cursor-pointer': sortable }">
            Status {{ getSortIcon('status') }}
          </th>
          <th @click="handleSort('creation')" :class="{ 'cursor-pointer': sortable }">
            Request By
          </th>
          <th>Approver</th>
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
            <td>
              <a href="#" @click="emit('view', timesheet.name)">{{ timesheet.name }}</a>
              <br />
              <span class="text-xs text-gray-500">
                {{ timesheet.year }} - {{ timesheet.month }}
              </span>
            </td>
            <td>
              <div class="flex items-center">
                <Clock class="w-4 h-4 mr-1" />
                {{ formatDuration(timesheet.total_hours, { hourOnly: true }) }}
              </div>
            </td>
            <td>
              <div class="flex items-center">
                <span class="w-2 h-6 block mr-2" :class="{
                  'bg-green-500': timesheet.workflow_state === 'Approved',
                  'bg-yellow-500': timesheet.workflow_state === 'Approval Review',
                  'bg-red-500': timesheet.workflow_state === 'Rejected',
                  'bg-gray-500': timesheet.workflow_state === 'Draft'
                }"></span>
                <span class="opacity-75" :class="{
                  'text-green-500': timesheet.workflow_state === 'Approved',
                  'text-yellow-500': timesheet.workflow_state === 'Approval Review',
                  'text-red-500': timesheet.workflow_state === 'Rejected',
                  'text-gray-500': timesheet.workflow_state === 'Draft'
                }">{{ timesheet.workflow_state }}</span>
              </div>
            </td>
            <td>
              <div class="flex items-center gap-2">
                <UserAvatar :email="timesheet.user_id" />
                <span class="text-xs text-gray-500">
                  {{ formatDate(timesheet.creation) }}
                </span>
              </div>
            </td>
            <td>
              <div class="cursor-pointer" @click="showTimeline(timesheet.name)">
                <div class="flex items-center gap-2">
                  <UserAvatar :email="timesheet.approver" />
                </div>
              </div>
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
  <dialog ref="timelineModal" class="modal">
    <div class="modal-box w-11/12 max-w-5xl">
      <Timeline :events="timelineEvents" />
      <div class="modal-action">
        <form method="dialog">
          <button class="btn">Close</button>
        </form>
      </div>
    </div>
  </dialog>
</template>

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