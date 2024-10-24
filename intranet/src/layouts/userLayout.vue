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
                <div class="flex-1 ">


                    <div class="flex-1">
                        <div class="flex items-center">
                            <img :src="cachedAppLogo" alt="App Logo" class="h-8 cursor-pointer mr-4" @click="router.push('/')" />
                            <div class="hidden lg:flex space-x-2">
                                <button class="btn btn-ghost btn-circle tooltip tooltip-bottom" @click="router.push({ name: 'ServiceReportList' })" data-tip="Service Report">
                                    <div class="indicator">
                                        <svg class="h-6" fill="#000000" viewBox="0 0 512 512" data-name="Layer 1" id="Layer_1"
                                            xmlns="http://www.w3.org/2000/svg">
                                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                            <g id="SVGRepo_iconCarrier">
                                                <title></title>
                                                <path
                                                    d="M219.59,292.5a8,8,0,0,1,0,11.31l-90.05,90.06a8,8,0,1,1-11.31-11.32l90.05-90.05A8,8,0,0,1,219.59,292.5Zm208.74,96A8,8,0,0,1,415,391.78l-27.15-27.15L373.1,379.39l27.16,27.17a8,8,0,0,1-3.32,13.3,51.5,51.5,0,0,1-15.08,2.21c-15.64,0-31.77-6.7-43.91-18.84-11.61-11.61-18.35-26.77-18.82-42.06l-52.38-52.39a8,8,0,0,1-1.77-1.33l-5.57-5.57a43.89,43.89,0,0,1-11.05,18.41l-97.47,97.47a43.34,43.34,0,0,1-29.17,12.84l-1.5,0a38.51,38.51,0,0,1-27.56-11.22c-15.59-15.59-14.85-41.71,1.66-58.22l97.47-97.47a44,44,0,0,1,18.4-11.05l-5.55-5.55a8,8,0,0,1-1.33-1.77l-52.55-52.56c-15.28-.46-30.43-7.2-42-18.81-16.11-16.13-22.64-39.27-16.64-59a8,8,0,0,1,13.31-3.32l27.16,27.15,14.76-14.77L120.15,96.91a8,8,0,0,1,3.32-13.31c19.71-6,42.87.51,59,16.63,11.62,11.61,18.36,26.77,18.83,42.07l70,70L379.11,104.42A7.71,7.71,0,0,1,381,103L418.3,83A8,8,0,0,1,429.13,93.8l-20.08,37.3a8,8,0,0,1-1.39,1.87L299.81,240.82l69.85,69.85c15.28.46,30.42,7.2,42,18.81C427.81,345.61,434.33,368.76,428.33,388.46ZM282.73,278.38l-49-49-11.89,11.88,49,49Zm-16.16-38.8,5.93,5.93,123-123,6.9-12.82-12.83,6.89ZM159.73,179.14l50.79,50.79,17.54-17.54a8,8,0,0,1,11.31,0l15.88,15.88,4.69-4.69-72.31-72.31a8,8,0,0,1-2.34-5.93c.41-12.08-4.74-24.4-14.14-33.79a47.85,47.85,0,0,0-27.61-13.88l20.74,20.75a8,8,0,0,1,0,11.31L138.2,155.81a8,8,0,0,1-11.31,0l-20.73-20.73A48,48,0,0,0,120,162.67c9.4,9.39,21.71,14.54,33.77,14.13h.28A8,8,0,0,1,159.73,179.14Zm85.41,108.47-20.68-20.67A27.17,27.17,0,0,0,203.11,275L105.63,372.5c-10.27,10.27-11,26.24-1.65,35.6a22.78,22.78,0,0,0,17.17,6.51,27.4,27.4,0,0,0,18.42-8.16L237.05,309a27.4,27.4,0,0,0,8.16-18.42A24,24,0,0,0,245.14,287.61Zm169.11,80.77a47.87,47.87,0,0,0-13.87-27.58c-9.4-9.4-21.71-14.54-33.76-14.13a8,8,0,0,1-5.93-2.34L288.5,252.14l-4.69,4.69,15.89,15.9a8,8,0,0,1,0,11.31l-17.53,17.53,50.61,50.63a8,8,0,0,1,2.34,5.92c-.4,12.08,4.75,24.4,14.14,33.8a47.89,47.89,0,0,0,27.61,13.87l-20.74-20.74a8,8,0,0,1,0-11.32l26.08-26.08a8,8,0,0,1,11.31,0Z">
                                                </path>
                                            </g>
                                        </svg>
                                    </div>
                                </button>
                                <button class="btn btn-ghost btn-circle tooltip tooltip-bottom" data-tip="Expense Entry" @click="router.push({ name: 'ExpenseEntryList' })">
                                    <svg class="h-6" viewBox="0 0 76 76" xmlns="http://www.w3.org/2000/svg"
                                        xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" baseProfile="full"
                                        enable-background="new 0 0 76.00 76.00" xml:space="preserve" fill="#000000">
                                        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                        <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                        <g id="SVGRepo_iconCarrier">
                                            <path fill="#000000" fill-opacity="1" stroke-width="0.2" stroke-linejoin="round"
                                                d="M 15.8333,23.75L 40.7708,23.75L 36.0208,28.5L 17.4166,28.5L 17.4166,47.5L 58.5833,47.5L 58.5833,28.5L 50.2708,28.5L 55.0208,23.75L 60.1667,23.75C 61.9156,23.75 63.3333,25.1678 63.3333,26.9167L 63.3333,49.0833C 63.3333,50.8322 61.9156,52.25 60.1667,52.25L 15.8333,52.25C 14.0844,52.25 12.6667,50.8322 12.6667,49.0833L 12.6667,26.9167C 12.6667,25.1678 14.0844,23.75 15.8333,23.75 Z M 31.2708,57L 44.7291,57L 37.9999,63.7292L 31.2708,57 Z M 55.0621,16.1879C 55.5053,16.6596 55.727,17.1679 55.727,17.7128L 55.5562,18.515L 55.0621,19.2378L 45.5648,28.735L 43.1676,31.1322L 40.868,33.4318L 38.8094,35.4905L 37.0954,37.1954L 35.8663,38.4153L 35.2563,39.0253L 34.2651,39.9311L 32.8621,41.0382L 31.3281,41.9714C 30.8076,42.2317 30.344,42.3618 29.9373,42.3618C 29.6201,42.3618 29.366,42.2663 29.1749,42.0751C 28.9837,41.884 28.8882,41.6238 28.8882,41.2944C 28.8882,40.8877 29.0183,40.4272 29.2786,39.9128L 30.2118,38.3787L 31.3098,36.9758L 32.2064,35.9937L 52.0122,16.1879L 52.735,15.6938L 53.5372,15.523C 54.0821,15.523 54.5904,15.7447 55.0621,16.1879 Z M 27.6499,42.0751L 29.1749,43.6001L 26.125,45.125L 27.6499,42.0751 Z ">
                                            </path>
                                        </g>
                                    </svg>
                                </button>
                                <button class="btn btn-ghost btn-circle tooltip tooltip-bottom" data-tip="Expense Request" @click="router.push({ name: 'ExpenseRequestList' })">
                                    <div class="indicator">
                                        <svg class="h-6" fill="#000000" viewBox="0 0 16 16" id="request-refund-16px"
                                            xmlns="http://www.w3.org/2000/svg">
                                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                            <g id="SVGRepo_iconCarrier">
                                                <path id="Path_45" data-name="Path 45"
                                                    d="M-16,11a2,2,0,0,0,2-2,2,2,0,0,0-2-2,2,2,0,0,0-2,2A2,2,0,0,0-16,11Zm0-3a1,1,0,0,1,1,1,1,1,0,0,1-1,1,1,1,0,0,1-1-1A1,1,0,0,1-16,8Zm2.5,4h-5A2.5,2.5,0,0,0-21,14.5,1.5,1.5,0,0,0-19.5,16h7A1.5,1.5,0,0,0-11,14.5,2.5,2.5,0,0,0-13.5,12Zm1,3h-7a.5.5,0,0,1-.5-.5A1.5,1.5,0,0,1-18.5,13h5A1.5,1.5,0,0,1-12,14.5.5.5,0,0,1-12.5,15Zm5-15h-7A2.5,2.5,0,0,0-17,2.5v3a.5.5,0,0,0,.5.5.5.5,0,0,0,.5-.5v-3A1.5,1.5,0,0,1-14.5,1h3V2A1.5,1.5,0,0,0-13,3.5,1.5,1.5,0,0,0-11.5,5V6h-1a.5.5,0,0,0-.5.5.5.5,0,0,0,.5.5h1v.5A.5.5,0,0,0-11,8a.5.5,0,0,0,.5-.5V7A1.5,1.5,0,0,0-9,5.5,1.5,1.5,0,0,0-10.5,4V3h1A.5.5,0,0,0-9,2.5.5.5,0,0,0-9.5,2h-1V1h3A1.5,1.5,0,0,1-6,2.5v5A1.5,1.5,0,0,1-7.5,9h-3a.5.5,0,0,0-.354.146L-12,10.293V9.5a.5.5,0,0,0-.5-.5.5.5,0,0,0-.5.5v2a.5.5,0,0,0,.309.462A.489.489,0,0,0-12.5,12a.5.5,0,0,0,.354-.146L-10.293,10H-7.5A2.5,2.5,0,0,0-5,7.5v-5A2.5,2.5,0,0,0-7.5,0ZM-10,5.5a.5.5,0,0,1-.5.5V5A.5.5,0,0,1-10,5.5ZM-11.5,4a.5.5,0,0,1-.5-.5.5.5,0,0,1,.5-.5Z"
                                                    transform="translate(21)"></path>
                                            </g>
                                        </svg>
                                    </div>
                                </button>
                                <button class="btn btn-ghost btn-circle tooltip tooltip-bottom" data-tip="Advance Request" @click="router.push({ name: 'AdvanceRequestList' })">
                                    <div class="indicator">
                                        <svg class="h-6" fill="#000000" viewBox="-2.5 0 19 19"
                                            xmlns="http://www.w3.org/2000/svg">
                                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                            <g id="SVGRepo_iconCarrier">
                                                <path
                                                    d="M8.978 14.043a4.224 4.224 0 0 0 1.077.139h.032v1.03a.435.435 0 0 1-.434.433H1.094a.435.435 0 0 1-.434-.434V3.237a.435.435 0 0 1 .434-.434h8.559a.435.435 0 0 1 .434.434v1.38l-.55.002a1.334 1.334 0 0 0-.559.124v-.832h-7.21v10.626h7.21v-.494zM4.995 7.452a1.068 1.068 0 0 1 .264.702 1.044 1.044 0 0 1-.524.902 1.677 1.677 0 0 1-.525.219v.238a.396.396 0 1 1-.792 0V9.28a1.844 1.844 0 0 1-.341-.107 1.19 1.19 0 0 1-.457-.335.396.396 0 1 1 .599-.518.413.413 0 0 0 .152.118 1.089 1.089 0 0 0 .205.066 1.616 1.616 0 0 0 .223.027.975.975 0 0 0 .505-.14c.163-.105.163-.194.163-.237a.28.28 0 0 0-.069-.181.637.637 0 0 0-.167-.135.86.86 0 0 0-.208-.074.98.98 0 0 0-.204-.02 2.058 2.058 0 0 1-.344-.028 1.575 1.575 0 0 1-.444-.143 1.287 1.287 0 0 1-.422-.34 1.09 1.09 0 0 1-.25-.682 1.103 1.103 0 0 1 .548-.933 1.66 1.66 0 0 1 .511-.208v-.228a.396.396 0 0 1 .792 0v.239a1.904 1.904 0 0 1 .348.121 1.369 1.369 0 0 1 .4.276.396.396 0 0 1-.559.56.578.578 0 0 0-.166-.114 1.121 1.121 0 0 0-.212-.074l-.023-.005a1.057 1.057 0 0 0-.174-.03.977.977 0 0 0-.494.132.32.32 0 0 0-.18.264.31.31 0 0 0 .074.183.503.503 0 0 0 .161.13.796.796 0 0 0 .22.071 1.27 1.27 0 0 0 .214.017 1.774 1.774 0 0 1 .373.038 1.654 1.654 0 0 1 .407.148 1.423 1.423 0 0 1 .396.314zm.881 3.186a4.195 4.195 0 0 0 .274.95H2.399v-.95zm1.184 2.303a4.25 4.25 0 0 0 .656.537H2.4v-.95h4.298a4.28 4.28 0 0 0 .363.413zm1.291-7.974H5.885v.95H8.35zm-1.193 1.89q-.05.047-.098.095a4.229 4.229 0 0 0-.661.856h-.514v-.95zm5.51 1.099a3.285 3.285 0 1 1-3.088-1.26v-.259h-.038a.475.475 0 0 1-.002-.95l1.026-.003h.001a.475.475 0 0 1 .002.95h-.04v.262a3.266 3.266 0 0 1 1.46.595l.336-.336a.475.475 0 0 1 .671.672l-.328.328zm-1.056 3.519a.475.475 0 0 0 0-.672L10.53 9.72V8.067a.475.475 0 0 0-.95 0V9.92a.474.474 0 0 0 .174.368l1.186 1.186a.475.475 0 0 0 .672 0z">
                                                </path>
                                            </g>
                                        </svg>
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex-none">

                    <button class="btn btn-ghost btn-circle tooltip tooltip-bottom" data-tip="Task" @click="router.push({ name: 'TaskList' })">
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
                    <button class="btn btn-ghost btn-circle tooltip tooltip-bottom" data-tip="Work Load" @click="router.push({ name: 'WorkLoad' })">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    </button>
                    <button class="btn btn-ghost btn-circle tooltip tooltip-bottom" data-tip="Mail Box" @click="router.push({ name: 'MailBoxList' })">
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
import { ref, onMounted, computed, watch } from 'vue'

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

const cachedAppLogo = ref('')
const appTitle = ref('')
const appFavicon = ref('')

const navbarSettingsResource = createResource({
    url: 'smartoffice.api.sitesetting.get_site_info',
    auto: true,
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

    // ใช้ logo จาก cache ก่อน
    cachedAppLogo.value = localStorage.getItem('appLogo') || ''

    navbarSettingsResource.submit().then(() => {
        if (navbarSettingsResource.data) {
            updateAppLogo(navbarSettingsResource.data.logo)
            appTitle.value = navbarSettingsResource.data.title
            appFavicon.value = navbarSettingsResource.data.favicon
            updateHeadTags()
        }
    })
})

function updateAppLogo(newLogo: string) {
    if (newLogo !== cachedAppLogo.value) {
        cachedAppLogo.value = newLogo
        localStorage.setItem('appLogo', newLogo)
    }
}

const totalTasks = computed(() => taskResource.data?.total || 0)
const totalMail = computed(() => mailboxResource.data?.total || 0)
const handleLogout = async () => {
    session.logout.submit()
}

function updateHeadTags() {
    // อัพเดท title
    document.title = appTitle.value

    // อัพเดท favicon
    let link = document.querySelector("link[rel~='icon']") as HTMLLinkElement
    if (!link) {
        link = document.createElement('link')
        link.rel = 'icon'
        document.head.appendChild(link)
    }
    link.href = appFavicon.value
}

// เพิ่ม watch เพื่อติดตามการเปลี่ยนแปลงของ appTitle และ appFavicon
watch([appTitle, appFavicon], () => {
    updateHeadTags()
})

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


