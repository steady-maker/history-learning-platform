import request from '@/utils/request'

// 查询任务列表
export function listTask(query) {
  return request({
    url: '/tasks/',
    method: 'get',
    params: query
  })
}

// 查询任务详细
export function getTask(taskId) {
  return request({
    url: '/tasks/' + taskId + '/',
    method: 'get'
  })
}

// 新增任务
export function addTask(data) {
  return request({
    url: '/tasks/',
    method: 'post',
    data: data
  })
}

// 删除任务
export function deleteTask(id) {
  return request({
    url: '/tasks/' + id + '/',
    method: 'delete',
  })
}

// 暂停任务
export function pauseTask(id) {
  return request({
    url: '/tasks/' + id + '/pause/',
    method: 'get',
  })
}

// 恢复任务
export function resumeTask(id) {
  return request({
    url: '/tasks/' + id + '/resume/',
    method: 'get',
  })
}