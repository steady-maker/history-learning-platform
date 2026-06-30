import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/hte";

// 查询题目列表
export function listQuestion(query) {
  return request({
    url: '/biz/question_bank/',
    method: 'get',
    params: query
  })
}

// 查询题目详细
export function getQuestion(questionId) {
  return request({
    url: '/biz/question_bank/' + parseStrEmpty(questionId) + '/',
    method: 'get'
  })
}

// 查询题目-提示词所需要的题目列表
export function getPromptQuestion(query) {
  return request({
    url: '/biz/question_bank/get_prompt_question/' ,
    method: 'get',
    params: query
  })
}

// 新增题目
export function addQuestion(data) {
  return request({
    url: '/biz/question_bank/',
    method: 'post',
    data: data
  })
}

// 修改题目
export function updateQuestion(data) {
  return request({
    url: '/biz/question_bank/' + parseStrEmpty(data.id) + '/',
    method: 'put',
    data: data
  })
}

// 删除题目
export function delQuestion(questionId) {
  return request({
    url: '/biz/question_bank/' + parseStrEmpty(questionId) + '/',
    method: 'delete'
  })
}

// 题目状态修改
export function changeQuestionStatus(questionId, status) {
  return request({
    url: '/biz/question_bank/' + parseStrEmpty(questionId) + '/',
    method: 'patch',
    data: { status: status }
  })
}

