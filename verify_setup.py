"""
Setup Verification Script for Windows + Ollama Migration
Checks if all components are properly configured
"""
import sys
import os
from pathlib import Path

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

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        import requests
        response = requests.get("http://localhost:11434", timeout=2)
        return print_status("Ollama server is running on http://localhost:11434", True)
    except:
        return print_status("Ollama server is NOT running", False)

def check_ollama_models():
    """Check if required Ollama models are available"""
    required_models = ["qwen2:7b-instruct-q4_K_M", "phi3:mini", "nomic-embed-text"]
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]
        
        all_found = True
        for model in required_models:
            found = any(model in name for name in model_names)
            print_status(f"  - {model}", found)
            all_found = all_found and found
        
        return all_found
    except:
        print_status("  Cannot check models (Ollama not running)", False)
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "langchain": "LangChain",
        "langchain_community": "LangChain Community",
        "chromadb": "ChromaDB",
        "ollama": "Ollama Python Client",
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
        print_status(".env file (You can create from .env.example)", False)
        print("  Note: .env is optional if using default Ollama settings")
        return True  # Not critical
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

def main():
    """Run all checks"""
    print("=" * 60)
    print("PathRAG Court Simulator - Setup Verification")
    print("=" * 60)
    print()
    
    checks = {
        "Python Version": check_python_version,
        "Ollama Server": check_ollama,
        "Ollama Models": check_ollama_models,
        "Python Dependencies": check_dependencies,
        "Directories": check_directories,
        "Environment File": check_env_file,
        "Documents": check_documents,
    }
    
    results = {}
    for name, check_func in checks.items():
        print(f"\n{name}:")
        results[name] = check_func()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    critical_checks = ["Python Version", "Ollama Server", "Ollama Models", "Python Dependencies"]
    critical_passed = all(results.get(check, False) for check in critical_checks)
    
    if critical_passed:
        print("✓ All critical checks passed! System is ready.")
        print("\nTo start the application, run:")
        print("  python app.py")
    else:
        print("✗ Some critical checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install Ollama: https://ollama.com/download/windows")
        print("  - Start Ollama: ollama serve")
        print("  - Pull models: ollama pull qwen2:7b-instruct-q4_K_M")
        print("  - Install deps: pip install -r requirements.txt")
    
    print()
    return 0 if critical_passed else 1

if __name__ == "__main__":
    sys.exit(main())
