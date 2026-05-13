#!/bin/bash
# Run both backend and frontend services

echo "=========================================="
echo "  Mutual Fund FAQ Assistant - Launcher"
echo "=========================================="
echo ""

# Kill any existing processes
pkill -f uvicorn 2>/dev/null
pkill -f streamlit 2>/dev/null
sleep 2

# Load environment variables
export $(grep -v '^#' /Users/vaish/Documents/CursorProjects/MutualFund_RAG_FAQ/.env | xargs) 2>/dev/null

# Start Backend
echo "🚀 Starting Backend (FastAPI) on port 8000..."
cd /Users/vaish/Documents/CursorProjects/MutualFund_RAG_FAQ
python3 -m uvicorn src.api:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/backend.pid

# Wait for backend to start
sleep 4

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend running at http://localhost:8000"
else
    echo "❌ Backend failed to start. Check /tmp/backend.log"
    exit 1
fi

echo ""

# Start Frontend
echo "🚀 Starting Frontend (Streamlit) on port 8501..."
export STREAMLIT_TELEMETRY_OPT_OUT=true
export STREAMLIT_SERVER_HEADLESS=true
python3 -m streamlit run src/app.py --server.port 8501 --server.address 127.0.0.1 --browser.serverAddress localhost > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/frontend.pid

# Wait for frontend
sleep 5

# Check if frontend is running
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Frontend running at http://localhost:8501"
else
    echo "⚠️  Frontend may still be starting..."
fi

echo ""
echo "=========================================="
echo "  Services Started!"
echo "=========================================="
echo ""
echo "📱 Frontend UI:  http://localhost:8501"
echo "🔌 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo ""
echo "To stop: ./stop_services.sh"
echo ""
