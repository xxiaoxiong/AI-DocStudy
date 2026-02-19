"""
创建测试用户
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.repositories.user import UserRepository
from app.models.user import User


def create_test_user():
    """创建测试用户"""
    db = SessionLocal()
    try:
        user_repo = UserRepository(User, db)
        
        # 检查是否已存在
        existing = user_repo.get_by_username("admin")
        if existing:
            print("测试用户 'admin' 已存在")
            return
        
        # 创建测试用户
        user = user_repo.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        
        print(f"✅ 测试用户创建成功:")
        print(f"   用户名: {user.username}")
        print(f"   邮箱: {user.email}")
        print(f"   密码: admin123")
        
    except Exception as e:
        print(f"❌ 创建测试用户失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()

