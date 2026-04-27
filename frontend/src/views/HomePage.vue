<template>
  <ion-page>
    <ion-content
      :scroll-events="true"
      @ionScroll="handleScroll"
      @wheel="collapseChart"
      @touchmove="collapseChart"
    >
      <div class="header">
        <button class="menu-btn" @click="openMenu">☰</button>

        <div class="title">
          {{ summary.balance >= 0 ? 'ОСТАТОК' : 'ДОЛГ' }}
        </div>
        <div class="balance">{{ summary.free_balance ?? summary.balance }} {{ currencySymbol }}</div>

        <div class="tabs">
          <span :class="{ active: activeTab === 'expense' }" @click="setActiveTab('expense')">
            Расходы
          </span>
          <span :class="{ active: activeTab === 'income' }" @click="setActiveTab('income')">
            Доходы
          </span>
        </div>
      </div>

      <div class="main-card">
        <div class="period-tabs">
          <span :class="{ activePeriod: period === 'day' }" @click="setPeriod('day')">День</span>
          <span :class="{ activePeriod: period === 'week' }" @click="setPeriod('week')">Неделя</span>
          <span :class="{ activePeriod: period === 'month' }" @click="setPeriod('month')">Месяц</span>
          <span :class="{ activePeriod: period === 'year' }" @click="setPeriod('year')">Год</span>
          <span :class="{ activePeriod: period === 'custom' }" @click="openCustomPeriod">Период</span>
        </div>

        <div class="period-label">{{ periodLabel }}</div>

        <div v-if="!isScrolled" class="donut-wrap">
          <div class="donut" :style="donutStyle">
            <div class="donut-inner">
              <template v-if="currentTotal > 0">
                {{ currentTotal }} {{ currencySymbol }}
              </template>
              <template v-else>
                За выбранный период данных не было
              </template>
            </div>
          </div>
        </div>

        <div v-else class="mini-chart-wrap">
          <div class="mini-chart">
            <div
              v-for="item in currentItems"
              :key="item.category"
              class="mini-part"
              :style="{
                width: getPercent(item.total) + '%',
                background: getItemColor(item)
              }"
            ></div>
          </div>

          <div class="mini-total">
            {{ currentTotal }} {{ currencySymbol }}
          </div>
        </div>

        <button class="add-btn" @click="goToAdd">+</button>
      </div>

      <div class="category-list">
        <div
          v-for="item in currentItems"
          :key="item.category"
          class="category-card"
        >
          <div class="category-left">
            <div class="category-icon" :style="{ background: getItemColor(item) }">
              {{ getCategoryIcon(item.category, activeTab) }}
            </div>

            <span>{{ item.category }}</span>
          </div>

          <div class="category-percent">
            {{ getPercent(item.total) }}%
          </div>

          <strong>{{ item.total }} {{ currencySymbol }}</strong>
        </div>
      </div>

      <ion-modal :is-open="isCustomModalOpen" @didDismiss="isCustomModalOpen = false">
        <ion-content class="modal-content">
          <div class="modal-card">
            <h2>Выбор периода</h2>

            <ion-item>
              <ion-input
                :value="customDateFrom"
                type="date"
                label="Дата начала"
                label-placement="floating"
                @ionInput="customDateFrom = String($event.detail.value || '')"
              />
            </ion-item>

            <ion-item>
              <ion-input
                :value="customDateTo"
                type="date"
                label="Дата окончания"
                label-placement="floating"
                @ionInput="customDateTo = String($event.detail.value || '')"
              />
            </ion-item>

            <ion-button expand="block" class="apply-btn" @click="applyCustomPeriod">
              Применить
            </ion-button>

            <ion-button expand="block" fill="clear" @click="isCustomModalOpen = false">
              Отмена
            </ion-button>
          </div>
        </ion-content>
      </ion-modal>
    </ion-content>
  </ion-page>
</template>

<script setup>
import {
  IonPage,
  IonContent,
  IonModal,
  IonItem,
  IonInput,
  IonButton,
  menuController,
} from '@ionic/vue'

import { computed, onActivated, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const activeTab = ref('expense')
const period = ref('week')
const profile = ref(null)
const isScrolled = ref(false)

const isCustomModalOpen = ref(false)
const customDateFrom = ref('')
const customDateTo = ref('')

const scrollTop = ref(0)

const collapseChart = () => {
  isScrolled.value = true
}

const handleScroll = (event) => {
  scrollTop.value = event.detail.scrollTop

  if (scrollTop.value <= 2) {
    isScrolled.value = false
  }
}

const setActiveTab = (tab) => {
  activeTab.value = tab
}

const summary = ref({
  income_total: 0,
  expense_total: 0,
  balance: 0,
  expenses_by_category: [],
  income_by_category: [],
})

const categoryColors = {
  Здоровье: '#ff3b3b',
  Досуг: '#35b8a6',
  Дом: '#ff8c32',
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

const categoryIcons = {
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

const currencySymbol = computed(() => {
  const currency = profile.value?.main_currency || 'RUB'

  const map = {
    RUB: '₽',
    EUR: '€',
    USD: '$',
    RSD: 'RSD',
  }

  return map[currency] || currency
})

const currentItems = computed(() => {
  return activeTab.value === 'expense'
    ? summary.value.expenses_by_category
    : summary.value.income_by_category
})

const currentTotal = computed(() => {
  return currentItems.value.reduce((sum, item) => sum + Number(item.total), 0)
})

const donutStyle = computed(() => {
  if (!currentItems.value.length || currentTotal.value <= 0) {
    return { background: '#cfd8d4' }
  }

  let start = 0

  const parts = currentItems.value.map((item) => {
    const percent = (Number(item.total) / currentTotal.value) * 100
    const end = start + percent
    const color = getItemColor(item)
    const part = `${color} ${start}% ${end}%`
    start = end
    return part
  })

  return {
    background: `conic-gradient(${parts.join(', ')})`,
  }
})

const periodLabel = computed(() => {
  if (period.value === 'day') return 'Сегодня'
  if (period.value === 'week') return 'Последние 7 дней'
  if (period.value === 'month') return 'Последний месяц'
  if (period.value === 'year') return 'Текущий год'

  if (period.value === 'custom' && customDateFrom.value && customDateTo.value) {
    return `${formatDateRu(customDateFrom.value)} — ${formatDateRu(customDateTo.value)}`
  }

  return 'Выбранный период'
})

const getItemColor = (item) => {
  return item.color || categoryColors[item.category] || '#6c9f8c'
}

const getCategoryIcon = (name, categoryType) => {
  return categoryIcons[name] || (categoryType === 'expense' ? '−' : '+')
}

const getPercent = (total) => {
  if (!currentTotal.value) return 0
  return Math.round((Number(total) / currentTotal.value) * 100)
}

const formatDate = (date) => {
  return date.toISOString().slice(0, 10)
}

const formatDateRu = (value) => {
  const [year, month, day] = value.split('-')
  return `${day}.${month}.${year}`
}

const getDateRange = () => {
  const today = new Date()
  let dateFrom = null
  let dateTo = formatDate(today)

  if (period.value === 'day') {
    dateFrom = formatDate(today)
  }

  if (period.value === 'week') {
    const from = new Date()
    from.setDate(today.getDate() - 7)
    dateFrom = formatDate(from)
  }

  if (period.value === 'month') {
    const from = new Date()
    from.setMonth(today.getMonth() - 1)
    dateFrom = formatDate(from)
  }

  if (period.value === 'year') {
    const from = new Date(today.getFullYear(), 0, 1)
    dateFrom = formatDate(from)
  }

  if (period.value === 'custom') {
    dateFrom = customDateFrom.value
    dateTo = customDateTo.value
  }

  return { dateFrom, dateTo }
}

const loadData = async () => {
  const profileRes = await api.get('/users/me')
  profile.value = profileRes.data

  const { dateFrom, dateTo } = getDateRange()

  let url = '/statistics/summary'

  if (dateFrom && dateTo) {
    url += `?date_from=${dateFrom}&date_to=${dateTo}`
  } else if (dateFrom) {
    url += `?date_from=${dateFrom}`
  }

  const summaryRes = await api.get(url)
  summary.value = summaryRes.data
}

const setPeriod = async (newPeriod) => {
  period.value = newPeriod
  await loadData()
}

const openCustomPeriod = () => {
  period.value = 'custom'

  if (!customDateFrom.value || !customDateTo.value) {
    const today = new Date()
    const from = new Date()
    from.setMonth(today.getMonth() - 1)

    customDateFrom.value = formatDate(from)
    customDateTo.value = formatDate(today)
  }

  isCustomModalOpen.value = true
}

const applyCustomPeriod = async () => {
  if (!customDateFrom.value || !customDateTo.value) {
    alert('Выберите дату начала и дату окончания')
    return
  }

  if (customDateFrom.value > customDateTo.value) {
    alert('Дата начала не может быть позже даты окончания')
    return
  }

  isCustomModalOpen.value = false
  await loadData()
}

const openMenu = async () => {
  await menuController.open()
}

const goToAdd = () => {
  router.push('/add')
}

onMounted(() => {
  loadData()
})

onActivated(() => {
  loadData()
})
</script>

<style scoped>
ion-content {
  --background: #f7f8f3;
}

.header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: #6c9f8c;
  color: white;
  padding: 20px 20px 26px;
  border-radius: 0 0 28px 28px;
  text-align: center;
}

.menu-btn {
  position: absolute;
  left: 16px;
  top: 20px;
  background: transparent;
  border: none;
  color: white;
  font-size: 28px;
}

.title {
  text-transform: uppercase;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.3px;
  line-height: 1.1;
}

.balance {
  font-size: 34px;
  font-weight: 700;
  margin-top: 4px;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 72px;
  margin-top: 12px;
  text-transform: uppercase;
  font-size: 20px;
}

.tabs span {
  opacity: 0.65;
  padding-bottom: 6px;
  cursor: pointer;
}

.tabs .active {
  opacity: 1;
  border-bottom: 3px solid white;
}

.main-card {
  position: sticky;
  top: 136px;
  z-index: 25;
  margin: 0 18px 16px;
  background: white;
  border-radius: 24px;
  padding: 22px 18px 28px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}

.period-tabs {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-weight: 600;
}

.period-tabs span {
  opacity: 0.65;
  cursor: pointer;
  padding-bottom: 6px;
  font-size: 16px;
  font-weight: 600;
}

.activePeriod {
  opacity: 1 !important;
  color: #4f806f;
  border-bottom: 3px solid #4f806f;
  font-weight: 700;
}

.period-label {
  text-align: center;
  color: #777;
  font-size: 15px;
  margin: 16px 0 14px;
  text-decoration: underline;
}

.donut-wrap {
  display: flex;
  justify-content: center;
}

.donut {
  width: 220px;
  height: 220px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #cfd8d4;
}

.donut-inner {
  width: 135px;
  height: 135px;
  border-radius: 50%;
  background: white;
  border: 3px dashed #e3e3e3;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 14px;
  font-size: 22px;
  color: #555;
}

.mini-chart-wrap {
  margin: 20px 0 38px;
}

.mini-chart {
  display: flex;
  height: 20px;
  border-radius: 20px;
  overflow: hidden;
  background: #cfd8d4;
}

.mini-total {
  text-align: center;
  margin-top: 14px;
  font-size: 24px;
  color: #555;
}

.mini-part {
  height: 100%;
}

.add-btn {
  position: absolute;
  right: 18px;
  bottom: 22px;
  width: 62px;
  height: 62px;
  border-radius: 50%;
  border: none;
  background: #f4c542;
  color: #222;
  font-size: 36px;
  box-shadow: 0 6px 14px rgba(0,0,0,0.18);
}

.category-list {
  padding: 0 18px 120px;
  min-height: 420px;
}

.category-card {
  background: white;
  border-radius: 18px;
  padding: 16px 14px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 48px 82px;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.07);
}

.category-left {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 17px;
  min-width: 0;
}

.category-left span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.category-percent {
  color: #777;
  text-align: right;
}

.category-card strong {
  text-align: right;
  font-size: 16px;
  white-space: nowrap;
}

.modal-content {
  --background: rgba(0, 0, 0, 0.25);
}

.modal-card {
  background: white;
  margin: 80px 18px;
  border-radius: 22px;
  padding: 22px;
}

.modal-card h2 {
  margin: 0 0 18px;
  color: #4f806f;
  text-align: center;
}

ion-item {
  margin-bottom: 12px;
  border-radius: 14px;
  --background: #ffffff;
}

.apply-btn {
  margin-top: 18px;
  --background: #f4c542;
  --color: #333;
  --border-radius: 24px;
}
</style>