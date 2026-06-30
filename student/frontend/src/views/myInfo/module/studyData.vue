<template>
  <div class="info-panel">
    <!-- 空数据提示（美化版） -->
    <div v-if="Object.keys(studyData).length === 0" class="empty-page">
      <div class="empty-icon">📊</div>
      <p class="empty-text">暂无学习数据</p>
      <p class="empty-desc">开始答题，解锁你的专属学习报告</p>
    </div>

    <!-- 学习数据卡片（美化版） -->
    <div v-else class="info-card">
      <!-- 头部：核心数据+渐变背景 -->
      <div class="card-header">
        <div class="header-left">
          <h3 class="header-title">我的历史学习报告</h3>
          <p class="header-desc">
            已完成 <span class="total-num">{{ studyData.total_answers }}</span> 道题，
            超越 <span class="beat-num">{{ studyData.beat_percent }}%</span> 的用户
          </p>
        </div>
        <!-- 排名小徽章 -->
        <div class="rank-badge">
          <span class="rank-icon">🏆</span>
          <span class="rank-text">学习达人</span>
        </div>
      </div>

      <!-- 主体：数据网格+卡片动效 -->
      <div class="card-body">
        <div class="study-grid">
          <!-- 选择题完成数 -->
          <div class="study-item" hover-effect>
            <div class="item-icon choice-icon">📝</div>
            <div class="item-content">
              <span class="label">选择题完成数</span>
              <span class="value">{{ studyData.choice_total }}</span>
            </div>
          </div>

          <!-- 选择题正确率（加进度条） -->
          <div class="study-item" hover-effect>
            <div class="item-icon accuracy-icon">🎯</div>
            <div class="item-content">
              <span class="label">选择题正确率</span>
              <span class="value">{{ studyData.choice_accuracy }}%</span>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: studyData.choice_accuracy + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <!-- 问答题完成数 -->
          <div class="study-item" hover-effect>
            <div class="item-icon essay-icon">✍️</div>
            <div class="item-content">
              <span class="label">问答题完成数</span>
              <span class="value">{{ studyData.essay_total }}</span>
            </div>
          </div>

          <!-- 问答题得分率（加进度条） -->
          <div class="study-item" hover-effect>
            <div class="item-icon score-icon">📈</div>
            <div class="item-content">
              <span class="label">问答题得分率</span>
              <span class="value">{{ studyData.essay_accuracy }}%</span>
              <div class="progress-bar">
                <div 
                  class="progress-fill essay-fill" 
                  :style="{ width: studyData.essay_accuracy + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <!-- 近7天答题数（修正字段名+图标） -->
          <div class="study-item" hover-effect>
            <div class="item-icon week-icon">📅</div>
            <div class="item-content">
              <span class="label">最近7天答题数</span>
              <span class="value">{{ studyData.last_7_days_answers }}</span>
              <!-- 新增：活跃度标签 -->
              <div class="active-tag" :class="getActiveClass(studyData.last_7_days_answers)">
                {{ getActiveText(studyData.last_7_days_answers) }}
              </div>
            </div>
          </div>

          <!-- 新增：累计学习时长（扩展字段） -->
          <div class="study-item" hover-effect>
            <div class="item-icon time-icon">⏱️</div>
            <div class="item-content">
              <span class="label">累计学习时长</span>
              <span class="value">{{ formatTime(studyData.total_study_time || 0) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 新增：底部数据更新提示 -->
      <div class="card-footer">
        <span class="update-time">
          📌 数据更新于：{{ studyData.update_time || '2026-03-02 16:00' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

// 定义props
const props = defineProps({
  studyData: {
    type: Object,
    required: true
  }
})

// 方法：格式化学习时长（秒转 时:分:秒）
const formatTime = (seconds) => {
  if (!seconds) return '0小时0分钟'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return h > 0 ? `${h}小时${m}分钟` : `${m}分钟`
}

// 方法：根据近7天答题数判断活跃度
const getActiveClass = (num) => {
  if (num >= 50) return 'active-high'
  if (num >= 20) return 'active-mid'
  return 'active-low'
}

// 方法：获取活跃度文本
const getActiveText = (num) => {
  if (num >= 50) return '超高活跃度'
  if (num >= 20) return '中等活跃度'
  return '待提升'
}
</script>

<style lang="scss" scoped>
// 全局变量
$primary-color: #165DFF;
$primary-light: #e8f3ff;
$essay-color: #722ED1;
$essay-light: #f9f0ff;
$success-color: #00B42A;
$warning-color: #FF7D00;
$danger-color: #F53F3F;
$light-gray: #f5f7fa;
$border-color: #e5e6eb;
$text-gray: #666;
$shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
$hover-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);

.info-panel {
  width: 100%;
  padding: 0 8px;
}

// 空数据样式（美化）
.empty-page {
  text-align: center;
  padding: 80px 0;
  color: #999;
  font-size: 16px;

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.6;
  }

  .empty-text {
    font-size: 18px;
    margin-bottom: 8px;
  }

  .empty-desc {
    font-size: 14px;
    color: #ccc;
  }
}

// 核心卡片样式
.info-card {
  background: linear-gradient(135deg, #fff 0%, #f8f9ff 100%);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: $shadow;
  border: 1px solid $border-color;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: $hover-shadow;
    transform: translateY(-2px);
  }

  // 头部样式
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid $border-color;

    .header-left {
      .header-title {
        font-size: 20px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
      }

      .header-desc {
        font-size: 14px;
        color: $text-gray;

        .total-num {
          color: $primary-color;
          font-weight: 600;
          font-size: 16px;
          margin: 0 4px;
        }

        .beat-num {
          color: $success-color;
          font-weight: 600;
          font-size: 16px;
          margin: 0 4px;
        }
      }
    }

    // 排名徽章
    .rank-badge {
      background: linear-gradient(135deg, $primary-color 0%, #4080ff 100%);
      color: #fff;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 14px;
      font-weight: 500;
      box-shadow: 0 2px 8px rgba(22, 93, 255, 0.3);

      .rank-icon {
        margin-right: 4px;
        font-size: 16px;
      }
    }
  }

  // 主体网格
  .card-body {
    .study-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;

      // 单个数据项
      .study-item {
        background: #fff;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 3px solid $primary-color;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.2s ease;

        &[hover-effect]:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          transform: translateX(4px);
        }

        // 图标样式
        .item-icon {
          font-size: 24px;
          width: 48px;
          height: 48px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: $primary-light;
          color: $primary-color;

          &.choice-icon {
            background: #f0f8ff;
            color: #409eff;
          }

          &.accuracy-icon {
            background: #f0fff4;
            color: #52c41a;
          }

          &.essay-icon {
            background: $essay-light;
            color: $essay-color;
          }

          &.score-icon {
            background: #fff7e6;
            color: #fa8c16;
          }

          &.week-icon {
            background: #e6f7ff;
            color: #1890ff;
          }

          &.time-icon {
            background: #f9e6ff;
            color: #eb2f96;
          }
        }

        // 内容区域
        .item-content {
          flex: 1;

          .label {
            font-size: 14px;
            color: $text-gray;
            display: block;
            margin-bottom: 4px;
          }

          .value {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            display: block;
          }

          // 进度条样式
          .progress-bar {
            height: 6px;
            width: 100%;
            background: #f0f0f0;
            border-radius: 3px;
            overflow: hidden;

            .progress-fill {
              height: 100%;
              background: linear-gradient(90deg, $primary-color 0%, #69b1ff 100%);
              border-radius: 3px;
              transition: width 0.8s ease;
            }

            .essay-fill {
              background: linear-gradient(90deg, $essay-color 0%, #9370db 100%);
            }
          }

          // 活跃度标签
          .active-tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-top: 4px;

            &.active-high {
              background: #f0fff4;
              color: $success-color;
            }

            &.active-mid {
              background: #fff7e6;
              color: $warning-color;
            }

            &.active-low {
              background: #fff2f0;
              color: $danger-color;
            }
          }
        }
      }
    }
  }

  // 底部样式
  .card-footer {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px dashed $border-color;

    .update-time {
      font-size: 12px;
      color: $text-gray;
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .info-card .card-body .study-grid {
    grid-template-columns: 1fr;
  }

  .info-card .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;

    .rank-badge {
      align-self: flex-end;
    }
  }
}
</style>