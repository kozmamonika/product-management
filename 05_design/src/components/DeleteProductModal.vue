<template>
  <div v-if="modelValue" class="fixed inset-0 bg-black/50 flex items-center justify-center">
    <div class="w-[444px] bg-white rounded-[8.75px] border border-black/10 shadow-[0_10px_15px_-3px_rgba(0,0,0,0.1),0_4px_6px_-2px_rgba(0,0,0,0.1)] p-[22px]">
      <div class="flex justify-between items-center mb-[18px]">
        <h2 class="text-base font-semibold leading-[1.531] text-black">Delete Product</h2>
        <button @click="$emit('update:modelValue', false)" class="text-[#717182]">
          <svg class="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
            <path d="M13 1L1 13M1 1L13 13" stroke="currentColor" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <p class="text-xs leading-[1.458] text-[#717182]">
        Are you sure you want to delete "{{ product?.name }}"? This action cannot be undone.
      </p>

      <div class="mt-[30px] flex justify-end gap-2">
        <button
          @click="$emit('update:modelValue', false)"
          class="h-8 px-3.5 border border-black/10 rounded-[6.75px] text-xs font-medium leading-[1.458]"
        >
          Cancel
        </button>
        <button
          @click="handleDelete"
          class="h-8 px-3.5 bg-[#D4183D] text-white rounded-[6.75px] text-xs font-medium leading-[1.458]"
        >
          Delete Product
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

const emit = defineEmits(['update:modelValue', 'delete'])

function handleDelete() {
  emit('delete')
  emit('update:modelValue', false)
}
</script>
