import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import { formatDate, formatCurrency } from './utils/formatters'

import {
  setConfig,
  frappeRequest,
  resourcesPlugin,
  FrappeUI
} from 'frappe-ui'

import { createPinia } from 'pinia'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

const pinia = createPinia()
app.use(router)
app.use(resourcesPlugin)
app.use(pinia)
app.provide('formatDate', formatDate)
app.provide('formatCurrency', formatCurrency)
// app.use(FrappeUI)

app.mount('#app')
