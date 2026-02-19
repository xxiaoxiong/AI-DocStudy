<template>
  <div class="exam-list">
    <div class="page-header">
      <h2>考试练习</h2>
    </div>

    <div class="content">
      <el-card>
        <el-empty description="考试练习功能开发中..." />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
// 考试列表页面
</script>

<style scoped lang="scss">
.exam-list {
  .page-header {
    padding: 16px 24px;
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    margin-bottom: 16px;

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }
  }

  .content {
    padding: 0 24px 24px;
  }
}
</style>

