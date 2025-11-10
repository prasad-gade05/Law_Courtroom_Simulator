@echo off
echo ========================================
echo Lex Simulacra - Enhanced UI Launcher
echo ========================================
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

REM Check if backend is running
echo.
echo Checking backend status...
curl -s http://localhost:8000/docs > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Backend server is not running!
    echo Please start the backend first by running:
    echo   python app.py
    echo.
    echo Press any key to start the UI anyway, or Ctrl+C to exit
    pause
)

REM Run enhanced Streamlit app
echo.
echo Starting Enhanced Streamlit UI...
echo Navigate to: http://localhost:8501
echo.
streamlit run interface\enhanced_stapp.py

pause
