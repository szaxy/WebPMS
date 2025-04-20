/**
 * 媒体文件URL处理工具
 * 用于确保媒体文件URL使用正确的主机和端口
 */

/**
 * 获取完整的媒体文件URL
 * @param {string} relativeUrl 相对路径，例如 /media/@attachments/...
 * @returns {string} 完整的媒体文件URL
 */
export function getFullMediaUrl(relativeUrl) {
  if (!relativeUrl) {
    console.warn('[mediaHelper] Received empty or null relativeUrl');
    return '';
  }

  // 强制去除可能存在的协议和域名部分，只处理相对路径
  const pathOnly = relativeUrl.replace(/^(?:https?:)?\/\/[^\/]+/, '');

  // 确保路径以/开头
  const normalizedUrl = pathOnly.startsWith('/') ? pathOnly : `/${pathOnly}`;

  // 获取当前协议和主机
  const protocol = window.location.protocol;
  const host = window.location.hostname;
  const port = '8754'; // 固定使用Nginx的端口

  // 构建完整URL
  const fullUrl = `${protocol}//${host}:${port}${normalizedUrl}`;
  console.log(`[mediaHelper] URL: ${fullUrl}`); // 日志记录
  return fullUrl;
}

/**
 * 格式化附件URL
 * @param {Object} attachment 附件对象
 * @returns {Object} 带有完整URL的附件对象
 */
export function formatAttachment(attachment) {
  if (!attachment) return null;

  const formattedAttachment = { ...attachment };

  if (attachment.file_path) {
    formattedAttachment.file_path = getFullMediaUrl(attachment.file_path);
  }

  if (attachment.thumbnail_path) {
    formattedAttachment.thumbnail_path = getFullMediaUrl(attachment.thumbnail_path);
  }

  return formattedAttachment;
}

/**
 * 格式化附件列表URL
 * @param {Array} attachments 附件对象数组
 * @returns {Array} 带有完整URL的附件对象数组
 */
export function formatAttachments(attachments) {
  if (!attachments || !Array.isArray(attachments)) return [];
  return attachments.map(formatAttachment);
}

export default {
  getFullMediaUrl,
  formatAttachment,
  formatAttachments
}; 