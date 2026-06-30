<template>
  <div class="app-container">
    <el-row :gutter="20">
      <splitpanes :horizontal="appStore.device === 'mobile'" class="default-theme">
        <!--题目数据-->
        <pane size="84">
          <el-col>
            <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
              <el-form-item label="标签名称" prop="name">
                <el-input v-model="queryParams.name" placeholder="请输入标签名称" clearable style="width: 180px" @keyup.enter="handleQuery" />
              </el-form-item>
              <el-form-item label="标签key" prop="tag_key">
                <el-input v-model="queryParams.tag_key" placeholder="请输入key" clearable style="width: 180px" @keyup.enter="handleQuery" />
              </el-form-item>
              <el-form-item label="状态" prop="status">
                <el-select v-model="queryParams.status" placeholder="题目状态" clearable style="width: 150px">
                  <el-option v-for="dict in sys_normal_disable" :key="dict.value" :label="dict.label" :value="dict.value" />
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
                <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasRole="['admin']">新增</el-button>
              </el-col>
              <el-col :span="1.5">
                <el-button type="success" plain icon="Edit" :disabled="single" @click="handleUpdate" v-hasRole="['admin']">修改</el-button>
              </el-col>
              <el-col :span="1.5">
                <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasRole="['admin']">删除</el-button>
              </el-col>
              <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
            </el-row>

            <el-table v-loading="loading" :data="tagList" @selection-change="handleSelectionChange">
              <el-table-column type="selection" width="50" align="center" />
              <el-table-column label="序号" align="center" key="index" width="120">
                <template #default="scope">
                  <span>{{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column label="标签名称" align="center" key="name" prop="name" :show-overflow-tooltip="true"  />
              <el-table-column label="标签key" align="center" key="tag_key" prop="tag_key" :show-overflow-tooltip="true"/>
              <el-table-column label="备注" align="center" key="remark" prop="remark" :show-overflow-tooltip="true"/>
              <!-- <el-table-column label="排序号" align="center" key="sortNum" prop="sortNum"/> -->
              <el-table-column label="创建时间" align="center" prop="create_time"  width="160">
                <template #default="scope">
                  <span>{{ parseTime(scope.row.create_time) }}</span>
                </template>
              </el-table-column>
              <!-- <el-table-column label="审核状态" align="center" key="status" prop="status"/> -->
              <el-table-column label="状态" align="center" key="status">
                <template #default="scope">
                  <el-switch
                    v-model="scope.row.status"
                    active-value=1
                    inactive-value=0
                    @change="handleStatusChange(scope.row)"
                  ></el-switch>
                </template>
              </el-table-column>
               
              <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
                <template #default="scope">
                  <el-tooltip content="修改" placement="top" >
                    <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)"  v-hasRole="['admin']"></el-button>
                  </el-tooltip>
                  <el-tooltip content="删除" placement="top" >
                    <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasRole="['admin']"></el-button>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
            <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
          </el-col>
        </pane>
      </splitpanes>
    </el-row>

    <!-- 添加或修改配置对话框 -->
    <el-dialog :title="title" v-model="open" width="700px" append-to-body>
      <el-form :model="form" :rules="rules" ref="tagRef">

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="标签名称" prop="name" label-width="auto">
              <el-input v-model="form.name" placeholder="请输入名称" />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="父标签" prop="parent_id" label-width="auto">
                <el-cascader
                  v-model="form.parent_id"
                  :options="tag_list"
                  :emitPath="false" 
                  :props="{ checkStrictly: true }"
                  clearable
                  ref="cascaderRef"
                  @change="handleChange"></el-cascader>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row gutter="12">
          <el-col :span="12">
            <el-form-item label="标签key" prop="tag_key" label-width="auto">
              <el-input v-model="form.tag_key" placeholder="请输入标签key" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item label="备注" label-width="auto">
              <el-input v-model="form.remark" type="textarea" placeholder="请输入内容" maxlength="100" show-word-limit></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="状态" prop="status" label-width="auto">
              <el-radio-group v-model="form.status">
                <el-radio v-for="dict in sys_normal_disable" :key="dict.value" :value="dict.value">{{ dict.label }}</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
        
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm" v-hasRole="['admin']">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="questionBank">
import useAppStore from '@/store/modules/app'
import { changeTagStatus, listTag, delTag, getTag, updateTag, addTag, getTagTree } from "@/api/biz/tag"
import { Splitpanes, Pane } from "splitpanes"
import "splitpanes/dist/splitpanes.css"
import { filterReadOnlyFields } from "@/utils/hte"
import {checkPermi} from "@/utils/permission"
const appStore = useAppStore()
const { proxy } = getCurrentInstance()
const { sys_normal_disable, sys_user_sex, sys_yes_no } = proxy.useDict("sys_normal_disable", "sys_user_sex", "sys_yes_no")
import { ElInput, ElMessageBox, } from 'element-plus'
import { requiredAndTrim } from "@/utils/validators"
import { el } from 'element-plus/es/locales.mjs'
import { ref,nextTick } from 'vue'
const tagList = ref([])
const open = ref(false)
const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref("")
const dateRange = ref([])
const tag_list = ref([])
const cascaderRef = ref(null)
const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    name: undefined,
    key: undefined,
    status: null,
  },
  rules: {
    name: requiredAndTrim("请输入标签名称"),
    tag_key: requiredAndTrim("请输入标签key"),
    status: [
      { required: true, message: "请选择状态", trigger: "change" }
    ],
    parent_id: [
    {
      validator: (rule, value, callback) => {
        // value 就是当前选中的 parent_id 值
        const currentId = data.form.id;
        // 校验逻辑：1.当前是编辑态（有自身id） 2.父标签id有值 3.父标签id === 自身id → 校验失败
        if (currentId && value && currentId === value) {
          callback(new Error('父标签不能选择当前标签本身'));
        } else {
          callback();
        }
      },
      trigger: ['change', 'blur'] 
    }
  ]
  }
})

const { queryParams, form, rules } = toRefs(data)
let update_tag_parent_id = null

onMounted(() => {
  getList()
  showTagTree()
})

function init(){
  getList()
  showTagTree()
  reset()
}


/** 查询标签列表 */
function getList() {
  loading.value = true
  listTag(proxy.addDateRange(queryParams.value, dateRange.value)).then(res => {
    loading.value = false
    tagList.value = res.data
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
    const index = tagList.value.findIndex(item => item.id === row.id) + 1 // 找到行在列表中的索引
    proxy.$modal.confirm(`是否确认删除序号为"${index}"的数据项？`).then(function () {
      return delTag(row.id) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
  // 2. 批量删除：保持原有逻辑
  else if (ids.value.length > 0) {
    proxy.$modal.confirm(`是否确认删除选中的${ids.value.length}条数据项？`).then(function () {
      return delTag(ids.value) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
}

/** 标签状态修改  */
function handleStatusChange(row) {
  let text = row.status === "0" ? "停用" : "启用"
  proxy.$modal.confirm('确认要' + text + '"' + row.name + '"标签吗?').then(function () {
    return changeTagStatus(row.id, row.status)
  }).then(() => {
    proxy.$modal.msgSuccess(text + "成功")
  }).catch(function () {
    row.status = row.status === "0" ? "1" : "0"
  })
}

/** 重置操作表单 */
function reset() {
  proxy.resetForm("tagRef")
  form.value = {
    id: null,
    name: '',
    tag_key: '',
    parent_id: null,
    remark: '',
    status: '0',
  }
}

/** 取消按钮 */
function cancel() {
  open.value = false
  reset()
}

/** 新增按钮操作 */
function handleAdd() {
  reset()
  open.value = true
  title.value = "添加标签"
}

/** 修改按钮操作 */
function handleUpdate(row) {
  const id = row.id || ids.value
  getTag(id).then(response => {
    update_tag_parent_id = row.parent_id || null
    form.value = response.data
    open.value = true
    title.value = "修改标签"
  })
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["tagRef"].validate(valid => {
    if (valid) {
      console.log("提交表单")
      console.log(form)
      if (form.value.id != undefined) {
        const payload = filterReadOnlyFields(form.value)
        updateTag(payload).then(response => {
          proxy.$modal.msgSuccess("修改成功")
          getList()
          showTagTree()
        })
      } else {
        addTag(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功")
          getList()
          showTagTree()
        })
      }
      open.value = false
    }
  })
}

// 获取标签树
function showTagTree(){
  getTagTree().then(res => {
    tag_list.value = res.data
  })
}

// 处理单个父级标签
function handleChange(value) {
  if (value && value.length > 0) {
    const parent_id_len = value.length
    const par_id = value[parent_id_len - 1]
    data.form.parent_id = par_id
  }
}

/** 选择条数  */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id)
  single.value = selection.length !== 1 
  multiple.value = selection.length === 0
}

</script>
