import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/hte";

// 查询标签列表
export function listTag(query) {
  return request({
    url: '/biz/tag/',
    method: 'get',
    params: query
  })
}

// 查询标签详细
export function getTag(tagId) {
  return request({
    url: '/biz/tag/' + parseStrEmpty(tagId) + '/',
    method: 'get'
  })
}

// 查询标签树
export function getTagTree() {
  return request({
    url: '/biz/tag/get_tag_tree/',
    method: 'get'
  })
}

// 新增标签
export function addTag(data) {
  return request({
    url: '/biz/tag/',
    method: 'post',
    data: data
  })
}

// 修改标签
export function updateTag(data) {
  return request({
    url: '/biz/tag/' + parseStrEmpty(data.id) + '/',
    method: 'put',
    data: data
  })
}

// 删除标签
export function delTag(tagId) {
  return request({
    url: '/biz/tag/' + parseStrEmpty(tagId) + '/',
    method: 'delete'
  })
}

// 标签状态修改
export function changeTagStatus(tagId, status) {
  return request({
    url: '/biz/tag/' + parseStrEmpty(tagId) + '/',
    method: 'patch',
    data: { status: status }
  })
}
