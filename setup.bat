@echo off
echo ============================================
echo PathRAG Court Simulator - Google Gemini
echo Windows Setup Script
echo ============================================
echo.

echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)
echo ✓ Python is installed
echo.

echo Step 2: Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo ✓ Virtual environment created
)
echo.

echo Step 3: Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

echo Step 4: Upgrading pip...
python -m pip install --upgrade pip
echo ✓ pip upgraded
echo.

echo Step 5: Installing Python dependencies...
echo This includes Google Generative AI SDK and LangChain integration
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo Step 6: Creating necessary directories...
if not exist "private_documents" mkdir private_documents
if not exist "public_documents" mkdir public_documents
if not exist "chroma_db" mkdir chroma_db
echo ✓ Directories created
echo.

echo Step 7: Setting up environment file...
if exist ".env" (
    echo ✓ .env file already exists
    echo WARNING: Please verify GOOGLE_API_KEY is set in .env
) else (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo ✓ .env file created
    echo.
    echo ============================================
    echo IMPORTANT: Configure Your API Key
    echo ============================================
    echo.
    echo 1. Visit https://aistudio.google.com/app/apikey
    echo 2. Create a new API key
    echo 3. Open .env file and add your key:
    echo    GOOGLE_API_KEY=your_actual_api_key_here
    echo.
    echo Press any key to open .env file in notepad...
    pause >nul
    notepad .env
)
echo.

echo Step 8: Verifying setup...
python verify_setup.py
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo Setup Verification Failed
    echo ============================================
    echo.
    echo Please fix the issues above before running the application.
    echo Most likely you need to set GOOGLE_API_KEY in .env file.
    echo.
    echo Get your API key from: https://aistudio.google.com/app/apikey
    echo.
    pause
    exit /b 1
)
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Your courtroom simulator is ready to use with Google Gemini API.
echo.
echo Key Features:
echo  - 10x faster than local models
echo  - No GPU required
echo  - Consistent performance
echo  - Cloud-powered inference
echo.
echo Next steps:
echo 1. Add your documents to private_documents and public_documents folders
echo 2. Verify GOOGLE_API_KEY is set in .env file
echo 3. Run the application with: python app.py
echo 4. Test with: python test_api_demo.py
echo.
echo Would you like to start the application now? (Y/N)
set /p start_now="Enter Y to start or N to exit: "
if /i "%start_now%"=="Y" (
    echo.
    echo Starting application...
    python app.py
) else (
    echo.
    echo To start later, run: python app.py
    echo.
)

echo.
echo Setup script completed.
pause
