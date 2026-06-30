<template>
  <div class="my-info-page">
    <!-- 左侧导航切换区（和题库页面保持一致布局） -->
    <div class="info-sidebar">
      <div class="sidebar-menu">
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'profile' }"
          @click="switchTab('profile')"
        >
          我的信息
        </div>
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'study' }"
          @click="switchTab('study')"
        >
          学习数据
        </div>
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'feedback' }"
          @click="switchTab('feedback')"
        >
          意见反馈
        </div>
      </div>
    </div>

    <!-- 右侧内容区（和题库页面content结构对齐） -->
    <div class="info-content">
      <!-- 我的信息面板 -->
      <div v-if="activeTab === 'profile'" class="info-panel">
        <!-- 空数据兼容（和题库页面空状态样式一致） -->
        <div v-if="!userInfo" class="empty-page">
          <p>暂无用户信息</p>
        </div>

        <!-- 信息卡片（模仿题库的question-card结构） -->
        <div v-else class="info-card">
          <div class="card-header">
            <div class="avatar-wrapper">
              <img :src="userInfo.avatar || defaultAvatar" alt="头像" class="avatar">
              <span class="username">{{ userInfo.username || '未设置用户名' }}</span>
            </div>
            <button class="edit-btn" @click="showUsernameModal = true">修改用户名</button>
          </div>

          <!-- 卡片主体（账号信息） -->
          <div class="card-body">
            <!-- 性别修改 -->
            <div class="info-item">
              <span class="label">性别：</span>
              <div class="value edit-item">
                <span v-if="!editMode">
                  {{ userInfo.gender === '0' ? "女" : userInfo.gender === '1' ? "男" : '未知' }}
                </span>
                <el-select 
                  v-else 
                  v-model="editForm.gender" 
                  size="small" 
                  placeholder="请选择性别"
                  class="edit-input"
                >
                  <el-option label="男" value="1"></el-option>
                  <el-option label="女" value="0"></el-option>
                </el-select>
              </div>
            </div>

            <!-- 手机号修改 -->
            <div class="info-item">
              <span class="label">手机号码：</span>
              <div class="value edit-item">
                <span v-if="!editMode">{{ userInfo.mobile || '未知' }}</span>
                <el-input 
                  v-else 
                  v-model="editForm.mobile" 
                  size="small" 
                  placeholder="请输入手机号码"
                  class="edit-input"
                  maxlength="11"
                ></el-input>
              </div>
            </div>

            <!-- 邮箱修改 -->
            <div class="info-item">
              <span class="label">邮箱：</span>
              <div class="value edit-item">
                <span v-if="!editMode">{{ userInfo.email || '未知' }}</span>
                <el-input 
                  v-else 
                  v-model="editForm.email" 
                  size="small" 
                  placeholder="请输入邮箱"
                  class="edit-input"
                ></el-input>
              </div>
            </div>
          </div>

          <!-- 卡片底部（修改密码入口） -->
          <div class="card-footer">
            <div class="left-btn">
              <button 
                class="edit-info-btn" 
                v-if="!editMode"
                @click="enterEditMode"
              >
                编辑信息
              </button>
              <button 
                class="save-info-btn" 
                v-if="editMode"
                @click="saveUserInfo"
              >
                保存信息
              </button>
              <button 
                class="cancel-edit-btn" 
                v-if="editMode"
                @click="cancelEditMode"
                style="margin-left: 8px;"
              >
                取消
              </button>
            </div>
            <!-- <button class="pwd-btn" @click="showPasswordModal = true">修改密码</button> -->
            <div class="right-btn-group">
              <button class="pwd-btn" @click="showPasswordModal = true">修改密码</button>
              <button class="logout-btn" @click="logout" style="margin-left: 8px;">退出登录</button>
          </div>
          </div>
        </div>
      </div>

      <!-- 学习数据面板 -->
      <StudyData v-if="activeTab === 'study'" :studyData="studyData"></StudyData>

      <!-- 意见反馈面板 -->
      <div v-if="activeTab === 'feedback'" class="info-panel">
        <div class="info-card">
          <div class="card-header">
            <span class="feedback-title">意见反馈</span>
          </div>

          <div class="card-body">
            <textarea 
              v-model="feedbackForm.content"
              placeholder="请输入您的反馈内容（建议/问题/优化等）..."
              rows="8"
              class="feedback-textarea"
            ></textarea>
          </div>

          <div class="card-footer">
            <button 
              class="submit-btn" 
              :disabled="!feedbackForm.content"
              @click="submitFeedback"
            >
              提交反馈
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改用户名弹窗（样式轻量化，贴合整体风格） -->
    <div v-if="showUsernameModal" class="modal-overlay" @click.self="showUsernameModal = false">
      <div class="modal">
        <div class="modal-header">
          <span>修改用户名</span>
        </div>
        <div class="modal-body">
          <input 
            v-model="editForm.username"
            type="text"
            placeholder="请输入新用户名"
            class="modal-input"
          >
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showUsernameModal = false">取消</button>
          <button class="confirm-btn" @click="saveUserInfo">确定</button>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗（表单式布局） -->
    <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
      <div class="modal" style="width: 400px;"> <!-- 调整弹窗宽度适配表单 -->
        <div class="modal-header">
          修改密码
        </div>
        <!-- 表单容器：label+input 左右对齐布局 -->
        <div class="modal-body">
          <form @submit.prevent="updatePassword"> <!-- 绑定表单提交事件 -->
            <div class="form-item">
              <label class="form-label">原密码：</label>
              <input 
                v-model="passwordForm.oldPwd"
                type="password"
                placeholder="请输入原密码"
                class="form-input"
                required
              >
            </div>
            <div class="form-item">
              <label class="form-label">新密码：</label>
              <input 
                v-model="passwordForm.newPwd"
                type="password"
                placeholder="请输入新密码（6-16位）"
                class="form-input"
                required
                minlength="6"
                maxlength="16"
              >
            </div>
            <div class="form-item">
              <label class="form-label">确认新密码：</label>
              <input 
                v-model="passwordForm.confirmPwd"
                type="password"
                placeholder="请再次输入新密码"
                class="form-input"
                required
              >
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showPasswordModal = false">取消</button>
          <button class="confirm-btn" @click="updatePassword">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import useUserStore from '@/store/modules/user'
import { ElMessageBox } from 'element-plus'
import { 
  getUserInfo, 
  updateUserInfo, 
  updateUserPassword, 
  getStudyData, 
  submitUserFeedback 
} from '@/api/user/user_info'
import StudyData from './module/studyData.vue'

// 1. 响应式数据（和题库页面命名风格一致）
const activeTab = ref('profile') // 当前激活标签：profile/study/feedback
const userInfo = ref(null) // 用户基础信息
const studyData = ref({}) // 学习数据
const feedbackForm = ref({ content: '' }) // 反馈表单
const showUsernameModal = ref(false) // 用户名弹窗状态
const showPasswordModal = ref(false) // 密码弹窗状态
const passwordForm = ref({ oldPwd: '', newPwd: '', confirmPwd: '' }) // 密码表单
const defaultAvatar = 'https://via.placeholder.com/64' // 默认头像
const userStore = useUserStore()

// 新增：编辑模式控制
const editMode = ref(false) // 是否处于编辑状态
// 编辑表单（初始化时同步用户信息）
const editForm = reactive({
  gender: null,
  mobile: null,
  email: null,
  username: null // 兼容原有用户名修改
})

/** 退出登录 */
const logout = () =>{
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logOut().then(() => {
    location.href = '/login'
  })
  }).catch(() => { })
}

// 2. 切换标签逻辑（和题库页面switchTab完全一致）
const switchTab = (tab) => {
  activeTab.value = tab
  // 切换到学习数据时懒加载
  if (tab === 'study' && Object.keys(studyData.value).length === 0) {
    fetchStudyData()
  }
}

// 3. 接口请求方法（和题库页面fetchQuestions风格一致）
/** 获取用户基础信息 */
const fetchUserInfo = async () => {
  try {
    const res = await getUserInfo()
    userInfo.value = res.data
  } catch (error) {
    ElMessage.error('获取用户信息失败')
    console.error(error)
  }
}

/** 获取学习数据 */
const fetchStudyData = async () => {
  try {
    const res = await getStudyData()
    studyData.value = res.data
  } catch (error) {
    console.error(error)
  }
}

/** 提交意见反馈 */
const submitFeedback = async () => {
  if (!feedbackForm.value.content.trim()) {
    ElMessage.warning('请输入反馈内容')
    return
  }
  try {
    await submitUserFeedback({ content: feedbackForm.value.content })
    ElMessage.success('反馈提交成功，我们会尽快处理')
    feedbackForm.value.content = ''
  } catch (error) {
    console.error(error)
  }
}

/** 修改密码 */
const updatePassword = async () => {
  const { oldPwd, newPwd, confirmPwd } = passwordForm.value
  if (!oldPwd || !newPwd || !confirmPwd) {
    ElMessage.warning('请填写完整密码信息')
    return
  }
  if (newPwd !== confirmPwd) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  try {
    await updateUserPassword({ old_password: oldPwd, new_password: newPwd })
    showPasswordModal.value = false
    // ElMessage.success('密码修改成功，请重新登录')
    // 可添加跳转到登录页的逻辑
  }catch{

  }
}

// 新增：进入编辑模式
const enterEditMode = () => {
  if (!userInfo.value) return
  // 同步当前用户信息到编辑表单
  editForm.gender = userInfo.value.gender || ''
  editForm.mobile = userInfo.value.mobile || ''
  editForm.email = userInfo.value.email || ''
  editForm.username = userInfo.value.username || ''
  editMode.value = true
}

// 新增：取消编辑模式
const cancelEditMode = () => {
  editMode.value = false
  // 重置编辑表单
  editForm.gender = userInfo.value.gender || ''
  editForm.mobile = userInfo.value.mobile || ''
  editForm.email = userInfo.value.email || ''
}

// 新增：保存用户信息
const saveUserInfo = async () => {
  // 简单校验
  if (editForm.mobile && !/^1[3-9]\d{9}$/.test(editForm.mobile)) {
    ElMessage.warning('请输入正确的手机号码')
    return
  }
  if (editForm.email && !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(editForm.email)) {
    ElMessage.warning('请输入正确的邮箱格式')
    return
  }

  try {
    // 构造提交参数（只提交有修改的字段）
    const submitData = {
      id: useUserStore().id,
      gender: editForm.gender,
      mobile: editForm.mobile,
      email: editForm.email,
      username: editForm.username // 用户名也一起提交，兼容原有修改
    }
    // 调用修改接口
    await updateUserInfo(submitData)
    // 更新本地用户信息
    userInfo.value.gender = editForm.gender
    userInfo.value.mobile = editForm.mobile
    userInfo.value.email = editForm.email
    userInfo.value.username = editForm.username
    // 退出编辑模式
    editMode.value = false
    showUsernameModal.value = false
    fetchUserInfo() // 刷新用户信息
    ElMessage.success('用户信息修改成功')
  } catch (error) {
    ElMessage.error('信息修改失败：' + (error.msg || '服务器错误'))
    console.error(error)
  }
}

// 4. 页面加载初始化（和题库页面onMounted一致）
onMounted(() => {
  fetchUserInfo()
})
</script>

<style lang="scss" scoped>
// 复用题库页面的全局色调变量，保证风格统一
$primary-color: #165DFF;
$light-gray: #f5f7fa;
$border-color: #e5e6eb;
$text-gray: #666;
$red: #F53F3F;
$green: #00B42A;

// 新增编辑样式，贴合原有风格
.edit-item {
  display: flex;
  align-items: center;

  .edit-input {
    width: 200px;
    --el-input-height: 32px;
  }
}

// 编辑/保存按钮样式
.edit-info-btn, .save-info-btn, .cancel-edit-btn {
  border: none;
  background: transparent;
  color: $primary-color;
  cursor: pointer;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 4px;

  &:hover {
    background-color: lighten($primary-color, 40%);
  }
}

.save-info-btn {
  background-color: $primary-color;
  color: #fff;

  &:hover {
    opacity: 0.9;
  }
}

.cancel-edit-btn {
  color: $text-gray;

  &:hover {
    background-color: $light-gray;
  }
}

.left-btn {
  display: flex;
  align-items: center;
}

// 整体布局（和题库页面.my-question-bank完全对齐）
.my-info-page {
  display: flex;
  height: 100vh;
  background-color: $light-gray;
}

// 左侧导航（和题库页面.bank-sidebar结构/样式一致）
.info-sidebar {
  width: 200px;
  background-color: #fff;
  border-right: 1px solid $border-color;
  padding: 20px 0;

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

// 右侧内容区（和题库页面.bank-content样式对齐）
.info-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;

  .info-panel {
    width: 100%;
  }

  // 信息卡片（模仿题库的question-card）
  .info-card {
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
      padding-bottom: 8px;
      border-bottom: 1px solid $border-color;

      .avatar-wrapper {
        display: flex;
        align-items: center;
        gap: 12px;

        .avatar {
          width: 64px;
          height: 64px;
          border-radius: 50%;
          object-fit: cover;
          border: 1px solid $border-color;
        }

        .username {
          font-size: 18px;
          font-weight: 500;
          color: #333;
        }
      }

      .study-desc, .feedback-title {
        font-size: 16px;
        color: #333;
        font-weight: 500;
      }

      .edit-btn {
        border: none;
        background: transparent;
        color: $primary-color;
        cursor: pointer;
        font-size: 14px;

        &:hover {
          text-decoration: underline;
        }
      }
    }

    .card-body {
      .info-item {
        display: flex;
        margin-bottom: 12px;
        font-size: 15px;

        .label {
          width: 100px;
          color: $text-gray;
        }

        .value {
          color: #333;
        }
      }

      .study-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;

        .study-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 12px;
          background-color: $light-gray;
          border-radius: 4px;

          .label {
            color: $text-gray;
            font-size: 14px;
          }

          .value {
            color: #333;
            font-weight: 500;
            font-size: 14px;
          }
        }
      }

      .feedback-textarea {
        width: 100%;
        padding: 12px;
        border: 1px solid $border-color;
        border-radius: 8px;
        resize: none;
        font-family: inherit;
        font-size: 14px;
        color: #333;
        background-color: #fff;

        &::placeholder {
          color: #999;
        }
      }
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 12px;
      padding-top: 8px;
      border-top: 1px solid $border-color;

      .submit-btn {
        background-color: $primary-color;
        color: #fff;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        cursor: pointer;
        font-size: 14px;

        &:disabled {
          background-color: lighten($primary-color, 30%);
          cursor: not-allowed;
        }

        &:hover:not(:disabled) {
          opacity: 0.9;
        }
      }

      .update-time {
        font-size: 12px;
        color: $text-gray;
      }

      .card-footer .right-btn-group {
        display: flex;
        align-items: center;
      }
      .logout-btn {
        padding: 4px 12px;
        border: 1px solid #f56c6c;
        background-color: #fff;
        color: #f56c6c;
        border-radius: 4px;
        cursor: pointer;
      }
      .logout-btn:hover {
        background-color: #fef0f0;
      }
      /* 保持和修改密码按钮样式一致 */
      .pwd-btn {
        padding: 4px 12px;
        border: 1px solid #409eff;
        background-color: #fff;
        color: #409eff;
        border-radius: 4px;
        cursor: pointer;
        margin-right: 8px;
      }
      .pwd-btn:hover {
        background-color: #ecf5ff;
      }
    }
  }

  // 空页面样式（和题库页面完全复用）
  .empty-page {
    text-align: center;
    padding: 60px 0;
    color: #999;
    font-size: 18px;
  }
}

// 弹窗样式（轻量化，贴合整体风格）
/* 表单项布局：label左对齐，input占满剩余宽度 */
.form-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}
/* 标签样式：固定宽度，右对齐，统一间距 */
.form-label {
  width: 90px;
  text-align: left;
  // margin-right: 12px;
  font-size: 14px;
  color: #333;
}
/* 输入框样式：适配表单布局，去掉默认样式 */
.form-input {
  flex: 1;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}
.form-input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}
/* 弹窗基础样式（如果已有可忽略） */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: #fff;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.modal-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}
.modal-footer {
  display: flex;
  justify-content: center; 
  margin-top: 20px;
  gap: 12px;
}
.cancel-btn {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
}
.confirm-btn {
  padding: 8px 16px;
  border: none;
  background: #409eff;
  color: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.confirm-btn:hover {
  background: #66b1ff;
}
.cancel-btn:hover {
  background: #f5f7fa;
}
</style>