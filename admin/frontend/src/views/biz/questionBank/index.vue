<template>
  <div class="app-container">
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

            <el-table v-loading="loading" :data="question_list" @selection-change="handleSelectionChange">
              <el-table-column type="selection" width="50" align="center" />
              <el-table-column label="序号" align="center" key="index" width="120">
                <template #default="scope">
                  <span>{{ (queryParams.pageNum - 1) * queryParams.pageSize + scope.$index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column label="题目唯一编号" align="center" key="code" prop="code" :show-overflow-tooltip="true"  />
              <el-table-column 
                  label="题目标签" 
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
              <el-table-column label="题目内容" align="center" key="content" prop="content" :show-overflow-tooltip="true"/>
              <el-table-column label="题目难度" align="center" key="difficulty" prop="difficulty">
                <template #default="scope" >
                    <el-tag 
                    size="small"
                    :type="getDifficultyTagType(scope.row.difficulty)">
                        {{ getDifficultyLabel(scope.row.difficulty) }}
                  </el-tag>
                </template>
              </el-table-column>
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
                  <el-tooltip content="修改" placement="top">
                    <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)"  v-hasRole="['admin']"></el-button>
                  </el-tooltip>
                  <el-tooltip content="删除" placement="top">
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

    <!-- 添加或修改题目配置对话框 -->
    <el-dialog :title="title" v-model="open" width="700px" append-to-body>
      <el-form :model="form" :rules="rules" ref="questionRef">

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="题目唯一编号" prop="code" label-width="auto">
              <el-input v-model="form.code" placeholder="请输入编号" />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="标签" prop="tags" label-width="auto">
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

        <el-row gutter="12">
          <el-col :span="12">
            <el-form-item label="是否高频考点" prop="is_high_frequency" label-width="auto">
              <el-select v-model="form.is_high_frequency" placeholder="请选择">
                <el-option v-for="dict in sys_yes_no" :key="dict.value" :label="dict.label" :value="dict.value"></el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="分值" prop="score" label-width="auto">
              <el-input type="number" v-model="form.score" placeholder="请输入分值" maxlength="30"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row gutter="12">
          <el-col :span="12">
            <el-form-item label="难度" prop="difficulty" label-width="auto">
              <el-select v-model="form.difficulty" placeholder="请选择">
                <el-option v-for="dict in question_difficulty" :key="dict.value" :label="dict.label" :value="dict.value"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="建议完成时间" prop="finish_time" label-width="auto">
                <el-input type="number" v-model="form.finish_time" placeholder="请输入建议完成时间(单位：分钟)" min="1">
                 <template #append>分钟</template>
                </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="题目类型" prop="type" label-width="auto">
              <el-select v-model="form.type" placeholder="请选择">
                <el-option v-for="dict in question_type" :key="dict.value" :label="dict.label" :value="dict.value"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row>
          <el-col>
            <el-form-item label="题目内容" prop="content"  label-width="auto">
              <el-input  type="textarea" v-model="form.content" placeholder="请输入内容" show-word-limit/>
            </el-form-item>
          </el-col>
        </el-row>

        <div v-if="(form.type === '1' || form.type === '2') && !hasSub">
          <!-- 用于校验正确选项数量的隐藏表单项 -->
          <el-form-item prop="option_list" style="display: none;"></el-form-item>

          <el-form-item label="添加选项">
            <span>
              <el-icon @click="handleAddOption" style="cursor: pointer; color: #f56c6c;"><Plus /></el-icon>
            </span>
          </el-form-item>

          <template v-for="(item, index) in form.option_list" :key="index">
            <div>
              <el-form-item :label="'选项' + String.fromCharCode(65 + index)">
                <span class="icon-wrap">
                  <el-icon @click="handleRemoveOption(index)" style="cursor: pointer; color: #f56c6c;">
                      <Minus />
                  </el-icon>
                </span>
              </el-form-item>

              <el-row>
                  <el-col>
                    <el-form-item label="选项内容" :prop="`detailOptList[${index}].option_content`" label-width="auto">
                      <el-input  type="textarea" v-model="item.option_content" placeholder="请输入内容" show-word-limit/>
                    </el-form-item>
                  </el-col>
              </el-row>
              <el-row>
                  <el-col>
                    <el-form-item label="是否正确选项" :prop="`detailOptList[${index}].is_correct`" label-width="auto">
                        <el-radio-group v-model="item.is_correct">
                          <el-radio v-for="dict in sys_yes_no" :key="dict.value" :value="dict.value">{{ dict.label }}</el-radio>
                        </el-radio-group>
                    </el-form-item>
                  </el-col>
              </el-row>
            </div>
          </template>
        </div>

        <el-row v-if="!hasSub">
          <el-col>
            <el-form-item label="参考答案" prop="answer" label-width="auto">
              <el-input  type="textarea" v-model="form.answer" placeholder="请输入内容" show-word-limit/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="相关图片" label-width="auto">
              <el-upload
                v-model:file-list="form.img_list"  
                :data="uploadData"
                :action=imgUploadUrl  
                :on-preview="picturePreview"
                :on-remove="pictureRemove"
                :headers="reqHeader"
                :on-success="handleSuccess"
                list-type="picture-card"         
                multiple                          
                accept="image/*"                  
              >
                  <el-icon><Plus /></el-icon>
              </el-upload>
              <el-dialog v-model="dialogVisible" width="80%">
                <img width="100%" :src="dialogImg" alt="图片预览" />
              </el-dialog>
            </el-form-item>
          </el-col>
        </el-row>

      <div>
        <el-form-item label="添加子题目">
          <span>
            <el-icon @click="handleAddDetail" style="cursor: pointer; color: #f56c6c;"><Plus /></el-icon>
          </span>
        </el-form-item>

        <template v-for="(item, index) in form.detailList">
          <div>
            <el-form-item :label="'子题目' + (index + 1)">
              <span class="icon-wrap">
                <el-icon @click="handleRemoveDetail(index)" style="cursor: pointer; color: #f56c6c;">
                    <Minus />
                </el-icon>
              </span>
            </el-form-item>

            <el-row>
                <el-col>
                  <el-form-item label="题目内容" :prop="`detailList[${index}].question`" label-width="auto">
                    <el-input  type="textarea" v-model="item.question" placeholder="请输入内容" show-word-limit/>
                  </el-form-item>
                </el-col>
            </el-row>

            <el-row gutter="12">
              <el-col :span="12">
                <el-form-item label="分值" :prop="`detailList[${index}].score`" label-width="auto">
                  <el-input type="number" v-model="item.score" placeholder="请输入分值" maxlength="30"/>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row>
                <el-col>
                  <el-form-item label="参考答案" :prop="`detailList[${index}].answer`" label-width="auto">
                    <el-input  type="textarea" v-model="item.answer" placeholder="请输入内容" show-word-limit/>
                  </el-form-item>
                </el-col>
            </el-row>

            <div v-if="form.type === '1' || form.type === '2'" >
              <el-form-item label="添加选项">
                <span>
                  <el-icon @click="handleAddDetailOption(index)" style="cursor: pointer; color: #f56c6c;"><Plus /></el-icon>
                </span>
              </el-form-item>

              <template v-for="(item, opt_index) in item.option_list" :key="opt_index">
                <div>
                  <el-form-item :label="'选项' + String.fromCharCode(65 + opt_index)">
                    <span class="icon-wrap">
                      <el-icon @click="handleRemoveDetailOption(opt_index,index)" style="cursor: pointer; color: #f56c6c;">
                          <Minus />
                      </el-icon>
                    </span>
                  </el-form-item>

                  <el-row>
                      <el-col>
                        <el-form-item label="选项内容" :prop="`detailList[${index}].option_list[${opt_index}].option_content`" label-width="auto">
                          <el-input  type="textarea" v-model="item.option_content" placeholder="请输入内容" show-word-limit/>
                        </el-form-item>
                      </el-col>
                  </el-row>
                  <el-row>
                      <el-col>
                        <el-form-item label="是否正确选项" :prop="`detailList[${index}].option_list[${opt_index}].is_correct`" label-width="auto">
                            <el-radio-group v-model="item.is_correct">
                              <el-radio v-for="dict in sys_yes_no" :key="dict.value" :value="dict.value">{{ dict.label }}</el-radio>
                            </el-radio-group>
                        </el-form-item>
                      </el-col>
                  </el-row>
                </div>
              </template>
            </div>            
          </div>
        </template>
      </div>

        <el-row>
          <el-col :span="24">
            <el-form-item label="题目备注" label-width="auto">
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
import { changeQuestionStatus, listQuestion, delQuestion, getQuestion, updateQuestion, addQuestion } from "@/api/biz/question_bank"
import { getTagTree } from "@/api/biz/tag"
import { Splitpanes, Pane } from "splitpanes"
import "splitpanes/dist/splitpanes.css"
import { filterReadOnlyFields } from "@/utils/hte"
import {checkPermi} from "@/utils/permission"
const appStore = useAppStore()
const { proxy } = getCurrentInstance()
const { sys_normal_disable, sys_yes_no,question_difficulty,question_type } = proxy.useDict("sys_normal_disable", "sys_yes_no","question_difficulty","question_type")
import { ElInput } from 'element-plus'
import { requiredAndTrim } from "@/utils/validators"
import { Plus,Minus } from '@element-plus/icons-vue'
import { getToken } from '@/utils/auth'
import { ref } from 'vue'
const question_list = ref([])
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
// 新增标记：是否处于修改题目状态
const isUpdating = ref(false)
/** 验证正确选项数量 */
const validateCorrectOptionCount = (rule, value, callback) => {
  // 只在类型为1或2且没有子项时校验
  if ((form.value.type === '1' || form.value.type === '2') && !hasSub.value) {
    // 统计正确选项数量
    const correctCount = form.value.option_list.filter(item => item.is_correct === '1').length;

    // 单选：必须有且仅有1个正确选项
    if (form.value.type === '1') {
      if (correctCount === 0) {
        callback(new Error('单选题必须选择一个正确选项'));
      } else if (correctCount > 1) {
        callback(new Error('单选题只能有一个正确选项'));
      } else {
        callback();
      }
    }
    // 多选：至少2个正确选项
    else if (form.value.type === '2') {
      if (correctCount < 2) {
        callback(new Error('多选题至少选择两个正确选项'));
      } else {
        callback();
      }
    } else {
      callback();
    }
  } else {
    callback();
  }
}

const data = reactive({
  form: {
    id: undefined,
    code: undefined,
    tags: [],
    is_high_frequency: undefined,
    score: undefined,
    difficulty: undefined,
    finish_time: undefined,
    type: undefined,
    content: undefined,
    answer: undefined,
    img_list: [],
    option_list: [], // 普通选项列表
    detailList: [], // 子题目列表（必须初始化空数组！）
    has_sub_question: "0", // 子题目标识（默认无）
    remark: undefined,
    status: "1"
  },
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    content: undefined,
    code: undefined,
    status: undefined,
  },
  rules: {
    code: requiredAndTrim("请输入题目编码"),
    tags: [{required:true,trigger:"blur",message:"请选择标签"}],
    score: [{required:true,trigger:"blur",message:"请输入分值"}],
    difficulty: [{required:true,trigger:"blur",message:"请选择难度"}],
    type: [{required:true,trigger:"blur",message:"请选择题目类型"}],
    content: requiredAndTrim("请输入题目内容"),
    answer: requiredAndTrim("请输入参考答案"),
    status: [{ required: true, trigger: "change", message: "请选择审核状态" }],
    option_list: [
      {
        validator: validateCorrectOptionCount,
        trigger: ['change', 'blur']
      }
    ]
  }
})
const dialogVisible = ref(false)
let dialogImg = ref("")
const { queryParams, form, rules } = toRefs(data)
//图片上传路径
const imgUploadUrl= import.meta.env.VITE_APP_BASE_URL + "/api/file/"
const uploadData = reactive({module_name:"images"})
const reqHeader = reactive({ Authorization: 'Bearer ' + getToken() })

const hasSub = ref(false)

onMounted(() => {
  getList()
  showTagTree()
})

/** 查询题目列表 */
function getList() {
  loading.value = true
  listQuestion(proxy.addDateRange(queryParams.value, dateRange.value)).then(res => {
    loading.value = false
    question_list.value = res.data
    // console.log("传来后保存的题目数据",question_list.value)
    hasSub.value = res.data.has_sub_question && res.data.has_sub_question == '1' ? true:false
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
    const index = question_list.value.findIndex(item => item.id === row.id) + 1 // 找到行在列表中的索引
    proxy.$modal.confirm(`是否确认删除序号为"${index}"的数据项？`).then(function () {
      return delQuestion(row.id) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
  // 2. 批量删除：保持原有逻辑
  else if (ids.value.length > 0) {
    proxy.$modal.confirm(`是否确认删除选中的${ids.value.length}条数据项？`).then(function () {
      return delQuestion(ids.value) 
    }).then(() => {
      getList()
      proxy.$modal.msgSuccess("删除成功")
    }).catch(() => {})
  } 
}

/** 题目状态修改  */
function handleStatusChange(row) {
  let text = row.status === "0" ? "停用" : "启用"
  proxy.$modal.confirm('确认要' + text + '"' + row.code + '"题目吗?').then(function () {
    return changeQuestionStatus(row.id, row.status)
  }).then(() => {
    proxy.$modal.msgSuccess(text + "成功")
  }).catch(function () {
    row.status = row.status === "0" ? "1" : "0"
  })
}

/** 选择条数  */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id)
  single.value = selection.length !== 1 
  multiple.value = selection.length === 0
}

/** 重置操作表单 */
function reset() {
  form.value = {
    id: undefined,
    content: undefined,
    code: undefined,
    tag: undefined,
    is_high_frequency: undefined,
    status: "1",
    remark: undefined,
    score: undefined,
    answer:undefined,
    difficulty: undefined,
    finish_time: undefined,
    img_list: [],
    detailList:[],
    option_list:[],
    answer:null,
  }
  hasSub.value = false
  proxy.resetForm("questionRef")
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
  title.value = "添加题目"
  // console.log(question_difficulty)
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset()
  isUpdating.value = true // 标记为修改态
  form.value = JSON.parse(JSON.stringify(row))
  const tagIds = form.value.tags.map(tag => tag.id)
  form.value.tags = tagIds
  hasSub.value = row.has_sub_question && row.has_sub_question == '1'
  open.value = true
  title.value = "修改题目"
  // 修改完成后关闭标记（nextTick确保watch已执行）
  nextTick(() => {
    isUpdating.value = false
  })
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["questionRef"].validate(valid => {
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
        updateQuestion(payload).then(response => {
          proxy.$modal.msgSuccess("修改成功")
          open.value = false
          getList()
        })
      } else {
        addQuestion(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功")
          open.value = false
          getList()
        })
      }
    }
  })
}

// 获取标签树
function showTagTree(){
  getTagTree().then(res => {
    tag_list.value = res.data
  })
}

/**根据难度值获取类型 */
function getDifficultyTagType(value) { 
  const item = question_difficulty.value.find(item=>item.value === value)
  return item ? item.elTagType : ''
}

/** 根据难度值获取标签值 */
function getDifficultyLabel(value){
  const item = question_difficulty.value.find(item=>item.value===value)
  return item ? item.label : ''
}

/** 图片预览 */
function picturePreview(file){
  // console.log(file)
  dialogImg = file.url
  dialogVisible.value = true
}

/** 图片上传成功 */
const handleSuccess = (response, file, fileList) => {
  // 替换当前文件的 url 为服务器永久路径
  file.url = import.meta.env.VITE_APP_BASE_URL + '/media/' + response.data
}

/** 添加子题目 */
const handleAddDetail = () =>{
  hasSub.value = true 
  form.value.detailList.push({
    question:"",
    score:"",
    answer:"",
    option_list:[],
  })
  form.value.has_sub_question = "1"
}

/** 移除子题目 */
const handleRemoveDetail = (index) =>{
  form.value.detailList.splice(index,1)
  if(form.value.detailList.length === 0){
    form.value.has_sub_question = "0"
    hasSub.value = false
  }
}

/** 添加选项 */
const handleAddOption = () =>{
  form.value.option_list.push({
    option_content:"",
    is_correct:"0",
    answer:"",
  })
  // 触发校验
  formRef.value.validateField('option_list');
}

/** 移除选项 */
const handleRemoveOption = (index) =>{
  form.value.option_list.splice(index,1)
  // 触发校验
  formRef.value.validateField('option_list');
}

/** 添加子题目选项 */
const handleAddDetailOption = (index) =>{
  form.value.detailList[index].option_list.push({
    option_content:"",
    is_correct:"0",
    answer:"",
  })
}

/** 移除子题目选项 */
const handleRemoveDetailOption = (index,detailIndex) =>{
  // console.log(index,detailIndex)
  // console.log(form.value.detailList)
  // console.log(form.value.detailList[detailIndex])
  // console.log(form.value.detailList[detailIndex].option_list)
  form.value.detailList[detailIndex].option_list.splice(index,1)
}

/** 处理题目状态改变 */
watch(
  () => form.value.type,
  (newVal, oldVal) => {
    if (newVal === oldVal || isUpdating.value) return; // 修改态跳过
    handleTypeChange(newVal, oldVal);
  },
  { immediate: false }
)

// 处理题型变化
const handleTypeChange = (newVal, oldVal) => {
  // 由非选择切换到选择
  if ((newVal === '1' || newVal === '2') && oldVal !== '1' && oldVal !== '2') {
    form.value.detailList = []
    // form.value.answer = null
    hasSub.value = false
  }
  // 由选择切换到非选择
  else if ((oldVal === '1' || oldVal === '2') && (newVal !== '1' && newVal !== '2') ) {
    form.value.option_list = []
    form.value.detailList = []
    hasSub.value = false
  }
}
</script>

<style scoped lang="scss">
  .icon-wrap {
  text-align: right;
  i {
    cursor: pointer;
  }
  .el-icon-plus {
    color: #409eff;
  }
  .el-icon-minus {
    color: red;
  }
}
</style>
