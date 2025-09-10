<template>
  <div v-if="modelValue" class="fixed inset-0 bg-black/50 flex items-center justify-center">
    <div class="w-[444px] bg-white rounded-[8.75px] border border-black/10 shadow-[0_10px_15px_-3px_rgba(0,0,0,0.1),0_4px_6px_-2px_rgba(0,0,0,0.1)] p-[22px]">
      <div class="flex justify-between items-center mb-[18px]">
        <h2 class="text-base font-semibold leading-[1.531] text-black">Product Details</h2>
        <button @click="$emit('update:modelValue', false)" class="text-[#717182]">
          <svg class="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
            <path d="M13 1L1 13M1 1L13 13" stroke="currentColor" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-xs leading-[1.458] text-[#717182] mb-1">Name</label>
          <p class="text-xs leading-[1.458] text-black">{{ product?.name }}</p>
        </div>

        <div>
          <label class="block text-xs leading-[1.458] text-[#717182] mb-1">Price</label>
          <p class="text-xs leading-[1.458] text-black">${{ product?.price?.toFixed(2) }}</p>
        </div>

        <div>
          <label class="block text-xs leading-[1.458] text-[#717182] mb-1">Description</label>
          <p class="text-xs leading-[1.458] text-black">{{ product?.description || 'No description available' }}</p>
        </div>

        <div>
          <label class="block text-xs leading-[1.458] text-[#717182] mb-1">Stock</label>
          <p class="text-xs leading-[1.458] text-black">{{ product?.stock }}</p>
        </div>
      </div>

      <div class="mt-[30px] flex justify-end">
        <button
          @click="$emit('update:modelValue', false)"
          class="h-8 px-3.5 border border-black/10 rounded-[6.75px] text-xs font-medium leading-[1.458]"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  product: Object
})
</script>
