import request from '@/utils/request'

// 登录方法
export function login(data) {
  return request({
    url: '/login/',
    headers: {
      isToken: false,
      repeatSubmit: false
    },
    method: 'post',
    data: data
  })
}


// 注册
export function register(data) {
  return request({
    url: '/register/',
    headers: {
      isToken: false
    },
    method: 'post',
    data: data
  })
}


// 获取用户详细信息
export function getInfo() {
  return request({
    url: '/system/user/user_info/',
    method: 'get'
  })
}

// 退出方法
export function logout() {
  return request({
    url: '/logout',
    method: 'post'
  })
}

// 获取验证码
export function getCode(data) {
  return request({
    url: 'code/',
    headers: {
      isToken: false
    },
    method: 'post',
    timeout: 20000,
    data: data
  })
}

export function getSliderImg(mobile) {
  return request({
    url: 'captcha/',
    headers: {
      isToken: false
    },
    method: 'get',
    timeout: 20000,
    params: {
      mobile: mobile
    }
  })
}

// 获取验证码
export function getCodeImg() {
  return request({
    url: 'captcha/',
    headers: {
      isToken: false
    },
    method: 'get',
    timeout: 20000
  })
}
