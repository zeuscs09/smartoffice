<script setup lang="ts">
interface Props {
  name: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  className: ''
})

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const sizeClasses = {
  sm: 'w-8 h-8 text-sm',
  md: 'w-12 h-12 text-lg',
  lg: 'w-32 h-32 text-4xl'
}
</script>

<template>
  <div
    :class="[
      'avatar placeholder',
      className
    ]"
  >
    <div
      :class="[
        'bg-neutral text-neutral-content rounded-full flex items-center justify-center',
        sizeClasses[size]
      ]"
    >
      <span>{{ getInitials(name) }}</span>
    </div>
  </div>
</template> 