<template>
  <div class="auth-container" :style="{ backgroundImage: `url(${bgImage})` }">

    <div class="right-section">
      <div class="form-container">
        <div class="header">
          <h1>欢迎您登录</h1>
          <p class="subtitle">历史学习管理平台</p>
        </div>

        <el-form ref="loginRef" :model="loginForm" :rules="loginRules">
          <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            type="text"
            prefix-icon="user"
            placeholder="请输入账号"
          />
          </el-form-item>
          <el-form-item prop="password">
            <div class="code-input-group">
            <el-input
              v-model="loginForm.password"
              type="password"
              prefix-icon="key"
              placeholder="请输入密码"
              @keyup.enter="handleLogin"
            />
            </div>
          </el-form-item>
          <el-form-item prop="code" v-if="captchaEnabled">
            <div class="code-input-group">
            <el-input
              v-model="loginForm.code"
              placeholder="请输入验证码"
              prefix-icon="postcard"
              style="width: 63%"
              @keyup.enter="handleLogin"
            />
            <div class="login-code">
              <img :src="codeUrl" @click="getCode" class="login-code-img"/>
            </div>
            </div>
          </el-form-item>
          <el-form-item>
              <el-checkbox v-model="loginForm.rememberMe" style="color: darkgray;">记住密码</el-checkbox>
          </el-form-item>
          <el-form-item>
            <el-button
              @click="handleLogin"
              type="primary"
              size="small"
              class="submit-btn"
              :loading="loading"
            >
            <span v-if="!loading">登 录</span>
            <span v-else>登 录 中...</span>
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getCodeImg } from "@/api/login"
import Cookies from "js-cookie"
import { encrypt, decrypt } from "@/utils/jsencrypt"
import useUserStore from '@/store/modules/user'
import bgImage from '@/assets/images/background.png'
import { requiredAndTrim } from "@/utils/validators"

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const { proxy } = getCurrentInstance()

const loginForm = ref({
  username: "",
  password: "",
  rememberMe: false,
  code: "",
  key: ""
})

const loginRules = {
  username: requiredAndTrim('请输入您的账号'),
  password: requiredAndTrim('请输入您的密码'),
  code: requiredAndTrim('请输入验证码')
}

const codeUrl = ref("")
const loading = ref(false)
// 验证码开关
const captchaEnabled = ref(true)
// 注册开关
const register = ref(false)
const redirect = ref(undefined)

watch(route, (newRoute) => {
    redirect.value = newRoute.query && newRoute.query.redirect
}, { immediate: true })

function handleLogin() {
  proxy.$refs.loginRef.validate(valid => {
    if (valid) {
      loading.value = true
      // 勾选了需要记住密码设置在 cookie 中设置记住用户名和密码
      if (loginForm.value.rememberMe) {
        Cookies.set("username", loginForm.value.username, { expires: 30 })
        Cookies.set("password", encrypt(loginForm.value.password), { expires: 30 })
        Cookies.set("rememberMe", loginForm.value.rememberMe, { expires: 30 })
      } else {
        // 否则移除
        Cookies.remove("username")
        Cookies.remove("password")
        Cookies.remove("rememberMe")
      }
      // 调用action的登录方法
      userStore.login(loginForm.value).then(() => {
        const query = route.query
        const otherQueryParams = Object.keys(query).reduce((acc, cur) => {
          if (cur !== "redirect") {
            acc[cur] = query[cur]
          }
          return acc
        }, {})
        router.push({ path: redirect.value || "/", query: otherQueryParams })
      }).catch(() => {
        loading.value = false
        // 重新获取验证码
        if (captchaEnabled.value) {
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
    loginForm.value.code = ""
    if (captchaEnabled.value) {
      codeUrl.value = "data:image/gif;base64," + data.image_base
      loginForm.value.key = data.key
    }
  })
}

function getCookie() {
  const username = Cookies.get("username")
  const password = Cookies.get("password")
  const rememberMe = Cookies.get("rememberMe")
  loginForm.value = {
    username: username === undefined ? loginForm.value.username : username,
    password: password === undefined ? loginForm.value.password : decrypt(password),
    rememberMe: rememberMe === undefined ? false : Boolean(rememberMe)
  }
}

getCode()
getCookie()
</script>

<style scoped>
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

/* Logo 区域 */
.logo-wrapper {
  position: absolute;
  top: 30px;
  left: 30px;
  z-index: 20;

}

.logo-img {
  max-width: 200px;
  height: auto;
  display: block;
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
:deep(.el-form .toggle-link) {
  text-align: left !important;
  width: 100%;
  display: block;
  margin-top: 10px;
}
.toggle-link {
  color: #999;
  font-size: 14px;
  margin-top: 10px;
  margin-bottom: 10px;
}

.toggle-link a {
  color: #0052cc;
  text-decoration: none;
  cursor: pointer;
}

.toggle-link a:hover {
  color: #0043a8;
  text-decoration: underline;
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
  color: #000; /* 黑色 */
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

/* 单独设置验证码按钮的基础样式 */
:deep(.code-btn) {
  width: 130px; 
  height: 40px; 
  font-size: 14px; 
  padding: 0 12px;
  border-radius: 6px; 
}

.submit-btn {
  width: 100%;
  height: 40px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 0.5px;
  margin-top: 16px;
}

:deep(.el-checkbox__label) {
  font-size: 12px;
  color: #666;
}

:deep(.el-checkbox__label a) {
  color: #0052cc;
  text-decoration: none;
  margin: 0 4px;
}

:deep(.el-checkbox__input.is-checked+.el-checkbox__label) {
    color: inherit;
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
.login-code-img {
  height: 40px;
  padding-left: 12px;
}
</style>