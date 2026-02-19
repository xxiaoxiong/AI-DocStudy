"""
向量化功能测试脚本
用于验证文档向量化过程是否正常工作
"""
import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_embedding_service():
    """测试Embedding服务"""
    print("=" * 60)
    print("测试1: Embedding服务")
    print("=" * 60)
    
    try:
        from app.services.ai.embedding import embedding_service
        
        # 测试单个文本
        print("\n1.1 测试单个文本向量化...")
        text = "这是一个测试文本"
        embedding = embedding_service.embed_text(text)
        print(f"✓ 成功生成向量，维度: {len(embedding)}")
        
        # 测试批量文本
        print("\n1.2 测试批量文本向量化...")
        texts = [
            "第一段文本内容",
            "第二段文本内容",
            "",  # 空文本
            "第四段文本内容"
        ]
        embeddings = embedding_service.embed_batch(texts)
        print(f"✓ 成功生成 {len(embeddings)} 个向量")
        
        # 验证数量匹配
        if len(embeddings) == len(texts):
            print("✓ 向量数量与输入文本数量匹配")
        else:
            print(f"✗ 向量数量不匹配: 期望 {len(texts)}, 实际 {len(embeddings)}")
            return False
        
        # 验证维度一致
        dims = [len(emb) for emb in embeddings]
        if len(set(dims)) == 1:
            print(f"✓ 所有向量维度一致: {dims[0]}")
        else:
            print(f"✗ 向量维度不一致: {set(dims)}")
            return False
        
        # 检查空文本的向量
        if all(v == 0.0 for v in embeddings[2]):
            print("✓ 空文本正确使用零向量")
        else:
            print("✗ 空文本未使用零向量")
            return False
        
        print("\n✓ Embedding服务测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ Embedding服务测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_chroma_storage():
    """测试Chroma存储"""
    print("\n" + "=" * 60)
    print("测试2: Chroma向量存储")
    print("=" * 60)
    
    try:
        import tempfile
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        from app.services.ai.embedding import embedding_service
        
        # 使用临时目录避免与运行中的后端服务器锁定的sqlite3冲突
        tmp_dir_obj = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        tmp_dir = tmp_dir_obj.name
        test_client = None
        try:
            test_client = chromadb.PersistentClient(
                path=tmp_dir,
                settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
            )
            collection_name = "doc_99999"
            test_doc_id = 99999
            chunks = [
                {
                    'id': 1,
                    'content': '这是第一个测试分块的内容',
                    'metadata': {'chunk_index': 0, 'document_id': test_doc_id}
                },
                {
                    'id': 2,
                    'content': '这是第二个测试分块的内容',
                    'metadata': {'chunk_index': 1, 'document_id': test_doc_id}
                }
            ]

            # 生成向量
            print("\n2.1 生成测试向量...")
            texts = [chunk['content'] for chunk in chunks]
            embeddings = embedding_service.embed_batch(texts)
            print(f"✓ 生成了 {len(embeddings)} 个向量")

            # 清理旧数据
            print("\n2.2 清理旧测试数据...")
            try:
                test_client.delete_collection(collection_name)
                print("✓ 清理完成")
            except Exception:
                print("✓ 无需清理")

            # 存储到Chroma
            print("\n2.3 存储向量到Chroma...")
            collection = test_client.get_or_create_collection(
                name=collection_name,
                metadata={"document_id": test_doc_id}
            )
            ids = [str(chunk['id']) for chunk in chunks]
            documents = [chunk['content'] for chunk in chunks]
            metadatas = [chunk.get('metadata', {}) for chunk in chunks]
            collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
            print("✓ 存储成功")

            # 验证存储
            print("\n2.4 验证存储结果...")
            count = collection.count()
            if count == len(chunks):
                print(f"✓ 存储数量正确: {count}")
            else:
                print(f"✗ 存储数量不匹配: 期望 {len(chunks)}, 实际 {count}")
                return False

            # 测试检索
            print("\n2.5 测试向量检索...")
            query_embedding = embedding_service.embed_text("测试分块")
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=2,
                include=["documents", "metadatas", "distances"]
            )
            if results['ids'] and len(results['ids'][0]) > 0:
                print(f"✓ 检索成功，返回 {len(results['ids'][0])} 个结果")
                for i in range(len(results['ids'][0])):
                    print(f"  结果 {i+1}: {results['documents'][0][i][:30]}... (距离: {results['distances'][0][i]:.4f})")
            else:
                print("✗ 检索失败，未返回结果")
                return False

            # 清理测试数据
            print("\n2.6 清理测试数据...")
            test_client.delete_collection(collection_name)
            print("✓ 清理完成")
        finally:
            del test_client
            tmp_dir_obj.cleanup()
        
        print("\n✓ Chroma存储测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ Chroma存储测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_document_chunking():
    """测试文档分块"""
    print("\n" + "=" * 60)
    print("测试3: 文档分块")
    print("=" * 60)
    
    try:
        from app.services.document.processor import DocumentProcessor
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        processor = DocumentProcessor(db)
        
        # 测试正常文本
        print("\n3.1 测试正常文本分块...")
        text = """第一段内容。这是一个测试段落。

第二段内容。这是另一个测试段落。

第三段内容。这是第三个测试段落。"""
        
        chunks = processor._chunk_document(999999, text)
        if chunks:
            print(f"✓ 成功生成 {len(chunks)} 个分块")
            for i, chunk in enumerate(chunks):
                print(f"  分块 {i}: {len(chunk['content'])} 字符")
        else:
            print("✗ 分块失败")
            return False
        
        # 测试空文本
        print("\n3.2 测试空文本分块...")
        empty_chunks = processor._chunk_document(999999, "")
        if not empty_chunks:
            print("✓ 空文本正确返回空列表")
        else:
            print("✗ 空文本应返回空列表")
            return False
        
        db.close()
        print("\n✓ 文档分块测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ 文档分块测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("开始向量化功能测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("Embedding服务", test_embedding_service()))
    results.append(("Chroma存储", test_chroma_storage()))
    results.append(("文档分块", test_document_chunking()))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！向量化功能正常")
    else:
        print("✗ 部分测试失败，请检查错误信息")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

