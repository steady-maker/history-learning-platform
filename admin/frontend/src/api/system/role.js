import request from '@/utils/request'

// 查询角色列表
export function listRole(query) {
  return request({
    url: '/system/role/',
    method: 'get',
    params: query
  })
}

// 查询角色详细
export function getRole(roleId) {
  return request({
    url: '/system/role/' + roleId + '/',
    method: 'get'
  })
}

// 新增角色
export function addRole(data) {
  return request({
    url: '/system/role/',
    method: 'post',
    data: data
  })
}

// 修改角色
export function updateRole(data) {
  return request({
    url: '/system/role/' + data.id + '/',
    method: 'put',
    data: data
  })
}

// 角色状态修改
export function changeRoleStatus(roleId, status) {
  return request({
    url: '/system/role/' + roleId + '/',
    method: 'patch',
    data: { status: status }
  })
}

// 删除角色
export function delRole(roleId) {
  return request({
    url: '/system/role/' + roleId + '/',
    method: 'delete'
  })
}

// 查询角色已授权用户列表
export function allocatedUserList(query) {
  return request({
    url: '/system/role/' + query.role_id + '/users/',
    method: 'get',
    params: query
  })
}

// 查询角色未授权用户列表
export function unallocatedUserList(query) {
  return request({
    url: '/system/role/' + query.role_id + '/unallocated_users/',
    method: 'get',
    params: query
  })
}

// 取消用户授权角色
export function authUserCancel(role_id, data) {
  return request({
    url: '/system/role/' + role_id + '/deallocate/',
    method: 'put',
    data: data
  })
}

// 授权用户选择
export function authUserSelectAll(role_id, data) {
  return request({
    url: '/system/role/' + role_id + '/allocate/',
    method: 'put',
    data: data
  })
}