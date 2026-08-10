<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import zhCn from 'element-plus/es/locale/lang/zh-cn.mjs'
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
}
</style>
