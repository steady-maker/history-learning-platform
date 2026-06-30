import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/hte";

// 查询提示词列表
export function listPrompt(query) {
  return request({
    url: '/biz/prompt/',
    method: 'get',
    params: query
  })
}

// 查询提示词详细
export function getPrompt(prompt_id) {
  return request({
    url: '/biz/prompt/' + parseStrEmpty(prompt_id) + '/',
    method: 'get'
  })
}

// 新增提示词
export function addPrompt(data) {
  return request({
    url: '/biz/prompt/',
    method: 'post',
    data: data
  })
}

// 修改提示词
export function updatePrompt(data) {
  return request({
    url: '/biz/prompt/' + parseStrEmpty(data.id) + '/',
    method: 'put',
    data: data
  })
}

// 删除提示词
export function delPrompt(prompt_id,data) {
  return request({
    url: '/biz/prompt/' + parseStrEmpty(prompt_id) + '/',
    method: 'delete',
    data:data
  })
}

// 提示词状态修改
export function changePromptStatus(prompt_id, status) {
  return request({
    url: '/biz/prompt/' + parseStrEmpty(prompt_id) + '/',
    method: 'patch',
    data: { status: status ,prompt_id: prompt_id}
  })
}
