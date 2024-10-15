import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'


import {
  setConfig,
  frappeRequest,
  resourcesPlugin,
  FrappeUI
} from 'frappe-ui'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)
// app.use(FrappeUI)

app.mount('#app')
