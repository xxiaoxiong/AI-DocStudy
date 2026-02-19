"""
检查数据库中的用户数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("检查数据库用户数据")
print("=" * 60)

try:
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash, verify_password
    
    db = SessionLocal()
    
    # 查询所有用户
    users = db.query(User).all()
    print(f"\n找到 {len(users)} 个用户:")
    
    for user in users:
        print(f"\n用户: {user.username}")
        print(f"  - ID: {user.id}")
        print(f"  - Email: {user.email}")
        print(f"  - Role: {user.role}")
        print(f"  - 密码哈希长度: {len(user.password_hash) if user.password_hash else 0}")
        print(f"  - 密码哈希前20字符: {user.password_hash[:20] if user.password_hash else 'None'}")
        
        # 测试密码验证
        if user.username == "admin":
            print(f"\n  测试admin密码验证:")
            test_passwords = ["admin123", "Admin123", "123456"]
            for pwd in test_passwords:
                try:
                    result = verify_password(pwd, user.password_hash)
                    print(f"    - 密码 '{pwd}': {'✅ 正确' if result else '❌ 错误'}")
                except Exception as e:
                    print(f"    - 密码 '{pwd}': ❌ 验证失败 - {str(e)[:50]}")
    
    db.close()
    
    # 测试生成新的密码哈希
    print(f"\n" + "=" * 60)
    print("测试生成新密码哈希:")
    print("=" * 60)
    
    test_password = "admin123"
    print(f"\n原始密码: {test_password}")
    print(f"密码长度: {len(test_password)} 字符")
    print(f"密码字节数: {len(test_password.encode('utf-8'))} 字节")
    
    try:
        new_hash = get_password_hash(test_password)
        print(f"\n✅ 新哈希生成成功")
        print(f"哈希长度: {len(new_hash)}")
        print(f"哈希值: {new_hash}")
        
        # 验证新哈希
        verify_result = verify_password(test_password, new_hash)
        print(f"\n验证新哈希: {'✅ 成功' if verify_result else '❌ 失败'}")
        
    except Exception as e:
        print(f"\n❌ 生成哈希失败: {e}")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)




