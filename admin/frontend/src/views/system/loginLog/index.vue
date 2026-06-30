<template>
   <div class="app-container">
      <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
         <el-form-item label="登录地址" prop="ip">
            <el-input
               v-model="queryParams.ip"
               placeholder="请输入登录地址"
               clearable
               style="width: 200px;"
               @keyup.enter="handleQuery"
            />
         </el-form-item>
         <el-form-item label="用户名" prop="username">
            <el-input
               v-model="queryParams.username"
               placeholder="请输入用户名"
               clearable
               style="width: 200px;"
               @keyup.enter="handleQuery"
            />
         </el-form-item>
         <el-form-item label="状态" prop="status">
            <el-select
               v-model="queryParams.status"
               placeholder="登录状态"
               clearable
               style="width: 150px"
            >
               <el-option
                  v-for="dict in sys_common_status"
                  :key="dict.value"
                  :label="dict.label"
                  :value="dict.value"
               />
            </el-select>
         </el-form-item>
                  <el-form-item label="状态" prop="login_type">
            <el-select
               v-model="queryParams.login_type"
               placeholder="登录类型"
               clearable
               style="width: 150px"
            >
               <el-option
                  v-for="dict in sys_login_type"
                  :key="dict.value"
                  :label="dict.label"
                  :value="dict.value"
               />
            </el-select>
         </el-form-item>
         <el-form-item label="登录时间" style="width: 308px">
            <el-date-picker
               v-model="dateRange"
               value-format="YYYY-MM-DD HH:mm:ss"
               type="daterange"
               range-separator="-"
               start-placeholder="开始日期"
               end-placeholder="结束日期"
               :default-time="[new Date(2000, 1, 1, 0, 0, 0), new Date(2000, 1, 1, 23, 59, 59)]"
            ></el-date-picker>
         </el-form-item>
         <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
         </el-form-item>
      </el-form>

      <el-row :gutter="10" class="mb8">
         <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
      </el-row>

      <el-table ref="logininforRef" v-loading="loading" :data="logininforList" :default-sort="defaultSort">
         <el-table-column label="序号" align="center" width="70">
            <template #default="scope">
               {{ scope.$index + 1 }}
            </template>
         </el-table-column>
         <el-table-column label="用户名" align="center" prop="username" :show-overflow-tooltip="true"/>
         <el-table-column label="登录地址" align="center" prop="ip" :show-overflow-tooltip="true" />
         <el-table-column label="登录地点" align="center" prop="region" :show-overflow-tooltip="true" />
         <el-table-column label="操作系统" align="center" prop="os" :show-overflow-tooltip="true" />
         <el-table-column label="浏览器" align="center" prop="browser" :show-overflow-tooltip="true" />
         <el-table-column label="登录类型" align="center" prop="login_type" width="90">
            <template #default="scope">
               <dict-tag :options="sys_login_type" :value="scope.row.login_type" />
            </template>
         </el-table-column>
         <el-table-column label="登录状态" align="center" prop="status" width="90">
            <template #default="scope">
               <dict-tag :options="sys_common_status" :value="scope.row.status" />
            </template>
         </el-table-column>
         <el-table-column label="描述" align="center" prop="remark" :show-overflow-tooltip="true" />
         <el-table-column label="访问时间" align="center" prop="create_time" width="180">
            <template #default="scope">
               <span>{{ parseTime(scope.row.create_time) }}</span>
            </template>
         </el-table-column>
      </el-table>

      <pagination
         v-show="total > 0"
         :total="total"
         v-model:page="queryParams.pageNum"
         v-model:limit="queryParams.pageSize"
         @pagination="getList"
      />
   </div>
</template>

<script setup name="LoginLog">
import { list } from "@/api/system/loginLog"

const { proxy } = getCurrentInstance()
const { sys_common_status } = proxy.useDict("sys_common_status")
const { sys_login_type } = proxy.useDict("sys_login_type")
const logininforList = ref([])
const loading = ref(true)
const showSearch = ref(true)
const total = ref(0)
const dateRange = ref([])
const defaultSort = ref({ prop: "create_time", order: "descending" })

// 查询参数
const queryParams = ref({
  pageNum: 1,
  pageSize: 20,
  ip: undefined,
  username: undefined,
  status: undefined,
  login_type: undefined
})

/** 查询登录日志列表 */
function getList() {
  loading.value = true
  list(proxy.addDateRange(queryParams.value, dateRange.value)).then(response => {
    logininforList.value = response.data
    total.value = response.count
    loading.value = false
  })
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

/** 重置按钮操作 */
function resetQuery() {
  dateRange.value = []
  proxy.resetForm("queryRef")
  queryParams.value.pageNum = 1
  proxy.$refs["logininforRef"].sort(defaultSort.value.prop, defaultSort.value.order)
}

getList()
</script>
