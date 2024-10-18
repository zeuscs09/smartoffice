<template>
    <UserLayout>
        <!-- add breadcrumb -->
       
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                </tr>
            </thead>
            <tbody> 
                <tr v-for="expenseRequest in expenseRequestStore.expenseRequests" :key="expenseRequest.id">
                    <td>{{ expenseRequest.id }}</td>
                    <td>{{ expenseRequest.name }}</td>
                    <td>{{ expenseRequest.email }}</td>
                </tr>
            </tbody>
        </table>
    </UserLayout>
</template>
<script setup lang="ts">
import UserLayout from '@/layouts/userLayout.vue'
import { useExpenseRequestStore } from '@/stores/expenseRequestStore'

const expenseRequestStore = useExpenseRequestStore()
</script>
