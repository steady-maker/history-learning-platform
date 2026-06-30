import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/hte";

// 上传附件
export function upload() {
  return request({
    url: '/att/file/upload/',
    method: 'post',
  })
}