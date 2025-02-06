<script setup lang="ts">
defineProps<{
  entries: string[]
}>()

const openExpenseEntry = (expenseId: string) => {
  window.open(`/app/smo-expense-entry/${expenseId}`, '_blank')
}
</script>

<template>
  <div class="flex gap-2">
    <button
      v-for="entry in entries"
      :key="entry"
      @click="openExpenseEntry(entry)"
      class="px-2 py-1 text-sm bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 hover:underline transition-colors"
    >
      {{ entry }}
    </button>
  </div>
</template> 