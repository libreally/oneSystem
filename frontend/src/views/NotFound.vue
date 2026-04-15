<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>页面未找到</h2>
      <p>抱歉，您访问的页面不存在或已被移除</p>
      <router-link to="/" class="btn btn-primary">返回首页</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
};
</script>

<style scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.not-found-content {
  text-align: center;
  background-color: #fff;
  padding: 60px 40px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 90%;
  transition: all 0.3s;
}

.not-found-content:hover {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
}

.not-found-content h1 {
  font-size: 72px;
  font-weight: 700;
  color: rgb(0, 101, 105);
  margin: 0 0 20px 0;
  line-height: 1;
}

.not-found-content h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 15px 0;
}

.not-found-content p {
  color: #666;
  margin: 0 0 30px 0;
  font-size: 16px;
  line-height: 1.6;
}

.btn {
  padding: 12px 30px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: rgb(0, 101, 105);
  color: white;
}

.btn-primary:hover {
  background: rgb(0, 80, 84);
  box-shadow: 0 4px 12px rgba(0, 101, 105, 0.3);
  transform: translateY(-2px);
}
</style>
