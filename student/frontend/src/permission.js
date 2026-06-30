import router from './router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { getToken } from '@/utils/auth'
import { ElMessage } from 'element-plus'
import { isRelogin } from '@/utils/request'
import useUserStore from '@/store/modules/user'
import useSettingsStore from '@/store/modules/settings'
NProgress.configure({ showSpinner: false })

// 需要登录才能访问的页面列表
const authRequiredPages = ['/recommender', '/order']
router.beforeEach((to, from, next) => {
  NProgress.start()
  const userStore = useUserStore()
  const token = getToken()
  const requiresAuth = authRequiredPages.some(path => to.path.startsWith(path))
  to.meta.title && useSettingsStore().setTitle(to.meta.title)
  if (token) {
    // 已登录
    if (to.path === '/login') {
      NProgress.done()
      return next({ path: '/' }) // 登录页直接跳首页
    }

    if (!userStore.username) {
      // 如果用户信息没拉取过，先请求
        isRelogin.show = true
        // 判断当前用户是否已拉取完user_info信息
        useUserStore().getInfo().then(() => {
          isRelogin.show = false
          next({ ...to, replace: true })
        }).catch(err => {
          useUserStore().logOut().then(() => {
            next({ path: '/' })
          })
        })
    } else {
      return next()
    }

  } else {
    // 未登录
    if (requiresAuth) {
      ElMessage({
        message: '该功能仅对登录用户开放，请先登录再继续操作。',
        type: 'warning',
        duration: 3000,
      })
      // 受保护页面，跳登录页
      // return next(`/login?redirect=${to.fullPath}`)
      return next({
        path: `/login`,
        query: {
          redirect: to.path,
          ...to.query,
        }
      })
    } else {
      return next()
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})