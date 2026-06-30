import request from '@/utils/request'

// 查询题目列表
export function listQuestion(query) {
  return request({
    url: '/question/question_bank/',
    method: 'get',
    params: query
  })
}

// 查询每日一题
export function dailyQuestion(query) {
  return request({
    url: '/question/question_bank/daily_question',
    method: 'get',
    params: query
  })
}

// 查询用户做过题目列表
export function listUserQuestion(query) {
  return request({
    url: '/question/question_bank/user_question_list/',
    method: 'get',
    params: query
  })
}

// 用户本题历史记录列表
export function listUserDone(query) {
  return request({
    url: '/question/question_bank/question_done_list/',
    method: 'get',
    params: query
  })
}

// 用户收藏题目
export function collectQuestion(questionId){
  return request({
    url: '/question/question_bank/user_question_collection/',
    method:'post',
    data: questionId
  })
}

// 用户取消收藏题目
export function cancelCollectQuestion(questionId){
  return request({
    url: '/question/question_bank/user_question_cancel_collection/',
    method:'post',
    data: questionId
  })
}


// 查询题目详细
export function getQuestion(questionId) {
  return request({
    url: `/question/question_bank/${questionId}/`,
    method: 'get'
  })
}

// 查询题目-提示词所需要的题目列表
export function getPromptQuestion(query) {
  return request({
    url: '/question/question_bank/get_prompt_question/' ,
    method: 'get',
    params: query
  })
}

// 提交题目答案
export function handleSubmitChoiceAnswer(data) {
  return request({
    url: '/question/question_bank/handle_submit_choice_answer/',
    method: 'post',
    data: data
  })
}

// 提交主观题目答案
export function handleSubjectiveAnswer(data) {
  return request({
    url: '/question/question_bank/handle_subjective_answer/',
    method: 'post',
    data: data,
    timeout: 100 * 1000 
  })
}

