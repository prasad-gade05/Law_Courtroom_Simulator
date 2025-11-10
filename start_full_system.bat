@echo off
echo ========================================
echo Lex Simulacra - Full System Launcher
echo ========================================
echo.
echo This will start both backend and frontend
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo.
echo Starting Backend API Server...
start "Lex Simulacra Backend" cmd /k "call venv\Scripts\activate.bat && python app.py"

echo Waiting for backend to start (10 seconds)...
timeout /t 10 /nobreak

echo.
echo Starting Enhanced Frontend UI...
start "Lex Simulacra Frontend" cmd /k "call venv\Scripts\activate.bat && streamlit run interface\enhanced_stapp.py"

echo.
echo ========================================
echo System Started Successfully!
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo Two new windows have been opened.
echo Close this window or press any key to exit.
pause
