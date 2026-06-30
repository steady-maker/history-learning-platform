<template>
        <!-- 顶部导航栏 -->
    <nav class="nav-bar">
      <div class="nav-left">
        <h2 class="logo">历史学习平台</h2>
        <router-link 
          class="nav-item" 
          :class="{ active: $route.path === '/index' }" 
          to="/"
        >
          首页
        </router-link>
        <router-link 
          class="nav-item" 
          :class="{ active: $route.path.startsWith('/questionBank') }" 
          to="questionBank"
        >
          题库
        </router-link>
        <router-link 
          class="nav-item" 
          :class="{ active: $route.path.startsWith('/myQuestionBank') }" 
          to="/myQuestionBank"
        >
          我的题库
        </router-link>
        <router-link 
          class="nav-item" 
          :class="{ active: $route.path.startsWith('/myInfo') }" 
          to="/myInfo"
        >
          个人信息
        </router-link>
      </div>
      <div class="nav-right">
        <!-- 仅在题库/我的题库页面显示搜索 -->
        <div 
          v-if="$route.path.startsWith('/question') || $route.path.startsWith('/my-question')" 
          class="search-box"
        >
          <input 
            v-model="searchKeyword" 
            type="text" 
            placeholder="搜索题目..." 
            class="search-input"
          >
          <button @click="handleSearch" class="search-btn">搜索</button>
        </div>
        <span class="user-info">欢迎您，亲爱的xxx</span>
      </div>
    </nav>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

// 路由变化时清空搜索
onMounted(() => {
  router.afterEach(() => {
    searchKeyword.value = ''
    searchResult.value = []
  })
})
</script>
<style lang="scss" scoped>
// 统一色调
$primary-color: #165DFF;
$light-gray: #f5f7fa;
$border-color: #e5e6eb;

// 导航栏样式
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid $border-color;
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
  text-decoration: none;
  color: #333;
  font-size: 16px;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
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

</style>