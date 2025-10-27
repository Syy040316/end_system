<template>
  <a-config-provider :locale="zhCN">
    <router-view />
  </a-config-provider>
</template>

<script setup lang="ts">
import zhCN from 'ant-design-vue/es/locale/zh_CN'
</script>

<style>
#app {
  min-height: 100vh;
  background: #f0f2f5;
}

body {
  margin: 0;
  padding: 0;
}
</style>
