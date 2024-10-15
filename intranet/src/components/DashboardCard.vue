<template>
  <div class="stat">
    <div class="stat-figure text-{{ color }}">
      <span>{{ icon }}</span>
    </div>
    <div class="stat-title">{{ title }}</div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-desc">{{ desc }}</div>
    <div class="stat-previous">ก่อนหน้า: {{ previous }}</div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'

const props = defineProps<{
  title: string
  value: number
  previous: number
  icon: string
  color: string
  desc: string
}>()
</script>

<style scoped>
.stat-previous {
  color: #6b7280; /* Tailwind CSS gray-500 */
  font-size: 0.875rem; /* Tailwind CSS text-sm */
}
</style>
