<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
      <!-- Navbar -->
      <div class="navbar bg-base-100 shadow-lg lg:hidden">
        <!-- <div class="flex-none">
          <label for="my-drawer-2" class="btn btn-square btn-ghost drawer-button lg:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </label>
        </div> -->
        <div class="flex-1">
          <a class="text-xl">Customer Portal</a>
        </div>
      </div>

      <!-- Content -->
      <div class="p-4 bg-base-100 flex-grow shadow-lg rounded-sm mt-2 sm:m-4">
        <slot></slot>
      </div>
    </div>

   
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
