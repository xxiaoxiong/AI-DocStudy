from app.core.database import SessionLocal
from sqlalchemy import text
import json

db = SessionLocal()

# 查询文档8的数据
result = db.execute(text('SELECT key_points, common_questions, summary FROM documents WHERE id = 8'))
row = result.fetchone()

print(f'key_points type: {type(row[0])}')
print(f'key_points value: {row[0]}')
print(f'\ncommon_questions type: {type(row[1])}')
print(f'common_questions value: {row[1]}')
print(f'\nsummary length: {len(row[2]) if row[2] else 0}')

# 尝试解析
if row[0]:
    try:
        kp = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        print(f'\nParsed key_points: {kp}')
        print(f'key_points count: {len(kp)}')
    except Exception as e:
        print(f'\nFailed to parse key_points: {e}')

if row[1]:
    try:
        cq = json.loads(row[1]) if isinstance(row[1], str) else row[1]
        print(f'\nParsed common_questions: {cq}')
        print(f'common_questions count: {len(cq)}')
    except Exception as e:
        print(f'\nFailed to parse common_questions: {e}')

db.close()

