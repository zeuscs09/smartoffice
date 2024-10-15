<template>
  <div class="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0" v-if="value">
    <span class="text-gray-600 font-medium">{{ label }}:</span>
    <span class="text-gray-800">{{ value }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
}>()
</script>

