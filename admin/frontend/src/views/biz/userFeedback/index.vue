<template>
  <div class="app-container">
    <el-row :gutter="20">
      <splitpanes :horizontal="appStore.device === 'content'" class="default-theme">
        <!--用户反馈数据-->
        <pane size="84">
          <el-col>
            <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
              <el-form-item label="反馈内容" prop="content">
                <el-input v-model="queryParams.content" placeholder="请输入反馈内容" clearable style="width: 180px" @keyup.enter="handleQuery" />
              </el-form-item>
              <el-form-item label="处理状态" prop="feedback_status">
                <el-select v-model="queryParams.feedback_status" placeholder="反馈处理状态" clearable style="width: 150px">
                  <el-option v-for="dict in feedback_type" :key="dict.value" :label="dict.label" :value="dict.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="创建时间" style="width: 308px">
                <el-date-picker v-model="dateRange" value-format="YYYY-MM-DD" type="daterange" range-separator="-" start-placeholder="开始日期" end-placeholder="结束日期"></el-date-picker>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
                <el-button icon="Refresh" @click="resetQuery">重置</el-button>
              </el-form-item>
            </el-form>

            <el-row :gutter="10" class="mb8">
              <el-col :span="1.5">
                <el-button type="success" plain icon="Edit" :disabled="single" @click="handleUpdate" v-hasRole="['admin']">修改</el-button>
              </el-col>
              <el-col :span="1.5">
                <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasRole="['admin']">删除</el-button>
              </el-col>
              <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
            </el-row>

            <el-table v-loading="loading" :data="userFeedbackList" @selection-change="handleSelectionChange">
              <el-table-column type="selection" width="50" align="center" />
              <el-table-column label="序号" align="center" key="index" width="120">
                <template #default="scope">
                  <span>{{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column label="用户名" align="center" key="username" prop="username" v-if="columns.username.visible" :show-overflow-tooltip="true"  />
              <el-table-column label="反馈内容" align="center" key="content" prop="content" v-if="columns.content.visible" :show-overflow-tooltip="true" />
              <el-table-column label="状态" align="center" key="feedback_status" v-if="columns.feedback_status.visible">
                <template #default="scope" >
                    <el-tag 
                    size="small"
                    :type="getFeedbackTagType(scope.row.feedback_status)">
                        {{ getFeedbackLabel(scope.row.feedback_status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="创建时间" align="center" prop="create_time" v-if="columns.create_time.visible" width="160">
                <template #default="scope">
                  <span>{{ parseTime(scope.row.create_time) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="备注" align="center" key="remark" prop="remark" :show-overflow-tooltip="true"/>
              <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
                <template #default="scope">
                  <el-tooltip content="修改" placement="top" >
                    <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" ></el-button>
                  </el-tooltip>
                  <el-tooltip content="删除" placement="top">
                    <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)"></el-button>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
            <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
          </el-col>
        </pane>
      </splitpanes>
    </el-row>

    <!-- 添加或修改用户配置对话框 -->
    <el-dialog :title="title" v-model="open" width="700px" append-to-body>
      <el-form :model="form" :rules="rules" ref="userFeedbackRef" label-width="80px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" maxlength="30" disabled/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="反馈内容" prop="content">
              <el-input type="textarea" v-model="form.content" placeholder="请输入反馈内容" maxlength="11" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="反馈处理状态">
              <el-select v-model="form.feedback_status" placeholder="请选择处理类型">
                <el-option
                  v-for="dict in feedback_type"
                  :key="dict.value" 
                  :value="dict.value"
                  :label="dict.label"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" placeholder="请输入内容" maxlength="100" show-word-limit></el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="UserFeedback">
import useAppStore from '@/store/modules/app'
import { listUserFeedback, delUserFeedback, updateUserFeedback } from "@/api/biz/webUser"
import { Splitpanes, Pane } from "splitpanes"
import "splitpanes/dist/splitpanes.css"
import { filterReadOnlyFields } from "@/utils/hte"
import {checkPermi} from "@/utils/permission"
const appStore = useAppStore()
const { proxy } = getCurrentInstance()
const { sys_normal_disable, sys_user_sex, sys_yes_no, feedback_type } = proxy.useDict("sys_normal_disable", "sys_user_sex", "sys_yes_no","feedback_type")
import { ElMessageBox, } from 'element-plus'
import { requiredAndTrim } from "@/utils/validators"
const userFeedbackList = ref([])
const open = ref(false)
const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref("")
const dateRange = ref([])

// 列显隐信息
const columns = ref({
  username: { label: '用户名', visible: true },
  content: { label: '反馈内容', visible: true },
  feedback_status: { label: '状态', visible: true },
  create_time: { label: '创建时间', visible: true }
})

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    username: undefined,
    content: undefined,
    feedback_status: undefined,
  },
})

const { queryParams, form, rules } = toRefs(data)

/**根据反馈状态值获取类型 */
function getFeedbackTagType(value) { 
  const item = feedback_type.value.find(item=>item.value === value)
  return item ? item.elTagType : ''
}

/** 根据反馈状态值获取标签值 */
function getFeedbackLabel(value){
  const item = feedback_type.value.find(item=>item.value===value)
  return item ? item.label : ''
}

/** 查询用户反馈内容列表 */
function getList() {
  loading.value = true
  listUserFeedback(proxy.addDateRange(queryParams.value, dateRange.value)).then(res => {
    loading.value = false
    userFeedbackList.value = res.data
    total.value = res.count
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
  handleQuery()
}

/** 删除按钮操作 */
function handleDelete(row) {
  if (row && row.id) {
    const index = userFeedbackList.value.findIndex(item => item.id === row.id) + 1 // 找到行在列表中的索引
    proxy.$modal.confirm(`是否确认删除序号为"${index}"的数据项？`).then(function () {
      return delUserFeedback(row.id) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
  // 2. 批量删除：保持原有逻辑
  else if (ids.value.length > 0) {
    proxy.$modal.confirm(`是否确认删除选中的${ids.value.length}条数据项？`).then(function () {
      return delUserFeedback(ids.value) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
}

/** 重置操作表单 */
function reset() {
  form.value = {
    id: undefined,
    username: undefined,
    content: undefined,
    feedback_status: "1",
    remark: undefined,
  }
  proxy.resetForm("userFeedbackRef")
}

/** 取消按钮 */
function cancel() {
  open.value = false
  reset()
}

/** 修改按钮操作 */
function handleUpdate(row) {
  // console.log('当前行的数据',row)
  form.value = JSON.parse(JSON.stringify(row)) // 防止赋值对象引用，从而修改了原row对象的值
  open.value = true
  isUpdate.value = true
  title.value = "修改用户反馈内容"
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["userFeedbackRef"].validate(valid => {
    if (valid) {
      if (form.value.id != undefined) {
        const payload = filterReadOnlyFields(form.value)
        updateUserFeedback(payload).then(response => {
          proxy.$modal.msgSuccess("修改成功")
          open.value = false
          getList()
        })
      }
    }
  })
}

onMounted(() => {
  getList()
})
</script>
