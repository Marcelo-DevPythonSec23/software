import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.message)
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config = {}) {
    return this.client.get<T>(url, config)
  }

  async post<T>(url: string, data?: any, config = {}) {
    return this.client.post<T>(url, data, config)
  }

  async put<T>(url: string, data?: any, config = {}) {
    return this.client.put<T>(url, data, config)
  }

  async delete<T>(url: string, config = {}) {
    return this.client.delete<T>(url, config)
  }
}

export const apiClient = new ApiClient()
