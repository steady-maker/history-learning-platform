import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/hte";
import service from '@/utils/request' // 项目封装的axios
import { getToken } from '@/utils/auth'

// 查询用户信息
export function getUserInfo() {
  return request({
    url: '/user/web_user/get_user_info/',
    method: 'get',
  })
}

// 查询用户打卡天数
export function getUserCheckInDays() {
  return request({
    url: '/user/web_user/get_user_check_in_count/',
    method: 'get',
  })
}

// 用户每日打卡
export function userCheckIn() {
  return request({
    url: '/user/web_user/user_daily_check_in/',
    method: 'post',
  })
}

// 修改用户信息
export function updateUserInfo(data) {
  return request({
    url: '/user/web_user/update_user_info/' ,
    method: 'put',
    data:data
  })
}

// 修改用户密码
export function updateUserPassword(data) {
  return request({
    url: '/user/web_user/change_password/',
    method: 'put',
    data:data
  })
}

// 获取学习数据
export function getStudyData() {
  return request({
    url: '/user/web_user/get_user_study_data/' ,
    method: 'get',
  })
}

// 提交用户反馈
export function submitUserFeedback(data) {
  return request({
    url: '/user/web_user/user_feedback/' ,
    method: 'post',
    data:data
  })
}