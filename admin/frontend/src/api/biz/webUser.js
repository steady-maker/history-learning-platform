import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/hte";

// 查询用户列表
export function listUser(query) {
  return request({
    url: '/biz/web_user/',
    method: 'get',
    params: query
  })
}

// 查询用户详细
export function getUser(userId) {
  return request({
    url: '/biz/web_user/' + parseStrEmpty(userId) + '/',
    method: 'get'
  })
}

// 新增用户
export function addUser(data) {
  return request({
    url: '/biz/web_user/',
    method: 'post',
    data: data
  })
}

// 修改用户
export function updateUser(data) {
  return request({
    url: '/biz/web_user/' + parseStrEmpty(data.id) + '/',
    method: 'put',
    data: data
  })
}

// 删除用户
export function delUser(userId) {
  return request({
    url: '/biz/web_user/' + parseStrEmpty(userId) + '/',
    method: 'delete'
  })
}

// 用户验证码重置
export function resetUserCode(data) {
  return request({
    url: '/biz/web_user/reset_verification_code_count/',
    method: 'put',
    data: data
  })
}

// 用户状态修改
export function changeUserStatus(userId, status) {
  return request({
    url: '/biz/web_user/' + parseStrEmpty(userId) + '/',
    method: 'patch',
    data: { status: status }
  })
}


// 修改用户个人信息
export function updateUserProfile(data) {
  return request({
    url: '/biz/web_user/update_user_info/',
    method: 'put',
    data: data
  })
}

// 用户头像上传
export function uploadAvatar(data) {
  return request({
    url: '/biz/web_user/profile/avatar',
    method: 'post',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    data: data
  })
}
// ============================= 用户反馈管理接口 ==============

// 查询用户反馈列表
export function listUserFeedback(query) {
  return request({
    url: '/biz/user_feedback/',
    method: 'get',
    params: query
  })
}

// 修改用户反馈状态
export function updateUserFeedback(data) {
  return request({
    url: '/biz/user_feedback/' + parseStrEmpty(data.id) + '/',
    method: 'put',
    data: data
  })
}

// 删除用户
export function delUserFeedback(feedbackId) {
  return request({
    url: '/biz/user_feedback/' + parseStrEmpty(feedbackId) + '/',
    method: 'delete'
  })
}