<template>
  <el-dialog
    v-model="visible"
    title="上传文档"
    width="500px"
    :close-on-click-modal="false"
  >
    <el-form :model="form" label-width="80px">
      <el-form-item label="文档标题">
        <el-input
          v-model="form.title"
          placeholder="不填写则使用文件名"
          clearable
        />
      </el-form-item>
      
      <el-form-item label="选择文件">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          accept=".pdf,.docx,.doc,.txt,.md"
          drag
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 PDF、Word、TXT、Markdown 格式，文件大小不超过 50MB
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        type="primary"
        :loading="uploading"
        :disabled="!selectedFile"
        @click="handleSubmit"
      >
        上传
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadInstance, UploadRawFile } from 'element-plus'
import { useDocument } from '../composables/useDocument'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const { uploading, handleUpload } = useDocument()

const uploadRef = ref<UploadInstance>()
const form = ref({
  title: ''
})
const selectedFile = ref<File | null>(null)

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const handleSubmit = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  try {
    await handleUpload(selectedFile.value, form.value.title || undefined)
    emit('success')
    handleClose()
  } catch (error) {
    // 错误已在 composable 中处理
  }
}

const handleClose = () => {
  form.value.title = ''
  selectedFile.value = null
  uploadRef.value?.clearFiles()
  visible.value = false
}
</script>

<style scoped lang="scss">
.el-upload__tip {
  color: #999;
  font-size: 12px;
  margin-top: 8px;
}
</style>



