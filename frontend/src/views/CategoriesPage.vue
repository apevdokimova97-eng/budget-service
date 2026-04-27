<template>
  <ion-page>
    <ion-content>
      <div class="header">
        <button class="back-btn" @click="goBack">‹</button>
        <h1>Категории</h1>

        <div class="tabs">
          <span :class="{ active: type === 'expense' }" @click="setType('expense')">
            Расходы
          </span>
          <span :class="{ active: type === 'income' }" @click="setType('income')">
            Доходы
          </span>
        </div>
      </div>

      <div class="categories-grid">
        <div
          v-for="category in categories"
          :key="category.id"
          class="category-item"
        >
          <div
            class="category-icon"
            :style="{ background: category.color || getCategoryColor(category.name) }"
          >
            {{ getCategoryIcon(category) }}
          </div>

          <div class="category-name">{{ category.name }}</div>

          <button
            v-if="!isDefaultCategory(category.name)"
            class="delete-btn"
            @click="deleteCategory(category.id)"
          >
            удалить
          </button>
        </div>

        <div class="category-item create" @click="openCreate">
          <div class="category-icon plus">+</div>
          <div class="category-name">Создать</div>
        </div>
      </div>

      <div v-if="isCreating" class="modal">
        <div class="modal-card">
          <h2>Новая категория</h2>

          <ion-item>
            <ion-input
              :value="newCategoryName"
              label="Название"
              label-placement="floating"
              @ionInput="newCategoryName = String($event.detail.value || '')"
            />
          </ion-item>

          <ion-item>
            <ion-input
              :value="newCategoryColor"
              type="color"
              label="Цвет"
              label-placement="floating"
              @ionInput="newCategoryColor = String($event.detail.value || '#6c9f8c')"
            />
          </ion-item>

          <div class="icon-picker-row" @click="isIconPickerOpen = true">
            <span class="icon-picker-label">Иконка</span>
            <span class="icon-preview">{{ newCategoryIcon }}</span>
            <span class="icon-picker-arrow">›</span>
          </div>

          <ion-button expand="block" class="save-btn" @click="createCategory">
            Создать
          </ion-button>

          <ion-button fill="clear" expand="block" @click="closeCreate">
            Отмена
          </ion-button>
        </div>
      </div>

      <div v-if="isIconPickerOpen" class="icon-modal">
        <div class="icon-modal-card">
          <h2>Выберите иконку</h2>

          <div class="icons-grid">
            <button
              v-for="icon in availableIcons"
              :key="icon"
              class="icon-choice"
              :class="{ selected: newCategoryIcon === icon }"
              @click="selectIcon(icon)"
            >
              {{ icon }}
            </button>
          </div>

          <ion-button expand="block" fill="clear" @click="isIconPickerOpen = false">
            Закрыть
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import {
  IonPage,
  IonContent,
  IonItem,
  IonInput,
  IonButton,
} from '@ionic/vue'

import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const type = ref('expense')
const categories = ref([])

const isCreating = ref(false)
const isIconPickerOpen = ref(false)

const newCategoryName = ref('')
const newCategoryColor = ref('#6c9f8c')
const newCategoryIcon = ref('🧾')

const defaultCategoryNames = [
  'Дом',
  'Досуг',
  'Здоровье',
  'Кафе',
  'Образование',
  'Подарки',
  'Продукты',
  'Семья',
  'Спорт',
  'Транспорт',
  'Зарплата',
  'Подарок',
  'Проценты по вкладу',
]

const defaultColors = {
  Дом: '#ff8c32',
  Досуг: '#35b8a6',
  Здоровье: '#ff3b3b',
  Кафе: '#9b7be9',
  Образование: '#3a9edb',
  Подарки: '#e24d8e',
  Продукты: '#61b947',
  Семья: '#f5b400',
  Спорт: '#f27611',
  Транспорт: '#2f80d1',
  Зарплата: '#2f80d1',
  Подарок: '#e24d8e',
  'Проценты по вкладу': '#61b947',
}

const defaultIconsByName = {
  Дом: '🏠',
  Досуг: '👛',
  Здоровье: '❤',
  Кафе: '🍽',
  Образование: '🎓',
  Подарки: '🎁',
  Продукты: '🛒',
  Семья: '👨‍👩‍👧',
  Спорт: '💪',
  Транспорт: '🚌',
  Зарплата: '💼',
  Подарок: '🎁',
  'Проценты по вкладу': '🏦',
}

const defaultIconsByKey = {
  home: '🏠',
  wallet: '👛',
  heart: '❤',
  cafe: '🍽',
  education: '🎓',
  gift: '🎁',
  basket: '🛒',
  family: '👨‍👩‍👧',
  sport: '💪',
  transport: '🚌',
  salary: '💼',
  bank: '🏦',
}

const availableIcons = [
  '🏠','🛒','🍽','🚕','🎁','❤','💊','🎓',
  '💪','👨‍👩‍👧','🎮','🎬','✈️','🐶','👕','🧾',
  '💼','💰','🏦','📈','💳','🔁','⭐','➕',
  '☕','🍕','🚗','🚌','🧸','📱','💻','🏖',
  '🛠','🧼','🧴','💡','📚','🎧','🏥','🛍'
]

const loadCategories = async () => {
  const res = await api.get(`/categories/?type=${type.value}`)
  categories.value = res.data
}

const setType = async (newType) => {
  type.value = newType
  await loadCategories()
}

const openCreate = () => {
  newCategoryName.value = ''
  newCategoryColor.value = '#6c9f8c'
  newCategoryIcon.value = type.value === 'expense' ? '🧾' : '💰'
  isCreating.value = true
}

const closeCreate = () => {
  isCreating.value = false
}

const selectIcon = (icon) => {
  newCategoryIcon.value = icon
  isIconPickerOpen.value = false
}

const createCategory = async () => {
  if (!newCategoryName.value.trim()) {
    alert('Введите название категории')
    return
  }

  await api.post('/categories/', {
    name: newCategoryName.value.trim(),
    type: type.value,
    color: newCategoryColor.value,
    icon: newCategoryIcon.value,
  })

  isCreating.value = false
  await loadCategories()
}

const deleteCategory = async (id) => {
  if (!confirm('Удалить категорию?')) return

  try {
    await api.delete(`/categories/${id}`)
    await loadCategories()
  } catch {
    alert('Категорию нельзя удалить, если к ней привязаны операции')
  }
}

const isDefaultCategory = (name) => {
  return defaultCategoryNames.includes(name)
}

const getCategoryColor = (name) => {
  return defaultColors[name] || '#6c9f8c'
}

const getCategoryIcon = (category) => {
  if (category.icon && defaultIconsByKey[category.icon]) {
    return defaultIconsByKey[category.icon]
  }

  if (category.icon && category.icon.length <= 4) {
    return category.icon
  }

  return defaultIconsByName[category.name] || (category.type === 'income' ? '+' : '−')
}

const goBack = () => {
  router.push('/home')
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
  padding: 22px 18px 28px;
  border-radius: 0 0 24px 24px;
  text-align: center;
  position: relative;
}

.back-btn {
  position: absolute;
  left: 16px;
  top: 18px;
  border: none;
  background: transparent;
  color: white;
  font-size: 42px;
}

h1 {
  margin: 0 0 20px;
  font-size: 26px;
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

.categories-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px 12px;
  padding: 28px 18px;
}

.category-item {
  text-align: center;
  min-height: 96px;
}

.category-icon {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 7px;
  color: white;
  font-size: 25px;
}

.category-name {
  font-size: 13px;
  color: #222;
  line-height: 1.15;
}

.plus {
  background: #f4c542;
  color: #333;
  font-size: 34px;
}

.delete-btn {
  margin-top: 4px;
  border: none;
  background: transparent;
  color: #999;
  font-size: 11px;
}

.modal,
.icon-modal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 50;
}

.icon-modal {
  z-index: 70;
}

.modal-card,
.icon-modal-card {
  background: white;
  border-radius: 22px;
  padding: 24px;
  width: 100%;
  max-width: 360px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-card h2,
.icon-modal-card h2 {
  margin: 0 0 18px;
  color: #4f806f;
  text-align: center;
}

ion-item {
  margin-bottom: 12px;
  border-radius: 14px;
  --background: #ffffff;
}

.icon-picker-row {
  background: white;
  border-radius: 14px;
  padding: 12px 14px;
  margin-bottom: 12px;
  border-bottom: 1px solid #ddd;
  display: grid;
  grid-template-columns: 1fr 44px 20px;
  align-items: center;
  cursor: pointer;
}

.icon-picker-label {
  color: #555;
  font-size: 14px;
}

.icon-preview {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #f1f1f1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 23px;
}

.icon-picker-arrow {
  font-size: 28px;
  color: #777;
  transform: rotate(90deg);
}

.icons-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  margin: 16px 0;
}

.icon-choice {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid transparent;
  background: #f1f1f1;
  font-size: 22px;
  cursor: pointer;
}

.icon-choice.selected {
  border-color: #f4c542;
  background: #fff3c4;
}

.save-btn {
  margin-top: 14px;
  --background: #f4c542;
  --color: #333;
  --border-radius: 24px;
}
</style>