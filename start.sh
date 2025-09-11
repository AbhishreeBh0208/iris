#!/bin/bash

echo "Starting Interstellar Intercept Mission Simulator..."

# Check if Python backend dependencies are installed
echo "Checking Python dependencies..."
if ! python3 -c "import fastapi, uvicorn, numpy, astropy" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Start the Python backend in the background
echo "Starting Python backend server..."
python3 backend_api.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start the Next.js frontend
echo "Starting Next.js frontend..."
npm run dev &
FRONTEND_PID=$!

echo "🚀 Mission Simulator is starting up!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes on exit
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
