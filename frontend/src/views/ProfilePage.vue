<template>
  <ion-page>
    <ion-content>
      <div class="header">
        <button class="back-btn" @click="goBack">‹</button>
        <h1>Профиль</h1>
      </div>

      <div class="profile">
        <div class="avatar-wrap" @click="selectAvatar">
          <div class="avatar">
            <img v-if="avatar" :src="avatar" />
            <span v-else>{{ initial }}</span>
          </div>

          <button class="edit-avatar">✎</button>
          <input ref="fileInput" type="file" accept="image/*" hidden @change="uploadAvatar" />
        </div>

        <ion-item>
          <ion-input
            :value="username"
            label="Имя"
            label-placement="floating"
            @ionInput="username = String($event.detail.value || '')"
          />
        </ion-item>

        <ion-item>
          <ion-input
            :value="email"
            label="Почта"
            label-placement="floating"
            readonly
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

        <ion-button expand="block" class="save-btn" @click="saveProfile">
          Сохранить изменения
        </ion-button>

        <ion-button expand="block" fill="clear" color="danger" @click="logout">
          Выйти
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
} from '@ionic/vue'

import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const fileInput = ref(null)

const username = ref('')
const email = ref('')
const mainCurrency = ref('RUB')
const avatar = ref(localStorage.getItem('avatar') || '')

const initial = computed(() => {
  return username.value?.charAt(0)?.toUpperCase() || 'U'
})

const loadProfile = async () => {
  const response = await api.get('/users/me')

  username.value = response.data.username
  email.value = response.data.email
  mainCurrency.value = response.data.main_currency
  avatar.value = localStorage.getItem('avatar') || ''
}

const selectAvatar = () => {
  fileInput.value.click()
}

const uploadAvatar = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()

  reader.onload = () => {
    avatar.value = reader.result
    localStorage.setItem('avatar', reader.result)
    window.dispatchEvent(new Event('profile-updated'))
  }

  reader.readAsDataURL(file)
}

const saveProfile = async () => {
  await api.put('/users/me', {
    username: username.value.trim(),
    main_currency: mainCurrency.value,
  })

  window.dispatchEvent(new Event('profile-updated'))

  alert('Профиль сохранён')
  router.push('/home')
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

const goBack = () => {
  router.push('/home')
}

onMounted(() => {
  loadProfile()
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

.profile {
  padding: 30px 24px;
}

.avatar-wrap {
  width: 150px;
  height: 150px;
  margin: 0 auto 34px;
  position: relative;
  cursor: pointer;
}

.avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: #f47a00;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 74px;
  color: white;
  overflow: hidden;
  border: 2px solid #6c9f8c;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.edit-avatar {
  position: absolute;
  right: 4px;
  bottom: 8px;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: none;
  background: #b8c7c1;
  color: white;
  font-size: 22px;
}

ion-item {
  margin-bottom: 14px;
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