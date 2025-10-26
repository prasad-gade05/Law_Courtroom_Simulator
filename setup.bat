@echo off
echo ============================================
echo Lex Simulacra - Law Courtroom Simulator
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
echo This includes Ollama and LangChain integration
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
    echo WARNING: Please verify OLLAMA_MODEL and OLLAMA_BASE_URL are set in .env
) else (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo ✓ .env file created
    echo.
    echo ============================================
    echo IMPORTANT: Configure Your Environment
    echo ============================================
    echo.
    echo Please verify your .env file contains:
    echo    OLLAMA_MODEL=gpt-oss:120b-cloud
    echo    OLLAMA_BASE_URL=https://cloud.ollamahub.com
    echo    SERPER_API_KEY=your_serper_key
    echo    KANOON_API_KEY=your_kanoon_key
    echo.
    echo Press any key to open .env file in notepad...
    pause >nul
    notepad .env
)
echo.

echo Step 8: Checking Ollama installation...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Ollama is not installed or not in PATH
    echo.
    echo Please install Ollama from: https://ollama.com/download
    echo After installation, restart this script.
    echo.
    pause
    exit /b 1
)
echo ✓ Ollama is installed
echo.

echo Step 9: Checking required Ollama models...
echo This may take several minutes if models need to be downloaded...
echo.

echo Checking main LLM model (gpt-oss:120b-cloud)...
ollama list | findstr /C:"gpt-oss:120b-cloud" >nul 2>&1
if %errorlevel% neq 0 (
    echo Model not found. Downloading gpt-oss:120b-cloud...
    echo This is a large model and may take 10-20 minutes depending on your connection.
    ollama pull gpt-oss:120b-cloud
    if %errorlevel% neq 0 (
        echo ✗ Failed to download gpt-oss:120b-cloud
        pause
        exit /b 1
    )
    echo ✓ gpt-oss:120b-cloud downloaded successfully
) else (
    echo ✓ gpt-oss:120b-cloud already available
)
echo.

echo Checking embedding model (nomic-embed-text)...
ollama list | findstr /C:"nomic-embed-text" >nul 2>&1
if %errorlevel% neq 0 (
    echo Model not found. Downloading nomic-embed-text...
    echo This is a smaller model and should take 1-2 minutes.
    ollama pull nomic-embed-text
    if %errorlevel% neq 0 (
        echo ✗ Failed to download nomic-embed-text
        pause
        exit /b 1
    )
    echo ✓ nomic-embed-text downloaded successfully
) else (
    echo ✓ nomic-embed-text already available
)
echo.

echo Step 10: Verifying setup...
python verify_setup.py
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo Setup Verification Failed
    echo ============================================
    echo.
    echo Please fix the issues above before running the application.
    echo.
    pause
    exit /b 1
)
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Your Lex Simulacra - Law Courtroom Simulator is ready to use with Ollama.
echo.
echo Key Features:
echo  - Cloud-based Ollama models via ollamahub.com
echo  - Local embedding generation
echo  - No GPU required
echo  - Consistent performance
echo.
echo Next steps:
echo 1. Add your documents to private_documents and public_documents folders
echo 2. Verify OLLAMA_MODEL and API keys are set in .env file
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
