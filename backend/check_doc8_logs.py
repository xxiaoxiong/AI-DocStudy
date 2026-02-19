from app.core.database import SessionLocal
from sqlalchemy import text
import json

db = SessionLocal()

# 查询文档8的处理日志
result = db.execute(text('SELECT logs FROM document_process_logs WHERE document_id = 8 ORDER BY id DESC LIMIT 1'))
row = result.fetchone()

if row and row[0]:
    try:
        logs_str = row[0]
        # 处理可能的双重JSON编码
        if logs_str.startswith('"'):
            logs_str = json.loads(logs_str)
        
        logs = json.loads(logs_str) if isinstance(logs_str, str) else logs_str
        
        print(f'Total logs: {len(logs)}')
        print('\n=== Processing Logs ===\n')
        
        for log in logs:
            level = log.get('level', 'info')
            message = log.get('message', '')
            time = log.get('time', '')
            
            # 重点关注AI相关的日志
            if 'AI' in message or 'ai' in message.lower() or '分析' in message:
                print(f'[{time}] [{level.upper()}] {message}')
                if log.get('details'):
                    print(f'  Details: {log.get("details")}')
                print()
    except Exception as e:
        print(f'Error parsing logs: {e}')
        import traceback
        traceback.print_exc()
else:
    print('No logs found')

db.close()

