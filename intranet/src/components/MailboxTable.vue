<template>
  <div>
    <!-- ตารางสำหรับหน้าจอขนาดกลางขึ้นไป -->
    <div class="hidden md:block overflow-x-auto mt-4">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th class="cursor-pointer" @click="$emit('sort', 'document_name')">
              No.
              <span class="ml-1" v-if="sortable">
                <span :class="{ 'text-primary': sortField === 'document_name' }">
                  {{ sortField === 'document_name' && sortOrder === 'asc' ? '▲' : '△' }}
                </span>
                <span :class="{ 'text-primary': sortField === 'document_name' }">
                  {{ sortField === 'document_name' && sortOrder === 'document_name' ? '▼' : '▽' }}
                </span>
              </span>
            </th>

            <th class="cursor-pointer" @click="$emit('sort', 'subject')">
              Subject
              <span class="ml-1" v-if="sortable">
                <span :class="{ 'text-primary': sortField === 'subject' }">
                  {{ sortField === 'subject' && sortOrder === 'asc' ? '▲' : '△' }}
                </span>
                <span :class="{ 'text-primary': sortField === 'subject' }">
                  {{ sortField === 'subject' && sortOrder === 'desc' ? '▼' : '▽' }}
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

          </tr>
        </thead>
        <tbody v-if="loading">
          <tr class="h-[500px]">
            <td colspan="5" class="text-center text-gray-500">
              <div class="flex justify-center items-center h-full">
                <div class="flex w-52 flex-col gap-4">
                  <div class="skeleton h-32 w-full"></div>
                  <div class="skeleton h-4 w-28"></div>
                  <div class="skeleton h-4 w-full"></div>
                  <div class="skeleton h-4 w-full"></div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
        <tbody v-else-if="data.length > 0">
          <tr v-for="report in data" :key="report.name">
            <td>
              <div class="cursor-pointer" @click="viewDocument(report.link, report.name)">
                {{ report.document_name }}
                <br />
                <span class="text-xs text-gray-500">{{ report?.doctype_description || report.document_type }}</span>
              </div>

            </td>
            <td>
              {{ report.subject }}
              <br />
              <span class="text-xs text-gray-500">{{ formatDate(report.creation) }}</span>
            </td>
            <td>
              {{ report.read ? 'Read' : 'Unread' }}
            </td>

            <td class="flex items-center gap-2">
              <UserAvatar :email="report.owner" />
              <span class="text-xs text-gray-500">{{ report.full_name }}</span>
            </td>

          </tr>
        </tbody>
        <tbody v-else>
          <tr class="h-[300px]">
            <td colspan="5" class="text-center text-gray-500">
              <div class="flex justify-center items-center h-full">
                <div class="text-lg font-bold"> ไม่พบข้อมูล</div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- การ์ดสำหรับหน้าจอขนาดเล็ก -->
    <div class="md:hidden space-y-4 mt-4">
      <div v-if="loading" class="card bg-base-100 shadow-xl animate-pulse">
        <div class="card-body">
          <div class="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
          <div class="h-4 bg-gray-300 rounded w-1/2 mb-2"></div>
          <div class="h-4 bg-gray-300 rounded w-1/4"></div>
        </div>
      </div>
      <div v-else-if="data.length > 0">
        <div v-for="report in data" :key="report.name" class="card bg-base-100 shadow-xl mb-4">
          <div class="card-body p-4">
            <div class="flex justify-between items-start mb-2">
              <h2 class="card-title text-base cursor-pointer" @click="viewDocument(report.link, report.name)">
                {{ report.document_name }}
              </h2>
              <span class="badge badge-sm" :class="{ 'badge-primary': !report.read, 'badge-ghost': report.read }">
                {{ report.read ? 'Read' : 'Unread' }}
              </span>
            </div>
            <p class="text-sm text-gray-600 mb-1">{{ report.subject }}</p>
            <p class="text-xs text-gray-500 mb-2">{{ report?.doctype_description || report.document_type }}</p>
            <div class="flex justify-between items-center mt-2">
              <div class="flex items-center gap-2">
                <UserAvatar :email="report.owner" />
                <span class="text-xs text-gray-500">{{ report.full_name }}</span>
              </div>
              <span class="text-xs text-gray-500">{{ formatDate(report.creation) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <p class="text-center text-gray-500">ไม่พบข้อมูล</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { defineProps, defineEmits, inject } from 'vue'
import UserAvatar from './UserAvatar.vue'
import { createResource } from 'frappe-ui'


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

// เพิ่มฟังก์ชันจำลองข้อมูลแนบ (ถ้าจำเป็น)
const getAttachments = (mail) => {
  // จำลองข้อมูลแนบ (ในการใช้งานจริงควรมาจากข้อมูล API)
  return mail.hasAttachments ? [
    { type: 'PDF', name: 'document.pdf' },
    { type: 'XLSX', name: 'spreadsheet.xlsx' }
  ] : [];
}

// ปรับปรุง computed property
const sortedData = computed(() => {
  if (!props.sortable) return props.data
  return [...props.data].sort((a, b) => {
    if (a[props.sortField] < b[props.sortField]) return props.sortOrder === 'asc' ? -1 : 1
    if (a[props.sortField] > b[props.sortField]) return props.sortOrder === 'asc' ? 1 : -1
    return 0
  }).map(mail => ({
    ...mail,
    attachments: getAttachments(mail),
    preview: mail.content ? mail.content.substring(0, 50) + '...' : ''
  }))
})

const viewDocument = async (link: string, mailId: string) => {
  await updateRead(mailId)
  location.href = link
}

// ฟังก์ชันสำหรับอัปเดตสถานะการอ่านและการเห็น
const updateRead = async (mailId: string) => {
  try {
    // สร้าง resource สำหรับอัปเดตเอกสาร

    const taskResource = createResource({
      url: 'smartoffice.api.mailbox.update_notification_read',
      auto: false,
    })

    // รอให้ข้อมูลโหลดเสร็จก่อน
    taskResource.fetch({
      name: mailId
    })

    console.log('อัปเดตสถานะการอ่านและการเห็นสำเร็จ')
  } catch (error) {
    console.error('เกิดข้อผิดพลาดในการอัปเดตสถานะ:', error)
  }
}

</script>

<style scoped>
.badge {
  @apply px-2 py-1 rounded-full text-xs font-semibold;
}

.card {
  @apply w-full;
}

.card-body {
  @apply p-4;
}

.card-title {
  @apply text-base mb-1;
}
</style>
