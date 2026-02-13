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
