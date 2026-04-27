<template>
  <ion-page>
    <ion-content>
      <div class="header">
        <button class="back-btn" @click="goBack">‹</button>
        <h1>Добавление операции</h1>

        <div class="tabs">
          <span :class="{ active: type === 'expense' }" @click="setType('expense')">
            Расходы
          </span>
          <span :class="{ active: type === 'income' }" @click="setType('income')">
            Доходы
          </span>
        </div>
      </div>

      <div class="form">
        <div class="amount-row">
          <ion-input
            :value="amount"
            type="number"
            placeholder="0"
            class="amount-input"
            @ionInput="amount = String($event.detail.value || '')"
          />

          <ion-select
            :value="currency"
            class="currency-select"
            @ionChange="currency = String($event.detail.value || 'RUB')"
          >
            <ion-select-option value="RUB">RUB</ion-select-option>
            <ion-select-option value="EUR">EUR</ion-select-option>
            <ion-select-option value="USD">USD</ion-select-option>
            <ion-select-option value="RSD">RSD</ion-select-option>
          </ion-select>
        </div>

        <div class="section-title">Категории</div>

        <div class="categories-grid">
          <div
            v-for="category in categories"
            :key="category.id"
            class="category-item"
            :class="{ selected: selectedCategoryId === category.id }"
            @click="selectedCategoryId = category.id"
          >
            <div class="category-icon">
              {{ getCategoryIcon(category.name, type) }}
            </div>
            <div class="category-name">{{ category.name }}</div>
          </div>
        </div>

        <ion-item>
          <ion-input
            :value="comment"
            label="Комментарий"
            label-placement="floating"
            @ionInput="comment = String($event.detail.value || '')"
          />
        </ion-item>

        <ion-button expand="block" class="save-btn" @click="saveTransaction">
          Добавить
        </ion-button>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import {
  IonPage,
  IonContent,
  IonInput,
  IonSelect,
  IonSelectOption,
  IonItem,
  IonButton,
} from '@ionic/vue'

import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const type = ref('expense')
const amount = ref('')
const currency = ref('RUB')
const comment = ref('')
const categories = ref([])
const selectedCategoryId = ref(null)

const loadCategories = async () => {
  const response = await api.get(`/categories/?type=${type.value}`)
  categories.value = response.data
  selectedCategoryId.value = categories.value.length ? categories.value[0].id : null
}

const setType = async (newType) => {
  type.value = newType
  await loadCategories()
}

const saveTransaction = async () => {
  if (!amount.value || Number(amount.value) <= 0) {
    alert('Введите сумму больше 0')
    return
  }

  if (!selectedCategoryId.value) {
    alert('Выберите категорию')
    return
  }

  await api.post('/transactions/', {
    category_id: selectedCategoryId.value,
    type: type.value,
    amount: Number(amount.value),
    currency: currency.value,
    comment: comment.value,
  })

  router.push('/home')
}

const goBack = () => {
  router.push('/home')
}

const getCategoryIcon = (name, categoryType) => {
  const icons = {
    Здоровье: '❤',
    Досуг: '👛',
    Дом: '🏠',
    Кафе: '🍽',
    Образование: '🎓',
    Подарки: '🎁',
    Продукты: '🛒',
    Семья: '👨‍👩‍👧',
    Спорт: '💪',
    Транспорт: '🚌',
    Зарплата: '💼',
    Подарок: '🎁',
    'Проценты по вкладу': '💰',
  }

  return icons[name] || (categoryType === 'expense' ? '−' : '+')
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
ion-content {
  --background: #f7f8f3;
}

.header {
  background: #6c9f8c;
  color: white;
  padding: 22px 18px 26px;
  border-radius: 0 0 24px 24px;
  position: relative;
  text-align: center;
}

.back-btn {
  position: absolute;
  left: 16px;
  top: 20px;
  background: transparent;
  border: none;
  color: white;
  font-size: 42px;
  line-height: 1;
}

h1 {
  font-size: 24px;
  margin: 0 0 24px;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 70px;
  text-transform: uppercase;
  font-size: 20px;
}

.tabs span {
  opacity: 0.55;
  padding-bottom: 6px;
  cursor: pointer;
}

.tabs .active {
  opacity: 1;
  border-bottom: 3px solid white;
}

.form {
  padding: 24px 18px;
}

.amount-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 28px;
}

.amount-input {
  max-width: 130px;
  font-size: 34px;
  text-align: center;
  border-bottom: 2px solid #ccc;
}

.currency-select {
  max-width: 110px;
  font-size: 26px;
  color: #4f806f;
}

.section-title {
  color: #999;
  font-size: 18px;
  margin: 16px 0;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px 12px;
  margin-bottom: 24px;
}

.category-item {
  text-align: center;
  cursor: pointer;
}

.category-icon {
  width: 62px;
  height: 62px;
  margin: 0 auto 6px;
  border-radius: 50%;
  background: #dfe3e1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  border: 3px solid transparent;
}

.category-item.selected .category-icon {
  border-color: #f4c542;
  background: #fff3c4;
}

.category-name {
  font-size: 13px;
  color: #333;
}

ion-item {
  margin-top: 20px;
  border-radius: 14px;
  --background: #ffffff;
}

.save-btn {
  margin-top: 28px;
  --background: #f4c542;
  --color: #333;
  --border-radius: 24px;
}
</style>