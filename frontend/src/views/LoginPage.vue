<template>
  <ion-page>
    <ion-content>
      <div class="auth-page">
        <div class="auth-card">
          <h1>Вход</h1>
          <p>Введите email и пароль для входа в личный бюджет</p>

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
              :value="password"
              type="password"
              label="Пароль"
              label-placement="floating"
              @ionInput="password = String($event.detail.value || '')"
            />
          </ion-item>

          <ion-button expand="block" class="main-btn" @click="login">
            Войти
          </ion-button>

          <ion-button fill="clear" expand="block" @click="goRegister">
            Зарегистрироваться
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

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const email = ref('')
const password = ref('')

const login = async () => {
  try {
    const payload = {
      email: email.value.trim(),
      password: password.value,
    }

    console.log('LOGIN PAYLOAD:', payload)

    const response = await api.post('/auth/login', payload)

    localStorage.setItem('token', response.data.access_token)
    router.push('/home')
  } catch (error) {
    console.log('LOGIN ERROR:', error.response?.data || error)
    alert(error.response?.data?.detail || 'Ошибка входа')
  }
}

const goRegister = () => {
  router.push('/register')
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
  font-size: 32px;
  margin-bottom: 8px;
}

p {
  color: #777;
  font-size: 14px;
  margin-bottom: 24px;
}

ion-item {
  margin-bottom: 14px;
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