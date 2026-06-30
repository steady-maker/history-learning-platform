<template>
  <el-dialog
    v-model="visible"
    width="380px"
    :close-on-click-modal="false"
    :show-close="false"
    class="captcha-dialog"
  >
    <div class="puzzle-container">
      <!-- 顶部标题区 -->
      <div class="puzzle-header">
        <span class="puzzle-header-left">拖动下方滑块完成拼图</span>
        <div class="puzzle-header-right">
          <el-icon class="icon-btn" @click="refreshImg">
            <Refresh />
          </el-icon>
          <el-icon class="icon-btn" @click="closeVerificationBox">
            <Close />
          </el-icon>
        </div>
      </div>

      <!-- 图片区域 -->
      <div :style="[{ position: 'relative', overflow: 'hidden' }, lockingWidthStyle]">
        <div :style="[{ position: 'relative' }, lockingWidthStyle, lockingHeightStyle]">
          <img
            id="pic-lost"
            ref="picLost"
            :style="[lockingWidthStyle, lockingHeightStyle]"
            :src="canvasStr"
            alt=""
          />
        </div>

        <div :style="[lockingWidthStyle, lockingHeightStyle]" class="puzzle-lost-box">
          <img id="block-fill" ref="blockFill" :src="blockStr" alt="" />
        </div>
      </div>

      <!-- 滑块区域 -->
      <div :style="lockingWidthStyle" class="slider-container">
        <div ref="sliderBtnMask" class="slide-verify-slider-mask">
          <div
            ref="sliderBtn" 
            class="mask-item"          
            @mousedown.prevent="startMove"
            @touchstart.prevent="startMove"
          >
          <div style="font-size: 16px;">
            <el-icon><Right /></el-icon>
          </div>
          </div>
        </div>
        <span>向右拖动</span>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getSliderImg, getCode } from '@/api/login'

const props = defineProps({
  mobile: String,
  modelValue: Boolean
})
const emit = defineEmits(['update:modelValue', 'success'])

const visible = ref(props.modelValue)
watch(() => props.modelValue, val => (visible.value = val))
watch(visible, val => emit('update:modelValue', val))

watch(visible, val => {
  if (val) nextTick(initSliderImg)
})

const canvasStr = ref('')
const blockStr = ref('')

const picLost = ref(null)
const blockFill = ref(null)
const sliderBtn = ref(null)
const sliderBtnMask = ref(null)

const dataWidth = 310
const puzzleSize = 40
let moveStart = 0

const lockingWidthStyle = reactive({ width: dataWidth + 'px' })
const lockingHeightStyle = reactive({ height: '155px' })

function closeVerificationBox() {
  visible.value = false
  resetAllState()
}

async function initSliderImg() {
  try {
    const res = await getSliderImg(props.mobile)
    const data = res.data
    blockFill.value.style.top = data.block_y + 'px'
    canvasStr.value = 'data:image/png;base64,' + data.canvas_str
    blockStr.value = 'data:image/png;base64,' + data.block_str
  } catch (e) {
  }
}

function refreshImg() {
  initSliderImg()
}

function startMove(e) {
  moveStart = e.pageX || e.targetTouches[0].pageX
  document.addEventListener('mousemove', moving)
  document.addEventListener('touchmove', moving)
  document.addEventListener('mouseup', moveEnd)
  document.addEventListener('touchend', moveEnd)
}

function moving(e) {
  if (!moveStart) return
  const moveX = e.pageX || e.targetTouches[0].pageX
  const d = moveX - moveStart
  if (d < 0 || d > dataWidth - puzzleSize) return
  sliderBtn.value.style.left = d + 'px'
  blockFill.value.style.left = d + 'px'
  sliderBtnMask.value.style.width = d + 'px'
}

async function moveEnd(e) {
  const moveX = e.pageX || e.changedTouches?.[0]?.pageX
  const d = moveX - moveStart
  moveStart = 0
  document.removeEventListener('mousemove', moving)
  document.removeEventListener('mouseup', moveEnd)

  try {
    await getCode({ mobile: props.mobile, block_x: d })
    ElMessage.success('验证成功')
    emit('success')
    closeVerificationBox()
  } catch (e) {
    if(e.response?.data?.code === 410) {
      closeVerificationBox()
    } else {
      setTimeout(() => {
        resetAllState()
        refreshImg()
      }, 800)
      return
    }
  }
}

function resetAllState() {
  canvasStr.value = ''
  blockStr.value = ''
  if (sliderBtn.value){
    sliderBtn.value.style.left = '0px'
  }
  if (sliderBtnMask.value) {
    sliderBtnMask.value.style.width = '0px'
  }
  if (blockFill.value) {
    blockFill.value.style.left = '0px'
    blockFill.value.style.top = '0px'
  }
}
</script>

<style scoped lang="scss">

$captcha-pic-width: 310px;
$captcha-pic-height: 155px;

.captcha-dialog :deep(.el-dialog) {
  border-radius: 16px;
  padding: 0;
}

.captcha-dialog :deep(.el-dialog__body) {
  padding: 15px 20px 25px !important;
}

.captcha-dialog :deep(.el-dialog__header) {
  display: none;
}

/* 容器 */
.puzzle-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-height: 255px;
}

/* 头部 */
.puzzle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: $captcha-pic-width;
  margin-bottom: 10px;
}

.puzzle-header-left {
  color: #333;
  font-size: 14px;
}
.puzzle-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  cursor: pointer;
}

.re-btn,
.close-btn {
  font-size: 16px;
  cursor: pointer;
  color: #666;
  margin-left: 8px;
}

.re-btn:hover {
  color: #67c23a;
}

.close-btn:hover {
  color: #f56c6c;
}

/* 滑块条容器 */
.slider-container{
    position: relative;
    text-align: center;
    width: 100%;
    height: 40px;
    line-height: 40px;
    margin-top: 15px;
    background: #f7f9fa;
    color: #45494c;
    border: 1px solid #e4e7eb;
    .slide-verify-slider-mask{
      position: absolute;
      left: 0;
      top: 0;
      height: 40px;
      border: 0 solid #1991fa;
      background: #d1e9fe;

      .mask-item{
        position: absolute;
        top: 0;
        left: 0px;
        width: 40px;
        height: 40px;
        background: #fff;
        box-shadow: 0 0 3px rgba(0, 0, 0, .3);
        cursor: pointer;
        transition: background .2s linear;

        &:hover{
          background: #1991fa;
          color: #fff;
        }
      }
    }
}


/* 验证提示 */
.ver-tips {
  position: absolute;
  left: 0;
  bottom: -22px;
  background: rgba(255, 255, 255, 0.9);
  height: 22px;
  line-height: 22px;
  font-size: 12px;
  width: 100%;
  margin: 0;
  text-align: left;
  padding: 0 8px;
  transition: all 0.4s;
}

.slider-tips {
  bottom: 0;
}

.ver-tips i {
  display: inline-block;
  width: 22px;
  height: 22px;
  vertical-align: top;
  background-image: url(../../assets/sprite.3.2.0.png);
  background-position: -4px -1229px;
}

/* 拼图块 */
#block-fill {
  position: absolute;
  left: 0;
  width: 45px;
  height: 45px;
}

.puzzle-lost-box {
  position: absolute;
  width: $captcha-pic-width;
  height: $captcha-pic-height;
  left: 0;
  top: 0;
  z-index: 111;
}
</style>
