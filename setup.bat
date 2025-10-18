@echo off
echo ============================================
echo PathRAG Court Simulator - Windows Setup
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

echo Step 2: Checking if Ollama is installed...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama is not installed!
    echo Please install Ollama from https://ollama.com/download/windows
    echo After installation, run this script again.
    pause
    exit /b 1
)
echo ✓ Ollama is installed
echo.

echo Step 3: Checking if Ollama is running...
curl -s http://localhost:11434 >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama is not running!
    echo Please start Ollama before running this script.
    echo You can start it by running: ollama serve
    pause
    exit /b 1
)
echo ✓ Ollama is running
echo.

echo Step 4: Pulling required Ollama models...
echo This may take a while depending on your internet connection...
echo.

echo Pulling llama3.1:8b (Main reasoning model)...
ollama pull llama3.1:8b
if %errorlevel% neq 0 (
    echo ERROR: Failed to pull llama3.1:8b
    pause
    exit /b 1
)
echo ✓ llama3.1:8b ready
echo.

echo Pulling mistral:7b (Alternative model)...
ollama pull mistral:7b
if %errorlevel% neq 0 (
    echo ERROR: Failed to pull mistral:7b
    pause
    exit /b 1
)
echo ✓ mistral:7b ready
echo.

echo Pulling nomic-embed-text (Embedding model)...
ollama pull nomic-embed-text
if %errorlevel% neq 0 (
    echo ERROR: Failed to pull nomic-embed-text
    pause
    exit /b 1
)
echo ✓ nomic-embed-text ready
echo.

echo Step 5: Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo ✓ Virtual environment created
)
echo.

echo Step 6: Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

echo Step 7: Upgrading pip...
python -m pip install --upgrade pip
echo ✓ pip upgraded
echo.

echo Step 8: Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo Step 9: Creating necessary directories...
if not exist "private_documents" mkdir private_documents
if not exist "public_documents" mkdir public_documents
if not exist "chroma_db" mkdir chroma_db
echo ✓ Directories created
echo.

echo Step 10: Checking .env file...
if exist ".env" (
    echo ✓ .env file exists
) else (
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo ✓ .env file created. Please edit it with your API keys if needed.
)
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Add your documents to the private_documents and public_documents folders
echo 2. Edit .env file with your API keys (optional)
echo 3. Run the application with: python app.py
echo.
echo To start the application now, press any key...
pause >nul

echo.
echo Starting application...
python app.py
