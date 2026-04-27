<template>
  <ion-page>
    <ion-content>
      <div class="header">
        <button class="back-btn" @click="goBack">‹</button>
        <h1>Графики</h1>

        <div class="tabs">
          <span :class="{ active: mode === 'general' }" @click="setMode('general')">
            Общий
          </span>
          <span :class="{ active: mode === 'expense' }" @click="setMode('expense')">
            Расходы
          </span>
          <span :class="{ active: mode === 'income' }" @click="setMode('income')">
            Доходы
          </span>
        </div>
      </div>

      <div class="chart-card">
        <div class="period-tabs">
          <span :class="{ activePeriod: groupBy === 'year' }" @click="setGroupBy('year')">
            по годам
          </span>
          <span :class="{ activePeriod: groupBy === 'month' }" @click="setGroupBy('month')">
            по месяцам
          </span>
          <span :class="{ activePeriod: groupBy === 'week' }" @click="setGroupBy('week')">
            по неделям
          </span>
          <span :class="{ activePeriod: groupBy === 'day' }" @click="setGroupBy('day')">
            по дням
          </span>
        </div>

        <div class="chart-container">
          <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
        </div>

        <div class="period-label">
          {{ periodLabel }}
        </div>

        <div class="legend">
          <span><i class="dot income"></i> доходы</span>
          <span><i class="dot expense"></i> расходы</span>
          <span><i class="dot savings"></i> накопления</span>
          <span><i class="dot profit"></i> прибыль</span>
          <span><i class="dot loss"></i> убыток</span>
        </div>
      </div>

      <div class="summary">
        <div class="summary-card">
          <span>Доходы</span>
          <strong>{{ summary.income_total }} {{ currency }}</strong>
        </div>

        <div class="summary-card">
          <span>Расходы</span>
          <strong>{{ summary.expense_total }} {{ currency }}</strong>
        </div>

        <div class="summary-card">
          <span>Накопления</span>
          <strong>{{ summary.savings_total || 0 }} {{ currency }}</strong>
        </div>

        <div class="summary-card">
          <span>Остаток</span>
          <strong>{{ summary.free_balance ?? summary.balance }} {{ currency }}</strong>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { IonPage, IonContent } from '@ionic/vue'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

import { Bar } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const router = useRouter()

const mode = ref('general')
const groupBy = ref('month')
const currency = ref('₽')
const dynamics = ref([])
const chartData = ref(null)

const summary = ref({
  income_total: 0,
  expense_total: 0,
  savings_total: 0,
  balance: 0,
  free_balance: 0,
})

const colors = {
  income: '#66a68c',
  expense: '#f4c542',
  savings: '#8e7be8',
  profit: '#62b5f5',
  loss: '#ff8a55',
}

const weekDays = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб']

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        font: {
          size: 13,
        },
      },
    },
    y: {
      beginAtZero: true,
      ticks: {
        font: {
          size: 11,
        },
      },
    },
  },
}

const periodLabel = computed(() => {
  const now = new Date()

  if (groupBy.value === 'year') {
    return 'Последние 5 лет'
  }

  if (groupBy.value === 'month') {
    return `${now.getFullYear()}`
  }

  if (groupBy.value === 'week') {
    return 'Последние 5 недель'
  }

  return formatMonthYear(now)
})

const formatDateKey = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

const formatMonthKey = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')

  return `${year}-${month}`
}

const formatDayLabel = (date) => {
  const day = String(date.getDate()).padStart(2, '0')
  return `${day}\n${weekDays[date.getDay()]}`
}

const formatWeekLabel = (date) => {
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${day}.${month}`
}

const formatMonthLabel = (date) => {
  const months = [
    'янв.',
    'февр.',
    'март',
    'апр.',
    'май',
    'июнь',
    'июль',
    'авг.',
    'сент.',
    'окт.',
    'нояб.',
    'дек.',
  ]

  return months[date.getMonth()]
}

const formatMonthYear = (date) => {
  const months = [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь',
  ]

  return `${months[date.getMonth()]} ${date.getFullYear()} г.`
}

const getMonday = (date) => {
  const result = new Date(date)
  const day = result.getDay()
  const diff = day === 0 ? -6 : 1 - day

  result.setDate(result.getDate() + diff)
  result.setHours(0, 0, 0, 0)

  return result
}

const getIsoWeekKey = (date) => {
  const temp = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
  const day = temp.getUTCDay() || 7

  temp.setUTCDate(temp.getUTCDate() + 4 - day)

  const yearStart = new Date(Date.UTC(temp.getUTCFullYear(), 0, 1))
  const weekNo = Math.ceil((((temp - yearStart) / 86400000) + 1) / 7)

  return `${temp.getUTCFullYear()}-W${String(weekNo).padStart(2, '0')}`
}

const getLastFivePeriods = () => {
  const now = new Date()
  const periods = []

  if (groupBy.value === 'year') {
    const currentYear = now.getFullYear()

    for (let i = 4; i >= 0; i--) {
      const year = currentYear - i

      periods.push({
        key: String(year),
        label: String(year),
      })
    }
  }

  if (groupBy.value === 'month') {
    for (let i = 4; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1)

      periods.push({
        key: formatMonthKey(date),
        label: formatMonthLabel(date),
      })
    }
  }

  if (groupBy.value === 'week') {
    const currentMonday = getMonday(now)

    for (let i = 4; i >= 0; i--) {
      const date = new Date(currentMonday)
      date.setDate(currentMonday.getDate() - i * 7)

      periods.push({
        key: getIsoWeekKey(date),
        label: formatWeekLabel(date),
      })
    }
  }

  if (groupBy.value === 'day') {
    for (let i = 4; i >= 0; i--) {
      const date = new Date(now)
      date.setDate(now.getDate() - i)

      periods.push({
        key: formatDateKey(date),
        label: formatDayLabel(date),
      })
    }
  }

  return periods
}

const normalizeDynamics = () => {
  const periods = getLastFivePeriods()

  return periods.map((period) => {
    const found = dynamics.value.find((item) => {
      const itemPeriod = String(item.period)

      if (groupBy.value === 'year') {
        return itemPeriod.startsWith(period.key)
      }

      if (groupBy.value === 'month') {
        return itemPeriod.startsWith(period.key)
      }

      if (groupBy.value === 'week') {
        return itemPeriod === period.key
      }

      if (groupBy.value === 'day') {
        return itemPeriod.startsWith(period.key)
      }

      return false
    })

    return {
      period: period.key,
      label: period.label,
      income: Number(found?.income || 0),
      expense: Number(found?.expense || 0),
      savings: Number(found?.savings || 0),
      profit: Number(found?.profit || 0),
      loss: Number(found?.loss || 0),
    }
  })
}

const buildChart = () => {
  const normalized = normalizeDynamics()
  const labels = normalized.map((item) => item.label)

  let datasets = []

  if (mode.value === 'general') {
    datasets = [
      {
        label: 'Доходы',
        data: normalized.map((item) => item.income),
        backgroundColor: colors.income,
      },
      {
        label: 'Расходы',
        data: normalized.map((item) => item.expense),
        backgroundColor: colors.expense,
      },
      {
        label: 'Накопления',
        data: normalized.map((item) => item.savings),
        backgroundColor: colors.savings,
      },
      {
        label: 'Прибыль',
        data: normalized.map((item) => item.profit),
        backgroundColor: colors.profit,
      },
      {
        label: 'Убыток',
        data: normalized.map((item) => item.loss),
        backgroundColor: colors.loss,
      },
    ]
  }

  if (mode.value === 'expense') {
    datasets = [
      {
        label: 'Расходы',
        data: normalized.map((item) => item.expense),
        backgroundColor: colors.expense,
      },
    ]
  }

  if (mode.value === 'income') {
    datasets = [
      {
        label: 'Доходы',
        data: normalized.map((item) => item.income),
        backgroundColor: colors.income,
      },
      {
        label: 'Накопления',
        data: normalized.map((item) => item.savings),
        backgroundColor: colors.savings,
      },
    ]
  }

  chartData.value = {
    labels,
    datasets,
  }
}

const loadData = async () => {
  const profileRes = await api.get('/users/me')

  const symbols = {
    RUB: '₽',
    EUR: '€',
    USD: '$',
    RSD: 'RSD',
  }

  currency.value = symbols[profileRes.data.main_currency] || profileRes.data.main_currency

  const summaryRes = await api.get('/statistics/summary')
  summary.value = summaryRes.data

  const dynamicsRes = await api.get(`/statistics/dynamics?group_by=${groupBy.value}`)
  dynamics.value = dynamicsRes.data

  buildChart()
}

const setMode = (newMode) => {
  mode.value = newMode
  buildChart()
}

const setGroupBy = async (newGroupBy) => {
  groupBy.value = newGroupBy
  await loadData()
}

const goBack = () => {
  router.push('/home')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
ion-content {
  --background: #f7f8f3;
}

.header {
  background: #6c9f8c;
  color: white;
  padding: 24px 18px 30px;
  border-radius: 0 0 32px 32px;
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
}

h1 {
  margin: 0 0 22px;
  font-size: 26px;
}

.tabs {
  display: flex;
  justify-content: space-around;
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

.chart-card {
  margin: -22px 18px 18px;
  background: white;
  border-radius: 24px;
  padding: 22px 14px 18px;
  min-height: 430px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

.period-tabs {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 14px;
  margin-bottom: 18px;
}

.period-tabs span {
  color: #555;
  opacity: 0.7;
  padding-bottom: 5px;
  cursor: pointer;
}

.activePeriod {
  opacity: 1 !important;
  color: #4f806f !important;
  border-bottom: 2px solid #4f806f;
  font-weight: 700;
}

.chart-container {
  height: 250px;
  position: relative;
}

.period-label {
  text-align: center;
  color: #b4bdb9;
  font-size: 21px;
  margin-top: 12px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px 14px;
  margin-top: 16px;
  color: #777;
  font-size: 13px;
}

.legend span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  display: inline-block;
}

.dot.income {
  background: #66a68c;
}

.dot.expense {
  background: #f4c542;
}

.dot.savings {
  background: #8e7be8;
}

.dot.profit {
  background: #62b5f5;
}

.dot.loss {
  background: #ff8a55;
}

.summary {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  padding: 0 18px 30px;
}

.summary-card {
  background: white;
  border-radius: 18px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.summary-card span {
  color: #777;
}

.summary-card strong {
  color: #4f806f;
}
</style>