<template>
  <ion-page>
    <ion-content>
      <div class="header">
        <button class="back-btn" @click="goBack">‹</button>
        <h1>Финансовые цели</h1>
      </div>

      <div class="goals-list">
        <div
          v-for="goal in goals"
          :key="goal.id"
          class="goal-card"
          @click="openGoal(goal.id)"
        >
          <div class="goal-top">
            <h3>{{ goal.title }}</h3>
            <button @click.stop="deleteGoal(goal.id)">×</button>
          </div>

          <p>
            {{ goal.current_amount }} / {{ goal.target_amount }} {{ goal.currency }}
          </p>

          <div class="progress">
            <div
              class="progress-fill"
              :style="{ width: Math.min(goal.progress_percent, 100) + '%' }"
            ></div>
          </div>

          <strong>{{ goal.progress_percent }}%</strong>
        </div>

        <p v-if="goals.length === 0" class="empty">
          Финансовых целей пока нет
        </p>
      </div>

      <ion-modal :is-open="isFormOpen" @didDismiss="isFormOpen = false">
        <ion-content class="modal-content">
          <div class="form-card">
            <h2>Новая цель</h2>

            <ion-item>
              <ion-input
                :value="title"
                label="Название цели"
                label-placement="floating"
                @ionInput="title = String($event.detail.value || '')"
              />
            </ion-item>

            <ion-item>
              <ion-input
                :value="targetAmount"
                type="number"
                label="Целевая сумма"
                label-placement="floating"
                @ionInput="targetAmount = String($event.detail.value || '')"
              />
            </ion-item>

            <ion-item>
              <ion-input
                :value="currentAmount"
                type="number"
                label="Уже накоплено"
                label-placement="floating"
                @ionInput="currentAmount = String($event.detail.value || '')"
              />
            </ion-item>

            <ion-item>
              <ion-select
                :value="currency"
                label="Валюта"
                label-placement="floating"
                @ionChange="currency = String($event.detail.value || 'RUB')"
              >
                <ion-select-option value="RUB">RUB</ion-select-option>
                <ion-select-option value="EUR">EUR</ion-select-option>
                <ion-select-option value="USD">USD</ion-select-option>
                <ion-select-option value="RSD">RSD</ion-select-option>
              </ion-select>
            </ion-item>

            <ion-button expand="block" class="save-btn" @click="createGoal">
              Сохранить
            </ion-button>

            <ion-button expand="block" fill="clear" @click="closeForm">
              Отмена
            </ion-button>
          </div>
        </ion-content>
      </ion-modal>

      <div class="bottom-action">
        <ion-button expand="block" class="add-goal-btn" @click="openForm">
          Добавить цель
        </ion-button>
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
  IonSelect,
  IonSelectOption,
  IonModal,
} from '@ionic/vue'

import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const goals = ref([])
const isFormOpen = ref(false)

const title = ref('')
const targetAmount = ref('')
const currentAmount = ref('0')
const currency = ref('RUB')

const loadGoals = async () => {
  const response = await api.get('/goals/')
  goals.value = response.data
}

const openForm = () => {
  title.value = ''
  targetAmount.value = ''
  currentAmount.value = '0'
  currency.value = 'RUB'
  isFormOpen.value = true
}

const closeForm = () => {
  isFormOpen.value = false
}

const openGoal = (id) => {
  router.push(`/goals/${id}`)
}

const createGoal = async () => {
  if (!title.value.trim()) {
    alert('Введите название цели')
    return
  }

  if (!targetAmount.value || Number(targetAmount.value) <= 0) {
    alert('Введите целевую сумму больше 0')
    return
  }

  await api.post('/goals/', {
    title: title.value.trim(),
    target_amount: Number(targetAmount.value),
    current_amount: Number(currentAmount.value || 0),
    currency: currency.value,
    deadline: null,
  })

  title.value = ''
  targetAmount.value = ''
  currentAmount.value = '0'
  currency.value = 'RUB'
  isFormOpen.value = false

  await loadGoals()
}

const deleteGoal = async (id) => {
  if (!confirm('Удалить цель?')) return

  await api.delete(`/goals/${id}`)
  await loadGoals()
}

const goBack = () => {
  router.push('/home')
}

onMounted(() => {
  loadGoals()
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
  font-size: 26px;
}

.goals-list {
  padding: 18px 0 110px;
}

.goal-card {
  margin: 0 18px 16px;
  background: white;
  border-radius: 22px;
  padding: 18px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  cursor: pointer;
}

.goal-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.goal-top h3 {
  margin: 0;
  color: #4f806f;
  font-size: 22px;
  font-weight: 600;
}

.goal-top button {
  border: none;
  background: transparent;
  font-size: 28px;
  color: #999;
}

.goal-card p {
  margin: 14px 0 10px;
  color: #222;
  font-size: 16px;
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

.empty {
  text-align: center;
  color: #777;
  margin-top: 30px;
}

.modal-content {
  --background: rgba(0, 0, 0, 0.25);
}

.form-card {
  margin: 80px 18px;
  background: white;
  border-radius: 22px;
  padding: 22px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.form-card h2 {
  margin: 0 0 18px;
  color: #4f806f;
  text-align: center;
  font-size: 26px;
}

ion-item {
  margin-bottom: 12px;
  border-radius: 14px;
  --background: #ffffff;
}

.save-btn,
.add-goal-btn {
  margin-top: 16px;
  --background: #f4c542;
  --color: #333;
  --border-radius: 24px;
}

.bottom-action {
  position: fixed;
  left: 18px;
  right: 18px;
  bottom: 18px;
  z-index: 20;
}
</style>