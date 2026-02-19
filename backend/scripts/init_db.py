"""
数据库初始化脚本
支持 MySQL 和 SQLite
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.core.config import settings

# 导入所有模型
from app.models.user import User
from app.models.document import Document, DocumentSection, DocumentChunk
from app.models.question import Question
from app.models.exam import Exam, ExamQuestion
from app.models.answer import AnswerRecord
from app.models.qa import QARecord


def init_db():
    """创建所有表"""
    print("=" * 50)
    print("开始初始化数据库...")
    print(f"数据库类型: {settings.database_url.split(':')[0]}")
    print("=" * 50)
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("\n✅ 数据库表创建成功！")
        
        # 显示创建的表
        print("\n已创建的表:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        
        print("\n" + "=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    init_db()
