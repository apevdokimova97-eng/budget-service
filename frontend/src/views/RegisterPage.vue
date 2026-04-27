<template>
  <ion-page>
    <ion-content>
      <div class="auth-page">
        <div class="auth-card">
          <h1>Регистрация</h1>
          <p>Создайте аккаунт для учета личного бюджета</p>

          <ion-item>
            <ion-input
              :value="email"
              type="email"
              label="Email"
              label-placement="floating"
              @ionInput="email = String($event.detail.value || '')"
            />
          </ion-item>

          <ion-item>
            <ion-input
              :value="username"
              label="Имя пользователя"
              label-placement="floating"
              @ionInput="username = String($event.detail.value || '')"
            />
          </ion-item>

          <ion-item>
            <ion-input
              :value="password"
              type="password"
              label="Пароль"
              label-placement="floating"
              @ionInput="password = String($event.detail.value || '')"
            />
          </ion-item>

          <ion-item>
            <ion-input
              :value="passwordRepeat"
              type="password"
              label="Повторите пароль"
              label-placement="floating"
              @ionInput="passwordRepeat = String($event.detail.value || '')"
            />
          </ion-item>

          <ion-item>
            <ion-select
              :value="mainCurrency"
              label="Основная валюта"
              label-placement="floating"
              @ionChange="mainCurrency = String($event.detail.value || 'RUB')"
            >
              <ion-select-option value="RUB">RUB</ion-select-option>
              <ion-select-option value="EUR">EUR</ion-select-option>
              <ion-select-option value="USD">USD</ion-select-option>
              <ion-select-option value="RSD">RSD</ion-select-option>
            </ion-select>
          </ion-item>

          <ion-button expand="block" class="main-btn" @click="register">
            Зарегистрироваться
          </ion-button>

          <ion-button fill="clear" expand="block" @click="goLogin">
            Уже есть аккаунт? Войти
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
  IonSelect,
  IonSelectOption,
} from '@ionic/vue'

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const email = ref('')
const username = ref('')
const password = ref('')
const passwordRepeat = ref('')
const mainCurrency = ref('RUB')

const register = async () => {
  if (password.value !== passwordRepeat.value) {
    alert('Пароли не совпадают')
    return
  }

  try {
    const payload = {
      email: email.value.trim(),
      username: username.value.trim(),
      password: password.value,
      password_repeat: passwordRepeat.value,
      main_currency: mainCurrency.value,
    }

    console.log('REGISTER PAYLOAD:', payload)

    await api.post('/auth/register', payload)

    const loginResponse = await api.post('/auth/login', {
        email: email.value.trim(),
        password: password.value,
    })

    localStorage.setItem('token', loginResponse.data.access_token)

    router.push('/home')
  } catch (error) {
    console.log('REGISTER ERROR:', error.response?.data || error)
    alert(error.response?.data?.detail || 'Ошибка регистрации')
  }
}

const goLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.auth-page {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #f7f8f3;
}

.auth-card {
  width: 100%;
  max-width: 360px;
  text-align: center;
}

h1 {
  color: #4f806f;
  font-size: 30px;
  margin-bottom: 8px;
}

p {
  color: #777;
  font-size: 14px;
  margin-bottom: 20px;
}

ion-item {
  margin-bottom: 12px;
  border-radius: 14px;
  --background: #ffffff;
}

.main-btn {
  margin-top: 20px;
  --background: #f4c542;
  --color: #333;
  --border-radius: 24px;
}
</style>