<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-left">
        <el-icon class="logo-icon" :size="28"><Reading /></el-icon>
        <span class="app-title">AI文档学习助手</span>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="32" :icon="UserFilled" />
            <span class="username">{{ username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 左侧菜单 -->
      <el-aside class="app-aside" width="240px">
        <el-menu
          :default-active="activeMenu"
          class="app-menu"
          router
          @select="handleMenuSelect"
        >
          <el-menu-item index="/documents">
            <el-icon><Folder /></el-icon>
            <span>文档管理</span>
          </el-menu-item>
          
          <el-menu-item index="/qa">
            <el-icon><ChatDotRound /></el-icon>
            <span>智能问答</span>
          </el-menu-item>

          <el-menu-item index="/exam">
            <el-icon><EditPen /></el-icon>
            <span>学习考试</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Reading, UserFilled, ArrowDown, User, Setting, SwitchButton,
  Folder, ChatDotRound, EditPen
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const username = ref('用户')

const activeMenu = computed(() => {
  const path = route.path
  // 文档详情页也高亮文档管理菜单
  if (path.startsWith('/document')) {
    return '/documents'
  }
  // 问答页面高亮智能问答
  if (path.startsWith('/qa')) {
    return '/qa'
  }
  // 考试页面高亮学习考试
  if (path.startsWith('/exam')) {
    return '/exam'
  }
  return path
})

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中...')
      break
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        localStorage.removeItem('token')
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}

const handleMenuSelect = (index: string) => {
  // 菜单选择处理
  console.log('Selected menu:', index)
}

onMounted(() => {
  // 可以从 localStorage 或 API 获取用户信息
  const userInfo = localStorage.getItem('userInfo')
  if (userInfo) {
    try {
      const user = JSON.parse(userInfo)
      username.value = user.username || user.email || '用户'
    } catch {
      username.value = '用户'
    }
  }
})
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;

  .app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    height: 60px;
    z-index: 1000;

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;

      .logo-icon {
        color: #fff;
        font-size: 28px;
      }

      .app-title {
        font-size: 20px;
        font-weight: 700;
        color: #fff;
        letter-spacing: 0.5px;
      }
    }

    .header-right {
      .user-info {
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        padding: 8px 16px;
        border-radius: 20px;
        transition: all 0.3s;

        &:hover {
          background: rgba(255, 255, 255, 0.15);
        }

        .username {
          color: #fff;
          font-size: 14px;
          font-weight: 500;
        }

        .el-icon {
          color: #fff;
        }
      }
    }
  }

  .main-container {
    flex: 1;
    overflow: hidden;

    .app-aside {
      background: #fff;
      box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
      overflow-y: auto;

      .app-menu {
        border-right: none;
        padding: 12px 0;

        :deep(.el-menu-item) {
          margin: 4px 12px;
          border-radius: 8px;
          height: 48px;
          line-height: 48px;

          &:hover {
            background: #f5f7fa;
          }

          &.is-active {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            color: #667eea;
            font-weight: 600;

            &::before {
              content: '';
              position: absolute;
              left: 0;
              top: 50%;
              transform: translateY(-50%);
              width: 3px;
              height: 24px;
              background: #667eea;
              border-radius: 0 2px 2px 0;
            }
          }

          .el-icon {
            font-size: 18px;
          }
        }

        :deep(.el-sub-menu) {
          .el-sub-menu__title {
            margin: 4px 12px;
            border-radius: 8px;
            height: 48px;
            line-height: 48px;

            &:hover {
              background: #f5f7fa;
            }

            .el-icon {
              font-size: 18px;
            }
          }

          .el-menu-item {
            margin: 4px 12px 4px 24px;
            min-width: auto;
          }
        }
      }
    }

    .app-main {
      background: #f0f2f5;
      overflow-y: auto;
      padding: 0;
    }
  }
}

// 滚动条样式
:deep(.app-aside::-webkit-scrollbar) {
  width: 6px;
}

:deep(.app-aside::-webkit-scrollbar-thumb) {
  background: #dcdfe6;
  border-radius: 3px;

  &:hover {
    background: #c0c4cc;
  }
}

:deep(.app-main::-webkit-scrollbar) {
  width: 8px;
}

:deep(.app-main::-webkit-scrollbar-thumb) {
  background: #dcdfe6;
  border-radius: 4px;

  &:hover {
    background: #c0c4cc;
  }
}
</style>

