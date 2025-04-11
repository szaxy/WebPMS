import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { useTokenInterceptor } from '@/utils/tokenInterceptor';

// 创建axios实例并应用token拦截器
const apiClient = axios.create({
  baseURL: '/api'
});
useTokenInterceptor(apiClient);

export const useCommentStore = defineStore('comment', () => {
  // 状态
  const comments = ref([]);
  const loading = ref(false);
  const error = ref(null);
  
  // 获取镜头相关的评论
  async function fetchShotComments(shotId) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await apiClient.get(`/comments/`, {
        params: { shot: shotId }
      });
      
      const result = response.data.results || response.data;
      comments.value = result;
      return result;
    } catch (err) {
      console.error('Error fetching comments:', err);
      error.value = '获取评论失败';
      return [];
    } finally {
      loading.value = false;
    }
  }
  
  // 添加评论
  async function addComment(commentData) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await apiClient.post('/comments/', commentData);
      
      // 如果是对镜头的评论，添加到本地评论列表
      if (commentData.shot && comments.value.length > 0) {
        comments.value = [response.data, ...comments.value];
      }
      
      return response.data;
    } catch (err) {
      console.error('Error adding comment:', err);
      error.value = '添加评论失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  // 标记评论为已解决
  async function resolveComment(commentId, resolved = true) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await apiClient.patch(`/comments/${commentId}/`, {
        is_resolved: resolved
      });
      
      // 更新本地评论状态
      const index = comments.value.findIndex(c => c.id === commentId);
      if (index !== -1) {
        comments.value[index] = {
          ...comments.value[index],
          is_resolved: resolved
        };
      }
      
      return response.data;
    } catch (err) {
      console.error('Error resolving comment:', err);
      error.value = '更新评论状态失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  // 删除评论
  async function deleteComment(commentId) {
    loading.value = true;
    error.value = null;
    
    try {
      await apiClient.delete(`/comments/${commentId}/`);
      
      // 从本地列表中移除
      comments.value = comments.value.filter(c => c.id !== commentId);
      
      return true;
    } catch (err) {
      console.error('Error deleting comment:', err);
      error.value = '删除评论失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  return {
    comments,
    loading,
    error,
    fetchShotComments,
    addComment,
    resolveComment,
    deleteComment
  };
}); 