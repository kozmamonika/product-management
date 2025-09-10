<template>
  <div class="fixed bottom-4 left-4 z-50">
    <!-- Cart Toggle Button -->
    <button
      @click="isExpanded = !isExpanded"
      class="bg-[#030213] text-white rounded-full p-3 shadow-lg hover:bg-black/90 transition-colors mb-2 flex items-center gap-2"
    >
      <svg class="w-5 h-5" viewBox="0 0 20 20" fill="none">
        <path d="M3 1H5L7 13H17L19 5H8" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="9" cy="17" r="1" stroke="white" stroke-width="1.5"/>
        <circle cx="15" cy="17" r="1" stroke="white" stroke-width="1.5"/>
      </svg>
      <span v-if="cart.item_count > 0" class="bg-red-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
        {{ cart.item_count }}
      </span>
    </button>

    <!-- Cart Panel -->
    <div
      v-if="isExpanded"
      class="bg-white rounded-lg shadow-xl border border-black/10 w-80 max-h-96 overflow-hidden"
    >
      <!-- Cart Header -->
      <div class="p-4 border-b border-gray-100 flex justify-between items-center">
        <h3 class="text-[13.2px] font-medium text-[#0A0A0A]">Shopping Cart</h3>
        <button
          v-if="cart.items.length > 0"
          @click="handleClearCart"
          class="text-[11.3px] text-red-600 hover:text-red-700"
        >
          Clear All
        </button>
      </div>

      <!-- Cart Items -->
      <div class="max-h-64 overflow-y-auto">
        <div v-if="cart.items.length === 0" class="p-4 text-center text-[#717182] text-[11.3px]">
          Your cart is empty
        </div>

        <div v-else>
          <div
            v-for="item in cart.items"
            :key="item.id"
            class="p-3 border-b border-gray-100 last:border-b-0"
          >
            <div class="flex justify-between items-start mb-2">
              <h4 class="text-[11.3px] font-medium text-[#0A0A0A] flex-1 pr-2">
                {{ item.product.name }}
              </h4>
              <button
                @click="handleRemoveItem(item.id)"
                class="text-red-600 hover:text-red-700 text-xs"
                title="Remove all"
              >
                ×
              </button>
            </div>
            <div class="flex justify-between items-center text-[10.7px] text-[#717182] mb-2">
              <span>${{ item.product.price.toFixed(2) }} × {{ item.quantity }}</span>
              <span class="font-medium text-[#030213]">${{ item.line_total.toFixed(2) }}</span>
            </div>
            <!-- Quantity Controls -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <button
                  @click="handleRemoveOne(item.id)"
                  class="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-xs font-medium"
                  title="Remove one"
                >
                  −
                </button>
                <span class="text-[11.3px] font-medium text-[#0A0A0A] min-w-[20px] text-center">
                  {{ item.quantity }}
                </span>
                <button
                  @click="handleAddOne(item.product_id)"
                  class="w-6 h-6 rounded-full bg-red-100 hover:bg-red-200 flex items-center justify-center text-xs font-medium"
                  title="Add one"
                >
                  +
                </button>
              </div>
              <span class="text-[10.7px] text-[#717182]">
                Stock: {{ item.product.stock }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Cart Total -->
      <div v-if="cart.items.length > 0" class="p-4 border-t border-gray-100 bg-gray-50">
        <div class="flex justify-between items-center">
          <span class="text-[12.8px] font-medium text-[#0A0A0A]">Total:</span>
          <span class="text-[12.8px] font-bold text-[#030213]">${{ cart.total.toFixed(2) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCart, removeFromCart, removeOneFromCart, addToCart, clearCart } from '../services/api'

const isExpanded = ref(false)
const cart = ref({
  items: [],
  total: 0,
  item_count: 0
})

const emit = defineEmits(['cartUpdated'])

async function fetchCart() {
  try {
    const response = await getCart()
    cart.value = response.data
    emit('cartUpdated', cart.value)
  } catch (error) {
    console.error('Error fetching cart:', error)
  }
}

async function handleRemoveOne(cartItemId) {
  try {
    await removeOneFromCart(cartItemId)
    await fetchCart()
  } catch (error) {
    if (error.response?.status === 204) {
      // Item was completely removed (quantity became 0)
      await fetchCart()
    } else {
      console.error('Error removing one item from cart:', error)
    }
  }
}

async function handleAddOne(productId) {
  try {
    await addToCart(productId, 1)
    await fetchCart()
  } catch (error) {
    console.error('Error adding one item to cart:', error)
    if (error.response?.status === 409) {
      alert(error.response.data.detail)
    }
  }
}

async function handleRemoveItem(cartItemId) {
  try {
    await removeFromCart(cartItemId)
    await fetchCart()
  } catch (error) {
    console.error('Error removing item from cart:', error)
  }
}

async function handleClearCart() {
  if (confirm('Are you sure you want to clear your cart?')) {
    try {
      await clearCart()
      await fetchCart()
    } catch (error) {
      console.error('Error clearing cart:', error)
    }
  }
}

// Expose fetchCart method to parent component
defineExpose({
  fetchCart
})

onMounted(() => {
  fetchCart()
})
</script>
