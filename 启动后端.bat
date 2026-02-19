@echo off
cd /d "%~dp0\backend"
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Checking dependencies...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet

echo Starting backend server...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

