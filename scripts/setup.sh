#!/bin/bash
# setup.sh - Complete Aayur AI Setup Script

echo "=========================================="
echo "     AAYUR AI - COMPLETE SETUP           "
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. Some commands may need sudo."
fi

# Step 1: Check prerequisites
print_status "1/10" "Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found. Please install Node.js 16+"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    print_success "Docker found"
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose found"
    else
        print_warning "Docker Compose not found. Docker Compose will be used if available."
    fi
else
    print_warning "Docker not found. Some features may not work without Docker."
fi

# Step 2: Create project structure
print_status "2/10" "Creating project structure..."

mkdir -p aayur-ai/{backend,frontend,ml_models,uploads,reports,logs,backups,database}
cd aayur-ai

print_success "Project structure created"

# Step 3: Setup backend
print_status "3/10" "Setting up backend..."

# Create virtual environment
python3 -m venv backend/venv
source backend/venv/bin/activate

# Install backend dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create .env file for backend
cat > backend/.env << EOF
# Application
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///./database/aayurai.db

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# CORS
CORS_ORIGINS=http://localhost:3000

# File uploads
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png

# AI Models
MODEL_DIR=./ml_models
USE_GPU=False

# Multilingual
DEFAULT_LOCALE=en
SUPPORTED_LOCALES=en,hi,ta,te,kn,ml,bn,gu,mr,pa,ur
TRANSLATIONS_DIR=./app/i18n/translations

# Security
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Redis (optional)
# REDIS_URL=redis://localhost:6379/0
EOF

print_success "Backend setup complete"

# Step 4: Setup frontend
print_status "4/10" "Setting up frontend..."

cd frontend

# Create .env file for frontend
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENV=development
REACT_APP_VERSION=1.0.0
EOF

# Install frontend dependencies
npm install

cd ..

print_success "Frontend setup complete"

# Step 5: Initialize database
print_status "5/10" "Initializing database..."

cd backend
python -c "
from app.core.database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

cd ..

print_success "Database initialized"

# Step 6: Create sample AI models
print_status "6/10" "Creating sample AI models..."

mkdir -p ml_models/{tongue,pulse,symptom}

# Create dummy model files
cat > ml_models/tongue/model.pth << EOF
# This is a placeholder for the actual tongue model
# In production, this would be a trained PyTorch model
EOF

cat > ml_models/pulse/model.pth << EOF
# This is a placeholder for the actual pulse model
EOF

cat > ml_models/symptom/model.pth << EOF
# This is a placeholder for the actual symptom model
EOF

print_success "Sample models created"

# Step 7: Create startup scripts
print_status "7/10" "Creating startup scripts..."

# Backend startup script
cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
python -m app.main
EOF

chmod +x start-backend.sh

# Frontend startup script
cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm start
EOF

chmod +x start-frontend.sh

# Complete startup script
cat > start-all.sh << 'EOF'
#!/bin/bash
echo "Starting Aayur AI..."

# Start backend in background
cd backend
source venv/bin/activate
python -m app.main &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend in background
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "     AAYUR AI STARTED SUCCESSFULLY       "
echo "=========================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

chmod +x start-all.sh

print_success "Startup scripts created"

# Step 8: Create backup script
print_status "8/10" "Creating backup script..."

cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Creating backup in $BACKUP_DIR..."

# Backup database
cp database/aayurai.db "$BACKUP_DIR/"

# Backup uploads
cp -r uploads "$BACKUP_DIR/"

# Backup reports
cp -r reports "$BACKUP_DIR/"

# Backup logs
cp -r logs "$BACKUP_DIR/"

# Create backup info
cat > "$BACKUP_DIR/backup-info.txt" << INFO
Backup Date: $(date)
Backup Directory: $BACKUP_DIR
Database Size: $(du -h database/aayurai.db | cut -f1)
Uploads Size: $(du -sh uploads | cut -f1)
Reports Size: $(du -sh reports | cut -f1)
INFO

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh

print_success "Backup script created"

# Step 9: Create systemd service (for Linux)
print_status "9/10" "Creating systemd service..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cat > aayur-ai.service << EOF
[Unit]
Description=Aayur AI Ayurvedic Diagnostic System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=$(pwd)/start-all.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    print_success "Systemd service file created"
    print_warning "To install as system service:"
    echo "  sudo cp aayur-ai.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable aayur-ai.service"
    echo "  sudo systemctl start aayur-ai.service"
else
    print_warning "Systemd service creation skipped (not Linux)"
fi

# Step 10: Final instructions
print_status "10/10" "Setup complete!"

cat > README.txt << 'EOF'
==========================================
     AAYUR AI - SETUP COMPLETE
==========================================

Your Aayur AI system has been successfully set up!

QUICK START:
1. Start all services:
   ./start-all.sh

2. Or start individually:
   - Backend: ./start-backend.sh
   - Frontend: ./start-frontend.sh

3. Open in browser:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

DIRECTORY STRUCTURE:
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── ml_models/        # AI models
├── uploads/          # User uploads
├── reports/          # Generated reports
├── logs/             # Application logs
├── database/         # Database files
└── backups/          # Backup files

USAGE:
1. Register an account
2. Start a new consultation
3. Upload tongue image and symptoms
4. Get AI-powered Ayurvedic diagnosis
5. View personalized recommendations

BACKUP:
Run ./backup.sh to create a backup of all data

TROUBLESHOOTING:
- Check logs in logs/ directory
- Ensure all services are running
- Check port availability (3000, 8000)

SUPPORT:
For issues, check the documentation or contact support

Enjoy using Aayur AI!
EOF

print_success "Setup complete!"
echo ""
echo "=========================================="
echo "     NEXT STEPS                           "
echo "=========================================="
echo ""
echo "1. Start the application:"
echo "   ./start-all.sh"
echo ""
echo "2. Open in browser:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo ""
echo "3. Register an account and start using!"
echo ""
echo "For more details, see README.txt"
echo "=========================================="