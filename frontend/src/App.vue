<template>
  <ion-app>
    <ion-menu content-id="main-content" side="start" class="app-menu">
      <ion-content>
        <div class="menu-header" @click="goProfile">
          <div class="avatar">
            <img v-if="avatar" :src="avatar" />
            <span v-else>{{ userInitial }}</span>
          </div>

          <div>
            <div class="username">{{ user?.username || 'Пользователь' }}</div>
            <div class="balance">Остаток: {{ balance }} {{ currencySymbol }}</div>
          </div>
        </div>

        <ion-list class="menu-list">
          <ion-item button @click="goPage('/home')">
            <span class="menu-icon">🏠</span>
            <ion-label>Главная</ion-label>
          </ion-item>

          <ion-item button @click="goPage('/statistics')">
            <span class="menu-icon">📊</span>
            <ion-label>Графики</ion-label>
          </ion-item>

          <ion-item button @click="goPage('/categories')">
            <span class="menu-icon">🗂</span>
            <ion-label>Категории</ion-label>
          </ion-item>

          <ion-item button @click="goPage('/add')">
            <span class="menu-icon">➕</span>
            <ion-label>Добавить операцию</ion-label>
          </ion-item>

          <ion-item button @click="goPage('/recurring-payments')">
            <span class="menu-icon">🔁</span>
            <ion-label>Регулярные платежи</ion-label>
          </ion-item>

          <ion-item button @click="goPage('/goals')">
            <span class="menu-icon">🎯</span>
            <ion-label>Финансовые цели</ion-label>
          </ion-item>

          <ion-item button @click="goPage('/assistant')">
            <span class="menu-icon">💡</span>
            <ion-label>Советы</ion-label>
          </ion-item>

          <ion-item button @click="goPage('/profile')">
            <span class="menu-icon">👤</span>
            <ion-label>Профиль</ion-label>
          </ion-item>

        </ion-list>

        <div class="menu-footer">
          <ion-button expand="block" fill="clear" class="logout-btn" @click="logout">
            🚪 Выйти
          </ion-button>
        </div>
      </ion-content>
    </ion-menu>

    <ion-router-outlet id="main-content" :key="$route.fullPath" />
  </ion-app>
</template>

<script setup>
import {
  IonApp,
  IonRouterOutlet,
  IonMenu,
  IonContent,
  IonList,
  IonItem,
  IonLabel,
  IonButton,
  menuController,
} from '@ionic/vue'

import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from './api'

const router = useRouter()
const route = useRoute()

const user = ref(null)
const balance = ref(0)
const avatar = ref(localStorage.getItem('avatar') || '')

const currencySymbol = computed(() => {
  const map = {
    RUB: '₽',
    EUR: '€',
    USD: '$',
    RSD: 'RSD',
  }

  return map[user.value?.main_currency] || user.value?.main_currency || '₽'
})

const userInitial = computed(() => {
  return user.value?.username?.charAt(0)?.toUpperCase() || 'U'
})

const loadMenuData = async () => {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const profileRes = await api.get('/users/me')
    user.value = profileRes.data

    const summaryRes = await api.get('/statistics/summary')
    balance.value = summaryRes.data.balance || 0

    avatar.value = localStorage.getItem('avatar') || ''
  } catch (e) {
    console.log(e)
  }
}

const goPage = async (path) => {
  await menuController.close()
  router.push(path)
}

const goProfile = async () => {
  await menuController.close()
  router.push('/profile')
}

const logout = async () => {
  localStorage.removeItem('token')
  await menuController.close()
  router.push('/login')
}

onMounted(() => {
  loadMenuData()

  window.addEventListener('profile-updated', () => {
    loadMenuData()
  })
})

watch(
  () => route.fullPath,
  () => {
    loadMenuData()
  }
)
</script>

<style scoped>
.app-menu {
  --width: 310px;
}

ion-content {
  --background: #6c9f8c;
}

.menu-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 32px 20px 26px;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.35);
  cursor: pointer;
}

.avatar {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: #f47a00;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  color: white;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.username {
  font-size: 20px;
  font-weight: 700;
}

.balance {
  font-size: 15px;
  margin-top: 6px;
  opacity: 0.95;
}

.menu-list {
  background: transparent;
  padding-top: 18px;
}

ion-item {
  --background: transparent;
  --color: white;
  --border-color: transparent;
  font-size: 18px;
  margin-bottom: 6px;
}

.menu-icon {
  width: 34px;
  display: inline-block;
  font-size: 22px;
  margin-right: 12px;
}

.menu-footer {
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: 24px;
}

.logout-btn {
  --color: white;
  font-size: 18px;
}
</style>