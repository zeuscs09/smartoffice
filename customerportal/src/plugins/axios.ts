import axios from 'axios'

const instance = axios.create({
  headers: {
    'Content-Type': 'application/json',
  }
})

// Add a request interceptor
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('customer_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add a response interceptor
instance.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.message || error.message
    return Promise.reject(new Error(message))
  }
)

export default instance
