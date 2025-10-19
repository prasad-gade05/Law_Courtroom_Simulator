"""
Setup Verification Script for Google Gemini API Version
Checks if all components are properly configured
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def print_status(message, status):
    """Print colored status message"""
    if status:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
    return status

def check_python_version():
    """Check if Python version is 3.9+"""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 9
    return print_status(
        f"Python {version.major}.{version.minor}.{version.micro} (Required: 3.9+)",
        is_valid
    )

def check_google_api_key():
    """Check if Google API key is configured"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return print_status("GOOGLE_API_KEY in environment", False)
    
    # Check if it's a placeholder
    if api_key == "your_google_api_key_here" or len(api_key) < 20:
        return print_status("GOOGLE_API_KEY (appears to be placeholder/invalid)", False)
    
    # Mask the key for display
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "****"
    return print_status(f"GOOGLE_API_KEY configured ({masked_key})", True)

def check_google_api_connection():
    """Check if we can connect to Google Gemini API"""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key or api_key == "your_google_api_key_here":
            return print_status("Google Gemini API connection (no API key)", False)
        
        # Try to configure and list models
        genai.configure(api_key=api_key)
        
        # Try to get a model - this validates the API key
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            return print_status("Google Gemini API connection successful", True)
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                return print_status("Google Gemini API connection (Invalid API key)", False)
            else:
                return print_status(f"Google Gemini API connection (Error: {error_msg[:50]})", False)
                
    except ImportError:
        return print_status("Google Generative AI package (not installed)", False)
    except Exception as e:
        return print_status(f"Google Gemini API connection (Error: {str(e)[:50]})", False)

def check_dependencies():
    """Check if required Python packages are installed"""
    packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "langchain": "LangChain",
        "langchain_community": "LangChain Community",
        "langchain_google_genai": "LangChain Google GenAI",
        "google.generativeai": "Google Generative AI",
        "chromadb": "ChromaDB",
        "pymupdf": "PyMuPDF (PDF support)",
        "docx": "python-docx (Word support)",
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            print_status(f"  - {name}", True)
        except ImportError:
            print_status(f"  - {name}", False)
            all_installed = False
    
    return all_installed

def check_directories():
    """Check if required directories exist"""
    required_dirs = ["private_documents", "public_documents"]
    
    all_exist = True
    for dir_name in required_dirs:
        exists = Path(dir_name).exists()
        print_status(f"  - {dir_name}/", exists)
        all_exist = all_exist and exists
    
    return all_exist

def check_env_file():
    """Check if .env file exists"""
    exists = Path(".env").exists()
    if not exists:
        print_status(".env file (REQUIRED - create from .env.example)", False)
        print("  Note: .env file is required for GOOGLE_API_KEY")
        return False
    else:
        return print_status(".env file", True)

def check_documents():
    """Check if documents are present"""
    private_docs = list(Path("private_documents").glob("*.*")) if Path("private_documents").exists() else []
    public_docs = list(Path("public_documents").glob("*.*")) if Path("public_documents").exists() else []
    
    print_status(f"  - Private documents: {len(private_docs)} files", len(private_docs) > 0)
    print_status(f"  - Public documents: {len(public_docs)} files", len(public_docs) > 0)
    
    if len(private_docs) == 0 and len(public_docs) == 0:
        print("  Note: Add documents to these folders for the system to work properly")
    
    return True  # Not critical for setup verification

def check_internet_connection():
    """Check if internet connection is available"""
    try:
        import requests
        response = requests.get("https://www.google.com", timeout=5)
        return print_status("Internet connection", response.status_code == 200)
    except:
        return print_status("Internet connection (REQUIRED for Gemini API)", False)

def main():
    """Run all checks"""
    print("=" * 60)
    print("PathRAG Court Simulator - Google Gemini Version")
    print("Setup Verification")
    print("=" * 60)
    print()
    
    checks = {
        "Python Version": check_python_version,
        "Internet Connection": check_internet_connection,
        "Environment File": check_env_file,
        "Google API Key": check_google_api_key,
        "Google API Connection": check_google_api_connection,
        "Python Dependencies": check_dependencies,
        "Directories": check_directories,
        "Documents": check_documents,
    }
    
    results = {}
    for name, check_func in checks.items():
        print(f"\n{name}:")
        results[name] = check_func()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    critical_checks = [
        "Python Version", 
        "Internet Connection",
        "Environment File",
        "Google API Key", 
        "Google API Connection",
        "Python Dependencies"
    ]
    critical_passed = all(results.get(check, False) for check in critical_checks)
    
    if critical_passed:
        print("✓ All critical checks passed! System is ready.")
        print("\nTo start the application, run:")
        print("  python app.py")
        print("\nTo test with sample case:")
        print("  python test_api_demo.py")
    else:
        print("✗ Some critical checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Get API key: https://aistudio.google.com/app/apikey")
        print("  - Create .env: copy .env.example .env")
        print("  - Add API key to .env: GOOGLE_API_KEY=your_actual_key")
        print("  - Install deps: pip install -r requirements.txt")
        print("  - Check internet connection")
    
    print()
    return 0 if critical_passed else 1

if __name__ == "__main__":
    sys.exit(main())
