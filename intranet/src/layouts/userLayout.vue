<template>

    <div class="container mx-auto bg-base-200 min-h-screen">

        <div class="drawer-content flex flex-col">
            <!-- Navbar -->
            <div class="navbar bg-base-100">
                <div class="flex-none lg:hidden">
                    <label for="my-drawer-2" class="btn btn-square btn-ghost">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                            class="inline-block w-6 h-6 stroke-current">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M4 6h16M4 12h16M4 18h16"></path>
                        </svg>
                    </label>
                </div>
                <div class="flex-1">
                    <img src="http://smarterp.localhost/files/logo.png" alt="TPS Logo" class="h-8 cursor-pointer"
                        @click="router.push('/')" />
                </div>
                <div class="flex-none">
                    <!-- <button class="btn btn-ghost btn-circle">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </button> -->
                    <button class="btn btn-ghost btn-circle" @click="router.push({ name: 'TaskList' })">
                        <div class="indicator">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
                                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                <g id="SVGRepo_iconCarrier">
                                    <path d="M11 19.5H21" stroke="currentColor" stroke-width="1.5"
                                        stroke-linecap="round" stroke-linejoin="round"></path>
                                    <path d="M11 12.5H21" stroke="currentColor" stroke-width="1.5"
                                        stroke-linecap="round" stroke-linejoin="round"></path>
                                    <path d="M11 5.5H21" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
                                        stroke-linejoin="round"></path>
                                    <path d="M3 5.5L4 6.5L7 3.5" stroke="currentColor" stroke-width="1.5"
                                        stroke-linecap="round" stroke-linejoin="round"></path>
                                    <path d="M3 12.5L4 13.5L7 10.5" stroke="currentColor" stroke-width="1.5"
                                        stroke-linecap="round" stroke-linejoin="round"></path>
                                    <path d="M3 19.5L4 20.5L7 17.5" stroke="currentColor" stroke-width="1.5"
                                        stroke-linecap="round" stroke-linejoin="round"></path>
                                </g>
                            </svg>
                            <span v-if="totalTasks > 0" class="badge badge-xs badge-primary indicator-item">{{
                                totalTasks }}</span>
                        </div>
                    </button>
                    <button class="btn btn-ghost btn-circle" @click="router.push({ name: 'WorkLoad' })">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    </button>
                    <button class="btn btn-ghost btn-circle" @click="router.push({ name: 'MailBoxList' })">
                        <div class="indicator">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
                                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                <g id="SVGRepo_iconCarrier">
                                    <path
                                        d="M3 8L10.8906 13.2604C11.5624 13.7083 12.4376 13.7083 13.1094 13.2604L21 8M5 19H19C20.1046 19 21 18.1046 21 17V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V17C3 18.1046 3.89543 19 5 19Z"
                                        stroke="#000000" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round"></path>
                                </g>
                            </svg>
                            <span v-if="totalMail > 0" class="badge badge-xs badge-primary indicator-item">{{ totalMail
                                }}</span>
                        </div>
                    </button>

                    <div class="dropdown dropdown-end">
                        <label tabindex="0" class="btn btn-ghost btn-circle avatar">
                            <div class="avatar">
                                <div class="w-8 rounded-full">
                                    <template v-if="userImage">
                                        <img :src="userImage" alt="User avatar" />
                                    </template>
                                    <template v-else>
                                        <div
                                            class="bg-primary text-primary-content flex items-center justify-center w-full h-full">
                                            {{ getInitials(fullName) }}
                                        </div>
                                    </template>
                                </div>
                            </div>
                        </label>
                        <ul tabindex="0"
                            class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
                            <li><a :href="`/app/user/${session.user}`">Profile</a></li>
                            <li><a href="/app">Desk</a></li>
                            <li><a @click="handleLogout">Logout</a></li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Page content here -->
            <div class="p-4 bg-base-100 flex-grow shadow-lg rounded-sm m-4">
                <slot></slot>
            </div>
        </div>

    </div>


</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { session } from '../data/session'
import { createResource } from 'frappe-ui'
import { ref, onMounted, computed } from 'vue'

const router = useRouter()
const fullName = ref('')
const userImage = ref('')
const taskResource = createResource({
    url: 'smartoffice.api.task.get_todos_with_smo_tasks',
    auto: false,
})

const mailboxResource = createResource({
    url: 'smartoffice.api.mailbox.get_mail_box',
    auto: false,
})

onMounted(() => {
    taskResource.fetch({
        page: 1,
        page_size: 1,
        status: 'Open',
    })
    mailboxResource.fetch({
        page: 1,
        page_size: 1,
        status: 'unread',
    })
    fullName.value = getCookie('full_name') || ''
    userImage.value = getCookie('user_image') || ''
})

const totalTasks = computed(() => taskResource.data?.total || 0)
const totalMail = computed(() => mailboxResource.data?.total || 0)
const handleLogout = async () => {
    session.logout.submit()
}


function getCookie(name: string) {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop()?.split(';').shift()
}

const getInitials = (name: string) => {
    return name.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2)
}
</script>

<style scoped>
/* Add any custom styles here */
</style>
