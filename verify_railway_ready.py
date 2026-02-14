#!/usr/bin/env python3
"""
Verify Railway Deployment Readiness
Checks all necessary files and configurations before deployment
"""

import os
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_directory_exists(dirpath, description):
    """Check if a directory exists and has content"""
    path = Path(dirpath)
    exists = path.exists() and path.is_dir()
    if exists:
        files = list(path.rglob("*"))
        file_count = len([f for f in files if f.is_file()])
        status = "✅"
        print(f"{status} {description}: {dirpath} ({file_count} files)")
    else:
        status = "❌"
        print(f"{status} {description}: {dirpath} (NOT FOUND)")
    return exists

def check_json_file(filepath, description):
    """Check if JSON file is valid"""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        print(f"✅ {description}: {filepath} (Valid JSON)")
        return True
    except Exception as e:
        print(f"❌ {description}: {filepath} (Invalid: {e})")
        return False

def check_env_example():
    """Check if .env.example has required variables"""
    required_vars = ['GEMINI_API_KEY', 'SECRET_KEY', 'DATABASE_URL']
    try:
        with open('backend/.env.example', 'r') as f:
            content = f.read()
        
        missing = [var for var in required_vars if var not in content]
        if not missing:
            print(f"✅ Environment variables documented in .env.example")
            return True
        else:
            print(f"⚠️  Missing variables in .env.example: {', '.join(missing)}")
            return False
    except:
        print(f"❌ backend/.env.example not found")
        return False

def main():
    print("=" * 60)
    print("🚀 Railway Deployment Readiness Check")
    print("=" * 60)
    print()
    
    checks = []
    
    # Core deployment files
    print("📋 Core Deployment Files:")
    checks.append(check_file_exists("railway.json", "Railway config"))
    checks.append(check_file_exists("nixpacks.toml", "Nixpacks config"))
    checks.append(check_file_exists("Dockerfile", "Dockerfile"))
    checks.append(check_file_exists("docker-compose.yml", "Docker Compose"))
    checks.append(check_file_exists(".dockerignore", "Docker ignore"))
    print()
    
    # Backend files
    print("🐍 Backend Files:")
    checks.append(check_file_exists("backend/requirements.txt", "Python dependencies"))
    checks.append(check_file_exists("backend/app/main.py", "Main application"))
    checks.append(check_file_exists("backend/Procfile", "Procfile"))
    checks.append(check_file_exists("backend/runtime.txt", "Python runtime"))
    checks.append(check_env_example())
    print()
    
    # Frontend files
    print("⚛️  Frontend Files:")
    checks.append(check_file_exists("frontend/package.json", "Package config"))
    checks.append(check_file_exists("frontend/vite.config.js", "Vite config"))
    checks.append(check_file_exists("frontend/.env.production", "Production env"))
    checks.append(check_file_exists("frontend/index.html", "HTML entry"))
    print()
    
    # Models directory
    print("🤖 AI Models:")
    checks.append(check_directory_exists("models", "Models directory"))
    checks.append(check_directory_exists("models/pulse", "Pulse models"))
    print()
    
    # JSON validation
    print("📝 JSON File Validation:")
    checks.append(check_json_file("railway.json", "Railway config"))
    checks.append(check_json_file("frontend/package.json", "Package.json"))
    print()
    
    # Documentation
    print("📚 Documentation:")
    checks.append(check_file_exists("README.md", "README"))
    checks.append(check_file_exists("SINGLE_RAILWAY_DEPLOYMENT.md", "Deployment guide"))
    checks.append(check_file_exists("RAILWAY_DEPLOYMENT_FIX.md", "Fix documentation"))
    print()
    
    # Git status
    print("🔍 Git Status:")
    try:
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                print(f"⚠️  Uncommitted changes detected:")
                for line in changes.split('\n')[:5]:  # Show first 5
                    print(f"   {line}")
                if len(changes.split('\n')) > 5:
                    print(f"   ... and {len(changes.split('\n')) - 5} more")
                checks.append(False)
            else:
                print(f"✅ No uncommitted changes")
                checks.append(True)
        else:
            print(f"⚠️  Not a git repository or git not available")
    except:
        print(f"⚠️  Could not check git status")
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"📊 Results: {passed}/{total} checks passed ({percentage:.1f}%)")
    print()
    
    if passed == total:
        print("✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        print()
        print("Next steps:")
        print("1. Commit changes: git add . && git commit -m 'Ready for deployment'")
        print("2. Push to GitHub: git push origin main")
        print("3. Railway will auto-deploy")
        print("4. Monitor build logs in Railway dashboard")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - Review issues above")
        print()
        print("Fix the issues and run this script again.")
        return 1

if __name__ == "__main__":
    exit(main())
