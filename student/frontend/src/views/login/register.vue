<template>
  <div class="auth-container" :style="{ backgroundImage: `url(${bgImage})` }">
      <div class="right-section">
        <div class="form-container">
            <div class="header">
              <h1>欢迎您注册</h1>
              <p class="subtitle">历史学习平台</p>
            </div>
            <el-form ref="registerRef" :model="registerForm" :rules="registerRules" class="register-form">
              <el-form-item prop="username">
                <el-input 
                  v-model="registerForm.username" 
                  type="text" 
                  size="large" 
                  auto-complete="off" 
                  placeholder="账号"
                >
                  <template #prefix><svg-icon icon-class="user" class="el-input__icon input-icon" /></template>
                </el-input>
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  size="large" 
                  auto-complete="off"
                  placeholder="密码"
                  @keyup.enter="handleRegister"
                >
                  <template #prefix><svg-icon icon-class="password" class="el-input__icon input-icon" /></template>
                </el-input>
              </el-form-item>
              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  size="large" 
                  auto-complete="off"
                  placeholder="确认密码"
                  @keyup.enter="handleRegister"
                >
                  <template #prefix><svg-icon icon-class="password" class="el-input__icon input-icon" /></template>
                </el-input>
              </el-form-item>
              <el-form-item prop="code" v-if="captchaEnabled">
                <div class="code-input-group">
                  <el-input
                    size="large" 
                    v-model="registerForm.code"
                    auto-complete="off"
                    placeholder="请输入验证码"
                    style="width: 63%"
                    @keyup.enter="handleRegister"
                  >
                    <template #prefix><svg-icon icon-class="validCode" class="el-input__icon input-icon" /></template>
                  </el-input>
                  <div class="register-code">
                    <img :src="codeUrl" @click="getCode" class="register-code-img"/>
                  </div>
                </div>
              </el-form-item>
              <el-form-item style="width:100%;">
                <el-button
                  :loading="loading"
                  size="large" 
                  type="primary"
                  class="submit-btn"
                  @click.prevent="handleRegister"
                >
                  <span v-if="!loading">注 册</span>
                  <span v-else>注 册 中...</span>
                </el-button>
                <div style="float: right;">
                  <router-link class="link-type" :to="'/login'">使用已有账户登录</router-link>
                </div>
              </el-form-item>
            </el-form>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessageBox } from "element-plus"
import { getCodeImg, login,register } from "@/api/login"
import { requiredAndTrim } from "@/utils/validators"
const bgImage = ref(new URL('@/assets/images/login/background.png', import.meta.url).href)
const title = import.meta.env.VITE_APP_TITLE
const router = useRouter()
const { proxy } = getCurrentInstance()

const registerForm = ref({
  username: "",
  password: "",
  confirmPassword: "",
  code: "",
  key: ""
})

const equalToPassword = (rule, value, callback) => {
  if (registerForm.value.password !== value) {
    callback(new Error("两次输入的密码不一致"))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, trigger: "blur", message: "请输入您的账号" },
    { min: 2, max: 20, message: "用户账号长度必须介于 2 和 20 之间", trigger: "blur" }
  ],
  password: [
    { required: true, trigger: "blur", message: "请输入您的密码" },
    { min: 5, max: 20, message: "用户密码长度必须介于 5 和 20 之间", trigger: "blur" },
    { pattern: /^[^<>"'|\\]+$/, message: "不能包含非法字符：< > \" ' \\\ |", trigger: "blur" }
  ],
  confirmPassword: [
    { required: true, trigger: "blur", message: "请再次输入您的密码" },
    { required: true, validator: equalToPassword, trigger: "blur" }
  ],
  code: requiredAndTrim('请输入验证码')
}

const codeUrl = ref("")
const loading = ref(false)
const captchaEnabled = ref(true)

function handleRegister() {
  proxy.$refs.registerRef.validate(valid => {
    if (valid) {
      loading.value = true
      register(registerForm.value).then(res => {
        const username = registerForm.value.username
        ElMessageBox.alert("<font color='red'>恭喜你，您的账号 " + username + " 注册成功！</font>", "系统提示", {
          dangerouslyUseHTMLString: true,
          type: "success",
        }).then(() => {
          router.push("/login")
        }).catch(() => {})
      }).catch(() => {
        loading.value = false
        if (captchaEnabled) {
          getCode()
        }
      })
    }
  })
}

function getCode() {
  getCodeImg().then(res => {
    captchaEnabled.value = res.captchaEnabled === undefined ? true : res.captchaEnabled
    const data = res.data
    if (captchaEnabled.value) {
      codeUrl.value = "data:image/gif;base64," + data.image_base
      // registerForm.value.uuid = res.uuid
      registerForm.value.key = data.key
    }
  })
}

getCode()
</script>

<style lang='scss' scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.auth-container {
  display: block;
  height: 100vh;
  width: 100vw;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  position: relative;
  overflow: hidden;
}

/* 右侧表单区域 */
.right-section {
  position: absolute;
  right: 13%;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: auto;
  height: auto;
  min-width: 420px;
}

.form-container {
  width: 100%;
  max-width: 400px;
  text-align: left;
}

.header {
  margin-bottom: 40px;
  cursor: default;
}

.header h1 {
  font-size: 30px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 10px;
  letter-spacing: 2px;
}

.header .subtitle {
  color: #1a71e7;
  font-size: 28px;
  font-weight: bold;
}

/* 表单样式 */
:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e4e7;
  border-radius: 6px;
  padding: 12px 16px;
  height: 40px;
}

:deep(.el-input__inner) {
  color: #000;
}

:deep(.el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 2px rgba(0, 82, 204, 0.2), 0 2px 12px rgba(0, 0, 0, 0.08);
  border-color: #0052cc;
}

/* 验证码输入组 */
.code-input-group {
  display: flex;
  gap: 10px;
  width: 100%;
}

.code-input-group :deep(.el-input) {
  flex: 1;
}

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s;
}

:deep(.el-button--primary) {
  background-color: #0052cc;
  border-color: #0052cc;
}

:deep(.el-button--primary:hover) {
  background-color: #0043a8;
  border-color: #0043a8;
}

.submit-btn {
  width: 100%;
  height: 40px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 0.5px;
  margin-top: 16px;
}

.register-code {
  width: 33%;
  height: 40px;
  float: right;
  img {
    cursor: pointer;
    vertical-align: middle;
  }
}

.register-code-img {
  height: 40px;
  padding-left: 12px;
}

/* 注册页面特有样式 */
.input-icon {
  height: 39px;
  width: 14px;
  margin-left: 0px;
}

.link-type {
  color: #0052cc;
  text-decoration: none;
  font-size: 12px;
}

.link-type:hover {
  color: #0043a8;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .right-section {
    width: 60%;
  }
}

@media (max-width: 768px) {
  .auth-container {
    flex-direction: column;
  }

  .right-section {
    width: 100%;
    margin-left: 0;
  }

  .form-container {
    max-width: 100%;
  }

  .header h1 {
    font-size: 24px;
  }

  .code-input-group {
    flex-direction: column;
  }

  .code-input-group :deep(.el-button) {
    width: 100%;
  }
}
</style>
