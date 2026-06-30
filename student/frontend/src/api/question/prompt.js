import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/hte";
import service from '@/utils/request' // 项目封装的axios
import { getToken } from '@/utils/auth'

// 查询提示词列表
export function listPrompt(query) {
  return request({
    url: '/question/prompt/',
    method: 'get',
    params: query
  })
}

// 查询提示词详细
export function getPrompt(prompt_id) {
  return request({
    url: '/question/prompt/' + parseStrEmpty(prompt_id) + '/',
    method: 'get'
  })
}

// 与Ai对话，获取提示
export function getQuestionPrompt(data) {
  return request({
    url: '/question/prompt/get_question_prompt/',
    method: 'post',
    data: data
  })
}

// 获取题目提示流式输出结果
export function getQuestionPromptStream(data) {
  const token = getToken();
  return fetch('/api/question/prompt/get_question_prompt_stream/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data),
    credentials: 'include' // 确保携带cookie（兼容CSRF）
  });
}

export function getChoiceQuestionReviewPromptStream(data) {
  const token = getToken();
  return fetch('/api/question/prompt/get_choice_question_review_prompt_stream/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data),
    credentials: 'include' // 确保携带cookie（兼容CSRF）
  });
}

export function getSubjectiveQuestionReviewPromptStream(data) {
  const token = getToken();
  return fetch('/api/question/prompt/get_subjective_question_review_prompt_stream/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data),
    credentials: 'include' // 确保携带cookie（兼容CSRF）
  });
}


export function getQuestionReviewPromptStream(data) {
  const token = getToken();
  return fetch('/api/question/prompt/get_question_review_prompt_stream/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data),
    credentials: 'include' // 确保携带cookie（兼容CSRF）
  });
}


// 辅助函数：获取CSRF Token
function getCsrfToken() {
  return document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
}