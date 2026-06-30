<template>
  <div class="app-container">
    <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleTabClick">
      <el-tab-pane label="题目提示词" name="tab1">
        <el-row :gutter="20">
          <splitpanes :horizontal="appStore.device === 'mobile'" class="default-theme">
            <!--题目数据-->
            <pane size="84">
              <el-col>
                <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
                  <el-form-item label="题目内容" prop="content">
                    <el-input v-model="queryParams.content" placeholder="请输入题目内容" clearable style="width: 180px" @keyup.enter="handleQuery" />
                  </el-form-item>
                  <el-form-item label="题目编号" prop="code">
                    <el-input v-model="queryParams.code" placeholder="请输入题目编号" clearable style="width: 180px" @keyup.enter="handleQuery" />
                  </el-form-item>
                  <el-form-item label="题目状态" prop="status">
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
                    <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasRole="['admin']">删除</el-button>
                  </el-col>
                  <right-toolbar v-model:showSearch="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
                </el-row>

                <el-table v-loading="loading" :data="questionList" @selection-change="handleSelectionChange">
                  <el-table-column type="selection" width="50" align="center" />
                  <el-table-column label="序号" align="center" key="index" width="120">
                    <template #default="scope">
                      <span>{{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="题目唯一编号" align="center" key="code" prop="code" :show-overflow-tooltip="true"  />
                  <el-table-column label="题目内容" align="center" key="content" prop="content" :show-overflow-tooltip="true"/>
                  <el-table-column label="提示词内容" align="center" key="prompt_content" prop="prompt_content" :show-overflow-tooltip="true"/>
                  <!-- <el-table-column label="备注" align="center" key="remark" prop="remark" :show-overflow-tooltip="true"/>
                  <el-table-column label="创建时间" align="center" prop="create_time"  width="160">
                    <template #default="scope">
                      <span>{{ parseTime(scope.row.create_time) }}</span>
                    </template>
                  </el-table-column> -->
                  <!-- <el-table-column label="提示词状态" align="center" key="status">
                    <template #default="scope">
                      <el-switch
                        v-model="scope.row.status" 
                        active-value=1
                        inactive-value=0
                        @change="handleStatusChange(scope.row)"
                        :before-change="(val) => checkPromptId(scope.row, val)"
                      ></el-switch>
                    </template>
                  </el-table-column> -->
                  
                  <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
                    <template #default="scope">
                      <!-- <el-tooltip content="新增提示词" placement="top" >
                        <el-button link type="primary" icon="Plus" v-if="!scope.row.prompt_id" @click="handleAdd(scope.row)"  v-hasRole="['admin']"></el-button>
                      </el-tooltip> -->
                      <el-tooltip content="修改" placement="top" >
                        <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)"  v-hasRole="['admin']"></el-button>
                      </el-tooltip>
                      <!-- <el-tooltip content="删除" placement="top" >
                        <el-button link type="primary" icon="Delete" v-if="scope.row.prompt_id" @click="handleDelete(scope.row)" v-hasRole="['admin']"></el-button>
                      </el-tooltip> -->
                    </template>
                  </el-table-column>
                </el-table>
                <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
              </el-col>
            </pane>
          </splitpanes>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="公共提示词" name="tab2">
          <publicPrompt>

          </publicPrompt>
      </el-tab-pane>

  </el-tabs>
    <!-- 添加或修改配置对话框 -->
    <el-dialog :title="title" v-model="open" width="700px" append-to-body>
      <el-form :model="form" :rules="rules" ref="promptRef">

        <el-row>
          <el-col>
            <el-form-item label="题目内容" prop="content" label-width="auto">
              <el-input type="textarea" v-model="form.content" placeholder="请输入名称" disabled="true"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col >
            <el-form-item v-if="!form.has_sub_question" label="题目答案" prop="answer" label-width="auto">
              <el-input type="textarea" v-model="form.answer" placeholder="请输入名称" disabled="true"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="相关图片" label-width="auto">
              <!-- 图片展示容器 -->
              <div class="image-preview-container">
                <!-- 解析后的图片列表 -->
                <el-image
                  v-for="url in parsedImageList"
                  :key="index"
                  :src="url"
                  class="preview-img"
                  fit="cover"
                  :preview-src-list="parsedImageList"
                  :initial-index="index"
                />
                <!-- 无图片时的占位提示 -->
                <div class="no-image-tip" v-if="parsedImageList.length === 0">
                  暂无相关图片
                </div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row >
          <el-col >
            <el-form-item label="AI进行提示时提示词" prop="when_prompted_content" label-width="auto">
              <el-input type="textarea" v-model="form.when_prompted_content" placeholder="请输入内容"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row >
          <el-col >
            <el-form-item label="AI进行评分时提示词" prop="when_rating_content" label-width="auto">
              <el-input type="textarea" v-model="form.when_rating_content" placeholder="请输入内容"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row >
          <el-col >
            <el-form-item label="AI进行复盘时提示词" prop="during_review_content" label-width="auto">
              <el-input type="textarea" v-model="form.during_review_content" placeholder="请输入内容"/>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- <el-row>
          <el-col :span="24">
            <el-form-item label="备注" label-width="auto">
              <el-input v-model="form.remark" type="textarea" placeholder="请输入内容" maxlength="100" show-word-limit></el-input>
            </el-form-item>
          </el-col>
        </el-row> -->
        <!-- <el-row>
          <el-col :span="12">
            <el-form-item label="提示词启用状态" prop="status" label-width="auto">
              <el-radio-group v-model="form.status">
                <el-radio v-for="dict in sys_normal_disable" :key="dict.value" :value="dict.value">{{ dict.label }}</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row> -->
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
import {changePromptStatus , delPrompt , updatePrompt , addPrompt } from "@/api/biz/prompt"
import { Splitpanes, Pane } from "splitpanes"
import "splitpanes/dist/splitpanes.css"
import { filterReadOnlyFields } from "@/utils/hte"
import {checkPermi} from "@/utils/permission"
const appStore = useAppStore()
const { proxy } = getCurrentInstance()
const { sys_normal_disable, sys_user_sex, sys_yes_no } = proxy.useDict("sys_normal_disable", "sys_user_sex", "sys_yes_no")
import { ElInput, ElMessageBox, ElMessage} from 'element-plus'
import { requiredAndTrim } from "@/utils/validators"
import { el } from 'element-plus/es/locales.mjs'
import { ref,nextTick,computed  } from 'vue'
import publicPrompt from "./module/publicPrompt"
const questionList = ref([])
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
const isUpdate = ref(false)
const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    content: undefined,
    status: null,
  },
  rules: {
    status: [
      { required: true, message: "请选择状态", trigger: "change" }
    ],
    // prompt_content: requiredAndTrim("请输入内容")
  }
})

const { queryParams, form, rules } = toRefs(data)
const activeName = ref('tab1')

onMounted(() => {
  getList()
})

function init(){
  getList()
  reset()
}
/** 查询提示词列表 */
function getList() {
  loading.value = true
  getPromptQuestion(proxy.addDateRange(queryParams.value, dateRange.value)).then(res => {
    loading.value = false
    questionList.value = res.data.map(item=>({
      ...item,
      status:item.status ? item.status : '0'
    }))
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
    const index = questionList.value.findIndex(item => item.id === row.id) + 1 // 找到行在列表中的索引
    proxy.$modal.confirm(`是否确认删除序号为"${index}"的数据项？`).then(function () {
      return delPrompt(row.id) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
  // 2. 批量删除：保持原有逻辑
  else if (ids.value.length > 0) {
    proxy.$modal.confirm(`是否确认删除选中的${ids.value.length}条数据项？`).then(function () {
      return delPrompt(ids.value) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
}

/** 提示词状态修改  */
function checkPromptId(row, newVal) {
  if (row.prompt_id === null || row.prompt_id === undefined || row.prompt_id === '') {
    ElMessage.error('该题目未添加关联提示词！')
    return false // 返回 false 直接阻止 Switch 切换
  }
  return true // 允许切换
}

function handleStatusChange(row) {
  let text = row.status === "0" ? "停用" : "启用"
  proxy.$modal.confirm('确认要' + text + '"' + "题目编号为：" + row.code + '"的提示词吗?').then(function () {
    return changePromptStatus(row.prompt_id, row.status)
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
    prompt_id:null,
    // prompt_content: '',
    when_prompted_content:'',
    when_rating_content:'', 
    during_review_content:'',
    remark: '',
    status: '0',
    content: '',
    answer:'',
    img_list:[],
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
  form.value = JSON.parse(JSON.stringify(row)) // 防止赋值对象引用，从而修改了原row对象的值
  open.value = true
  title.value = "新增提示词"
}

/** 修改按钮操作 */
function handleUpdate(row) {
  // console.log('当前行的数据',row)
  form.value = JSON.parse(JSON.stringify(row)) // 防止赋值对象引用，从而修改了原row对象的值
  open.value = true
  isUpdate.value = true
  title.value = "修改提示词"
}

/** 选择条数  */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.prompt_id)
  single.value = selection.length !== 1 
  multiple.value = selection.length === 0
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["promptRef"].validate(valid => {
    if (valid) {
      // console.log("提交表单")
      // console.log(form)
      if (isUpdate.value) {
        const payload = filterReadOnlyFields(form.value)
        updatePrompt(payload).then(response => {
          proxy.$modal.msgSuccess("修改成功")
          getList()
        })
      } else {
        addPrompt(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功")
          getList()
        })
      }
      open.value = false
    }
  })
}

/** 点击tab切换菜单内容 */
function handleTabClick(){
  //   if (tab.name === 'tab2') {

  // } else if (tab.name === 'tab1') {

  // }
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
</script>


<style scoped>
.image-preview-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 8px 0;
}
.preview-img {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
}
.no-image-tip {
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
  border: 1px dashed #dcdfe6;
  color: #909399;
  font-size: 12px;
}
</style>