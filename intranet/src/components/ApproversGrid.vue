<script setup lang="ts">
import UserAvatar from '@/components/UserAvatar.vue'
import { inject } from 'vue'
const formatDuration = inject('formatDuration') as (duration: number) => string
type Approver = {
  name: string
  user_id: string
  approver_role: string
  status: 'Approved' | 'Rejected' | 'Pending'
  action_date?: string
  receive_date?: string
  comment?: string
  duration?: number
}

interface Props {
  approvers: Approver[]
}

const props = defineProps<Props>()

const getStatusClasses = (status: Approver['status']) => ({
  'bg-green-50 border-green-200': status === 'Approved',
  'bg-red-50 border-red-200': status === 'Rejected',
  'bg-gray-50 border-gray-200 opacity-50': status === 'Pending' || !status,
})

const getStatusBadgeClasses = (status: Approver['status']) => ({
  'px-2 py-0.5 text-xs font-medium rounded-full': true,
  'bg-green-100 text-green-800': status === 'Approved',
  'bg-red-100 text-red-800': status === 'Rejected', 
  'bg-gray-100 text-gray-800': status === 'Pending' || !status
})

const formatDateTime = (dateString?: string): string => {
  if (!dateString) return ''
  return dateString.split('.')[0].replace('T', ' ')
}
</script>

<template>
  <div class="bg-white rounded-lg shadow p-4">
    <h2 class="text-base font-medium text-gray-900 mb-3">Approvers</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      <div 
        v-for="approver in approvers" 
        :key="approver.name"
        class="flex items-start space-x-3 p-3 rounded-lg border"
        :class="getStatusClasses(approver.status)"
      >
        <UserAvatar 
          :email="approver.user_id" 
          size="sm" 
        />
        <div class="min-w-0 flex-1">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-sm text-gray-900">{{ approver.user_id }}</p>
              <p class="text-xs text-gray-500">{{ approver.approver_role }}</p>
            </div>
            <span 
              :class="getStatusBadgeClasses(approver.status)"
              class="px-1.5 py-0.5 text-xs shrink-0"
            >
              {{ approver.status }}
            </span>
          </div>
          <div class="flex flex-col text-[11px] text-gray-500 mt-0.5">
            <span v-if="approver.receive_date">
              Received: {{ formatDateTime(approver.receive_date) }}
            </span>
            <span v-if="approver.action_date">
              Action: {{ formatDateTime(approver.action_date) }}
            </span>
            <span v-if="approver.duration">
              Duration: {{ formatDuration(approver.duration) }}
            </span>
          </div>
          <p 
            v-if="approver.comment" 
            class="text-xs text-gray-600 mt-0.5"
          >
            {{ approver.comment }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
