"""
启动前模型检查脚本 - 自动检测并下载缺失的词嵌入模型
"""
import os
import sys
from pathlib import Path

def check_embedding_model():
    """检查词嵌入模型是否存在"""
    print("\n[检查] 词嵌入模型...")
    
    # 可能的模型路径
    possible_paths = [
        "./models/AI-ModelScope/bge-small-zh-v1___5",
        "./models/AI-ModelScope/bge-small-zh-v1.5",
        "./models/BAAI/bge-small-zh-v1.5",
        "./models/bge-small-zh-v1.5",
    ]
    
    for model_path in possible_paths:
        full_path = Path(model_path)
        if full_path.exists() and (full_path / "config.json").exists():
            print(f"[OK] 找到词嵌入模型: {model_path}")
            return True, str(full_path.absolute())
    
    print("[警告] 未找到词嵌入模型")
    return False, None

def download_embedding_model():
    """下载词嵌入模型"""
    print("\n" + "=" * 60)
    print("开始下载词嵌入模型...")
    print("=" * 60)
    
    # 检查并安装 modelscope
    try:
        import modelscope
        print("[OK] modelscope 已安装")
    except ImportError:
        print("[INFO] 正在安装 modelscope...")
        print(f"[INFO] 当前 Python 版本: {sys.version}")
        print(f"[INFO] Python 路径: {sys.executable}")
        os.system(f'"{sys.executable}" -m pip install modelscope -i https://pypi.tuna.tsinghua.edu.cn/simple')
        try:
            import modelscope
        except ImportError:
            print("[ERROR] modelscope 安装失败")
            print("[提示] 请确保使用正确的 Python 环境")
            return False, None
    
    # 下载模型
    print("\n模型: BAAI/bge-small-zh-v1.5")
    print("来源: ModelScope (国内镜像)")
    print("目标目录: ./models")
    print("\n这可能需要几分钟时间，请耐心等待...\n")
    
    try:
        from modelscope import snapshot_download
        
        model_dir = snapshot_download(
            'AI-ModelScope/bge-small-zh-v1.5',
            cache_dir='./models'
        )
        
        print(f"\n[OK] 模型下载成功！")
        print(f"模型路径: {model_dir}")
        return True, model_dir
        
    except Exception as e:
        print(f"\n[ERROR] 下载失败: {e}")
        print("\n请尝试手动下载:")
        print("1. 访问 https://hf-mirror.com/BAAI/bge-small-zh-v1.5")
        print("2. 下载所有文件到本地目录")
        print("3. 修改配置文件指向本地路径")
        return False, None

def main():
    """主检查流程"""
    print("=" * 60)
    print("词嵌入模型检查工具")
    print("=" * 60)
    
    # 检查词嵌入模型
    embedding_ok, embedding_path = check_embedding_model()
    if not embedding_ok:
        print("\n是否现在下载词嵌入模型? (Y/n): ", end="")
        choice = input().strip().lower()
        if choice in ['', 'y', 'yes']:
            embedding_ok, embedding_path = download_embedding_model()
        else:
            print("[跳过] 词嵌入模型下载")
    
    # 总结
    print("\n" + "=" * 60)
    print("检查结果:")
    print("=" * 60)
    print(f"词嵌入模型: {'OK' if embedding_ok else 'FAIL'}")
    if embedding_ok and embedding_path:
        print(f"  路径: {embedding_path}")
    print("=" * 60)
    
    if embedding_ok:
        print("\n[OK] 词嵌入模型检查通过，可以启动服务！")
        return 0
    else:
        print("\n[警告] 词嵌入模型缺失，服务可能无法正常运行")
        print("请确保词嵌入模型已下载")
        return 1

if __name__ == "__main__":
    sys.exit(main())
