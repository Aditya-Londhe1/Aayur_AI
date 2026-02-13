"""
Verify all files are ready for Railway deployment
"""

import os
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_file(filepath, description):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = f"{Colors.GREEN}✓{Colors.END}" if exists else f"{Colors.RED}✗{Colors.END}"
    print(f"{status} {filepath:<50} {description}")
    return exists

def check_directory(dirpath, description):
    """Check if a directory exists"""
    exists = os.path.isdir(dirpath)
    status = f"{Colors.GREEN}✓{Colors.END}" if exists else f"{Colors.RED}✗{Colors.END}"
    print(f"{status} {dirpath:<50} {description}")
    return exists

def main():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}Railway Deployment Readiness Check{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    checks = []
    
    # Backend files
    print(f"{Colors.YELLOW}Backend Files:{Colors.END}")
    checks.append(check_file("backend/app/main.py", "FastAPI application"))
    checks.append(check_file("backend/requirements.txt", "Python dependencies"))
    checks.append(check_file("backend/Procfile", "Railway start command"))
    checks.append(check_file("backend/runtime.txt", "Python version"))
    checks.append(check_file("backend/.env", "Environment variables"))
    checks.append(check_file("backend/alembic.ini", "Database migrations"))
    
    print(f"\n{Colors.YELLOW}Frontend Files:{Colors.END}")
    checks.append(check_file("frontend/package.json", "Node dependencies"))
    checks.append(check_file("frontend/vite.config.js", "Vite configuration"))
    checks.append(check_file("frontend/index.html", "HTML template"))
    checks.append(check_file("frontend/src/main.jsx", "React entry point"))
    
    print(f"\n{Colors.YELLOW}Deployment Files:{Colors.END}")
    checks.append(check_file("railway.json", "Railway configuration"))
    checks.append(check_file("nixpacks.toml", "Build configuration"))
    checks.append(check_file(".gitignore", "Git ignore rules"))
    
    print(f"\n{Colors.YELLOW}Documentation:{Colors.END}")
    checks.append(check_file("RAILWAY_DEPLOYMENT_GUIDE.md", "Deployment guide"))
    checks.append(check_file("RAILWAY_DEPLOYMENT_CHECKLIST.md", "Deployment checklist"))
    checks.append(check_file("README.md", "Project documentation"))
    
    print(f"\n{Colors.YELLOW}Directories:{Colors.END}")
    checks.append(check_directory("backend/app", "Backend application"))
    checks.append(check_directory("frontend/src", "Frontend source"))
    checks.append(check_directory("backend/alembic", "Database migrations"))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total) * 100
    
    if passed == total:
        print(f"{Colors.GREEN}✓ All checks passed! ({passed}/{total}){Colors.END}")
        print(f"{Colors.GREEN}✓ Ready for Railway deployment!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ {passed}/{total} checks passed ({percentage:.1f}%){Colors.END}")
        print(f"{Colors.YELLOW}⚠ Some files are missing{Colors.END}")
    
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    # Additional checks
    print(f"{Colors.YELLOW}Additional Information:{Colors.END}")
    
    # Check if git repo
    if os.path.exists(".git"):
        print(f"{Colors.GREEN}✓{Colors.END} Git repository initialized")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} Not a git repository (run: git init)")
    
    # Check requirements.txt content
    if os.path.exists("backend/requirements.txt"):
        with open("backend/requirements.txt", "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
            print(f"{Colors.GREEN}✓{Colors.END} {len(lines)} Python packages in requirements.txt")
    
    # Check package.json
    if os.path.exists("frontend/package.json"):
        import json
        with open("frontend/package.json", "r") as f:
            pkg = json.load(f)
            deps = len(pkg.get("dependencies", {}))
            print(f"{Colors.GREEN}✓{Colors.END} {deps} Node packages in package.json")
    
    print(f"\n{Colors.BLUE}Next Steps:{Colors.END}")
    print("1. Push code to GitHub")
    print("2. Go to https://railway.app")
    print("3. Deploy from GitHub repository")
    print("4. Follow RAILWAY_DEPLOYMENT_GUIDE.md")
    print(f"\n{Colors.GREEN}Good luck with your deployment! 🚀{Colors.END}\n")

if __name__ == "__main__":
    main()
