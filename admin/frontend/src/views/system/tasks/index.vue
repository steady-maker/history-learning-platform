<template>
   <div class="app-container">
      <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
         <el-form-item label="任务名称" prop="id">
            <el-input
               v-model="queryParams.id"
               placeholder="请输入任务id"
               clearable
               style="width: 240px"
               @keyup.enter="handleQuery"
            />
         </el-form-item>
         <el-form-item label="任务名称" prop="name">
            <el-input
               v-model="queryParams.name"
               placeholder="请输入任务名称"
               clearable
               style="width: 240px"
               @keyup.enter="handleQuery"
            />
         </el-form-item>
         <el-form-item label="触发函数" prop="func">
            <el-input
               v-model="queryParams.func"
               placeholder="请输入触发函数"
               clearable
               style="width: 240px"
               @keyup.enter="handleQuery"
            />
         </el-form-item>
         <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
         </el-form-item>
      </el-form>

      <el-row :gutter="10" class="mb8">
         <el-col :span="1.5">
            <el-button
               type="primary"
               plain
               icon="Plus"
               @click="handleAdd"
            >新增</el-button>
         </el-col>
         <el-col :span="1.5">
            <el-button
               type="success"
               plain
               icon="Edit"
               :disabled="single"
               @click="handleUpdate"
            >修改</el-button>
         </el-col>
         <el-col :span="1.5">
            <el-button
               type="danger"
               plain
               icon="Delete"
               :disabled="multiple"
               @click="handleDelete"
            >删除</el-button>
         </el-col>
         <el-col :span="1.5">
            <el-button
               type="warning"
               plain
               icon="VideoPause"
               :disabled="multiple"
               @click="handlePause"
            >暂停</el-button>
         </el-col>
         <el-col :span="1.5">
            <el-button
               type="info"
               plain
               icon="VideoPlay"
               :disabled="multiple"
               @click="handleResume"
            >恢复</el-button>
         </el-col>
         <!-- <el-col :span="1.5">
            <el-button
               type="warning"
               plain
               icon="Download"
               @click="handleExport"
               v-hasPermi="['system:config:export']"
            >导出</el-button>
         </el-col> -->
         <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
      </el-row>

      <el-table v-loading="loading" :data="configList" @selection-change="handleSelectionChange">
         <el-table-column type="selection" width="55" align="center" />
         <el-table-column label="任务ID" align="center" prop="id" :show-overflow-tooltip="true" />
         <el-table-column label="任务名称" align="center" prop="name" :show-overflow-tooltip="true" />
         <el-table-column label="任务类型" align="center" prop="type">
            <template #default="scope">
               <dict-tag :options="sys_task_type" :value="scope.row.type" />
            </template>
         </el-table-column>
         <el-table-column label="触发时机" align="center" prop="trigger" :show-overflow-tooltip="true" />
         <el-table-column label="触发函数" align="center" prop="func" :show-overflow-tooltip="true" />
         <el-table-column label="下次执行时间" align="center" prop="next_run_time" width="180">
            <template #default="scope">
               <span>  {{ scope.row.next_run_time === 'paused' ? '暂停中……' : parseTime(scope.row.next_run_time)}}</span>
            </template>
         </el-table-column>
         <el-table-column label="操作" align="center" width="300" class-name="small-padding fixed-width">
            <template #default="scope">
               <el-button link type="success" icon="Edit" @click="handleUpdate(scope.row)" >修改</el-button>
               <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" >删除</el-button>
               <el-button link type="warning" icon="VideoPause" @click="handlePause(scope.row)" v-if="scope.row.next_run_time != 'paused'" >暂停</el-button>
               <el-button link type="primary" icon="VideoPlay" @click="handleResume(scope.row)" v-else>恢复</el-button>
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

      <!-- 添加或修改参数配置对话框 -->
      <el-dialog :title="title" v-model="open" width="600px" append-to-body>
      <el-form ref="taskRef" :model="form" :rules="rules" label-width="100px">
         <el-form-item label="任务ID" prop="id">
            <el-input v-model="form.id" placeholder="请输入任务ID" :disabled="update"/>
         </el-form-item>
         <!-- 任务名称 -->
         <el-form-item label="任务名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入任务名称" />
         </el-form-item>

         <!-- 触发函数 -->
         <el-form-item label="触发函数" prop="func">
            <el-input v-model="form.func" placeholder="请输入触发函数" />
         </el-form-item>

         <!-- 任务类型选择 -->
            <el-form-item label="任务类型" prop="type">
               <el-select v-model="form.type">
                  <el-option
                     v-for="item in sys_task_type"
                     :key="item.value"
                     :label="item.label"
                     :value="item.value"
                  ></el-option>
               </el-select>
            </el-form-item>

         <!-- Cron表达式 -->
         <el-form-item v-if="form.type === 'cron'" label="Cron 表达式" prop="cron_expr">
            <el-input v-model="form.cron_expr" placeholder="请输入 Cron 表达式" />
         </el-form-item>
         <el-card v-if="form.type === 'cron'" closable type="danger">
         请使用不带秒的五段 Cron 表达式，同时注意数字范围：
         <br />
         <pre>
              *   *   *   *   * 
            # |   |   |   |   |
            # |   |   |   |   day of the week (0–6) (Sunday to Saturday)
            # |   |   |   month (1–12)
            # |   |   day of the month (1–31)
            # |   hour (0–23)
            # minute (0–59)
         </pre>
         <br />
         <el-link type="danger" href="https://en.wikipedia.org/wiki/Cron" target="_blank">详见 维基百科 Cron 表达式</el-link>
         </el-card>

         <!-- 指定时间 -->
         <el-form-item v-if="form.type === 'date'" label="执行时间" prop="run_date">
            <el-date-picker
            v-model="form.run_date"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="请选择执行时间"
            style="width: 100%"
            />
         </el-form-item>
         <el-tag v-if="form.type === 'date'" type="danger" style="display: flex; justify-content: center; align-items: center;">
         注意：到了执行时间就会执行，执行完一次该任务就会被删除
         </el-tag>

         <!-- 间隔任务 -->
         <el-form-item v-if="form.type === 'interval'" label="间隔任务" prop="interval">
         <el-row>
            <el-col :span="12" style="display: flex; justify-content: center; align-items: center;">
               <span>周</span>
            </el-col>
            <el-col :span="12" style="display: flex; justify-content: center; align-items: center;">
               <span>天</span>
            </el-col>
            <el-col :span="12">
               <el-input-number v-model="form.weeks" :min="0" style="width: 100%" />
            </el-col>
            <el-col :span="12">
               <el-input-number v-model="form.days" :min="0" style="width: 100%" />
            </el-col>
         </el-row>

         <el-row>
            <el-col :span="8" style="display: flex; justify-content: center; align-items: center;">
               <span>小时</span>
            </el-col>
            <el-col :span="8" style="display: flex; justify-content: center; align-items: center;">
               <span>分钟</span>
            </el-col>
            <el-col :span="8" style="display: flex; justify-content: center; align-items: center;">
               <span>秒</span>
            </el-col>
            <el-col :span="8">
               <el-input-number v-model="form.hours" :min="0" style="width: 100%" />
            </el-col>
            <el-col :span="8">
               <el-input-number v-model="form.minutes" :min="0" style="width: 100%" />
            </el-col>
            <el-col :span="8">
               <el-input-number v-model="form.seconds" :min="0" style="width: 100%" />
            </el-col>
         </el-row>

         <el-row>
            <el-col :span="12" style="display: flex; justify-content: center; align-items: center;">
               <span>开始时间</span>
            </el-col>
            <el-col :span="12" style="display: flex; justify-content: center; align-items: center;">
               <span>结束时间</span>
            </el-col>
            <el-col :span="12">
               <el-date-picker
               v-model="form.start_date"
               type="datetime"
               value-format="YYYY-MM-DD HH:mm:ss"
               placeholder="选择开始时间"
               style="width: 100%"
               />
            </el-col>
            <el-col :span="12">
               <el-date-picker
               v-model="form.end_date"
               type="datetime"
               value-format="YYYY-MM-DD HH:mm:ss"
               placeholder="选择结束时间"
               style="width: 100%"
               />
            </el-col>
         </el-row>
         </el-form-item>
         <el-tag v-if="form.type === 'interval'" type="danger" style="display: flex; justify-content: center; align-items: center;">
         注意：如果设置了开始时间，则到了开始时间会立刻执行一次，然后再按设定的间隔执行
         </el-tag>
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

<script setup name="Tasks">
import { listTask, addTask, getTask, deleteTask, pauseTask, resumeTask } from "@/api/system/tasks"
import { requiredAndTrim } from "@/utils/validators"
const { proxy } = getCurrentInstance()
const { sys_task_type } = proxy.useDict("sys_task_type")

const configList = ref([])
const open = ref(false)
const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref("")
const update = ref(false)

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 20,
    id: undefined,
    name: undefined,
    func: undefined
  },
  rules: {
    id: requiredAndTrim('任务ID不能为空'),
    name: requiredAndTrim('任务名称不能为空'),
    func: requiredAndTrim('触发函数不能为空'),
    type: [{ required: true, message: "任务类型不能为空", trigger: "change" }]
  }
})

const { queryParams, form, rules } = toRefs(data)

/** 查询参数列表 */
function getList() {
  loading.value = true
    listTask(queryParams.value).then(response => {
    configList.value = response.data
    total.value = response.count
    loading.value = false
  })
}

/** 取消按钮 */
function cancel() {
  open.value = false
  reset()
}

/** 表单重置 */
function reset() {
  form.value = {}
  proxy.resetForm("taskRef")
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1
  getList()
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef")
  handleQuery()
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id)
  single.value = selection.length != 1
  multiple.value = !selection.length
}

/** 新增按钮操作 */
function handleAdd() {
  reset()
  open.value = true
  title.value = "添加参数"
  update.value = false
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset()
  const id = row.id || ids.value
  getTask(id).then(response => {
    form.value = response.data
    open.value = true
    title.value = "修改任务"
    update.value = true
  })
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["taskRef"].validate(valid => {
    if (valid) {
      if (form.value.id != undefined) {
        addTask(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功")
          open.value = false
          update.value = false
          getList()
        })
      } else {
        addTask(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功")
          open.value = false
          getList()
        })
      }
    }
  })
}

/** 删除按钮操作 */
function handleDelete(row) {
  const task_ids = row.id || ids.value
  proxy.$modal.confirm('是否确认删除参数编号为"' + task_ids + '"的数据项？').then(function () {
    return deleteTask(task_ids)
  }).then(() => {
    getList()
    proxy.$modal.msgSuccess("删除成功")
  }).catch(() => {})
}

/** 暂停按钮操作 */
function handlePause(row) {
  const task_ids = row.id || ids.value
  proxy.$modal.confirm('是否确认暂停参数编号为"' + task_ids + '"的数据项？').then(function () {
    return pauseTask(task_ids)
  }).then(() => {
    getList()
    proxy.$modal.msgSuccess("暂停成功")
  }).catch(() => {})
}

/** 恢复按钮操作 */
function handleResume(row) {
  const task_ids = row.id || ids.value
  proxy.$modal.confirm('是否确认恢复参数编号为"' + task_ids + '"的数据项？').then(function () {
    return resumeTask(task_ids)
  }).then(() => {
    getList()
    proxy.$modal.msgSuccess("恢复成功")
  }).catch(() => {})
}

/** 导出按钮操作 */
function handleExport() {
  proxy.download("system/config/export", {
    ...queryParams.value
  }, `config_${new Date().getTime()}.xlsx`)
}


getList()
</script>
