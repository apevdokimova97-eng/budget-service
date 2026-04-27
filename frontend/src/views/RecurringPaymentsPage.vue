<template>
  <ion-page>
    <ion-content>
      <div class="header">
        <button class="back-btn" @click="goBack">‹</button>
        <h1>Регулярные платежи</h1>
      </div>

      <div class="reminder-card" v-if="reminders.length">
        <h2>Напоминания</h2>

        <div
          v-for="reminder in reminders"
          :key="reminder.id"
          class="reminder-item"
        >
          <strong>{{ reminder.title }}</strong>
          <span>{{ reminder.message }}</span>
          <b>{{ reminder.amount }} {{ reminder.currency }}</b>
        </div>
      </div>

      <div class="payments-list">
        <div
          v-for="payment in payments"
          :key="payment.id"
          class="payment-card"
        >
          <div>
            <h3>{{ payment.title }}</h3>
            <p>
              {{ payment.amount }} {{ payment.currency }} · {{ payment.payment_day }} числа каждого месяца
            </p>
            <small>Напоминания: за 3 дня, за 1 день и в день платежа</small>
          </div>

          <button class="delete-btn" @click="deletePayment(payment.id)">×</button>
        </div>

        <p v-if="payments.length === 0" class="empty">
          Регулярных платежей пока нет
        </p>
      </div>

      <ion-modal :is-open="isFormOpen" @didDismiss="isFormOpen = false">
        <ion-content class="modal-content">
          <div class="form-card">
            <h2>Новый платеж</h2>

            <ion-item>
              <ion-input
                :value="title"
                label="Название"
                label-placement="floating"
                @ionInput="title = String($event.detail.value || '')"
              />
            </ion-item>

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
              <ion-select
                :value="categoryId"
                label="Категория расходов"
                label-placement="floating"
                @ionChange="categoryId = Number($event.detail.value)"
              >
                <ion-select-option
                  v-for="category in categories"
                  :key="category.id"
                  :value="category.id"
                >
                  {{ category.name }}
                </ion-select-option>
              </ion-select>
            </ion-item>

            <ion-item>
              <ion-select
                :value="paymentDay"
                label="День платежа"
                label-placement="floating"
                @ionChange="paymentDay = Number($event.detail.value)"
              >
                <ion-select-option v-for="day in 31" :key="day" :value="day">
                  {{ day }}
                </ion-select-option>
              </ion-select>
            </ion-item>

            <ion-button expand="block" class="save-btn" @click="createPayment">
              Сохранить
            </ion-button>

            <ion-button expand="block" fill="clear" @click="closeForm">
              Отмена
            </ion-button>
          </div>
        </ion-content>
      </ion-modal>

      <div class="bottom-action">
        <ion-button expand="block" class="add-payment-btn" @click="openForm">
          Добавить платеж
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

const title = ref('')
const amount = ref('')
const paymentDay = ref(15)
const categoryId = ref(null)
const isFormOpen = ref(false)

const categories = ref([])
const payments = ref([])
const reminders = ref([])

const loadCategories = async () => {
  const response = await api.get('/categories/?type=expense')
  categories.value = response.data

  if (categories.value.length && !categoryId.value) {
    categoryId.value = categories.value[0].id
  }
}

const loadPayments = async () => {
  const response = await api.get('/recurring-payments/')
  payments.value = response.data
}

const loadReminders = async () => {
  const response = await api.get('/recurring-payments/reminders')
  reminders.value = response.data.reminders || []
}

const openForm = () => {
  title.value = ''
  amount.value = ''
  paymentDay.value = 15

  if (categories.value.length && !categoryId.value) {
    categoryId.value = categories.value[0].id
  }

  isFormOpen.value = true
}

const closeForm = () => {
  isFormOpen.value = false
}

const createPayment = async () => {
  if (!title.value.trim()) {
    alert('Введите название платежа')
    return
  }

  if (!amount.value || Number(amount.value) <= 0) {
    alert('Введите сумму больше 0')
    return
  }

  if (!categoryId.value) {
    alert('Выберите категорию')
    return
  }

  await api.post('/recurring-payments/', {
    title: title.value.trim(),
    amount: Number(amount.value),
    currency: 'RUB',
    category_id: categoryId.value,
    payment_day: paymentDay.value,
  })

  title.value = ''
  amount.value = ''
  paymentDay.value = 15
  isFormOpen.value = false

  await loadPayments()
  await loadReminders()
}

const deletePayment = async (id) => {
  if (!confirm('Удалить регулярный платеж?')) return

  await api.delete(`/recurring-payments/${id}`)
  await loadPayments()
  await loadReminders()
}

const goBack = () => {
  router.push('/home')
}

onMounted(async () => {
  await loadCategories()
  await loadPayments()
  await loadReminders()
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

.reminder-card,
.payment-card {
  margin: 18px;
  background: white;
  border-radius: 22px;
  padding: 18px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.form-card {
  margin: 80px 18px;
  background: white;
  border-radius: 22px;
  padding: 18px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

h2 {
  margin-top: 0;
  color: #4f806f;
}

ion-item {
  margin-bottom: 10px;
  border-radius: 14px;
  --background: #ffffff;
}

.save-btn,
.add-payment-btn {
  margin-top: 16px;
  --background: #f4c542;
  --color: #333;
  --border-radius: 24px;
}

.reminder-item {
  display: grid;
  gap: 4px;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.reminder-item strong {
  color: #4f806f;
}

.reminder-item span {
  color: #666;
}

.payments-list {
  padding-bottom: 100px;
}

.payment-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.payment-card h3 {
  margin: 0 0 6px;
  color: #4f806f;
}

.payment-card p {
  margin: 0 0 6px;
  color: #333;
}

.payment-card small {
  color: #777;
}

.delete-btn {
  border: none;
  background: transparent;
  font-size: 30px;
  color: #999;
}

.empty {
  text-align: center;
  color: #777;
  margin-top: 30px;
}

.modal-content {
  --background: rgba(0, 0, 0, 0.25);
}

.bottom-action {
  position: fixed;
  left: 18px;
  right: 18px;
  bottom: 18px;
  z-index: 20;
}
</style>