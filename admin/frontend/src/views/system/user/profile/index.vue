<template>
   <div class="app-container">
      <el-row :gutter="20">
         <el-col :span="6" :xs="24">
            <el-card class="box-card">
               <template v-slot:header>
                 <div class="clearfix">
                   <span>个人信息</span>
                 </div>
               </template>
               <div>
                  <div class="text-center">
                     <userAvatar />
                  </div>
                  <ul class="list-group list-group-striped">
                     <li class="list-group-item">
                        <svg-icon icon-class="user" /> 用户名
                        <div class="pull-right">{{ state.user.username }}</div>
                     </li>
                     <li class="list-group-item">
                        <svg-icon icon-class="phone" /> 手机号码
                        <div class="pull-right">{{ state.user.mobile }}</div>
                     </li>
                     <li class="list-group-item">
                        <svg-icon icon-class="email" /> 用户邮箱
                        <div class="pull-right">{{ state.user.email }}</div>
                     </li>
                     <li class="list-group-item">
                        <svg-icon icon-class="tree" /> 所属部门
                        <div class="pull-right" >{{ state.user.dept_name }}</div>
                     </li>
                     <li class="list-group-item">
                        <svg-icon icon-class="date" /> 创建日期
                        <div class="pull-right">{{ state.user.create_time }}</div>
                     </li>
                  </ul>
               </div>
            </el-card>
         </el-col>
         <el-col :span="18" :xs="24">
            <el-card>
               <template v-slot:header>
                 <div class="clearfix">
                   <span>基本资料</span>
                 </div>
               </template>
               <el-tabs v-model="selectedTab">
                  <el-tab-pane label="基本资料" name="userinfo">
                     <userInfo :user="state.user" />
                  </el-tab-pane>
                  <el-tab-pane label="修改密码" name="resetPwd">
                     <resetPwd />
                  </el-tab-pane>
               </el-tabs>
            </el-card>
         </el-col>
      </el-row>
   </div>
</template>

<script setup>
import { computed } from 'vue'
import useUserStore from '@/store/modules/user'
import { useRoute } from 'vue-router'
import userAvatar from "./userAvatar"
import userInfo from "./userInfo"
import resetPwd from "./resetPwd"

const route = useRoute()
const selectedTab = ref("userinfo")

const userStore = useUserStore()

// 这里直接取 store 的状态
const state = reactive({
  user: computed(() => ({
    username: userStore.username,
    mobile: userStore.mobile,
    email: userStore.email,
    dept_name: userStore.dept_name,
    create_time: userStore.create_time,
    gender: userStore.gender,
    nickname: userStore.nickname,
  }))
})
onMounted(() => {
  const activeTab = route.params && route.params.activeTab
  if (activeTab) {
    selectedTab.value = activeTab
  }
})
</script>