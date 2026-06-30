<template>
  <div class="app-container home">
    <!-- 数据概览卡片（新增AI核心指标，适配15天维度） -->
    <div class="stats-card-group">
      <div class="stats-card">
        <div class="card-header">
          <span class="card-title">总用户数</span>
          <span class="card-icon">👥</span>
        </div>
        <div class="card-value">{{ statisticData.user.total }}</div>
        <div class="card-trend">
          <span class="trend-up">+{{ statisticData.user.growth_rate }}%</span>
          <span class="trend-desc">较上月</span>
        </div>
      </div>
      <div class="stats-card">
        <div class="card-header">
          <span class="card-title">累计答题数</span>
          <span class="card-icon">📝</span>
        </div>
        <div class="card-value">{{ statisticData.answer.total }}</div>
        <div class="card-trend">
          <span class="trend-up">+{{ statisticData.answer.growth_rate }}%</span>
          <span class="trend-desc">较上月</span>
        </div>
      </div>
      <div class="stats-card">
        <div class="card-header">
          <span class="card-title">15天AI总使用次数</span>
          <span class="card-icon">🤖</span>
        </div>
        <div class="card-value">{{ statisticData.ai_usage_total.total_ai_usage }}</div>
        <div class="card-trend">
          <span class="trend-up">+{{ statisticData.ai_usage_total.growth_rate }}%</span>
          <span class="trend-desc">较前15天</span>
        </div>
      </div>
      <div class="stats-card">
        <div class="card-header">
          <span class="card-title">15天平均留存率</span>
          <span class="card-icon">📈</span>
        </div>
        <div class="card-value">{{ statisticData.user_retention.avg_15d_retention_rate }}%</div>
        <div class="card-trend">
          <span class="trend-up">+{{ statisticData.user_retention.growth_rate }}%</span>
          <span class="trend-desc">较前15天</span>
        </div>
      </div>
    </div>
    <!-- 数据可视化图表区域（核心替换：近15天 AI功能使用+用户留存率 多折线图） -->
    <div class="chart-group">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">近15天AI功能使用&用户留存率趋势</span>
        </div>
        <div class="chart-content">
          <div id="aiRetentionChart" style="width: 100%; height: 300px"></div>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">标签分布</span>
        </div>
        <div class="chart-content">
          <div id="categoryChart" style="width: 100%; height: 300px"></div>
        </div>
      </div>
    </div>
    <!-- 最近反馈列表（原有不变） -->
    <div class="feedback-group">
      <div class="feedback-header">
        <span class="feedback-title">最近用户反馈</span>
        <el-button size="small" type="primary" @click="goToFeedbackManage">查看全部</el-button>
      </div>
      <div class="feedback-table">
        <el-table :data="recentFeedbackList" border size="small" style="width: 100%">
          <el-table-column label="序号" align="center" key="index" width="120">
            <template #default="scope">
              <span>{{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="content" label="反馈内容" show-overflow-tooltip></el-table-column>
          <el-table-column label="状态" align="center" key="feedback_status">
            <template #default="scope" >
                <el-tag 
                size="small"
                :type="getFeedbackTagType(scope.row.feedback_status)">
                    {{ getFeedbackLabel(scope.row.feedback_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="提交时间" width="180"></el-table-column>
        </el-table>
      </div>
    </div>
    <!-- 系统信息 + 数据补充（新增AI日维度数据，适配15天维度） -->
    <div class="system-info-group">
      <div class="system-info">
        <div class="info-title">系统信息</div>
        <div class="info-content">
          <div class="info-item">
            <span class="info-label">系统版本：</span>
            <span class="info-value">{{ systemInfoData.version }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">运行时长：</span>
            <span class="info-value">{{ systemInfoData.uptime }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">服务器负载：</span>
            <span class="info-value">{{ systemInfoData.server_load }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">数据库容量：</span>
            <span class="info-value">{{ systemInfoData.db_size }}</span>
          </div>
        </div>
      </div>
      <div class="data-panel">
        <div class="info-title">核心数据概览</div>
        <div class="info-content">
          <div class="info-item">
            <span class="info-label">今日答题数：</span>
            <span class="info-value">{{ statisticData.today_data.today_answer_count }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">今日新增用户：</span>
            <span class="info-value">{{ statisticData.today_data.today_new_user_count }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">今日AI使用次数：</span>
            <span class="info-value">{{ statisticData.today_data.today_ai_use_count }}</span>
          </div>
          <!-- <div class="info-item">
            <span class="info-label">今日AI判题次数：</span>
            <span class="info-value">{{ avgAccuracy }}</span>
          </div> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup name="Index">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getIndexInfo} from '@/api/biz/index'
import { listUserFeedback } from '@/api/biz/webUser'
import { listSystemInfo } from '@/api/system/config'

// 系统版本
const version = ref('1.0.0')

// 原有统计数据,需要有原值，或者上面{{}}中对值有判断，否则会渲染错误
const statisticData = ref({
  "feedback": { "current_month": 0, "last_month_total": 0, "pending": 0, "total": 0, "growth_rate": 0.0, "pending_rate": 0.0 },
  "answer": { "current_month": 0, "last_month_total": 0, "total": 985620, "growth_rate": 15.8 },
  "user": { "current_month_new": 1856, "last_month_total": 0, "total": 15826, "growth_rate": 12.5 },
  "ai_usage_total":{
                "ai_tip_counts": 0,
                "ai_judge_counts": 0,
                "ai_review_counts": 0,
                "total_ai_usage": 0,
                "growth_rate": 0.0
            },
  "ai_usage_trend": [],
  "user_retention": {
      "avg_15d_retention_rate": 0.0,
      "growth_rate": 0.0,
      "daily_retention": []
  },
  "today_data":{
      "today_ai_use_count":'',
      "today_answer_count":'',
      "today_new_user_count":'',
  }
})

const systemInfoData = ref({
  "system_version": "",
  "uptime": "",
  "server_load": "",
  "db_size": ""
})


// 日期格式：MM-DD，适配图表展示，真实项目由接口按天聚合返回
const aiRetentionData = ref([])
const tagFrequencyData = ref([])

// 运行时长/系统信息（原有不变）
const runTime = ref('30天12小时45分钟')
const serverLoad = ref(28)
const dbSize = ref('2.8GB')

// 最近反馈列表
const recentFeedbackList = ref([])
const queryParams = ref({  
    pageNum: 1,
    pageSize: 10,
})
const { proxy } = getCurrentInstance()
const { feedback_type } = proxy.useDict("feedback_type")

// 获取系统信息
function getSystemInfo() { 
    listSystemInfo().then(res => {
    systemInfoData.value = res.data
  })
}

// 获取反馈列表
function getFeedbackList() {
  listUserFeedback(proxy.addDateRange(queryParams.value)).then(res => {
    recentFeedbackList.value = res.data
  })
}

/**根据反馈状态值获取类型 */
function getFeedbackTagType(value) { 
  const item = feedback_type.value.find(item=>item.value === value)
  return item ? item.elTagType : ''
}

/** 根据反馈状态值获取标签值 */
function getFeedbackLabel(value){
  const item = feedback_type.value.find(item=>item.value===value)
  return item ? item.label : ''
}

/**
 * 工具函数：生成近15天的完整日期数组（格式：YYYY-MM-DD）
 * @returns {string[]} 近15天日期数组（从15天前到今天）
 */
function generateLast15Days() {
  const days = []
  const today = new Date()
  // 生成近15天（包含今天，共15天）
  for (let i = 14; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    // 格式化为 YYYY-MM-DD
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    days.push(`${month}-${day}`)
  }
  return days
}

/**
 * 工具函数：将数组数据转为日期映射表
 * @param {Array} list 原始数据列表
 * @param {string} dateKey 日期字段名
 * @returns {Object} 日期: 数据 的映射表
 */
function convertToDateMap(list, dateKey) {
  const map = {}
  list.forEach(item => {
    const date = item[dateKey]
    if (date) {
      map[date] = item
    }
  })
  return map
}

// 获取首页统计数据
function fetchIndexInfo() {
  // 1. 生成完整15天日期（不管后端返回多少，先固定日期轴）
  const last15Days = generateLast15Days()
  
  getIndexInfo().then(res => {
    if (res.code === 200) {
      // 2. 赋值原始统计数据
      statisticData.value = res.data
      
      // 3. 提取后端返回的原始数据（兼容空）
      const aiTrendList = res.data.ai_usage_trend || []
      const retentionList = res.data.user_retention?.daily_retention || []
      
      // 4. 转为日期映射表（方便快速查找）
      const aiMap = convertToDateMap(aiTrendList, 'stat_date')
      const retentionMap = convertToDateMap(retentionList, 'first_login_date')
      
      // 5. 补全15天数据（核心逻辑：遍历完整日期，无数据则补0）
      const aiRetentionList = last15Days.map(date => {
        // 查找当前日期的AI数据（无则补0）
        const aiItem = aiMap[date] || {
          ai_tip_counts: 0,
          ai_judge_counts: 0,
          ai_review_counts: 0
        }
        // 查找当前日期的留存率数据（无则补0）
        const retentionItem = retentionMap[date] || {
          retained_users: 0,
          new_users: 0,
          daily_retention_rate_percent: 0
        }
        
        // 拼装单条数据
        return {
          date: date,
          aiTip: aiItem.ai_tip_counts || 0,
          aiJudge: aiItem.ai_judge_counts || 0,
          aiReview: aiItem.ai_review_counts || 0,
          // retainedUsers: retentionItem.retained_users || 0,
          // newUsers: retentionItem.new_users || 0,
          retention: retentionItem.daily_retention_rate_percent || 0
        }
      })
      aiRetentionData.value = aiRetentionList
      // console.log('aiRetentionData:', aiRetentionData.value)

      // 获取饼图数据
      tagFrequencyData.value = res.data.tag_frequency
      initCharts()
      
      // 6. 拆解为图表所需的独立数组
      // aiRetentionData.value = {
      //   xAxis: last15Days, // 完整15天日期轴
      //   aiTipData: aiRetentionList.map(item => item.aiTip),
      //   aiJudgeData: aiRetentionList.map(item => item.aiJudge),
      //   aiReviewData: aiRetentionList.map(item => item.aiReview),
      //   retentionRateData: aiRetentionList.map(item => item.retentionRate),
      //   newUsersData: aiRetentionList.map(item => item.newUsers),
      //   list: aiRetentionList // 补全15天的完整列表
      // }
    }
  }).catch(err => {
    console.error('获取统计数据失败：', err)
    // 异常时：日期轴保留15天，数据全补0
    aiRetentionData.value = {
      xAxis: last15Days,
      aiTipData: Array(15).fill(0),
      aiJudgeData: Array(15).fill(0),
      aiReviewData: Array(15).fill(0),
      retentionRateData: Array(15).fill(0),
      newUsersData: Array(15).fill(0),
      list: last15Days.map(date => ({
        date,
        aiTip: 0,
        aiJudge: 0,
        aiReview: 0,
        retainedUsers: 0,
        newUsers: 0,
        retentionRate: 0
      }))
    }
  })
}

// 初始化图表（核心：近15天AI+留存多折线图 + 保留原有知识点饼图）
const initCharts = () => {
  // 1. 核心替换：近15天 AI提示/判题/复盘 + 用户留存率 多折线双Y轴图
  const aiRetentionChart = echarts.init(document.getElementById('aiRetentionChart'))
  const aiRetentionOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e5e9f2',
      borderWidth: 1,
      padding: 12,
      textStyle: { color: '#333' },
      // 悬浮展示当日所有指标，数据清晰
      formatter: (params) => {
        let res = `<div style="font-weight: 600; margin-bottom: 8px;">2026-${params[0].name}</div>`
        params.forEach(item => {
          const unit = item.seriesName.includes('留存率') ? '%' : '次'
          res += `<div>${item.seriesName}：<span style="color: ${item.color};">${item.value}${unit}</span></div>`
        })
        return res
      }
    },
    legend: {
      data: ['AI提示次数', 'AI判题次数', 'AI复盘次数', '用户留存率(%)'],
      top: 0,
      right: 0,
      textStyle: { fontSize: 12, color: '#666' },
      itemGap: 10 // 缩小图例间距，适配15天布局
    },
    grid: { left: '6%', right: '5%', bottom: '12%', top: '20%', containLabel: true },
    xAxis: {
      type: 'category',
      data: aiRetentionData.value.map(item => item.date),
      axisLine: { lineStyle: { color: '#e5e9f2' } },
      axisTick: { show: false },
      axisLabel: { 
        textStyle: { color: '#666', fontSize: 11 },
        interval: 0 // 强制显示所有15天日期，不会隐藏
      }
    },
    // 双Y轴：左侧=AI使用次数（数值），右侧=留存率（百分比），指标无冲突
    yAxis: [
      {
        type: 'value',
        name: 'AI使用次数（次）',
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          textStyle: { color: '#666', fontSize: 11 },
          formatter: (v) => v > 1000 ? `${(v/1000).toFixed(1)}k` : v
        },
        splitLine: { lineStyle: { color: '#f5f7fa' } }
      },
      {
        type: 'value',
        name: '用户留存率（%）',
        min: 45,
        max: 50,
        interval: 1,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { textStyle: { color: '#F53F3F', fontSize: 11 }, formatter: '{value}%' },
        splitLine: { show: false }
      }
    ],
    series: [
      // AI提示次数（主色，蓝色）
      {
        name: 'AI提示次数',
        type: 'line',
        yAxisIndex: 0,
        data: aiRetentionData.value.map(item => item.aiTip),
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false, // 悬浮才显示标记点，避免视觉杂乱
        lineStyle: { width: 2.5, color: '#165DFF' },
        itemStyle: { color: '#165DFF', borderColor: '#fff', borderWidth: 2 },
        emphasis: { symbolSize: 7 },
        label: { 
          show: true, 
          position: 'top', 
          fontSize: 10, 
          color: '#165DFF',
          formatter: (v) => v.value > 1000 ? `${(v.value/1000).toFixed(1)}k` : v.value 
        }
      },
      // AI判题次数（绿色）
      {
        name: 'AI判题次数',
        type: 'line',
        yAxisIndex: 0,
        data: aiRetentionData.value.map(item => item.aiJudge),
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false,
        lineStyle: { width: 2.5, color: '#00B42A' },
        itemStyle: { color: '#00B42A', borderColor: '#fff', borderWidth: 2 },
        emphasis: { symbolSize: 7 },
        label: { 
          show: true, 
          position: 'top', 
          fontSize: 10, 
          color: '#00B42A',
          formatter: (v) => v.value > 1000 ? `${(v.value/1000).toFixed(1)}k` : v.value 
        }
      },
      // AI复盘次数（橙色）
      {
        name: 'AI复盘次数',
        type: 'line',
        yAxisIndex: 0,
        data: aiRetentionData.value.map(item => item.aiReview),
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false,
        lineStyle: { width: 2.5, color: '#FF7D00' },
        itemStyle: { color: '#FF7D00', borderColor: '#fff', borderWidth: 2 },
        emphasis: { symbolSize: 7 },
        label: { 
          show: true, 
          position: 'top', 
          fontSize: 10, 
          color: '#FF7D00' 
        }
      },
      // 用户留存率（红色虚线+菱形标记，与AI次数视觉区分）
      {
        name: '用户留存率(%)',
        type: 'line',
        yAxisIndex: 1,
        data: aiRetentionData.value.map(item => item.retention),
        smooth: true,
        symbol: 'diamond', // 菱形标记，易识别
        symbolSize: 6,
        showSymbol: false,
        lineStyle: { width: 2.5, color: '#F53F3F', type: 'dashed' }, // 虚线区分百分比指标
        itemStyle: { color: '#F53F3F', borderColor: '#fff', borderWidth: 2 },
        emphasis: { symbolSize: 8 },
        label: { 
          show: true, 
          position: 'top', 
          fontSize: 10, 
          color: '#F53F3F',
          formatter: '{value}%' 
        }
      }
    ]
  }
  aiRetentionChart.setOption(aiRetentionOption)

  // 2. 保留原有知识点答题分布饼图（样式微调，适配整体）
  const categoryChart = echarts.init(document.getElementById('categoryChart'))
  const categoryOption = {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
    legend: { top: '0%', left: 'center', textStyle: { fontSize: 12, color: '#666' } },
    series: [
      {
        name: '标签数',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
        labelLine: { show: false },
        data: tagFrequencyData.value
      }
    ]
  }
  categoryChart.setOption(categoryOption)

  // 窗口自适应（适配所有图表，包括15天折线图）
  const resizeHandler = () => {
    aiRetentionChart.resize()
    categoryChart.resize()
  }
  window.addEventListener('resize', resizeHandler)

  // 组件卸载清理，防止内存泄漏（企业开发规范）
  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler)
    aiRetentionChart.dispose()
    categoryChart.dispose()
  })
}

// 跳转反馈管理（原有不变）
const goToFeedbackManage = () => {
  ElMessage.info('跳转到反馈管理页面')
}
// 处理反馈（原有不变）
const handleFeedback = (id) => {
  ElMessage.success(`开始处理反馈ID：${id}`)
}

// 挂载初始化（原有不变）
onMounted(() => {
  fetchIndexInfo()
  getFeedbackList()
  getSystemInfo()
  initCharts()
})
</script>

<style scoped lang="scss">
// 所有样式完全复用原有，无任何修改，直接适配15天维度图表
.app-container {
  width: 100%;
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f7fa;
  box-sizing: border-box;
}
.stats-card-group {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
  .stats-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
    &:hover {
      box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      .card-title {
        font-size: 14px;
        color: #666;
        font-weight: 500;
      }
      .card-icon {
        font-size: 20px;
      }
    }
    .card-value {
      font-size: 28px;
      font-weight: 600;
      color: #333;
      margin-bottom: 8px;
    }
    .card-trend {
      display: flex;
      align-items: center;
      font-size: 12px;
      .trend-up {
        color: #00B42A;
        font-weight: 500;
        margin-right: 5px;
      }
      .trend-down {
        color: #FF7D00;
        font-weight: 500;
        margin-right: 5px;
      }
      .trend-warning {
        color: #F53F3F;
        font-weight: 500;
        margin-right: 5px;
      }
      .trend-desc {
        color: #999;
      }
    }
  }
}
.chart-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
  .chart-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      .chart-title {
        font-size: 16px;
        font-weight: 600;
        color: #333;
      }
    }
    .chart-content {
      width: 100%;
      height: 300px;
    }
  }
}
.feedback-group {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
  .feedback-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    .feedback-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
    }
  }
  .feedback-table {
    width: 100%;
  }
}
.system-info-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
  .system-info, .data-panel {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    .info-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin-bottom: 15px;
    }
    .info-content {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 15px;
      @media (max-width: 480px) {
        grid-template-columns: 1fr;
      }
      .info-item {
        display: flex;
        align-items: center;
        .info-label {
          font-size: 14px;
          color: #666;
          width: 120px;
        }
        .info-value {
          font-size: 14px;
          color: #333;
          font-weight: 500;
        }
      }
    }
  }
}
</style>