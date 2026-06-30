// src/utils/validators.js

/**
 * 非空（去除首尾空格）校验
 * @param {string} message 错误提示
 */
export function requiredTrim(message = '该字段不能为空') {
  return {
    validator: (_, value, callback) => {

      // null、undefined 判空
      if (value === null || value === undefined) {
        return callback(new Error(message))
      }

      // 字符串类型才去 trim
      if (typeof value === 'string' && !value.trim()) {
        return callback(new Error(message))
      }

      callback()
    },
    trigger: 'blur'
  }
}

/**
 * 组合校验：
 * 1. Element Plus 的 required
 * 2. 去空格校验
 *
 * 使用时只需要写 required(message)
 */
export function requiredAndTrim(message = '该字段不能为空') {
  return [
    { required: true, message, trigger: 'blur' },
    requiredTrim(message)
  ]
}

export default {
  requiredAndTrim,
  requiredTrim
}
