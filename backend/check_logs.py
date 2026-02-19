from app.core.database import SessionLocal
from sqlalchemy import text
import json

db = SessionLocal()

# 查询最新文档的处理日志
result = db.execute(text('SELECT status, progress, current_step, logs, error_message FROM document_process_logs WHERE document_id = 6 ORDER BY id DESC LIMIT 1'))
row = result.fetchone()

if row:
    print('Status:', row[0])
    print('Progress:', row[1])
    print('Current Step:', row[2])
    print('Error:', row[4])
    print('\n=== 处理日志 ===')
    
    if row[3]:
        logs_data = row[3]
        if isinstance(logs_data, str):
            logs = json.loads(logs_data)
        else:
            logs = logs_data
        
        for log in logs[-30:]:  # 显示最后30条日志
            if isinstance(log, dict):
                print(f"{log.get('time', '')} [{log.get('level', '')}] {log.get('message', '')}")
                if log.get('details'):
                    print(f"  详情: {log.get('details')}")
            else:
                print(log)
else:
    print('没有找到处理日志')

db.close()

