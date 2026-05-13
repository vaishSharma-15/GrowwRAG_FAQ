#!/bin/bash
# Stop all services

echo "Stopping services..."
pkill -f uvicorn 2>/dev/null
pkill -f streamlit 2>/dev/null
rm -f /tmp/backend.pid /tmp/frontend.pid
echo "✅ All services stopped"
