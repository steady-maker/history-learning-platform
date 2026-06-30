import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/hte";

// 查询用户列表
export function listUser(query) {
  return request({
    url: '/system/user/',
    method: 'get',
    params: query
  })
}

// 查询用户详细
export function getUser(userId) {
  return request({
    url: '/system/user/' + parseStrEmpty(userId) + '/',
    method: 'get'
  })
}

// 新增用户
export function addUser(data) {
  return request({
    url: '/system/user/',
    method: 'post',
    data: data
  })
}

// 修改用户
export function updateUser(data) {
  return request({
    url: '/system/user/' + parseStrEmpty(data.id) + '/',
    method: 'put',
    data: data
  })
}

// 删除用户
export function delUser(userId) {
  return request({
    url: '/system/user/' + parseStrEmpty(userId) + '/',
    method: 'delete'
  })
}

// 用户密码重置
export function resetUserPwd(data) {
  return request({
    url: '/system/user/reset_pwd/',
    method: 'put',
    data: data
  })
}

// 用户状态修改
export function changeUserStatus(userId, status) {
  return request({
    url: '/system/user/' + parseStrEmpty(userId) + '/',
    method: 'patch',
    data: { status: status }
  })
}


// 修改用户个人信息
export function updateUserProfile(data) {
  return request({
    url: '/system/user/update_user_info/',
    method: 'put',
    data: data
  })
}

// 用户密码重置
export function updateUserPwd(oldPassword, newPassword) {
  const data = {
    oldPassword,
    newPassword
  }
  return request({
    url: '/system/user/change_password/',
    method: 'put',
    data: data
  })
}

// 用户头像上传
export function uploadAvatar(data) {
  return request({
    url: '/system/user/profile/avatar',
    method: 'post',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    data: data
  })
}

// 查询部门下拉树结构
export function deptTreeSelect() {
  return request({
    url: '/system/dept/dept_tree/',
    method: 'get'
  })
}
