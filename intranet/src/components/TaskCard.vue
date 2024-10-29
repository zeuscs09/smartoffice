<template>
  <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden">
    <!-- ส่วนหัวของการ์ด -->
    <div class="bg-gray-100 p-4 border-b border-gray-200">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold text-gray-800 truncate max-w-[70%]">
          <span v-if="todo.priority === 'Low'" class="text-green-500 mr-2" title="ความสำคัญต่ำ">&#9679;</span>
          <span v-else-if="todo.priority === 'Medium'" class="text-yellow-500 mr-2" title="ความสำคัญปานกลาง">&#9679;</span>
          <span v-else-if="todo.priority === 'High'" class="text-red-500 mr-2" title="ความสำคัญสูง">&#9679;</span>
          {{ todo.customer_name }}
        </h3>
        <div class="flex space-x-2">
          <button 
            @click="viewTask(todo)"
            class="btn btn-ghost btn-sm tooltip tooltip-bottom" 
            data-tip="View Task"
          >
            <span class="text-xl">&#128065;</span>
          </button>
          <button 
            @click="createServiceReport(todo)"
            class="btn btn-ghost btn-sm tooltip tooltip-bottom" 
            data-tip="Create Service Report"
          >
            <span class="text-xl">&#10133;</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- เนื้อหาของการ์ด -->
    <div class="p-4">
      <div class="grid grid-cols-1 gap-2 text-sm">
        <div class="flex items-center">
          <span class="mr-2 text-gray-500 text-lg">&#128197;</span>
          <span class="text-gray-700">{{ formatDate(todo.due_date) }}</span>
        </div>
        <div class="flex items-center">
          <span class="mr-2 text-gray-500 text-lg">&#128221;</span>
          <span class="text-gray-700 truncate">{{ todo.description }}</span>
        </div>
        <div class="flex items-center">
          <span class="mr-2 text-gray-500 text-lg">&#128205;</span>
          <span class="text-gray-700">{{ todo.site_name }}</span>
        </div>
        <div class="flex items-center">
          <span class="mr-2 text-gray-500 text-lg">&#128100;</span>
          <span class="text-gray-700">{{ todo.contact_person }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

interface Todo {
  name: string
  reference_name: string
  description: string
  priority: string
  due_date: string
  project: string
  site_name: string
  contact_person: string
  customer_name: string
}

defineProps<{
  todo: Todo
}>()

const router = useRouter()

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('th-TH', { year: 'numeric', month: 'long', day: 'numeric' })
}

const viewTask = (todo: Todo): void => {
  router.push({ name: 'TaskDetail', params: { id: todo.reference_name }, query: { todo: todo.name } })
}

const createServiceReport = (todo: Todo): void => {
  window.open(`/app/smo-service-report/new?from_todo=${todo.name}&from_page=/intranet/tasks&task=${todo.reference_name}&from=frontend`, '_blank')
}
</script>
