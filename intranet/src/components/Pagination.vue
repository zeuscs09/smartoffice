<template>
  <div class="flex justify-between items-center mt-4">
    <div class="join">
      <button class="join-item btn" @click="$emit('previous')" :disabled="isFirstPage">
        «
      </button>
      <button class="join-item btn">
        Page {{ currentPage }}
      </button>
      <button class="join-item btn" @click="$emit('next')" :disabled="isLastPage">
        »
      </button>
    </div>
    <select v-model="localPageSize" @change="updatePageSize" class="select select-bordered">
      <option :value="10">10</option>
      <option :value="20">20</option>
      <option :value="50">50</option>
    </select>
  </div>
  <div class="text-sm text-gray-600 mt-2 ml-3">
    {{ displayedItemsCount }} / {{ totalItems }} Items
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  currentPage: number;
  isFirstPage: boolean;
  isLastPage: boolean;
  pageSize: number;
  displayedItemsCount: number;
  totalItems: number;
}>();

const emit = defineEmits(['previous', 'next', 'update:pageSize']);

const localPageSize = ref(props.pageSize);

watch(() => props.pageSize, (newValue) => {
  localPageSize.value = newValue;
});

const updatePageSize = () => {
  emit('update:pageSize', localPageSize.value);
};
</script>
