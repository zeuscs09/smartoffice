<template>
  <div class="bg-base-100 p-4 rounded-sm shadow-xl hover:shadow-md transition-shadow duration-300 border border-base-100 relative">
    <!-- เพิ่ม icon แสดง priority -->
   
    <div class="flex justify-between items-start mb-2 mt-4">
      <h3 class="text-base font-medium">
        <span v-if="todo.priority === 'Low'" class="text-green-500 text-xl" title="ความสำคัญต่ำ">&#9679; </span>
        <span v-else-if="todo.priority === 'Medium'" class="text-yellow-500 text-xl" title="ความสำคัญปานกลาง">&#9679;</span>
        <span v-else-if="todo.priority === 'High'" class="text-red-500 text-xl" title="ความสำคัญสูง">&#9679;</span>
        <span class="pl-2">{{ todo.description }}</span>
      </h3>
      <div class="flex space-x-2">
        <button 
          @click="viewTask(todo)"
          class="btn btn-ghost btn-sm tooltip tooltip-bottom" 
          data-tip="ดูรายละเอียด"
        >
          <span>&#128065;</span>
        </button>
        <button 
          class="btn btn-ghost btn-sm tooltip tooltip-bottom" 
          data-tip="สร้าง Service Report" 
          @click="createServiceReport(todo)"
        >
          <span>&#10133;</span>
        </button>
      </div>
    </div>
    <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
      <div class="flex items-center">
        <span class="mr-2 text-gray-500">&#128197;</span>
        <span>{{ formatDate(todo.due_date) }}</span>
      </div>
      <div class="flex items-center">
        <span class="mr-2 text-gray-500">&#128193;</span>
        <span>{{ todo.project }}</span>
      </div>
      <div class="flex items-center">
        <span class="mr-2 text-gray-500">&#128205;</span>
        <span>{{ todo.site_name }}</span>
      </div>
      <div class="flex items-center">
        <span class="mr-2 text-gray-500">&#128100;</span>
        <span>{{ todo.contact_person }}</span>
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
  location.href = `/app/smo-service-report/new?from_todo=${todo.name}&from_page=/&task=${todo.reference_name}` 
  
}
</script>
