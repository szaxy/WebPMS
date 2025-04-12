/**
 * 字符串工具函数
 */

/**
 * 截断文本到指定长度，超出部分显示省略号
 * @param {string} text - 原始文本
 * @param {number} length - 最大长度
 * @returns {string} 截断后的文本
 */
export const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

/**
 * 截断文件名，保留扩展名
 * @param {string} filename - 文件名
 * @param {number} maxLength - 最大长度，默认20
 * @returns {string} 截断后的文件名
 */
export const truncateFilename = (filename, maxLength = 20) => {
  if (!filename) return ''
  
  if (filename.length > maxLength) {
    const ext = filename.split('.').pop()
    return filename.substring(0, maxLength - 6) + '...' + (ext ? '.' + ext : '')
  }
  
  return filename
} 