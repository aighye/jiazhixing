<template>
  <router-view />
</template>

<script setup>
</script>

<style>
/* 校验提示语统一为红色 */
.el-message--warning {
  --el-message-bg-color: #fef0f0;
  --el-message-border-color: #fde2e2;
  --el-message-text-color: #f56c6c;
}
.el-message--warning .el-message__content {
  color: #f56c6c !important;
}
/* 提示语显示在页面正中央 */
.el-message {
  position: fixed !important;
  top: 50% !important;
  bottom: auto !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  z-index: 9999 !important;
}
</style>
