<template>
  <div class="question-bank-container" v-if="!showDoQuestion">
    <!-- 多维度筛选栏：题型 + 标签 + 搜索 -->
    <div class="filter-bar">
      <!-- 题型筛选 -->
      <div class="filter-group">
        <span class="filter-label">题型：</span>
        <button
          class="filter-btn"
          :class="{ active: selectedType === 'all' }"
          @click="handleTypeFilter('all')"
        >
          全部
        </button>
        <button
          v-for="type in question_type"
          :key="type.value"
          class="filter-btn"
          :class="{ active: selectedType === type.value }"
          @click="handleTypeFilter(type.value)"
        >
          {{ type.label }}
        </button>
      </div>

      <!-- 标签筛选（级联选择） -->
      <div class="filter-group">
        <span class="filter-label">标签：</span>
        <el-cascader
          v-model="selectedTags"
          :options="tagTreeOptions"
          :props="cascaderProps"
          clearable
          collapse-tags
          collapse-tags-tooltip
          placeholder="请选择标签"
          @change="handleTagChange"
          style="width: 300px;"
        />
      </div>

       <!-- 重置筛选按钮 -->
      <div class="reset-filter" v-if="selectedType !== 'all' || selectedTags.length > 0 || searchKeyword">
        <button @click="resetAllFilters" class="reset-btn">重置筛选</button>
      </div>

      <!-- 搜索框 -->
      <div class="search-box">
        <input 
          v-model="searchKeyword" 
          type="text" 
          placeholder="搜索题目关键词..." 
          class="search-input"
          @keyup.enter="handleSearch"
        >
        <button @click="handleSearch" class="search-btn">搜索</button>
      </div>

    </div>

    <!-- 题目列表区域 -->
    <div class="question-content">
      <div v-if="searchKeyword" class="search-result">
        <h4>搜索结果：{{ searchKeyword }}</h4>
        <div v-if="question_list.length === 0" class="empty-result">
          <p>😔 未找到相关题目，请尝试更换关键词或筛选条件</p>
        </div>
      </div>
      <div v-else class="filter-tip" v-if="selectedType !== 'all' || selectedTags.length > 0">
        <h3>
          筛选条件：
          <span class="tip-item">{{ selectedType === 'all' ? '全部题型' : typeMap[selectedType] }}</span>；
          <el-tag type="success" size="small" class="tip-item" v-for="tag in selectedTags" :key="tag">{{ getTagLabel(tag) }}</el-tag>
        </h3>
      </div>

      <div class="question-list">
        <div 
          class="question-item" 
          v-for="item in question_list" 
          :key="item.id"
          @click="handleChangeQuestion(item)"
        >
          <p class="question-text">{{ truncateText(item.content,150)}}</p>
          <div class="question-meta">
            <span class="question-tag">{{ getTypeName(item.type) }}</span>
            <span class="question-tags">
              <span class="mini-tag" v-for="tag in item.tags" :key="tag">{{ tag.name }}</span>
              <span class="mini-tag">{{ item.code }}</span>
            </span>
          </div>
        </div>

        <div class="block">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="queryParams.pageNum"
            :page-sizes="[10, 20, 30, 50]"
            :page-size="queryParams.pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total">
          </el-pagination>
        </div>
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
const { proxy } = getCurrentInstance()
import { listQuestion } from "@/api/question/question_bank"
const { sys_normal_disable, sys_yes_no,question_difficulty,question_type } = proxy.useDict("sys_normal_disable", "sys_yes_no","question_difficulty","question_type")
import { ElInput } from 'element-plus'
import { getTagTree } from "@/api/question/tag"
// import doQuestion from './module/doQuestion.vue'
import { get } from '@vueuse/core'

const router = useRouter()

// 基础数据
const searchKeyword = ref('')
const selectedType = ref('all')
const selectedTags = ref([]) // 存储选中的标签ID数组
const question_list = ref([])
const tag_list = ref([])
const tagTreeOptions = ref([]) // 标签树选项
const queryParams = ref({
    pageNum: 1,
    pageSize: 10,
    content: undefined,
    code: undefined,
    status: undefined,
    tag_ids: undefined,
    type: undefined,
})
const total = ref(0)
const showDoQuestion = ref(false)

// 级联选择器配置
const cascaderProps = {
  multiple: true,
  value: 'value',
  label: 'label',
  children: 'children',
  checkStrictly: true, // 允许选择任意级别的选项
  emitPath: false // 不返回路径，只返回value
}

onMounted(() => {
  getList()
  showTagTree()
})

/** 查询题目列表 */
function getList() {
  // loading.value = true
  // console.log("查询参数：", queryParams.value)
  listQuestion(proxy.addDateRange(queryParams.value)).then(res => {
    // loading.value = false
    question_list.value = res.data
    total.value = res.count
  })
}

/**  跳转做题页面 */
const handleChangeQuestion = (question) => {
  // console.log('点击了题目：', question)
    router.push({
    path: '/doQuestion',
    query: { id: question.id }
  })
}

/** 查找题目类型 */
const getTypeName = (type) => {
  return question_type.value.find(item => item.value === type)?.label
}

// 题型映射
const typeMap = computed(() => {
  const map = {}
  question_type.value.forEach(type => {
    map[type.value] = type.label
  })
  return map
})

/** 重置查询条件 */
const resetQueryParams = () => {
  queryParams.value = {
    pageNum: 1,
    pageSize: 10,
    content: undefined,
    tag_ids: undefined,
    type: undefined,
  }
}

// 题型筛选切换
const handleTypeFilter = (type) => {
  selectedType.value = type
  queryParams.value.type = type === 'all' ? undefined : type
  getList()
}

// 标签选择变化处理
const handleTagChange = (tags) => {
  queryParams.value.tag_ids = tags.join(',')
  getList()
  // console.log("选中的标签ID数组：", queryParams.tag_ids)
}

// 获取标签树
function showTagTree(){
  getTagTree().then(res => {
    tag_list.value = res.data
    // 将标签树数据转换为级联选择器格式
    tagTreeOptions.value = transformTagTree(res.data)
  })
}

// 将标签树数据转换为级联选择器格式
function transformTagTree(data) {
  return data.map(item => ({
    value: item.value,
    label: item.label,
    children: item.children && item.children.length > 0 ? transformTagTree(item.children) : undefined
  }))
}

// 搜索处理
const handleSearch = () => {
  // 搜索时自动触发筛选
  queryParams.value.content = searchKeyword.value || undefined
  getList()
}

// 重置所有筛选条件
const resetAllFilters = () => {
  selectedType.value = 'all'
  selectedTags.value = []
  searchKeyword.value = ''
  resetQueryParams()
}

// 根据标签值获取标签名称
const getTagLabel = (tagValue) => {
  // 从标签树中递归查找标签名称
  const findLabel = (options, value) => {
    for (const option of options) {
      if (option.value === value) {
        return option.label
      }
      if (option.children && option.children.length > 0) {
        const found = findLabel(option.children, value)
        if (found) return found
      }
    }
    return null
  }
  return findLabel(tagTreeOptions.value, tagValue) || tagValue
}

/** 截取部分题目题干 */
const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
}

/** 处理分页变化 */
const handleSizeChange = (newValue) =>{
  queryParams.value.pageSize = newValue
  getList()
}

const handleCurrentChange = (newValue) =>{
  queryParams.value.pageNum = newValue
  getList()
}

</script>

<style lang="scss" scoped>
$primary-color: #165DFF;
$light-gray: #f5f7fa;
$border-color: #e5e6eb;

.question-bank-container {
  width: 100%;
  height: 100%;
}

// 多维度筛选栏
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 16px 0;
  border-bottom: 1px solid $border-color;
  margin-bottom: 16px;

  .filter-group {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;

    .filter-label {
      color: #333;
      font-size: 14px;
      font-weight: 500;
      white-space: nowrap;
    }

    .filter-btn {
      padding: 6px 16px;
      border: 1px solid $border-color;
      border-radius: 4px;
      background-color: #fff;
      color: #666;
      cursor: pointer;
      transition: all 0.3s;

      &.active {
        background-color: $primary-color;
        color: #fff;
        border-color: $primary-color;
      }

      &:hover {
        border-color: $primary-color;
        color: $primary-color;
      }
    }

    .tag-list {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;

      .tag-item {
        padding: 4px 12px;
        border: 1px solid $border-color;
        border-radius: 12px;
        background-color: #fff;
        color: #666;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.3s;

        &.active {
          background-color: $primary-color;
          color: #fff;
          border-color: $primary-color;
        }

        &:hover {
          border-color: $primary-color;
          color: $primary-color;
        }
      }
    }
  }

  .search-box {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 8px;

    .search-input {
      padding: 6px 12px;
      border: 1px solid $border-color;
      border-radius: 4px;
      outline: none;
      width: 240px;

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
  }
}

// 重置按钮
.reset-filter {
  margin-left: 20px;
  display: flex;
  align-items: center;

  .reset-btn {
    padding: 4px 12px;
    border: 1px solid $border-color;
    border-radius: 4px;
    background-color: #fff;
    color: #666;
    font-size: 12px;
    cursor: pointer;

    &:hover {
      border-color: $primary-color;
      color: $primary-color;
    }
  }
}

// 内容区域
.question-content {
  .search-result, .filter-tip {
    margin: 10px 0 18px;
    padding: 10px 14px;
    border-radius: 8px;
    background-color: rgba(22, 93, 255, 0.06);
    border: 1px solid rgba(22, 93, 255, 0.18);

    h4 {
      margin: 0;
      color: #333;
      font-size: 14px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;

      .tip-item {
        background-color: rgba(22, 93, 255, 0.18);
        color: $primary-color;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        border: 1px solid rgba(22, 93, 255, 0.32);
        display: inline-flex;
        align-items: center;
      }
    }
  }

  .empty-result {
    text-align: center;
    padding: 40px;
    background-color: $light-gray;
    border-radius: 8px;
    color: #999;
    font-size: 14px;
  }

  .question-list {
    .question-item {
      padding: 16px;
      border: 1px solid $border-color;
      border-radius: 8px;
      margin-bottom: 12px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        border-color: $primary-color;
        background-color: rgba(22, 93, 255, 0.02);
      }

      .question-text {
        margin: 0 0 8px 0;
        color: #333;
        font-size: 14px;
        line-height: 1.5;
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
    }
  }
}
</style>