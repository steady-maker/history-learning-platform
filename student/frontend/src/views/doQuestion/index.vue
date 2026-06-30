<template>
  <div class="do-question-container" >

    <!-- 左侧做题历史 -->
    <div class="history-sidebar-wrapper" :style="{ marginRight: historyCollapsed ? '8%' : '0' }">

      <!-- 展开按钮（折叠状态显示） -->
      <button 
        @click="historyCollapsed = !historyCollapsed" 
        v-if="historyCollapsed" 
        class="collapse-btn"
        style="left: 0;"
      >
        {{ '▶' }}
      </button>

      <!-- 侧边栏主体 -->
      <div 
        class="history-sidebar" 
        :class="{ 'collapsed': historyCollapsed }"
        :style="{ width: historySidebarWidth + 'px' }"
        v-if="!historyCollapsed"
      >


        <div class="history-header">
          <h4>
              历史做题记录
          </h4>
          <span>          
            <button 
            @click="historyCollapsed = !historyCollapsed" 
            class="collapse-btn"
            >
            {{ '◀' }}
            </button>
         </span>
                    
        </div>

        <div class="history-list">
          <div
            v-for="(item,key) in historyList"
            :key="item.answer_seq"
            class="history-item"
            :class="{ active: item.answer_seq === activeSeq }"
            @click="selectHistory(item)"
          >
            <!-- <div class="item-title">{{ truncateText(stripMarkdown(item.content || item.question || ''), 72) }}</div> -->
            <div class="item-title">第{{ key }}次回答</div>
            <div class="item-meta">
              <span
                class="item-score"
                :class="{ correct: isCorrect(item), wrong: !isCorrect(item) }"
              >
                {{ item.total_score || 0 }} / {{ question.score || 0 }}
              </span>
              <span class="item-time">{{ formatCreatedTime(item) }}</span>
            </div>
          </div>
        </div>
      </div>

            <!-- 侧边拖动手柄 -->
      <div 
        class="resize-handle" 
        v-if="!historyCollapsed"
        @mousedown="startHistoryResize"
      ></div>
    </div>

    <div class="main-content">
      <!-- 题目内容区 -->
      <div class="question-content">
          <!-- 顶部返回栏 -->
      <div class="question-header">
        <button @click="goBack" class="back-btn">
          <span class="arrow-icon"></span>返回题库
        </button>
        <!-- 做题耗时显示 -->
        <div class="time-cost">
          <span>题目编号：{{question.code}}</span>
          题目消耗时间：{{ formatTime(timeCost) }}
        </div>
        <div class="time-cost" v-if="isSubmitted">
          <template v-if="question.has_sub_question === '1'">
            本题得分：
            <span 
              v-for="(subQ, index) in question.detailList" 
              :key="subQ.sub_question_id || index"
              class="sub-score-item"
            ><span> 第{{ index + 1 }}小问：</span>
              <!-- 按子题ID匹配得分，无得分时显示0 -->
              {{ gotScore[subQ.sub_question_id] || 0 }} / {{ subQ.score }}  &nbsp;&nbsp;   
            </span>
          </template>
          <template v-else>
            本题得分：
            <span>{{ gotScore[question.id] || 0 }} / {{ question.score }}</span>
          </template>
        </div>
        <button @click="handleAiFeedback" class="ai-review-btn" v-if="isSubmitted">
          我要复盘
        </button>
      </div>

      <!-- 主题目题干 -->
      <div class="question-title" v-html="formattedQuestionContent"></div>

      <!-- 题目图片渲染 -->
      <div class="question-images" v-if="renderImageList.length">
          <div class="question-image-item" v-for="(img, index) in renderImageList" :key="index">
            <img 
              :src="img.url" 
              :alt="`题目图片${index + 1}`" 
              class="question-image"
              loading="lazy"
              @error="handleImageError($event, index)"
              @load="handleImageLoad($event)"
            >
          </div>
      </div>

        <!-- 作答区域 -->
      <div class="answer-area">

          <!-- 选择题 -->
          <div v-if="question.type === '1' || question.type === '2'" class="choice-group">
            <!-- 有子题目（连环题） -->
            <div v-if="question.has_sub_question === '1'" class="sub-question-group">
              <!-- 循环渲染每个子问题 -->
              <div class="sub-question-item" v-for="(subQ, subIndex) in question.detailList" :key="subQ.sub_question_id || subIndex">
                <!-- 子问题题干 -->
                <div class="sub-question-title">
                  {{ subIndex + 1 }}. {{ subQ.question }}
                </div>
                
                <!-- 子问题选项 -->
                <div 
                  class="option-item" 
                  v-for="(option, index) in subQ.option_list" 
                  :key="option.option_id || index"
                  @click="selectOption(subQ.sub_question_id || subIndex, index)"
                  :class="[
                    { active: !isSubmitted && isOptionSelected(subQ.sub_question_id || subIndex, index) },
                    isSubmitted && {  
                      correct: isOptionCorrect(subQ.sub_question_id || subIndex, index),    
                      incorrect: isOptionIncorrect(subQ.sub_question_id || subIndex, index) 
                    }
                  ]"
                >
                  {{ String.fromCharCode(65 + index) }}. {{ option.option_content }}
                </div>
              </div>
            </div>

              <!-- 无子题目（普通单选题） -->
            <div v-else class="normal-question-options">
                <div 
                  class="option-item" 
                  v-for="(option, index) in question.option_list" 
                  :key="option.option_id || index"
                  @click="selectOption(0, index)"
                  :class="[
                    { active: !isSubmitted && isOptionSelected(0, index) },
                    isSubmitted && {  
                      correct: isOptionCorrect(0, index),    
                      incorrect: isOptionIncorrect(0, index) 
                    }
                  ]"
                >
                  {{ String.fromCharCode(65 + index) }}. {{ option.option_content }}
                </div>
            </div>
          </div>

          <!-- 填空题 -->
          <div v-if="question.typeKey === 'fill'" class="fill-group">
            <input 
              v-model="fillAnswer" 
              type="text" 
              placeholder="请输入答案" 
              class="fill-input"
              @input="saveDraft"
            >
          </div>

          <!-- 问答题 -->
          <div v-if="question.type === '5'" class="answer-group">
            <!-- 有子题目（连环问答题） -->
            <div v-if="question.has_sub_question === '1'" class="sub-question-group">
              <!-- 循环渲染每个子问题 -->
              <div 
                class="sub-question-item" 
                v-for="(subQ, subIndex) in question.detailList" 
                :key="subQ.sub_question_id || subIndex"
              >
                <!-- 子问题题干 -->
                <div class="sub-question-title">
                  {{ subQ.question }}
                </div>
                
                <!-- 子问题答题输入框 -->
                <textarea 
                  v-model="textAnswers[subQ.sub_question_id]"
                  placeholder="请输入答题内容" 
                  class="answer-textarea sub-answer-textarea"
                  @input="(e) => saveDraft(subQ.sub_question_id || subIndex, e.target.value)"
                  :disabled="isSubmitted"
                ></textarea>
              </div>
            </div>

            <!-- 无子题目（普通问答题） -->
            <div v-else class="normal-question-answer">
              <textarea 
                v-model="textAnswers[question.id]" 
                placeholder="请输入答题内容" 
                class="answer-textarea"
                @input="saveDraft"
                :disabled="isSubmitted"
              ></textarea>
            </div>

          </div>

              <!-- 提交后展示参考答案 -->
          <div v-if="isSubmitted" class="reference-answer">
            <span class="label">参考答案：</span>
            <!-- {{ correctTextAnswers }} -->
            <div class="question-title" v-html="formattedQuestionTextAnswerContent"></div>
          </div>

            <!-- 底部提交栏 -->
          <div class="question-footer" v-if="!isSubmitted">
            <button @click="getAiPromptStream" class="submit-btn">我要提示</button>
            <button @click="submitAnswer" class="submit-btn">提交答案</button>
          </div>
      </div>

    </div>

    </div>

        <!-- AI提示对话区（可收起） -->
    <div class="ai-sidebar-wrapper" :style="{marginLeft:aiPanelCollapsed ? '8%': '0'}">
        <div 
          class="resize-handle" 
          v-if="!aiPanelCollapsed"
          @mousedown="startResize"
        ></div>

        <!-- 展开按钮（折叠状态显示） -->
        <button 
          @click="aiPanelCollapsed = !aiPanelCollapsed" 
          v-if="aiPanelCollapsed" 
          class="collapse-btn"
          style="right:0;"
        >
          {{ '◀' }}
        </button>

        <!-- 侧边栏主体 -->
        <div 
          class="ai-sidebar" 
          :class="{ 'collapsed': aiPanelCollapsed }"
          :style="{ width: sidebarWidth + 'px' }"
          v-if="!aiPanelCollapsed"
        >

          <div class="ai-header">

            <span>
              <button 
                @click="aiPanelCollapsed = !aiPanelCollapsed" 
                class="collapse-btn"
              >
                {{ '▶' }}
              </button>
            </span>
            <h4>AI提示对话区</h4>
          </div>

          <div class="chat-container">
            <div class="chat-messages">
              <!-- 聊天消息列表 -->
              <div 
                v-for="(msg, index) in messages" 
                :key="index"
                :class="['message', msg.role]"
              >
                <div class="avatar">
                  {{ msg.role === 'user' ? '👤' : '🤖' }}
                </div>
                <div 
                  class="content"
                  v-html="markdownToHtml(msg.content)" 
                ></div>
              </div>

              <!-- 加载中状态 -->
              <div class="message assistant loading" v-if="loading">
                <div class="avatar">🤖</div>
                <div class="content">正在思考...</div>
              </div>
            </div>
          </div>
        </div>
    </div>
    
  </div>

</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getChoiceQuestionReviewPromptStream, getQuestionPromptStream,getSubjectiveQuestionReviewPromptStream,getQuestionReviewPromptStream } from '@/api/question/prompt'
import { handleSubmitChoiceAnswer, handleSubjectiveAnswer, getQuestion, listUserQuestion,listUserDone } from '@/api/question/question_bank'
import { ElMessage } from 'element-plus'
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { useQuestionStore } from '@/store/modules/question'
const questionStore = useQuestionStore()
const router = useRouter()
const route = useRoute()

// 配置 marked 解析器（可选，优化渲染效果）
marked.setOptions({
  breaks: true,        // 把 \n 转成 <br>
  gfm: true,           // 支持 GitHub Flavored Markdown
  headerIds: false,    // 不自动给标题加 ID
  mangle: false        // 不转义 HTML 实体
});

// 封装一个安全的 Markdown 转 HTML 函数
function markdownToHtml(markdown) {
  if (!markdown) return '';
  const rawHtml = marked.parse(markdown);
  return DOMPurify.sanitize(rawHtml); // 净化 HTML，防止 XSS
}

// 基础状态
const selectedOptions = ref({});
const fillAnswer = ref('')
const aiPanelCollapsed = ref(false)
const timeCost = ref(0)
const isSubmitted = ref(false)
const gotScore = ref({})
const correctAnswer = ref('')
const submitAnswers = ref({}); 
let timer = null

const loading = ref(false);
const sessionId = ref('');  // 会话ID（多轮复用）
const remainingRounds = ref(3);  // 剩余对话轮数
const messages = ref([]);  // 完整对话记录
// 侧边栏宽度（默认+拖动后的值）
const sidebarWidth = ref(400);
// 历史侧边栏宽度
const historySidebarWidth = ref(320);
// 子问答题答案（对象格式，key=子题ID/index，value=答案内容）
const textAnswers = ref({})
const correctTextAnswers = ref('')

// 拖动相关变量
let startX = 0;
let startWidth = 0;
// 历史侧边栏拖动变量
let historyStartX = 0;
let historyStartWidth = 0;

let question = reactive({})

// 历史做题记录（左侧列表）
const historyList = ref([])
const activeSeq = ref('')
const historyCollapsed = ref(true)

// 左侧历史栏拖动相关函数
const startHistoryResize = (e) => {
  historyStartX = e.clientX;
  historyStartWidth = historySidebarWidth.value;
  document.addEventListener('mousemove', handleHistoryResize);
  document.addEventListener('mouseup', stopHistoryResize);
};

const handleHistoryResize = (e) => {
  // console.log('开始拖动左侧', '初始X:', historyStartX, '当前X:', e.clientX, '初始宽度:', historyStartWidth)
  const moveDistance = e.clientX - historyStartX;
  const newWidth = historyStartWidth + moveDistance;
  if (newWidth >= 100 && newWidth <= 500) {
    historySidebarWidth.value = newWidth;
  }
};

const stopHistoryResize = () => {
  document.removeEventListener('mousemove', handleHistoryResize);
  document.removeEventListener('mouseup', stopHistoryResize);
};

/** 获取本题历史记录 */
const fetchHistory = (questionId) => {
  listUserDone({question_id:questionId}).then(res=>{
    if(res.code == 200){
      historyList.value = res.data.record_list || []
      const questionAnswerList = res.data.question_answer_list || []
      correctTextAnswers.value = questionAnswerList.answer_content || "暂无答案"
      correctAnswer.value = questionAnswerList.correct_option_ids || []
    }
  })
}

/** 切换历史记录 */
const selectHistory = (item) => {
  if (!item ) return
  activeSeq.value = item.answer_seq
  
  // 查看历史记录（已完成状态）
  if (item.answer_seq) {
    isSubmitted.value = true

    // 每一个item都是返回的答案结构
    const scoreMap = {};
    const answerMap = {};
    console.log('历史记录原始数据', item)

    Object.entries(item).forEach(([key, val]) => {
      // 过滤掉 cost_time、create_time 等非题目字段
      if (val?.got_score !== undefined) {
        scoreMap[key] = val.got_score; 
        answerMap[key] = val.answer;  
      }
    });

    // 完成已有答案等内容赋值
    gotScore.value = scoreMap
    timeCost.value = item.cost_time

    // 单选或者多选，需要反选选项index
    if (question.type === "1" || question.type === "2") {
      // console.log('历史记录答案原始数据', answerMap)
      try {
        // 有子题目,
        if (question.has_sub_question === "1") {
          const selectedIndexes = {}
          const submitResult = {}

          for (const [subId, ansStr] of Object.entries(answerMap)) {
            const answerIds = JSON.parse(ansStr || "[]")
            const subQ = question.detailList.find(item => item.sub_question_id == subId)
            const option_list = subQ?.option_list || []

            const indexes = answerIds
              .map(id => option_list.findIndex(o => o.option_id === id))
              .filter(idx => idx !== -1)

            selectedIndexes[subId] = indexes
            submitResult[subId] = answerIds
          }

          selectedOptions.value = selectedIndexes
          submitAnswers.value = submitResult

        } else {
          const qid = question.id
          const ansStr = answerMap[qid] || "[]"
          const answerIds = JSON.parse(ansStr)

          const selectedIndexes = answerIds
            .map(id => question.option_list.findIndex(o => o.option_id === id))
            .filter(idx => idx !== -1)

          // 单选只保留第一个
          if (question.type === "1") {
            selectedOptions.value = selectedIndexes.slice(0, 1)
          } else {
            selectedOptions.value = selectedIndexes
          }

          submitAnswers.value = answerIds
        }
      } catch (e) {
        selectedOptions.value = []
        submitAnswers.value = []
      }
    }else {
      try {
        // 初始化 textAnswers 为对象（必须是对象才能用 textAnswers[id]）
        textAnswers.value = {}
        console.log("当前answer_map",answerMap)

        if (question.has_sub_question === "1") {
          // 有子题：遍历 answerMap，把答案塞进 textAnswers 对象
          for (const [subId, ans] of Object.entries(answerMap)) {
            textAnswers.value[subId] = ans || ""
          }
          console.log("当前textAnswers.value",textAnswers.value)
        } else {
          // 无子题：直接赋值 textAnswers[主题目ID]
          textAnswers.value[question.id] = answerMap[question.id] || ""
          console.log("当前textAnswers.value",textAnswers.value)
        }
      } catch (e) {
        // 异常兜底
        textAnswers.value = {}
        console.log("当前textAnswers.value",textAnswers.value)
      }
    }

    // Ai聊天内容
    messages.value = item.session_msg || []
    sessionId.value = item.session_id || ''
    clearInterval(timer)
    
    return
  }
}

/** 判断得分样式 */
const isCorrect = (item) => {
  if (!item) return false
  const score = Number(item.total_score)
  const full = Number(question.score )
  return !Number.isNaN(score) && !Number.isNaN(full) && score >= full
}

const stripMarkdown = (text) => {
  if (!text) return ''
  // 简单去掉 Markdown 语法，避免展示过长标签
  return String(text)
    .replace(/\r?\n/g, ' ')
    .replace(/\*\*|__|\*|_|~~|`/g, '')
    .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
    .replace(/>\s*/g, '')
    .replace(/#{1,6}\s*/g, '')
    .trim()
}

/** 截取题目内容 */
const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) {
    return text
  }
  return text.substring(0, maxLength) + '...'
}

/** 处理题目时间 */
const formatCreatedTime = (item) => {
  const timeValue = item.create_time || item.created_at || item.gmt_create || item.createdTime || item.time
  if (!timeValue) return '--'
  const date = new Date(timeValue)
  if (Number.isNaN(date.getTime())) return String(timeValue)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

/** 初始化题目 */
const initQuestion = (questionId) => {
  getQuestion(questionId).then(res=>{
    if(res.code == 200){
      Object.assign(question, res.data) 
    }
  })
}

/** 格式化题目内容 */
const formattedQuestionContent = computed(() => {
  if (!question?.content) return ''
  const res = markdownToHtml(question.content)
  return res
})

/** 格式化题目文本答案内容 */
const formattedQuestionTextAnswerContent = computed(() => {
  // console.log('参考答案原始数据', correctTextAnswers.value)
  if (!correctTextAnswers.value) return ''
  const res = markdownToHtml(correctTextAnswers.value)
  // return markdownToHtml(correctTextAnswers.value)
  // console.log("参考答案：",res)
  return res 
})

// 开始拖动
const startResize = (e) => {
  startX = e.clientX;
  startWidth = sidebarWidth.value;
  // 监听鼠标移动和松开事件
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
};

// 拖动中
const handleResize = (e) => {
  // 计算新宽度（约束最小/最大范围）
  const moveDistance = startX - e.clientX;
  const newWidth = startWidth + moveDistance;
  // sidebarWidth.value = newWidth;
  // console.log('拖动中', '初始X:', startX, '当前X:', e.clientX, '初始宽度:', startWidth, '新宽度:', newWidth)
  // 约束宽度范围：300px（最小）~ 800px（最大）
  if (newWidth >= 200 ) {
    sidebarWidth.value = newWidth;
  }
};

// 结束拖动
const stopResize = () => {
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
};

// 格式化时间
const formatTime = (seconds) => {
  // console.log('格式化时间',seconds)
  const min = Math.floor(seconds / 60)
  const sec = seconds % 60
  return `${min}分${sec}秒`
}

// 保存草稿（用户中途退出时自动保存）
const saveDraft = () => {
  // console.log('保存草稿',question)
  const draft = {
    questionId: question.id,
    selectedOptions: selectedOptions.value,
    fillAnswer: fillAnswer.value,
    textAnswers: textAnswers.value,
    timeCost: timeCost.value
  }
  localStorage.setItem(`draft_${question.id}`, JSON.stringify(draft))
}

// 加载草稿
const loadDraft = () => {
  const draft = localStorage.getItem(`draft_${question.id}`)
  if (draft) {
    const data = JSON.parse(draft)
    selectedOptions.value = data.selectedOptions
    fillAnswer.value = data.fillAnswer
    textAnswers.value = data.textAnswers
    timeCost.value = data.timeCost
  }
}

// 选中选项的方法（区分子题）
const selectOption = (subId = 0, index) => {
  // console.log('selectOption', subId, index)
  const { type, has_sub_question, option_list, detailList } = question;
  // 提交后禁止选择
  if (isSubmitted.value) return;

  // 1. 统一获取当前题/子题的选中索引
  let currentSelectedIndexes = [];
  if (has_sub_question === '1') {
    currentSelectedIndexes = selectedOptions.value[subId] || [];
  } else {
    currentSelectedIndexes = selectedOptions.value || [];
  }

  // 2. 区分单/多选，更新选中索引
  if (type === '1') {
    // 单选：直接替换为当前索引
    currentSelectedIndexes = [index];
  } else if (type === '2') {
    // 多选：切换选中状态
    const idx = currentSelectedIndexes.indexOf(index);
    if (idx > -1) {
      currentSelectedIndexes.splice(idx, 1);
    } else {
      currentSelectedIndexes.push(index);
    }
  }

  // 3. 关键：同步更新「要提交的option_id」
  let currentSubmitAnswers = [];
  if (has_sub_question === '1') {
    // 连环题：从detailList取当前子题的option_list
    const currentSubQ = detailList.find(item => (item.sub_question_id === subId));
    // console.log(currentSubQ);
    currentSubmitAnswers = currentSelectedIndexes.map(idx => {
      return currentSubQ?.option_list[idx]?.option_id || '';
    }).filter(Boolean); // 过滤空值
  } else {
    // 普通题：从全局option_list取
    currentSubmitAnswers = currentSelectedIndexes.map(idx => {
      return option_list[idx]?.option_id || '';
    }).filter(Boolean);
  }

  // 4. 单选只保留第一个（确保格式统一）
  if (type === '1') {
    currentSubmitAnswers = currentSubmitAnswers.length > 0 ? [currentSubmitAnswers[0]] : [];
  }

  // 5. 把更新后的值存回变量
  if (has_sub_question === '1') {
    // console.log('更新子问题答案', subId, currentSubmitAnswers);
    selectedOptions.value[subId] = currentSelectedIndexes; // 存索引（样式用）
    submitAnswers.value[subId] = currentSubmitAnswers;     // 存option_id（提交用）
  } else {
    selectedOptions.value = currentSelectedIndexes;         // 存索引（样式用）
    submitAnswers.value = currentSubmitAnswers;             // 存option_id（提交用）
  }
};

/**
 * 判断选项是否被选中
 * @param {Number|String} subId 子题ID（连环题必传，普通题传0/undefined）
 * @param {Number} index 选项索引
 * @returns {Boolean} 是否选中
 */
const isOptionSelected = (subId = 0, index) => {
  const { type, has_sub_question } = question;
  // 1. 先统一获取当前题/子题的选中状态
  let currentSelected = [];
  if (has_sub_question === '1') {
    // 连环题：按子题ID取选中状态（对象结构：{subId: [选中索引]}）
    currentSelected = selectedOptions.value[subId] || [];
  } else {
    // 普通题：直接取全局选中状态
    currentSelected = selectedOptions.value || [];
  }

  // 2. 区分单/多选判断逻辑
  if (type === '1') {
    // 单选：currentSelected 是数组（存唯一选中索引），判断第一个元素是否等于index
    // 补充：处理空数组的情况（用户未选择时返回false）
    return currentSelected.length > 0 && currentSelected[0] === index;
  } else if (type === '2') {
    // 多选：判断数组中是否包含当前索引
    return currentSelected.includes(index);
  }
  return false;
};

/**
 * 判断选项是否正确（提交后生效）
 * @param {Number|String} subId 子问题ID（和后端返回的subId一致）
 * @param {Number} index 选项索引
 * @returns {Boolean} 是否为正确答案
 */
const isOptionCorrect = (subId = 0, index) => {
  const { has_sub_question, detailList } = question;

  // 基础容错：未提交/无正确答案时直接返回false
  if (!isSubmitted.value || !correctAnswer.value) return false;

  // 统一转为字符串匹配后端subId（解决数字/字符串类型不匹配）
  let targetCorrectAnswers = [];
  if (has_sub_question === '1') {
    const backendSubId = String(subId);
    targetCorrectAnswers = correctAnswer.value[backendSubId] || [];
  } else {
    targetCorrectAnswers = correctAnswer.value || [];
  }

  // 按子问题ID精准匹配子题，获取当前选项的option_id
  let currentOptionId = '';
  if (has_sub_question === '1') {
    const currentSubQ = detailList.find(
      item => String(item.sub_question_id) === String(subId)
    );
    currentOptionId = currentSubQ?.option_list[index]?.option_id;
  } else {
    currentOptionId = question.option_list[index]?.option_id;
  }

  // 统一转为数字判断，避免option_id类型不匹配（如"61"和61）
  const normalizedTarget = targetCorrectAnswers.map(id => Number(id));
  const normalizedCurrent = Number(currentOptionId);
  return !isNaN(normalizedCurrent) && normalizedTarget.includes(normalizedCurrent);
};

/**
 * 判断选项是否错误（提交后生效）
 * @param {Number|String} subId 子问题ID
 * @param {Number} index 选项索引
 * @returns {Boolean} 是否为错误选项（选中且不正确）
 */
const isOptionIncorrect = (subId = 0, index) => {
  if (!isSubmitted.value) return false;
  return isOptionSelected(subId, index) && !isOptionCorrect(subId, index);
};

// 提交答案
const submitAnswer = () => {
  if (isSubmitted.value) {
    ElMessage.warning('您已提交过答案了哦！')
    return
  }

  if (loading.value){
    ElMessage({
      message: '正在获取判题信息，请稍候...',
      type: 'warning',
    })
    return;
  } 

  loading.value = true;
  const { id: question_id, type } = question
  const isChoice = type === '1' || type === '2'
  const userAnswer = isChoice ? submitAnswers.value : textAnswers.value

  // console.log('提交答案', {
  //   question_id,
  //   userAnswer,
  //   timeCost: timeCost.value,
  //   sessionId: sessionId.value,
  //   textanswer:textAnswers.value
  // })

  const submitFn = isChoice 
    ? handleSubmitChoiceAnswer 
    : handleSubjectiveAnswer

  submitFn({
    user_answer: userAnswer,
    question_id,
    cost_time: timeCost.value,
    chat_session_id: sessionId.value || ''
  }).then(res => {
    if (res.code !== 200) return
    clearInterval(timer)
    gotScore.value = res.data.user_score
    sessionId.value = res.data.session_id
    if (isChoice) {
      correctAnswer.value = res.data.correct_answer
      correctTextAnswers.value = res.data.correct_answer_str
    } else {
      correctTextAnswers.value = res.data.correct_answer
      if (res.data?.ai_response) {
        const aiResponse = res.data.ai_response;
        messages.value.push({ 
          role: 'assistant', 
          content: aiResponse 
        })
      }
    }
    ElMessage.success('提交成功！')
    isSubmitted.value = true
    loading.value = false;
  }).catch(() => {
    loading.value = false;
    ElMessage.error('提交失败！')
  })
}

/** AI提示 */
const getAiPromptStream = async () => {
  if (!question.id) {
    alert('题目ID不能为空！');
    return;
  }
  if (remainingRounds.value <= 0){
    ElMessage({
      message: '提示次数已用完！',
      type: 'warning',
    })
    return 
  }
  remainingRounds.value -= 1;
  // console.log("剩余提问次数",remainingRounds.value)

  if (loading.value){
    ElMessage({
      message: '正在获取提示，请稍候...',
      type: 'warning',
    })
    return;
  }

  loading.value = true;
  aiPanelCollapsed.value = false; // 获取提示时自动展开侧边栏
  const currentAiReply = ref('');
  const aiMsgIndex = messages.value.length;
  messages.value.push({ role: 'assistant', content: '' });

  try {
    const response = await getQuestionPromptStream({
      question_id: question.id,
      session_id: sessionId.value || ''
    });

    // console.log("ai提示",response)

    // 验证响应是否成功
    if (!response.ok) {
      throw new Error(`请求失败：${response.status}`);
    }
    // 验证是否支持流式
    if (!response.body) {
      throw new Error("浏览器不支持流式响应");
    }

    // 核心：获取Fetch的ReadableStream读取器
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    // 逐段读取流式数据
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // 解码并分割后端返回的JSON行
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n').filter(line => line.trim());
      
      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          // 处理不同类型的流式数据
          switch (data.type) {
            case 'meta':
              sessionId.value = data.data.session_id;
              // remainingRounds.value = data.data.remaining_rounds;
              break;
            case 'content':
              currentAiReply.value += data.data;
              messages.value[aiMsgIndex].content = currentAiReply.value;
              break;
            case 'error':
              messages.value[aiMsgIndex].content = "获取提示失败";
              loading.value = false;
              break;
            case 'end':
              loading.value = false;
              break;
          }
        } catch (e) {
          console.error('解析单行失败：', e, '原始数据：', line);
        }
      }
    }
  } catch (error) {
    loading.value = false;
    messages.value[aiMsgIndex].content = `❌ 获取提示失败！`;
    console.error('流式请求异常：', error);
  }
};

// AI复盘
const handleAiFeedback = async () => {
  if (!question.id) {
    alert('题目ID不能为空！');
    return;
  }
  if (loading.value){
    ElMessage({
      message: '正在获取复盘信息，请稍候...',
      type: 'warning',
    })
    return;
  } 

  loading.value = true;
  aiPanelCollapsed.value = false;
  const currentAiReply = ref('');
  const aiMsgIndex = messages.value.length;
  messages.value.push({ role: 'assistant', content: '' });

  try {
    let response = null
    const { type } = question
    const isChoice = type === '1' || type === '2'
    const userAnswer = isChoice ? submitAnswers.value : textAnswers.value
    response = await getQuestionReviewPromptStream({
      question_id: question.id,
      session_id: sessionId.value || '',
      user_answer: userAnswer
    });

    // 验证响应是否成功
    if (!response.ok) {
      throw new Error(`请求失败：${response.status} `);
    }
    // 验证是否支持流式
    if (!response.body) {
      throw new Error("浏览器不支持流式响应");
    }

    // 核心：获取Fetch的ReadableStream读取器
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    // 逐段读取流式数据
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // 解码并分割后端返回的JSON行
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n').filter(line => line.trim());
      
      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          // 处理不同类型的流式数据
          switch (data.type) {
            case 'meta':
              sessionId.value = data.data.session_id;
              // remainingRounds.value = data.data.remaining_rounds;
              break;
            case 'content':
              currentAiReply.value += data.data;
              messages.value[aiMsgIndex].content = currentAiReply.value;
              break;
            case 'error':
              messages.value[aiMsgIndex].content = `❌ 获取复盘信息失败！`;
              loading.value = false;
              break;
            case 'end':
              loading.value = false;
              break;
          }
        } catch (e) {
          console.error('解析单行失败：', e, '原始数据：', line);
        }
      }
    }
  } catch (error) {
    loading.value = false;
    messages.value[aiMsgIndex].content = `❌ 获取复盘信息失败！`;
    console.error('流式请求异常：', error);
  }
}

// 返回题库
const goBack = () => {
  saveDraft()
  router.push('/questionBank')
}

// 计时逻辑
onMounted(() => {
  timer = setInterval(() => {
    timeCost.value++
    saveDraft()
  }, 1000)

  const questionId = route.query.id
  if (!questionId) {
    alert('未获取到题目ID')
    router.push('/')
    return
  } else {
    initQuestion(questionId)
    fetchHistory(questionId)
  }
})

watch(
  () => route.query.id,
  (newId) => {
    if (!newId) return
    initQuestion(newId)
  }
)

/** 处理图片内容 */
const renderImageList = computed(() => {
  let imgList = []
  const rawImgList = question.img_list

  // 步骤1：处理 JSON 字符串（如果存储的是序列化后的 JSON）
  if (typeof rawImgList === 'string' && rawImgList) {
    try {
      imgList = JSON.parse(rawImgList)
    } catch (e) {
      console.warn('图片JSON解析失败', e)
      return []
    }
  } else if (Array.isArray(rawImgList)) {
    // 步骤2：如果是 el-upload 原生的 file-list 数组
    imgList = rawImgList
  }

  // 步骤3：提取每张图片的 URL（适配 el-upload 上传后的返回格式）
  return imgList.map(item => {
    // 适配常见的上传返回格式（根据你的实际接口返回调整！）
    return {
      // 情况1：上传成功后接口返回的 url 字段（最常见）
      url: item.url || item.response?.data?.url || item.raw?.url || '',
      // 补充：如果你的存储格式是之前的 entities 结构，可兼容
      // url: item.entity_content?.image?.image_ori?.url || item.url || ''
    }
  }).filter(img => img.url) // 过滤空URL
})

// 图片加载错误兜底
const handleImageError = (e, index) => {
  e.target.src = '/static/images/empty-img.png' // 替换为你的占位图
  console.warn(`第${index+1}张图片加载失败`)
}

// 图片加载完成（可选）
const handleImageLoad = (e) => {
  e.target.classList.add('loaded')
}

onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  clearInterval(timer)
  saveDraft()
})


</script>

<style lang="scss" scoped>
$primary-color: #165DFF;
$light-gray: #f5f7fa;
$border-color: #e5e6eb;

// 整体做题容器
.do-question-container {
  display: flex;
  // grid-template-columns: 320px 1fr 400px;
  gap: 24px;
  padding: 24px;
  background-color: #fff;
  overflow-x: auto; /* 宽度不足时允许横向滚动 */
}

.history-sidebar-wrapper,
.ai-sidebar-wrapper {
  flex-shrink: 0;  // 防止被压缩
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 12px;
  border-bottom: 1px solid #eee;
  padding: 10px 15px;
}

.history-sidebar-wrapper {
  display: flex;
  align-items: stretch;
  // min-height: 800px;
  max-height: 1000px;
  position: relative;
  transition: all 0.3s ease;
}

.history-sidebar {
  width: 320px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: width 0.3s ease;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.2s, border 0.2s;
  border: 1px solid transparent;
}

.history-item:hover {
  background-color: rgba(102, 126, 234, 0.08);
}

.history-item.active {
  border-color: $primary-color;
  background: rgba(22, 93, 255, 0.12);
}

.item-title {
  font-size: 14px;
  color: #333;
  line-height: 1.4;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  color: #666;
}

.item-score {
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.04);
}

.item-score.correct {
  color: #0b6623;
  background: rgba(0, 182, 42, 0.12);
}

.item-score.wrong {
  color: #a2261d;
  background: rgba(245, 63, 63, 0.12);
}

.main-content {
  flex: 1; /* 占据剩余空间，让 AI 侧边栏在右侧 */
  min-width: 0; /* 防止内容溢出导致布局错乱 */
  // margin: 0 5%;
  // height: 100%;
}


// 左侧题目内容区通用样式
.question-header, 
.question-content, 
.time-cost, 
.answer-area, 
.question-footer {
  width: 100%;
}

// 顶部返回栏
.question-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  
  .back-btn {
    font-size: 18px;
    padding: 6px 12px;
    font-weight: 500;
    border: 1px solid $border-color;
    border-radius: 4px;
    background-color: #fff;
    color: $primary-color;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    
    &:hover {
      background-color: $light-gray;
    }
  }
  
  .ai-review-btn {
    padding: 6px 20px;
    background-color: $primary-color;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    margin: 0 auto;
    display: inline-block;
    
    &:hover {
      background-color: #0F4BD1;
    }
  }
}

// 自定义返回箭头
.arrow-icon {
  width: 8px;
  height: 8px;
  border-left: 2px solid #333;
  border-bottom: 2px solid #333;
  transform: rotate(45deg);
  display: inline-block;
}

.back-btn:hover .arrow-icon {
  border-color: #212529;
}

// 子问题样式
.sub-question-item {
  margin-bottom: 40px;
}

.sub-question-group {
  margin-bottom: 24px;
}

.sub-question-title {
  font-weight: 600;
  margin: 12px 0;
  color: #303133;
}

// 耗时/得分显示
.time-cost {
  float: right;
  color: #666;
  font-size: 14px;
  margin: 16px 0;
  padding: 8px 16px;
  background-color: rgba(22, 93, 255, 0.05);
  border-radius: 4px;
  width: auto;
}

// 题目题干
.question-content {
  .question-title {
    font-size: 18px;
    color: #333;
    line-height: 1.6;
    margin-bottom: 16px;
    padding: 16px;
    background-color: $light-gray;
    border-radius: 8px;
  }
}

// 作答区域样式
.answer-area {
  // 选择题样式
  .choice-group {
    .option-item {
      width: auto;
      padding: 12px 16px;
      border: 1px solid $border-color;
      border-radius: 6px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s;
      
      &.active {
        border-color: $primary-color;
        background-color: rgba(22, 93, 255, 0.05);
        color: $primary-color;
      }
      
      &:hover {
        border-color: $primary-color;
      }
      
      // 提交后对错样式
      &.correct {
        border-color: #67c23a;
        background-color: #f0f9eb;
        color: #67c23a;
      }
      
      &.incorrect {
        border-color: #f56c6c;
        background-color: #fef0f0;
        color: #f56c6c;
      }
    }
  }
  
  // 填空题样式
  .fill-group {
    .fill-input {
      width: 100%;
      padding: 12px;
      border: 1px solid $border-color;
      border-radius: 6px;
      outline: none;
      
      &:focus {
        border-color: $primary-color;
      }
    }
  }
  
  // 问答题样式
  .answer-group {
    .answer-textarea {
      width: 100%;
      height: 200px;
      padding: 12px;
      border: 1px solid $border-color;
      border-radius: 6px;
      outline: none;
      resize: none;
      
      &:focus {
        border-color: $primary-color;
      }
      
      &:disabled {
        background-color: #f8f8f8;
        color: #666;
        cursor: not-allowed;
      }
    }
    
    .sub-answer-textarea {
      min-height: 80px;
      height: auto;
    }
    
  }
}
// 参考答案样式
.reference-answer {
  margin-top: 5%;
  padding: 8px;
  background-color: #f5fafe;
  border-left: 3px solid $primary-color;
  font-size: 13px;
  
  .label {
    font-weight: 600;
    color: $primary-color;
  }
}

// 底部提交按钮栏
.question-footer {
  display: flex;
  margin-top: 32px;
  text-align: center;
  
  .submit-btn {
    padding: 8px 24px;
    background-color: $primary-color;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    margin: 0 auto;
    display: inline-block;
    
    &:hover {
      background-color: #0F4BD1;
    }
  }
}

// AI提示侧边栏样式
.ai-sidebar-wrapper {
  display: flex;
  align-items: stretch;
  // height: 600px;
  min-height: 800px;
  max-height: 1000px;
  // height:100%;
  position: relative;
  transition: all 0.3s ease;

  // 收起状态：宽度为箭头按钮宽度
  &.collapsed {
    width: 40px;
  }
}

.ai-sidebar {
  right: 0;        /* 右侧贴边 */
  width: 400px; /* 默认宽度 */
  height: 100%; /* 占满整个视口高度 */
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: width 0.3s ease;

  // 收起时：宽度为0，隐藏内容
  .ai-sidebar-wrapper.collapsed & {
    width: 0;
    border: none;
  }
}

// 折叠/展开按钮（始终显示在最右侧）
.collapse-btn {
  position: absolute;
  top: 10px;
  color: #000000;
  border: none;
  background-color: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

// 侧边栏拖动手柄
.resize-handle {
  width: 15px;
  border-left: 2px solid transparent;
  cursor: ew-resize;
}

// 侧边栏头部
.ai-header {
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

// 聊天容器
.chat-container {
  height: calc(100% - 50px);
  padding: 10px;
}

// 聊天消息区
.chat-messages {
  height: 100%;
  padding: 20px;
  overflow-y: auto;
  background-color: #f9f9f9;
  line-height: 1.6;
  
  // 消息通用样式
  .message {
    display: flex;
    margin: 8px 0;
    // max-width: 80%;
    
    &.assistant {
      flex-direction: row;
      margin-right: auto;
      
      .content {
        background: #f5f5f5;
      }
    }
    
    &.user {
      justify-content: flex-end;
    }
    
    &.system {
      margin: 0 auto 20px;
      background-color: #e8f4f8;
      border-radius: 8px;
      padding: 10px;
      max-width: 100%;
    }
    
    &.loading .content {
      color: #999;
    }
    
    .avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #eee;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 8px;
    }
    
    .content {
      padding: 8px 12px;
      border-radius: 12px;
      // max-width: 80%;
      line-height: 1.4;
      font-size: 14px;
      
      h1, h2, h3 {
        margin: 12px 0 8px;
        font-weight: 600;
      }
      
      p {
        margin: 8px 0;
      }
      
      ul, ol {
        margin: 8px 0;
        padding-left: 24px;
      }
      
      li {
        margin: 4px 0;
      }
      
      strong {
        font-weight: 600;
      }
      
      code {
        background: #f5f5f5;
        padding: 2px 4px;
        border-radius: 4px;
        font-family: monospace;
      }
    }
  }
}
</style>