"""
Setup Verification Script for Ollama Version
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

def check_ollama_config():
    """Check if Ollama configuration is set"""
    model = os.getenv("OLLAMA_MODEL")
    base_url = os.getenv("OLLAMA_BASE_URL")
    
    if not model:
        return print_status("OLLAMA_MODEL in environment", False)
    
    print_status(f"OLLAMA_MODEL configured ({model})", True)
    
    if base_url:
        print_status(f"OLLAMA_BASE_URL configured ({base_url})", True)
    else:
        print_status("OLLAMA_BASE_URL (using default localhost)", True)
    
    return True

def check_ollama_installation():
    """Check if Ollama is installed and accessible"""
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return print_status("Ollama installation", True)
        else:
            return print_status("Ollama installation (not accessible)", False)
    except FileNotFoundError:
        return print_status("Ollama installation (not found in PATH)", False)
    except Exception as e:
        return print_status(f"Ollama installation (Error: {str(e)[:50]})", False)

def check_ollama_models():
    """Check if required Ollama models are available"""
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return print_status("Ollama models (cannot list)", False)
        
        output = result.stdout
        
        # Check for main model
        main_model = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")
        main_model_found = main_model in output
        print_status(f"  - Main model ({main_model})", main_model_found)
        
        # Check for embedding model
        embed_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        embed_model_found = embed_model in output
        print_status(f"  - Embedding model ({embed_model})", embed_model_found)
        
        return main_model_found and embed_model_found
        
    except Exception as e:
        return print_status(f"Ollama models check (Error: {str(e)[:50]})", False)

def check_dependencies():
    """Check if required Python packages are installed"""
    packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "langchain": "LangChain",
        "langchain_community": "LangChain Community",
        "langchain_ollama": "LangChain Ollama",
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
        base_url = os.getenv("OLLAMA_BASE_URL", "")
        if "cloud" in base_url.lower():
            # Cloud Ollama requires internet
            response = requests.get("https://www.google.com", timeout=5)
            return print_status("Internet connection (REQUIRED for cloud Ollama)", response.status_code == 200)
        else:
            # Local Ollama - internet is optional
            try:
                response = requests.get("https://www.google.com", timeout=5)
                return print_status("Internet connection", response.status_code == 200)
            except:
                return print_status("Internet connection (optional for local Ollama)", True)
    except:
        return print_status("Internet connection check failed", False)

def main():
    """Run all checks"""
    print("=" * 60)
    print("Lex Simulacra - Law Courtroom Simulator")
    print("Setup Verification")
    print("=" * 60)
    print()
    
    checks = {
        "Python Version": check_python_version,
        "Internet Connection": check_internet_connection,
        "Environment File": check_env_file,
        "Ollama Configuration": check_ollama_config,
        "Ollama Installation": check_ollama_installation,
        "Ollama Models": check_ollama_models,
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
        "Environment File",
        "Ollama Configuration",
        "Ollama Installation",
        "Ollama Models",
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
        print("  - Install Ollama: https://ollama.com/download")
        print("  - Pull models: ollama pull gpt-oss:120b-cloud")
        print("  - Pull embeddings: ollama pull nomic-embed-text")
        print("  - Create .env: copy .env.example .env")
        print("  - Set OLLAMA_MODEL in .env")
        print("  - Install deps: pip install -r requirements.txt")
    
    print()
    return 0 if critical_passed else 1

if __name__ == "__main__":
    sys.exit(main())
