<template>
  <div class="max-w-7xl mx-auto">
    <!-- Header -->
    <h1 class="text-[13.2px] leading-[1.59] text-[#0A0A0A]">Product Management</h1>

    <!-- Search and Add -->
    <div class="mt-[49px] mb-[51.5px] flex items-center justify-between">
      <div class="relative w-[392px]">
        <input
          v-model="search"
          type="text"
          placeholder="Search products..."
          class="w-full h-[31.5px] px-[35px] py-2 bg-[#F3F3F5] rounded-[6.75px] text-[10.7px] leading-[1.37] text-[#0A0A0A] placeholder-[#0A0A0A] focus:outline-none"
        />
        <svg class="absolute left-3 top-2 w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
          <path d="M13.25 13.25L9.5 9.5M11 6C11 8.76142 8.76142 11 6 11C3.23858 11 1 8.76142 1 6C1 3.23858 3.23858 1 6 1C8.76142 1 11 3.23858 11 6Z" stroke="black" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <button
        @click="isAddingProduct = true"
        class="inline-flex items-center gap-2 bg-[#030213] text-white rounded-[6.75px] px-[14.42px] h-[31.5px] text-[11.3px] leading-[1.55] font-medium hover:bg-black/90 transition-colors"
      >
        <svg class="w-2 h-2" viewBox="0 0 8 8" fill="none">
          <path d="M4 0V8M8 4H0" stroke="white" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Add Product
      </button>
    </div>

    <!-- Products Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div v-for="product in filteredProducts" :key="product.id" class="bg-white rounded-[12.75px] border border-black/10 p-6 flex flex-col">
        <h4 class="text-[13.2px] leading-[1.06] text-[#0A0A0A] mb-4">{{ product.name }}</h4>
        <p class="text-[11.3px] leading-[1.55] text-[#717182] mb-4 flex-grow">{{ product.description || 'No description available' }}</p>
        <div class="flex justify-between items-center mb-3.5">
          <span class="text-[11.3px] leading-[1.55] text-[#717182]">Stock: {{ product.stock }}</span>
          <span class="text-[12.8px] leading-[1.64] font-medium text-[#030213]">${{ product.price.toFixed(2) }}</span>
        </div>
        <div class="flex gap-2 mb-3">
          <button
            @click="viewingProduct = product"
            class="inline-flex items-center gap-1 border border-black/10 rounded-[6.75px] px-3 py-1.5 text-[11.3px] leading-[1.55] font-medium hover:bg-gray-50 transition-colors"
          >
            <span>View</span>
            <svg class="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
              <path d="M6.41667 3.5H3.5V10.5H10.5V7.58333" stroke="black" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 7L10.5 3.5" stroke="black" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button
            @click="startEdit(product)"
            class="inline-flex items-center gap-1 border border-black/10 rounded-[6.75px] px-3 py-1.5 text-[11.3px] leading-[1.55] font-medium hover:bg-gray-50 transition-colors"
          >
            <span>Edit</span>
            <svg class="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
              <path d="M7.36667 2.63333L11.3667 6.63333" stroke="black" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2.63333 11.3667V7.36667L9.91667 0.083333C10.2247 -0.224892 10.7753 -0.224892 11.0833 0.083333L13.9167 2.91667C14.2249 3.22473 14.2249 3.77527 13.9167 4.08333L6.63333 11.3667H2.63333Z" stroke="black" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button
            @click="deletingProduct = product"
            class="inline-flex items-center justify-center w-[31.5px] bg-[#D4183D] rounded-[6.75px] hover:bg-red-700 transition-colors"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
              <path d="M11.6667 3.5L2.33333 3.5" stroke="white" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M5.83333 6.41667V9.91667" stroke="white" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8.16667 6.41667V9.91667" stroke="white" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M10.5 3.5V11.0833C10.5 11.4555 10.3771 11.8126 10.1583 12.0782C9.93958 12.3437 9.63768 12.5 9.32292 12.5H4.67708C4.36232 12.5 4.06042 12.3437 3.84171 12.0782C3.623 11.8126 3.5 11.4555 3.5 11.0833V3.5" stroke="white" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8.75 3.5V2.04167C8.75 1.85725 8.67559 1.68077 8.54354 1.54873C8.41149 1.41668 8.23501 1.34227 8.05059 1.34227H5.94941C5.76499 1.34227 5.58851 1.41668 5.45646 1.54873C5.32441 1.68077 5.25 1.85725 5.25 2.04167V3.5" stroke="white" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        <!-- Add to Cart Button -->
        <button
          @click="handleAddToCart(product)"
          :disabled="product.stock === 0 || addingToCart === product.id"
          class="w-full inline-flex items-center justify-center gap-2 bg-red-400 text-white rounded-[6.75px] px-3 py-2 text-[11.3px] leading-[1.55] font-medium hover:bg-red-500 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          <svg v-if="addingToCart === product.id" class="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
            <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          <svg v-else class="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
            <path d="M7 0V14M14 7H0" stroke="white" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span v-if="addingToCart === product.id">Adding...</span>
          <span v-else-if="product.stock === 0">Out of Stock</span>
          <span v-else>Add to Cart</span>
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!products.length" class="text-center py-8 text-[#717182]">
      <p>No products found. Add your first product to get started.</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8 text-[#717182]">
      <p>Loading products...</p>
    </div>

    <!-- Modals -->
    <ProductModal
      v-model="isAddingProduct"
      :is-edit="false"
      @submit="handleAdd"
    />

    <ProductModal
      v-model="editingProduct"
      :product="editingProduct"
      :is-edit="true"
      @submit="handleEdit"
    />

    <ProductDetailsModal
      v-model="viewingProduct"
      :product="viewingProduct"
    />

    <DeleteProductModal
      v-model="deletingProduct"
      :product="deletingProduct"
      @delete="handleDelete"
    />

    <!-- Shopping Cart -->
    <ShoppingCart ref="cartRef" @cartUpdated="handleCartUpdated" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getProducts, createProduct, updateProduct, deleteProduct, addToCart } from '../services/api'
import ProductModal from './ProductModal.vue'
import ProductDetailsModal from './ProductDetailsModal.vue'
import DeleteProductModal from './DeleteProductModal.vue'
import ShoppingCart from './ShoppingCart.vue'

const products = ref([])
const search = ref('')
const loading = ref(false)
const isAddingProduct = ref(false)
const editingProduct = ref(null)
const viewingProduct = ref(null)
const deletingProduct = ref(null)
const addingToCart = ref(null)
const cartRef = ref(null)

const filteredProducts = computed(() => {
  if (!search.value) return products.value
  const searchTerm = search.value.toLowerCase()
  return products.value.filter(p =>
    p.name.toLowerCase().includes(searchTerm) ||
    (p.description && p.description.toLowerCase().includes(searchTerm))
  )
})

async function fetchProducts() {
  loading.value = true
  try {
    const response = await getProducts()
    products.value = response.data
  } catch (error) {
    console.error('Error fetching products:', error)
  } finally {
    loading.value = false
  }
}

async function handleAdd(formData) {
  try {
    await createProduct(formData)
    await fetchProducts()
    isAddingProduct.value = false
  } catch (error) {
    console.error('Error adding product:', error)
  }
}

function startEdit(product) {
  editingProduct.value = { ...product }
}

async function handleEdit(formData) {
  try {
    await updateProduct(formData.id, {
      price: formData.price,
      stock: formData.stock
    })
    await fetchProducts()
    editingProduct.value = null
  } catch (error) {
    console.error('Error updating product:', error)
  }
}

async function handleDelete() {
  if (!deletingProduct.value) return

  try {
    await deleteProduct(deletingProduct.value.id)
    await fetchProducts()
    deletingProduct.value = null
  } catch (error) {
    console.error('Error deleting product:', error)
  }
}

async function handleAddToCart(product) {
  if (product.stock === 0) return

  addingToCart.value = product.id
  try {
    await addToCart(product.id, 1)
    await fetchProducts() // Refresh products to update stock
    if (cartRef.value) {
      await cartRef.value.fetchCart() // Refresh cart
    }
  } catch (error) {
    console.error('Error adding to cart:', error)
    if (error.response?.status === 409) {
      alert(error.response.data.detail)
    }
  } finally {
    addingToCart.value = null
  }
}

function handleCartUpdated() {
  // Refresh products when cart is updated (e.g., items removed)
  fetchProducts()
}

// Fetch products on component mount
fetchProducts()
</script>
