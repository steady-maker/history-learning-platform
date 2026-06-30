<template>
  <div class="app-container">
    <!-- 主体内容区（不再包含导航栏，依赖layout的header） -->
    <main class="content-wrapper">
      <!-- 欢迎横幅（视觉吸睛核心） -->
      <div class="welcome-banner">
        <div class="banner-content">
          <h1>欢迎回来，{{ userInfo.username || '同学' }} 🌟</h1>
          <p>每日解锁历史新知，让学习更有趣</p>
          <button class="start-btn" @click="goToQuestionBank">立即答题</button>
        </div>
        <div class="banner-illustration">📜</div>
      </div>

            <!-- 学习打卡模块（互动引流） -->
      <div class="section">
        <div class="section-header">
          <h2>每日打卡 📅</h2>
          <span class="section-desc">坚持打卡，养成学习习惯</span>
        </div>
        <div class="check-in-simple">
          <p class="check-in-count">累计打卡：{{ totalCheckInDays }} 天</p>
          <button 
            class="btn-primary check-in-btn" 
            @click="checkIn"
            :disabled="todayChecked"
          >
            {{ todayChecked ? '今日已打卡 ✔' : '今日打卡' }}
          </button>
        </div>
      </div>

      <!-- 今日一题（核心引流模块） -->
      <div class="section">
        <div class="section-header">
          <h2>今日一题 📝</h2>
          <span class="section-desc">每天一道精选题，夯实历史基础</span>
        </div>
        <div class="today-question-card">
          <div class="question-content">
            <p>{{ truncateText(todayQuestion.content,150) || '今日题目加载中...' }}</p>
            <!-- <div class="question-meta">
              <span class="question-tag">{{ getTypeName(todayQuestion.type) }}</span>
              <span class="question-tags">
                <span class="mini-tag" v-for="tag in todayQuestion.tags" :key="tag">{{ tag.name }}</span>
              </span>
            </div> -->
          </div>
          <div class="question-action">
            <button class="btn-primary" @click="goToTodayQuestion">开始答题</button>
          </div>
        </div>
      </div>

      <!-- 热门知识点（学习内容入口） -->
      <div class="section">
        <div class="section-header">
          <h2>热门知识点 🔥</h2>
          <span class="section-desc">大家都在学的核心考点</span>
        </div>
        <div class="hot-topics">
          <div class="topic-item" v-for="topic in hotTopics" :key="topic.id" @click="goToTopicDetail(topic.id)">
            <div class="topic-icon">{{ topic.icon }}</div>
            <div class="topic-info">
              <h4>{{ topic.name }}</h4>
              <p>{{ topic.desc }}</p>
            </div>
            <div class="topic-tag">{{ topic.difficulty }}</div>
          </div>
        </div>
      </div>

      <!-- 历史趣闻/帖子模块（丰富内容） -->
      <div class="section">
        <div class="section-header">
          <h2>历史趣闻 📖</h2>
          <span class="section-desc">解锁课本外的历史故事</span>
        </div>
        <div class="history-posts">
          <div class="post-card" v-for="post in historyPosts" :key="post.id">
            <div class="post-img">{{ post.icon }}</div>
            <div class="post-content">
              <h3>{{ post.title }}</h3>
              <p class="post-desc">{{ post.desc }}</p>
              <div class="post-meta">
                <span>{{ post.readCount }}人阅读</span>
                <span>{{ post.likeCount }}❤️</span>
              </div>
            </div>
            <button class="post-btn" @click="goToPostDetail(post.id)">查看详情</button>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import useUserStore from '@/store/modules/user'
import { ElMessage } from 'element-plus'
import { dailyQuestion } from '@/api/question/question_bank'
import { userCheckIn,getUserCheckInDays } from '@/api/user/user_info'
import { useQuestionStore } from '@/store/modules/question'
const { proxy } = getCurrentInstance()
const { question_type } = proxy.useDict("question_type")
const userStore = useUserStore()
const questionStore = useQuestionStore()

const router = useRouter()
const userInfo = ref({
  userName: '历史爱好者',
}) 

// 今日一题数据
const todayQuestion = ref({
  content: '',
  tags: ''
})

// 热门知识点数据
const hotTopics = ref([
  { id: 1, icon: '🏛️', name: '中国古代政治制度', desc: '从分封制到中央集权的演变', difficulty: '中等' },
  { id: 2, icon: '⚔️', name: '近代列强侵华', desc: '鸦片战争、甲午战争等重要战役', difficulty: '较难' },
  { id: 3, icon: '📜', name: '新文化运动', desc: '思想解放与文化转型', difficulty: '简单' },
  { id: 4, icon: '🌍', name: '世界反法西斯战争', desc: '中国战场的贡献与意义', difficulty: '中等' }
])

// 历史趣闻帖子数据
const historyPosts = ref([
  { id: 1, icon: '🏮', title: '古代春节居然有这么多习俗', desc: '你知道吗？古代春节不仅贴春联，还有驱傩、守岁等数十种习俗...', readCount: 1256, likeCount: 328 },
  { id: 2, icon: '🗡️', title: '岳飞背后刺的不是“精忠报国”？', desc: '正史记载岳飞背后刺字其实是“尽忠报国”，流传过程中才逐渐变成...', readCount: 987, likeCount: 256 },
  { id: 3, icon: '🏯', title: '故宫为什么没有厕所？', desc: '明清时期故宫数万宫人，却没有一处现代厕所，他们是怎么解决的？', readCount: 876, likeCount: 198 }
])

// 打卡数据
const checkInDays = ref(2)
const hasCheckInToday = ref(false)
const totalCheckInDays = ref(0)

// 跳转方法
const goToQuestionBank = () => router.push('/questionBank')
const goToTodayQuestion = () => {
  // questionStore.setCurrentQuestion(todayQuestion.value)
  // questionStore.setCurrentQuestion(todayQuestion.value)
  router.push({
    path: '/doQuestion',
    query: { id: todayQuestion.value.id }
  })
}
const goToTopicDetail = (id) => router.push(`/topic/${id}`)
const goToPostDetail = (id) => router.push(`/post/${id}`)

// 打卡方法
const checkIn = () => {
  if (hasCheckInToday.value) {
    ElMessage.warning('今日已打卡！')
    return
  }
  userCheckIn().then(res=>{
    if(res.code === 200){
      hasCheckInToday.value = true
      getTotalCheckInDays()
      console.log('test')
      ElMessage.success(res.msg)
    }
  })
}

/** 获取总打卡天数 */
function getTotalCheckInDays(){
  getUserCheckInDays().then(res=>{
    totalCheckInDays.value = res.data
  })
}

/** 获取用户基础信息 */
const fetchUserInfo = async () => {
  try {
    userStore.getInfo().then(res=>{
      userInfo.value = res.user
    })
    
  } catch (error) {
    ElMessage.error('获取用户信息失败')
    console.error(error)
  }
}

/** 获取每日一题 */
function fetchDailyQuestion(){
  dailyQuestion().then(res=>{
    todayQuestion.value = res.data
  })
}

/** 查找题目类型 */
const getTypeName = (type) => {
  return question_type.value.find(item => item.value === type)?.label
}

/** 截取部分题目题干 */
const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
}

onMounted(() => {
  fetchUserInfo()
  fetchDailyQuestion()
  getTotalCheckInDays()
})
</script>

<style lang="scss" scoped>
// 全局变量（与学习数据页面保持一致）
$primary-color: #165DFF;
$primary-light: #e8f3ff;
$success-color: #00B42A;
$warning-color: #FF7D00;
$danger-color: #F53F3F;
$text-gray: #666;
$border-color: #e5e6eb;
$shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
$hover-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%);
}

// 内容区（适配全局layout的header，增加顶部间距）
.content-wrapper {
  flex: 1;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  margin-top: 16px; // 适配全局header的间距，避免内容顶到header
}

// 欢迎横幅（吸睛核心）
.welcome-banner {
  background: linear-gradient(135deg, $primary-color 0%, #4080ff 100%);
  border-radius: 16px;
  padding: 40px 32px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  box-shadow: $shadow;
  position: relative;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    top: -50px;
    right: -50px;
    width: 200px;
    height: 200px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
  }

  .banner-content {
    z-index: 1;
    h1 {
      font-size: 32px;
      margin-bottom: 12px;
    }
    p {
      font-size: 18px;
      opacity: 0.9;
      margin-bottom: 24px;
    }
    .start-btn {
      background: #fff;
      color: $primary-color;
      border: none;
      border-radius: 8px;
      padding: 12px 24px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
      }
    }
  }

  .banner-illustration {
    font-size: 120px;
    opacity: 0.8;
    z-index: 1;
    animation: float 3s ease-in-out infinite;
  }
}

// 板块通用样式
.section {
  margin-bottom: 32px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h2 {
      font-size: 20px;
      font-weight: 600;
      color: #333;
    }

    .section-desc {
      font-size: 14px;
      color: $text-gray;
    }
  }
}

// 今日一题卡片
.today-question-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: $shadow;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: $hover-shadow;
    transform: translateY(-2px);
  }

  .question-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;

        .question-tag {
          background-color: rgba(22, 93, 255, 0.1);
          color: $primary-color;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
        }

        .question-tags {
          .mini-tag {
            background-color: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 11px;
            margin-right: 4px;
          }
        }
      }

  .question-action {
    text-align: right;
    .btn-primary {
      background: $primary-color;
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 10px 20px;
      font-size: 16px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background: #0e48d8;
        transform: translateY(-2px);
      }
    }
  }
}

// 热门知识点
.hot-topics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;

  .topic-item {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: $shadow;
    display: flex;
    align-items: center;
    gap: 16px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      box-shadow: $hover-shadow;
      transform: translateX(4px);
    }

    .topic-icon {
      font-size: 32px;
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background: $primary-light;
      color: $primary-color;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .topic-info {
      flex: 1;
      h4 {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 4px;
      }
      p {
        font-size: 14px;
        color: $text-gray;
      }
    }

    .topic-tag {
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      background: $primary-light;
      color: $primary-color;
      &[data-difficulty="简单"] {
        background: #f0fff4;
        color: $success-color;
      }
      &[data-difficulty="中等"] {
        background: #fff7e6;
        color: $warning-color;
      }
      &[data-difficulty="较难"] {
        background: #fff2f0;
        color: $danger-color;
      }
    }
  }
}

// 历史趣闻帖子
.history-posts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;

  .post-card {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: $shadow;
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: all 0.3s ease;

    &:hover {
      box-shadow: $hover-shadow;
      transform: translateY(-4px);
    }

    .post-img {
      font-size: 48px;
      text-align: center;
      margin-bottom: 8px;
    }

    .post-content {
      flex: 1;
      h3 {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 8px;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      .post-desc {
        font-size: 14px;
        color: $text-gray;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        margin-bottom: 8px;
      }
      .post-meta {
        font-size: 12px;
        color: #999;
        display: flex;
        gap: 16px;
      }
    }

    .post-btn {
      background: transparent;
      color: $primary-color;
      border: 1px solid $primary-color;
      border-radius: 6px;
      padding: 8px 0;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background: $primary-color;
        color: #fff;
      }
    }
  }
}

// 打卡模块
.check-in-simple {
  padding: 20px;
  text-align: center;
}
.check-in-count {
  font-size: 16px;
  margin-bottom: 15px;
  color: #333;
}
.check-in-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  background: #409eff;
  color: white;
  font-size: 14px;
  cursor: pointer;
}
.check-in-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

// 浮动动画
@keyframes float {
  0% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0); }
}

// 响应式适配
@media (max-width: 768px) {
  .welcome-banner {
    flex-direction: column;
    text-align: center;
    gap: 24px;

    .banner-illustration {
      font-size: 80px;
    }
  }

  .hot-topics {
    grid-template-columns: 1fr;
  }

  .history-posts {
    grid-template-columns: 1fr;
  }

  .check-in-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>