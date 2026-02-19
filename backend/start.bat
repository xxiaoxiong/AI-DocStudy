@echo off
chcp 65001 >nul

echo ========================================
echo   Backend Quick Start
echo ========================================
echo.

echo [1/3] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)
echo OK: Virtual environment activated
echo.

echo [2/3] Installing dependencies...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo OK: Dependencies installed
echo.

echo [3/3] Starting backend server...
echo.
echo ========================================
echo   Backend server starting...
echo   URL: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000



