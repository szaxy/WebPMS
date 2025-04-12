/**
 * 状态工具函数
 */

/**
 * 获取状态标签类型
 * @param {string} status - 状态代码
 * @returns {string} Element UI标签类型
 */
export const getStatusTagType = (status) => {
  const statusMap = {
    'waiting': 'info',
    'in_progress': 'primary',
    'submit_review': 'warning',
    'revising': 'danger',
    'internal_approved': 'success',
    'client_review': 'warning',
    'client_rejected': 'danger',
    'client_approved': 'success',
    'client_revision': 'danger',
    'deleted_merged': 'info',
    'suspended': 'info',
    'completed': 'success'
  }
  
  return statusMap[status] || 'info'
}

/**
 * 获取阶段标签类型
 * @param {string} stage - 阶段代码
 * @returns {string} Element UI标签类型
 */
export const getStageTagType = (stage) => {
  const stageMap = {
    'LAY': 'info',
    'BLK': 'warning',
    'ANI': 'primary',
    'PASS': 'success'
  }
  
  return stageMap[stage] || 'info'
}

/**
 * 获取状态显示名称
 * @param {string} status - 状态代码
 * @returns {string} 状态显示名称
 */
export const getStatusDisplayName = (status) => {
  const statusNames = {
    'waiting': '等待开始',
    'in_progress': '正在制作',
    'submit_review': '提交内审',
    'revising': '正在修改',
    'internal_approved': '内审通过',
    'client_review': '客户审核',
    'client_rejected': '客户退回',
    'client_approved': '客户通过',
    'client_revision': '客户返修',
    'deleted_merged': '已删除或合并',
    'suspended': '暂停制作',
    'completed': '已完结'
  }
  
  return statusNames[status] || status
}

/**
 * 获取阶段显示名称
 * @param {string} stage - 阶段代码
 * @returns {string} 阶段显示名称
 */
export const getStageDisplayName = (stage) => {
  const stageNames = {
    'LAY': 'Layout',
    'BLK': 'Block',
    'ANI': 'Animation',
    'PASS': 'Pass'
  }
  
  return stageNames[stage] || stage
} 