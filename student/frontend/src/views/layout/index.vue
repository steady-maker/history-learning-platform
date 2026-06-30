<template>
  <div class="layout-container">
    <!-- 全局导航栏（固定不变） -->
    <nav class="nav-bar">
      <div class="nav-left">
        <h2 class="logo">历史学习平台</h2>
        <div 
          class="nav-item" 
          :class="{ active: $route.path === '/index' }"
          @click="navigateTo('/index')"
        >
          首页
        </div>
        <div 
          class="nav-item" 
          :class="{ active: $route.path.startsWith('/questionBank') }"
          @click="navigateTo('/questionBank')"
        >
          题库
        </div>
        <div 
          class="nav-item" 
          :class="{ active: $route.path.startsWith('/myQuestionBank') }"
          @click="navigateTo('/myQuestionBank')"
        >
          我的题库
        </div>
        <div 
          class="nav-item" 
          :class="{ active: $route.path.startsWith('/myInfo') }"
          @click="navigateTo('/myInfo')"
        >
          个人信息
        </div>
      </div>
    </nav>

    <main :class="['content-wrapper', { 'full-width': isWidePage }]">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const searchKeyword = ref('')

const isWidePage = computed(() => {
  // 做题页需要全宽展示，避免多层留白
  return route.path.startsWith('/doQuestion')
})

// 路由跳转方法
const navigateTo = (path) => {
  router.push(path)
}

// 搜索处理
const handleSearch = () => {
  if (searchKeyword.value) {
    router.push({
      path: $route.path,
      query: { keyword: searchKeyword.value }
    })
  }
}
</script>

<style lang="scss" scoped>
$primary-color: #165DFF;
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid #e5e6eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.nav-left {
  display: flex;
  align-items: center;
  gap: 24px;
}
.logo {
  color: $primary-color;
  font-size: 20px;
  margin: 0;
}
.nav-item {
  color: #333;
  font-size: 16px;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s;
  &.active {
    color: $primary-color;
    border-bottom-color: $primary-color;
  }
  &:hover {
    color: $primary-color;
  }
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
}
.search-input {
  padding: 6px 12px;
  border: 1px solid #e5e6eb;
  border-radius: 4px;
  outline: none;
  &:focus {
    border-color: $primary-color;
  }
}
.search-btn {
  background-color: $primary-color;
  color: #fff;
  border: none;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  &:hover {
    background-color: #0F4BD1;
  }
}
.user-info {
  color: #666;
  font-size: 14px;
}
.content-wrapper {
  flex: 1;
  // padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.content-wrapper.full-width {
  max-width: 100%;
  margin: 0;
  padding: 0 16px; /* 保留左右间距，避免太贴边 */
}
</style>