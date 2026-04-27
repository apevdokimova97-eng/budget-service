<template>
  <ion-page>
    <ion-content>
      <div class="header">
        <button class="back-btn" @click="goBack">‹</button>
        <h1>{{ goal?.title || 'Цель' }}</h1>
      </div>

      <div v-if="goal" class="goal-card">
        <p>{{ goal.current_amount }} / {{ goal.target_amount }} {{ goal.currency }}</p>

        <div class="progress">
          <div
            class="progress-fill"
            :style="{ width: Math.min(goal.progress_percent, 100) + '%' }"
          ></div>
        </div>

        <strong>{{ goal.progress_percent }}%</strong>
      </div>

      <div class="form-card">
        <h2>Пополнить цель</h2>

        <ion-item>
          <ion-input
            :value="amount"
            type="number"
            label="Сумма"
            label-placement="floating"
            @ionInput="amount = String($event.detail.value || '')"
          />
        </ion-item>

        <ion-item>
          <ion-input
            :value="comment"
            label="Комментарий"
            label-placement="floating"
            @ionInput="comment = String($event.detail.value || '')"
          />
        </ion-item>

        <ion-button expand="block" class="save-btn" @click="addContribution">
          Внести сумму
        </ion-button>
      </div>

      <div class="history">
        <h2>История накоплений</h2>

        <div
          v-for="item in contributions"
          :key="item.id"
          class="history-card"
        >
          <div>
            <strong>{{ item.amount }} {{ item.currency }}</strong>
            <p>{{ formatDate(item.date) }}</p>
            <small v-if="item.comment">{{ item.comment }}</small>
          </div>

          <button class="delete-btn" @click="deleteContribution(item.id)">×</button>
        </div>

        <p v-if="contributions.length === 0" class="empty">
          Пополнений пока нет
        </p>
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
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const route = useRoute()

const goalId = String(route.params.id)

const goal = ref(null)
const contributions = ref([])

const amount = ref('')
const comment = ref('')

const loadGoal = async () => {
  const response = await api.get('/goals/')
  const foundGoal = response.data.find((item) => String(item.id) === goalId)

  if (!foundGoal) {
    alert('Цель не найдена')
    router.push('/goals')
    return
  }

  goal.value = foundGoal
}

const loadContributions = async () => {
  const response = await api.get(`/goals/${goalId}/contributions`)
  contributions.value = response.data
}

const addContribution = async () => {
  if (!amount.value || Number(amount.value) <= 0) {
    alert('Введите сумму больше 0')
    return
  }

  await api.post(`/goals/${goalId}/contributions`, {
    amount: Number(amount.value),
    currency: goal.value?.currency || 'RUB',
    comment: comment.value,
  })

  amount.value = ''
  comment.value = ''

  await loadGoal()
  await loadContributions()
}

const deleteContribution = async (id) => {
  if (!confirm('Удалить пополнение?')) return

  await api.delete(`/goals/contributions/${id}`)

  await loadGoal()
  await loadContributions()
}

const formatDate = (value) => {
  return new Date(value).toLocaleDateString('ru-RU')
}

const goBack = () => {
  router.push('/goals')
}

onMounted(async () => {
  await loadGoal()
  await loadContributions()
})
</script>

<style scoped>
ion-content {
  --background: #f7f8f3;
}

.header {
  background: #6c9f8c;
  color: white;
  padding: 24px 18px;
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
  font-size: 24px;
}

.goal-card,
.form-card,
.history {
  margin: 18px;
  background: white;
  border-radius: 22px;
  padding: 18px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

h2 {
  margin-top: 0;
  color: #4f806f;
}

.progress {
  height: 12px;
  background: #e5e5e5;
  border-radius: 20px;
  overflow: hidden;
  margin: 12px 0;
}

.progress-fill {
  height: 100%;
  background: #f4c542;
}

ion-item {
  margin-bottom: 10px;
  border-radius: 14px;
  --background: #ffffff;
}

.save-btn {
  margin-top: 16px;
  --background: #f4c542;
  --color: #333;
  --border-radius: 24px;
}

.history-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 14px 0;
  border-bottom: 1px solid #eee;
}

.history-card strong {
  color: #4f806f;
}

.history-card p {
  margin: 4px 0;
  color: #777;
}

.history-card small {
  color: #555;
}

.delete-btn {
  border: none;
  background: transparent;
  font-size: 28px;
  color: #999;
}

.empty {
  text-align: center;
  color: #777;
}
</style>