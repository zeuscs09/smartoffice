<template>
  <div>
    <div v-if="loading" class="flex justify-center items-center h-40">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
    <div v-else-if="error" class="text-center py-8">
      <p class="text-error">เกิดข้อผิดพลาดในการโหลดข้อมูล</p>
    </div>
    <div v-else>
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th>เลขที่เอกสาร</th>
            <th>วันที่</th>
            <th>สถานะ</th>
            <th>ผู้รับผิดชอบ</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in data" :key="doc.name">
            <td>
              {{ doc.task_name }}
              <br>
              <span class="text-xs text-gray-500 cursor-pointer" @click="viewDocument(doc.name)">{{ doc.name }}</span>
            </td>
            <td>{{ formatDate(doc.job_start_on) }}</td>
            <td>
              <span :class="getStatusClass(doc.workflow_state)">{{ doc.workflow_state }}</span>
            </td>
            <td>
              <UserAvatar :email="doc.teams" />
            </td>
          </tr>
        </tbody>
      </table>
      <div class="text-right">
        <button class="btn btn-link" @click="router.push({ name: 'ServiceReportList' })">ดูทั้งหมด</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, inject } from 'vue'
import UserAvatar from './UserAvatar.vue';
import { useRouter } from 'vue-router';
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
  }
})

// ใช้ inject เพื่อเรียกใช้ formatDate
const formatDate = inject('formatDate') as (date: string) => string

const router = useRouter()

const getStatusClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'draft': return 'badge badge-warning'
    case 'submitted': return 'badge badge-success'
    case 'cancelled': return 'badge badge-error'
    default: return 'badge'
  }
}

const viewDocument = (docName: string) => {
  location.href = `/app/smo-service-report/${docName}`
}
</script>

<style scoped>
.badge {
  @apply px-2 py-1 rounded-full text-xs font-semibold;
}
</style>
