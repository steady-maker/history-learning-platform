<template>
  <div class="my-question-bank">
    <!-- 左侧导航切换区 -->
    <div class="bank-sidebar">
      <div class="sidebar-menu">
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'all' }"
          @click="switchTab('all')"
        >
          全部题目
        </div>
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'wrong' }"
          @click="switchTab('wrong')"
        >
          错题列表
        </div>
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'collect' }"
          @click="switchTab('collect')"
        >
          我的收藏
        </div>
      </div>
    </div>

    <!-- 右侧题目列表区 -->
    <div class="bank-content">

      <!-- 题目列表 -->
      <div class="question-list">
        <!-- 空数据提示 -->
        <div v-if="filteredQuestions.length === 0" class="empty-page">
          <p>{{ emptyTipText }}</p>
        </div>

        <!-- 题目卡片 -->
        <div v-for="question in filteredQuestions" :key="question.question_id" class="question-card" >
          <!-- 题目头部（ID+标签+收藏按钮） -->
          <div class="card-header">
            <div class="question-tags">
              <span v-for="tag in question.tags" :key="tag" class="tag">{{ tag.name }}</span>
            </div>
            <button 
              class="collect-btn"
              :class="{ collected: question.is_collect === '1' }"
              @click="toggleCollect(question.question_id)"
            >
              {{ question.is_collect === '1' ? '取消收藏' : '收藏' }}
            </button>
          </div>

          <!-- 题干内容 -->
          <div class="card-body" @click="handleChangeQuestion(question)">
            <p class="question-content">{{ truncateText(question.content,150) }}</p>
          </div>

          <!-- 题目底部（得分/完成时间） -->
          <div class="card-footer">
            <span class="score">得分: {{ question.user_score }}/{{ question.full_score }}</span>
            <span class="complete-time">完成时间: {{ formatDuration(question.cost_time) }}</span>
          </div>
        </div>
      </div>
      
      <!-- <div class="block">
          <span class="demonstration">完整功能</span>
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="queryParams.pageNum"
            :page-sizes="[10, 20, 30, 50]"
            :page-size="queryParams.pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total">
          </el-pagination>
      </div> -->
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listUserQuestion, collectQuestion, cancelCollectQuestion } from '@/api/question/question_bank'
import { useRouter } from 'vue-router'
const router = useRouter()

// 1. 定义响应式数据
const activeTab = ref('all') // 当前激活的标签：all/wrong/collect
const allQuestions = ref([]) // 接口返回的所有题目数据
const queryParams = ref({
    pageNum: 1,
    pageSize: 10,
    content: undefined,
    code: undefined,
    status: undefined,
})
// 2. 切换标签逻辑
const switchTab = (tab) => {
  activeTab.value = tab
}

// 3. 过滤对应标签的题目
const filteredQuestions = computed(() => {
  switch (activeTab.value) {
    case 'all':
      return allQuestions.value // 全部题目
    case 'wrong':
      // 错题：得分小于满分的题目
      return allQuestions.value.filter(item => item.is_right==='0')
    case 'collect':
      // 收藏：已收藏的题目
      return allQuestions.value.filter(item => item.is_collect==='1')
    default:
      return allQuestions.value
  }
})

/**  跳转做题页面 */
const handleChangeQuestion = (question) => {
  // console.log('点击了题目：', questionId)
    router.push({
    path: '/doQuestion',
    query: { id: question.question_id }
  })
}


const emptyTipText = computed(() => {
  const tipMap = {
    all: '暂无作答记录',
    wrong: '暂无错题，继续保持！',
    collect: '暂无收藏的题目'
  }
  return tipMap[activeTab.value]
})

// 5. 收藏/取消收藏逻辑
const toggleCollect = (questionId) => {
  // 找到对应题目，切换收藏状态
  const target = allQuestions.value.find(item => item.question_id === questionId)
  if (target) {
    if(target.is_collect === '0'){
      collectQuestion({question_id:questionId})
    }else{
      cancelCollectQuestion({question_id:questionId})
    }
    // 切换状态
    target.is_collect = target.is_collect === '0' ? '1' : '0'
  }
}

/** 获取用户做过题目 */
const fetchQuestions = async () => {
  const res = await listUserQuestion()
  allQuestions.value = res.data
}

// 7. 页面加载时请求数据
onMounted(() => {
  fetchQuestions()
})

/** 格式化耗时（秒 -> 时分秒） */
const formatDuration = (seconds) => {
  if (seconds === null || seconds === undefined || seconds === '') return '--';
  const s = Number(seconds);
  if (Number.isNaN(s) || s < 0) return '--';
  const hrs = Math.floor(s / 3600);
  const mins = Math.floor((s % 3600) / 60);
  const secs = s % 60;
  const pad = (n) => String(n).padStart(2, '0');
  return `${hrs}小时${pad(mins)}分${pad(secs)}秒`;
}

/** 截取部分题目题干 */
const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
}

/** 处理分页变化 */
// const handleSizeChange = (newValue) =>{
//   queryParams.value.pageSize = newValue
//   getList()
// }

// const handleCurrentChange = (newValue) =>{
//   queryParams.value.pageNum = newValue
//   getList()
// }


</script>

<style lang="scss" scoped>
// 全局色调
$primary-color: #165DFF;
$light-gray: #f5f7fa;
$border-color: #e5e6eb;
$text-gray: #666;
$red: #F53F3F;
$green: #00B42A;

// 整体布局
.my-question-bank {
  display: flex;
  height: 100vh;
  background-color: $light-gray;
}

// 左侧导航
.bank-sidebar {
  width: 200px;
  background-color: #fff;
  border-right: 1px solid $border-color;
  padding: 20px 0;

  .sidebar-title {
    font-size: 18px;
    font-weight: 600;
    text-align: center;
    padding: 0 20px 20px;
    border-bottom: 1px solid $border-color;
    color: $primary-color;
  }

  .sidebar-menu {
    margin-top: 20px;

    .menu-item {
      padding: 12px 20px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        background-color: $light-gray;
      }

      &.active {
        background-color: lighten($primary-color, 40%);
        color: $primary-color;
        font-weight: 500;
        border-left: 3px solid $primary-color;
      }
    }
  }
}

// 右侧内容区
.bank-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;

  // 题目列表
  .question-list {
    .question-card {
      background-color: #fff;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .question-id {
          font-size: 14px;
          color: $text-gray;
        }

        .question-tags {
          display: flex;
          gap: 8px;

          .tag {
            background-color: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 11px;
            margin-right: 4px;
          }
        }

        .collect-btn {
          border: none;
          background: transparent;
          color: $primary-color;
          cursor: pointer;
          font-size: 14px;

          &.collected {
            color: $red;
          }
        }
      }

      .card-body {
        .question-content {
          font-size: 16px;
          color: #333;
          line-height: 1.6;
          margin: 0;
        }
      }

      .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;
        font-size: 14px;
        color: $text-gray;

        .score {
          &:not(:first-child) {
            color: $red;
          }
        }
      }
    }
  }

  // 空页面样式
  .empty-page {
    text-align: center;
    padding: 60px 0;
    color: #999;
    font-size: 18px;
  }
}
</style>