<template>
  <div class="app-container">
    <el-row :gutter="20">
      <splitpanes :horizontal="appStore.device === 'mobile'" class="default-theme">
        <!--题目数据-->
        <pane size="84">
          <el-col>
            <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="90px">
              <el-form-item label="提示词内容" prop="prompt_content">
                <el-input v-model="queryParams.prompt_content" placeholder="请输入内容" clearable style="width: 180px" @keyup.enter="handleQuery" />
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
                <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasRole="['admin']">删除</el-button>
              </el-col>
              <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
            </el-row>

            <el-table v-loading="loading" :data="publicList" @selection-change="handleSelectionChange">
              <el-table-column type="selection" width="50" align="center" />
              <el-table-column label="序号" align="center" key="index" width="120">
                <template #default="scope">
                  <span>{{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column 
                  label="提示词标签" 
                  align="center" 
                  prop="tags" 
                  :show-overflow-tooltip="true">
                  <template #default="scope">
                    <div v-if="!scope.row.tags || scope.row.tags.length === 0">
                      <span class="text-gray">无</span>
                    </div>
                    <div v-else>
                      <el-tag 
                        v-for="tag in scope.row.tags" 
                        :key="tag.id" 
                        size="small" 
                        type="info"
                        style="margin-right: 4px;"
                      >
                        {{ tag.name }}
                      </el-tag>
                    </div>
                  </template>
              </el-table-column>
              <el-table-column label="公共提示词内容" align="center" key="prompt_content" prop="prompt_content" :show-overflow-tooltip="true"/>
              <el-table-column label="类型" align="center" key="type" prop="type" :show-overflow-tooltip="true">
                  <template #default="scope" >
                    <el-tag 
                    size="small"
                    :type="getTagType(scope.row.type)">
                        {{ getTypeLabel(scope.row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="备注" align="center" key="remark" prop="remark" :show-overflow-tooltip="true"/>
              <el-table-column label="创建时间" align="center" prop="create_time"  width="160">
                <template #default="scope">
                  <span>{{ parseTime(scope.row.create_time) }}</span>
                </template>
              </el-table-column>
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
      <el-form :model="form" :rules="rules" ref="promptRef">

        <el-row >
          <el-col >
            <el-form-item label="提示词内容" prop="prompt_content" label-width="auto">
              <el-input type="textarea" v-model="form.prompt_content" placeholder="请输入内容"/>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row gutter="12">
          <el-col :span="12">
            <el-form-item label="提示词类型" prop="type" label-width="auto">
              <el-select v-model="form.type" placeholder="请选择提示词类型">
                <el-option
                  v-for="dict in prompt_type"
                  :key="dict.value" 
                  :value="dict.value"
                  :label="dict.label"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="标签" prop="tag" label-width="auto">
              <el-cascader
                v-model="form.tags"
                :options="tag_list"
                :emitPath="false" 
                :props="{ checkStrictly: true, multiple:true}"
                clearable
                ></el-cascader>
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
            <el-form-item label="提示词启用状态" prop="status" label-width="auto">
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
import { getPromptQuestion } from "@/api/biz/question_bank"
import {changePromptStatus , delPrompt , updatePrompt , addPrompt,listPrompt } from "@/api/biz/prompt"
import { Splitpanes, Pane } from "splitpanes"
import "splitpanes/dist/splitpanes.css"
import { filterReadOnlyFields } from "@/utils/hte"
import {checkPermi} from "@/utils/permission"
const appStore = useAppStore()
const { proxy } = getCurrentInstance()
const { sys_normal_disable, prompt_type } = proxy.useDict("sys_normal_disable","prompt_type")
import { ElInput, ElMessageBox, ElMessage} from 'element-plus'
import { requiredAndTrim } from "@/utils/validators"
import { getTagTree } from "@/api/biz/tag"
import { ref,nextTick,computed  } from 'vue'
import { el } from 'element-plus/es/locales.mjs'

const publicList = ref([])
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
    prompt_content: undefined,
    status: null,
  },
  rules: {
    status: [
      { required: true, message: "请选择状态", trigger: "change" }
    ],
    prompt_content: requiredAndTrim("请输入内容")
  }
})

const { queryParams, form, rules } = toRefs(data)
const activeName = ref('tab1')

onMounted(() => {
  getList()
  showTagTree()
})

function init(){
  getList()
  reset()
}
/** 查询提示词列表 */
function getList() {
  loading.value = true
  listPrompt(proxy.addDateRange(queryParams.value, dateRange.value)).then(res => {
    loading.value = false
    publicList.value = res.data
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
    const data = {is_public:'1'}
  if (row && row.id) {
    const index = publicList.value.findIndex(item => item.id === row.id) + 1 // 找到行在列表中的索引
    proxy.$modal.confirm(`是否确认删除序号为"${index}"的数据项？`).then(function () {
      return delPrompt(row.id,data) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
  // 2. 批量删除：保持原有逻辑
  else if (ids.value.length > 0) {
    proxy.$modal.confirm(`是否确认删除选中的${ids.value.length}条数据项？`).then(function () {
      return delPrompt(ids.value,data) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
}

/** 停用启用 */
function handleStatusChange(row) {
  const index = publicList.value.findIndex(item => item.id === row.id) + 1 // 找到行在列表中的索引
  let text = row.status === "0" ? "停用" : "启用"
  proxy.$modal.confirm('确认要' + text + '"' + "序号为" + index + '"的提示词吗?').then(function () {
    return changePromptStatus(row.id, row.status)
  }).then(() => {
    proxy.$modal.msgSuccess(text + "成功")
  }).catch(function () {
    row.status = row.status === "0" ? "1" : "0"
  })
}

/** 重置操作表单 */
function reset() {
  form.value = {
    id: null,
    prompt_content: '',
    remark: '',
    status: '0',
    is_public:'1',
    tags:[],
    type:null,
  }
  proxy.resetForm("promptRef")
}

/** 取消按钮 */
function cancel() {
  open.value = false
  reset()
}

/** 新增按钮操作 */
function handleAdd(row) {
  reset()
  open.value = true
  title.value = "修改提示词"
}

/** 修改按钮操作 */
function handleUpdate(row) {
  // console.log('当前行的数据',row)
  form.value = JSON.parse(JSON.stringify(row))
  const tagIds = form.value.tags.map(tag => tag.id)
  form.value.tags = tagIds
  open.value = true
  title.value = "修改提示词"
}

/** 选择条数  */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id)
  single.value = selection.length !== 1 
  multiple.value = selection.length === 0
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["promptRef"].validate(valid => {
    if (valid) {
      // 处理标签数组
      if(form.value.tags){
        console.log(form.value.tags)
        form.value.tags = form.value.tags.map(item =>{
          if(Array.isArray(item)){
            const tag_len = item.length
            return item[tag_len-1]
          }
          return item 
        })
      }
      if (form.value.id != undefined) {
        const payload = filterReadOnlyFields(form.value)
        updatePrompt(payload).then(response => {
          proxy.$modal.msgSuccess("修改成功")
          getList()
        })
      } else {
        form.value.is_public='1'
        addPrompt(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功")
          getList()
        })
      }
      console.log("提交表单")
      console.log(form.value)
      open.value = false
    }
  })
}

/** 处理传来的图片数据 */
const parsedImageList = computed(() => {
  if (!form.value.img_list) {
    return []
  }

  try {
    const jsonArray = form.value.img_list.map(item=>item.url)
    if (jsonArray && jsonArray.length > 0) {
      return jsonArray
    }
    return []
  } catch (e) {
    // JSON解析失败时的容错
    console.log('图片JSON数据解析失败：', e)
    return []
  }
})

// 获取标签树
function showTagTree(){
  getTagTree().then(res => {
    tag_list.value = res.data
  })
}

/**获取类型 */
function getTagType(value) { 
  const item = prompt_type.value.find(item=>item.value === value)
  return item ? item.elTagType : ''
}

/** 根据类型获取标签 */
function getTypeLabel(value){
  const item = prompt_type.value.find(item=>item.value===value)
  return item ? item.label : ''
}
</script>


<style scoped>
/* 确保容器没有额外的内边距 */
.app-container {
  padding: 0;
  margin: 0;
}
</style>