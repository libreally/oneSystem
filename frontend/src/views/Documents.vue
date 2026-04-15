<template>
  <div class="page active">
    <div class="card">
      <div class="card-title">
        <span>📄 文档管理</span>
        <div class="card-actions">
          <button class="btn btn-primary" @click="showUploadDialog = true">上传文件</button>
        </div>
      </div>
      
      <!-- 文件列表 -->
      <table class="data-table">
        <thead>
          <tr>
            <th>文件名</th>
            <th>类型</th>
            <th>修改时间</th>
            <th>大小</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in documents" :key="doc.path">
            <td>{{ doc.filename }}</td>
            <td>{{ getFileType(doc.extension) }}</td>
            <td>{{ formatDate(doc.mtime) }}</td>
            <td>{{ formatSize(doc.size) }}</td>
            <td>
              <button class="btn btn-secondary" @click="previewDocument(doc)">预览</button>
              <button class="btn btn-secondary" @click="downloadDocument(doc.filename)">下载</button>
              <button class="btn btn-danger" @click="deleteDocument(doc.filename)">删除</button>
            </td>
          </tr>
          <tr v-if="documents.length === 0">
            <td colspan="5" class="empty-state">
              暂无上传的文件
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 上传文件对话框 -->
    <div class="dialog" v-if="showUploadDialog">
      <div class="dialog-content">
        <div class="dialog-header">
          <h3>上传文件</h3>
          <button class="close-btn" @click="showUploadDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <input type="file" ref="fileInput" @change="handleFileChange" multiple>
          <button class="btn btn-primary upload-btn" @click="uploadFile">确认上传</button>
        </div>
      </div>
    </div>
    
    <!-- 预览对话框 -->
    <div class="dialog" v-if="showPreviewDialog">
      <div class="dialog-content preview-dialog">
        <div class="dialog-header">
          <h3>文件预览</h3>
          <button class="close-btn" @click="showPreviewDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <img v-if="previewType === 'image'" :src="previewUrl" class="preview-image">
          <div v-else class="preview-info">
            <p><strong>文件名：</strong>{{ previewData.filename }}</p>
            <p><strong>大小：</strong>{{ formatSize(previewData.size) }}</p>
            <p><strong>修改时间：</strong>{{ formatDate(previewData.mtime) }}</p>
            <p><strong>类型：</strong>{{ getFileType(previewData.extension) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// 响应式数据
const documents = ref([]);
const showUploadDialog = ref(false);
const showPreviewDialog = ref(false);
const fileInput = ref(null);
const selectedFiles = ref([]);
const previewUrl = ref('');
const previewType = ref('');
const previewData = ref({});

// 初始化
onMounted(() => {
  fetchDocuments();
});

// 获取文档列表
async function fetchDocuments() {
  try {
    const response = await fetch('/api/documents');
    const data = await response.json();
    if (data.success) {
      documents.value = data.data.documents;
    }
  } catch (error) {
    console.error('获取文档列表失败:', error);
  }
}

// 处理文件选择
function handleFileChange(event) {
  selectedFiles.value = event.target.files;
}

// 上传文件
async function uploadFile() {
  if (selectedFiles.value.length === 0) {
    alert('请选择要上传的文件');
    return;
  }
  
  const formData = new FormData();
  for (let i = 0; i < selectedFiles.value.length; i++) {
    formData.append('file', selectedFiles.value[i]);
  }
  
  try {
    const response = await fetch('/api/documents/', {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    if (data.success) {
      alert('文件上传成功');
      showUploadDialog.value = false;
      fetchDocuments();
    } else {
      alert('文件上传失败: ' + data.message);
    }
  } catch (error) {
    console.error('文件上传失败:', error);
    alert('文件上传失败');
  }
}

// 下载文件
function downloadDocument(filename) {
  window.location.href = `/api/documents/${filename}`;
}

// 删除文件
async function deleteDocument(filename) {
  if (!confirm('确定要删除这个文件吗？')) {
    return;
  }
  
  try {
    const response = await fetch(`/api/documents/${filename}`, {
      method: 'DELETE'
    });
    const data = await response.json();
    if (data.success) {
      alert('文件删除成功');
      fetchDocuments();
    } else {
      alert('文件删除失败: ' + data.message);
    }
  } catch (error) {
    console.error('文件删除失败:', error);
    alert('文件删除失败');
  }
}

// 预览文件
async function previewDocument(doc) {
  try {
    const ext = doc.extension.toLowerCase();
    if (['.jpg', '.jpeg', '.png', '.gif'].includes(ext)) {
      previewType.value = 'image';
      previewUrl.value = `/api/documents/preview/${doc.filename}`;
    } else {
      previewType.value = 'info';
      previewData.value = doc;
    }
    showPreviewDialog.value = true;
  } catch (error) {
    console.error('文件预览失败:', error);
    alert('文件预览失败');
  }
}



// 辅助函数
function getFileType(extension) {
  const typeMap = {
    '.doc': 'Word 文档',
    '.docx': 'Word 文档',
    '.txt': '文本文件',
    '.pdf': 'PDF 文件',
    '.xls': 'Excel 表格',
    '.xlsx': 'Excel 表格',
    '.csv': 'CSV 文件',
    '.ppt': 'PowerPoint 演示',
    '.pptx': 'PowerPoint 演示',
    '.jpg': '图片文件',
    '.jpeg': '图片文件',
    '.png': '图片文件',
    '.gif': '图片文件'
  };
  return typeMap[extension] || '其他文件';
}

function formatDate(timestamp) {
  return new Date(timestamp * 1000).toLocaleString('zh-CN');
}

function formatSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
</script>

<style scoped>
.page { display: block; }
.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-actions {
  display: flex;
  gap: 10px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}
.data-table th {
  background: #fafafa;
  font-weight: 600;
  font-size: 14px;
}
.data-table tr:hover {
  background: #f5f7fa;
}
.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  margin-right: 5px;
}
.btn-primary {
  background: rgb(0, 101, 105);
  color: white;
}
.btn-secondary {
  background: #f5f7fa;
  color: #333;
}
.btn-danger {
  background: #ff4d4f;
  color: white;
}
.btn:hover {
  opacity: 0.8;
}
.upload-btn {
  margin-top: 15px;
  width: 100%;
}

/* 对话框样式 */
.dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.dialog-content {
  background: white;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.preview-dialog {
  width: 600px;
}
.dialog-header {
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}
.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.close-btn:hover {
  color: #333;
}
.dialog-body {
  padding: 20px;
}
.dialog-body input[type="file"] {
  width: 100%;
  margin-bottom: 15px;
}
.dialog-body input[type="text"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}
.preview-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}
.preview-info {
  line-height: 1.6;
}
</style>
