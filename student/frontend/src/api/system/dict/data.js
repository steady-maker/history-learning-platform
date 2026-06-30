import request from '@/utils/request'

// 根据字典类型查询字典数据信息
export function getDicts(dictType) {
  return request({
    url: '/system/dict_data/type/' + dictType + '/',
    method: 'get',
    headers: {
      isToken: false
    }
  })
}

