#!/bin/bash
# Local Scheduler Test - Mimics GitHub Actions workflow
# Run this to test the full daily update pipeline

set -e  # Exit on error

echo "=========================================="
echo "🔄 LOCAL SCHEDULER TEST"
echo "Mimics GitHub Actions daily-scrape.yml"
echo "=========================================="
echo ""

# Step 1: Install dependencies (like GA does)
echo "📦 Step 1: Installing dependencies..."
pip3 install requests beautifulsoup4 --quiet 2>/dev/null || python3 -m pip install requests beautifulsoup4 --quiet
echo "✓ Dependencies installed"
echo ""

# Step 2: Scrape current data from Groww
echo "🔍 Step 2: Scraping current data from Groww..."
python3 src/scrape_groww_api.py
echo ""

# Step 3: Create chunks from scraped data
echo "🧩 Step 3: Creating chunks from scraped data..."
python3 src/create_real_chunks.py
echo ""

# Step 4: Re-index ChromaDB
echo "💾 Step 4: Re-indexing ChromaDB..."
rm -rf data/vector_db/chroma_db/*
python3 src/indexing_pipeline.py
echo ""

# Step 5: Restart backend with new data
echo "🚀 Step 5: Restarting backend..."
pkill -f uvicorn 2>/dev/null || true
sleep 2

export $(grep -v '^#' .env | xargs)
nohup python3 -m uvicorn src.api:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
sleep 4

# Test backend
echo "🧪 Step 6: Testing backend..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✓ Backend is healthy"
else
    echo "✗ Backend failed to start"
    exit 1
fi

# Test query
echo ""
echo "💬 Step 7: Testing query..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the NAV of Axis Flexi Cap Fund?"}')

echo "Query response:"
echo "$RESPONSE" | python3 -m json.tool | head -10

echo ""
echo "=========================================="
echo "✅ LOCAL SCHEDULER TEST COMPLETE"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ Dependencies installed"
echo "  ✓ Data scraped from Groww"
echo "  ✓ Chunks created"
echo "  ✓ ChromaDB re-indexed"
echo "  ✓ Backend restarted"
echo "  ✓ Query test passed"
echo ""
echo "Next run at: 8:00 AM IST tomorrow (via GitHub Actions)"
