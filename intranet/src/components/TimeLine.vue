<template>
  <ul class="timeline timeline-vertical">
    <li v-for="(event, index) in events" :key="index">
      <hr :class="{ 'bg-green-500': event.status === 'Approved', 'bg-red-500': event.status === 'Rejected' }" />
      <div :class="[
        index % 2 === 0 ? 'timeline-start' : 'timeline-end',
        'timeline-box'
      ]">
        <div class="flex items-center" :class="{ 'flex-row-reverse': index % 2 === 0 }">
          <UserAvatar :email="event.by" :class="[index % 2 === 0 ? 'ml-2' : 'mr-2']" />
          <div>
            <div class="text-sm">
              {{ event.approve_role }}
            </div>
            <div class="badge badge-sm" :class="{
              'badge-success': event.status === 'Approved',
              'badge-error': event.status === 'Rejected',
              'badge-ghost': event.status === 'Pending'
            }">{{ event.action }}</div>
          </div>
        </div>
      </div>
      <div class="timeline-middle">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" :class="[
          'h-5 w-5',
          event.status === 'Approved' ? 'text-green-500' :
            event.status === 'Rejected' ? 'text-red-500' : 'text-gray-500'
        ]">
          <path v-if="event.status === 'Approved'" fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
            clip-rule="evenodd" />
          <path v-else-if="event.status === 'Rejected'" fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
            clip-rule="evenodd" />
          <path v-else fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z"
            clip-rule="evenodd" />
        </svg>
      </div>
      <div :class="[
        index % 2 === 0 ? 'timeline-end' : 'timeline-start',
      ]">
        {{ event.date ? formatDate(event.date) : '' }}
      </div>
      <hr :class="{ 'bg-green-500': event.status === 'Approved', 'bg-red-500': event.status === 'Rejected' }" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import UserAvatar from '@/components/UserAvatar.vue'

const formatDate = inject('formatDate') as (date: string) => string

interface TimelineEvent {
  date: string
  action: string
  status: string
  approve_role: string
  by: string
}

defineProps<{
  events: TimelineEvent[]
}>()
</script>

