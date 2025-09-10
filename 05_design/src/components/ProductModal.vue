<template>
  <div v-if="modelValue" class="fixed inset-0 bg-black/50 flex items-center justify-center">
    <div class="w-[444px] bg-white rounded-[8.75px] border border-black/10 shadow-[0_10px_15px_-3px_rgba(0,0,0,0.1),0_4px_6px_-2px_rgba(0,0,0,0.1)] p-[22px]">
      <div class="flex justify-between items-center mb-[18px]">
        <h2 class="text-base font-semibold leading-[1.531] text-black">{{ isEdit ? 'Edit' : 'Add' }} Product</h2>
        <button @click="$emit('update:modelValue', false)" class="text-[#717182]">
          <svg class="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
            <path d="M13 1L1 13M1 1L13 13" stroke="currentColor" stroke-width="1.17" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-xs leading-[1.458] text-[#717182] mb-1">Name</label>
          <input
            v-model="form.name"
            type="text"
            :disabled="isEdit"
            class="w-full h-8 px-3 rounded-[6.75px] border border-black/10 text-xs leading-[1.458] disabled:bg-gray-50"
            :class="{ 'border-red-500': v$.form.name.$error }"
            required
          />
          <span v-if="v$.form.name.$error" class="text-[10px] text-red-500">Name is required</span>
        </div>

        <div>
          <label class="block text-xs leading-[1.458] text-[#717182] mb-1">Price</label>
          <input
            v-model.number="form.price"
            type="number"
            step="0.01"
            class="w-full h-8 px-3 rounded-[6.75px] border border-black/10 text-xs leading-[1.458]"
            :class="{ 'border-red-500': v$.form.price.$error }"
            required
          />
          <span v-if="v$.form.price.$error" class="text-[10px] text-red-500">Price must be greater than 0</span>
        </div>

        <div>
          <label class="block text-xs leading-[1.458] text-[#717182] mb-1">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full px-3 py-2 rounded-[6.75px] border border-black/10 text-xs leading-[1.458] resize-none"
          ></textarea>
        </div>

        <div>
          <label class="block text-xs leading-[1.458] text-[#717182] mb-1">Stock</label>
          <input
            v-model.number="form.stock"
            type="number"
            class="w-full h-8 px-3 rounded-[6.75px] border border-black/10 text-xs leading-[1.458]"
            :class="{ 'border-red-500': v$.form.stock.$error }"
            required
          />
          <span v-if="v$.form.stock.$error" class="text-[10px] text-red-500">Stock must be 0 or greater</span>
        </div>

        <div class="mt-[30px] flex justify-end gap-2">
          <button
            type="button"
            @click="$emit('update:modelValue', false)"
            class="h-8 px-3.5 border border-black/10 rounded-[6.75px] text-xs font-medium leading-[1.458]"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="h-8 px-3.5 bg-[#030213] text-white rounded-[6.75px] text-xs font-medium leading-[1.458]"
          >
            {{ isEdit ? 'Save Changes' : 'Add Product' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required, minValue } from '@vuelidate/validators'

const props = defineProps({
  modelValue: Boolean,
  isEdit: Boolean,
  product: Object
})

const emit = defineEmits(['update:modelValue', 'submit'])

const form = ref({
  name: '',
  price: 0,
  description: '',
  stock: 0
})

const rules = computed(() => ({
  form: {
    name: { required },
    price: { required, minValue: minValue(0.01) },
    stock: { required, minValue: minValue(0) }
  }
}))

const v$ = useVuelidate(rules, { form })

watch(() => props.product, (newProduct) => {
  if (newProduct) {
    form.value = { ...newProduct }
  } else {
    form.value = { name: '', price: 0, description: '', stock: 0 }
  }
}, { immediate: true })

async function handleSubmit() {
  const result = await v$.value.$validate()
  if (!result) return

  emit('submit', {
    ...form.value,
    id: props.product?.id
  })
}
</script>
