@echo off
cd /d "%~dp0\backend"
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo Checking models...
echo ========================================
python check_models.py
if errorlevel 1 (
    echo.
    echo [WARNING] Model check failed or incomplete
    echo Press any key to continue anyway, or Ctrl+C to exit...
    pause >nul
)

echo.
echo Checking dependencies...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet

echo.
echo Starting backend server...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

