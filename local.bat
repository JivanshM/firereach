@echo off
title FireReach - Autonomous Outreach Engine
color 0C

echo.
echo  ========================================
echo    FIREREACH - Autonomous Outreach Engine
echo    Rabbitt AI Ecosystem
echo  ========================================
echo.

:: Check if .env exists
if not exist "backend\.env" (
    echo [!] backend\.env not found!
    echo [!] Creating from .env.example...
    copy backend\.env.example backend\.env
    echo.
    echo  YOU MUST edit backend\.env with your API keys before running:
    echo.
    echo    GEMINI_API_KEY    - https://aistudio.google.com/apikey
    echo    FINNHUB_API_KEY   - https://finnhub.io/register
    echo    GNEWS_API_KEY     - https://gnews.io/
    echo    RESEND_API_KEY    - https://resend.com/signup
    echo.
    echo  Open backend\.env in your editor, add the keys, then run this again.
    pause
    exit /b 1
)

:: Check for required keys in .env
findstr /C:"your_gemini_api_key_here" backend\.env >nul 2>&1
if %errorlevel%==0 (
    echo [!] WARNING: GEMINI_API_KEY is still set to placeholder!
    echo [!] Edit backend\.env with your real API keys first.
    echo.
    pause
    exit /b 1
)

echo [1/3] Installing backend dependencies...
cd backend
pip install -r requirements.txt -q 2>nul
cd ..

echo [2/3] Installing frontend dependencies...
cd frontend
call npm install --silent 2>nul
cd ..

echo [3/3] Starting servers...
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo.
echo  Press Ctrl+C in either window to stop.
echo.

:: Start backend in a new window
start "FireReach Backend" cmd /k "cd /d %~dp0backend && python main.py"

:: Wait a moment for backend to boot
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
start "FireReach Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

:: Wait then open browser
timeout /t 4 /nobreak >nul
start http://localhost:5173

echo.
echo  FireReach is running! Browser should open shortly.
echo  Close this window or press any key to exit this launcher.
pause >nul
