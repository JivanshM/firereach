@echo off
:: Fix working directory to bat file location (critical for double-click)
cd /d "%~dp0"

title ReachAI - Autonomous Outreach Engine
color 0C

echo.
echo  ========================================
echo    REACHAI - Autonomous Outreach Engine
echo    Powered by AI
echo  ========================================
echo.

:: Check if backend .env exists
if not exist "backend\.env" (
    echo [!] backend\.env not found!
    echo [!] Creating from .env.example...
    copy "backend\.env.example" "backend\.env"
    echo.
    echo  YOU MUST edit backend\.env with your API keys before running:
    echo.
    echo    AIML_API_KEY      - https://aimlapi.com/
    echo    GEMINI_API_KEY    - https://aistudio.google.com/apikey
    echo    FINNHUB_API_KEY   - https://finnhub.io/register
    echo    GNEWS_API_KEY     - https://gnews.io/
    echo.
    echo  Open backend\.env in your editor, add the keys, then run this again.
    pause
    exit /b 1
)

:: Check if frontend .env exists
if not exist "frontend\.env" (
    echo [!] frontend\.env not found!
    echo [!] Creating from .env.example...
    copy "frontend\.env.example" "frontend\.env"
    echo.
    echo  YOU MUST edit frontend\.env with your EmailJS keys:
    echo.
    echo    VITE_EMAILJS_SERVICE_ID
    echo    VITE_EMAILJS_TEMPLATE_ID
    echo    VITE_EMAILJS_PUBLIC_KEY
    echo.
    echo  Get keys from https://emailjs.com then run this again.
    pause
    exit /b 1
)

echo [1/3] Installing backend dependencies...
python -m pip install -r "%~dp0backend\requirements.txt" -q --disable-pip-version-check 2>nul

echo [2/3] Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install --silent 2>nul
cd /d "%~dp0"

echo [3/3] Starting servers...
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo.
echo  Press Ctrl+C in either window to stop.
echo.

:: Start backend in a new window
start "ReachAI Backend" cmd /k "cd /d %~dp0backend && python main.py"

:: Wait a moment for backend to boot
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
start "ReachAI Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

:: Wait then open browser
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo.
echo  ReachAI is running! Browser should open shortly.
echo  Close this window or press any key to exit this launcher.
pause >nul
