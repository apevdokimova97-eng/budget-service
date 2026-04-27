<template>
  <ion-page>
    <ion-content>
      <div class="header">
        <button class="back-btn" @click="goBack">‹</button>
        <h1>Советы</h1>
        <p>Анализ бюджета и рекомендации</p>
      </div>

      <div class="summary-card">
        <div>
          <span>Доходы</span>
          <strong>{{ data.income_total }} {{ currency }}</strong>
        </div>

        <div>
          <span>Расходы</span>
          <strong>{{ data.expense_total }} {{ currency }}</strong>
        </div>

        <div>
          <span>Баланс</span>
          <strong>{{ data.balance }} {{ currency }}</strong>
        </div>
      </div>

      <div class="advice-list">
        <div
          v-for="item in data.advice"
          :key="item.title"
          class="advice-card"
          :class="item.type"
        >
          <h2>{{ item.title }}</h2>
          <p>{{ item.message }}</p>
        </div>

        <p v-if="data.advice.length === 0" class="empty">
          Рекомендаций пока нет
        </p>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import {
  IonPage,
  IonContent,
} from '@ionic/vue'

import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const currency = ref('₽')

const data = ref({
  income_total: 0,
  expense_total: 0,
  balance: 0,
  advice: [],
})

const loadData = async () => {
  const profileRes = await api.get('/users/me')

  const symbols = {
    RUB: '₽',
    EUR: '€',
    USD: '$',
    RSD: 'RSD',
  }

  currency.value = symbols[profileRes.data.main_currency] || profileRes.data.main_currency

  const adviceRes = await api.get('/assistant/advice')
  data.value = adviceRes.data
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
  padding: 24px 18px 28px;
  border-radius: 0 0 24px 24px;
  position: relative;
  text-align: center;
}

.back-btn {
  position: absolute;
  left: 16px;
  top: 18px;
  background: transparent;
  border: none;
  color: white;
  font-size: 42px;
}

h1 {
  margin: 0;
  font-size: 26px;
}

.header p {
  margin: 8px 0 0;
  opacity: 0.9;
}

.summary-card {
  margin: 18px;
  background: white;
  border-radius: 22px;
  padding: 18px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  display: grid;
  gap: 12px;
}

.summary-card div {
  display: flex;
  justify-content: space-between;
}

.summary-card span {
  color: #777;
}

.summary-card strong {
  color: #4f806f;
}

.advice-list {
  padding: 0 18px 28px;
}

.advice-card {
  background: white;
  border-radius: 22px;
  padding: 18px;
  margin-bottom: 14px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  border-left: 6px solid #6c9f8c;
}

.advice-card.warning {
  border-left-color: #e2a400;
}

.advice-card.success {
  border-left-color: #4f9d69;
}

.advice-card.info {
  border-left-color: #6c9f8c;
}

.advice-card h2 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #4f806f;
}

.advice-card p {
  margin: 0;
  color: #555;
  line-height: 1.4;
}

.empty {
  text-align: center;
  color: #777;
  margin-top: 30px;
}
</style>