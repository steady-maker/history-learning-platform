import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/hte";

// 查询后台首页统计信息
export function getIndexInfo() {
  return request({
    url: '/common/index/',
    method: 'get',
  })
}