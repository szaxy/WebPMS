/**
 * 日期工具函数
 */

import { format } from 'date-fns'

/**
 * 格式化日期为本地格式
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {string} 格式化后的日期字符串，如果输入为空则返回'-'
 */
export const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('zh-CN').format(date)
}

/**
 * 格式化日期为短格式 (MM-dd)
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {string} 格式化后的短日期字符串，如果输入为空则返回''
 */
export const formatShortDate = (dateString) => {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    return format(date, 'MM-dd')
  } catch (e) {
    return dateString
  }
}

/**
 * 格式化日期时间为本地格式，包含时分信息
 * @param {string|Date} dateTimeString - 日期时间字符串或Date对象
 * @returns {string} 格式化后的日期时间字符串，如果输入为空则返回'-'
 */
export const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  
  try {
    const date = new Date(dateTimeString)
    return format(date, 'yyyy-MM-dd HH:mm')
  } catch (e) {
    return dateTimeString || '-'
  }
}

/**
 * 获取截止日期的样式类名
 * @param {Object} shot - 镜头对象
 * @returns {string} CSS类名
 */
export const getDeadlineClass = (shot) => {
  if (!shot.deadline) return ''
  
  const today = new Date()
  const deadline = new Date(shot.deadline)
  const diffDays = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) {
    return 'text-danger' // 已逾期
  } else if (diffDays <= 7) {
    return 'text-warning' // 临近
  }
  return ''
}

/**
 * 获取提交日期的样式类名
 * @param {Object} shot - 镜头对象
 * @returns {string} CSS类名
 */
export const getSubmitDateClass = (shot) => {
  if (!shot.deadline || !shot.last_submit_date) return ''
  
  const today = new Date()
  const deadline = new Date(shot.deadline)
  const diffDays = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24))
  
  if (shot.last_submit_date) {
    if (diffDays < 0) {
      return 'text-warning' // 已提交但逾期
    }
    return ''
  }
  
  if (diffDays < 0) {
    return 'text-danger' // 未提交且逾期
  }
  return ''
} 