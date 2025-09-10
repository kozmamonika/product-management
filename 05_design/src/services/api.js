import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const getProducts = () => axios.get(`${API_BASE_URL}/products/`)
export const getProduct = (id) => axios.get(`${API_BASE_URL}/products/${id}`)
export const createProduct = (data) => axios.post(`${API_BASE_URL}/products/`, data)
export const updateProduct = (id, data) => axios.put(`${API_BASE_URL}/products/${id}`, data)
export const deleteProduct = (id) => axios.delete(`${API_BASE_URL}/products/${id}`)
