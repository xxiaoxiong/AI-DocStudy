"""
快速创建管理员用户
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin():
    """创建管理员用户"""
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print("⚠️  管理员用户已存在，正在更新密码...")
            # 更新密码
            existing.password_hash = get_password_hash("admin123")
            db.commit()
            print("✅ 管理员密码已更新")
            print("   用户名: admin")
            print("   密码: admin123")
            return
        
        # 创建新管理员
        password_hash = get_password_hash("admin123")
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=password_hash,
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("✅ 管理员用户创建成功")
        print("   用户名: admin")
        print("   密码: admin123")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

