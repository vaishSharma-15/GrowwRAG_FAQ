#!/usr/bin/env python3
"""
Update mutual fund values from Groww website
Edit data/current_values.json with correct values, then run this script to update the system
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def update_system():
    """Update the entire system with current values"""
    
    print("=" * 70)
    print("🔄 UPDATING MUTUAL FUND VALUES")
    print("=" * 70)
    print()
    
    # Load current values
    values_file = Path("data/current_values.json")
    if not values_file.exists():
        print("❌ Error: data/current_values.json not found")
        return
    
    with open(values_file, 'r') as f:
        data = json.load(f)
    
    print(f"📊 Loading values from: {values_file}")
    print(f"📅 Last updated: {data['last_updated']}")
    print(f"🔢 Schemes: {len(data['schemes'])}")
    print()
    
    # Show current values
    print("Current values:")
    for scheme in data['schemes']:
        print(f"  • {scheme['name'][:35]:35} NAV: ₹{scheme['nav']:8} | Expense: {scheme['expense_ratio']}%")
    print()
    
    # Update scraped data file
    scraped_file = Path("data/extracted/groww_current_data.json")
    scraped_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to scraped format
    scraped_data = []
    for scheme in data['schemes']:
        scraped_data.append({
            "name": scheme['name'],
            "code": scheme['code'],
            "nav": scheme['nav'],
            "expense_ratio": scheme['expense_ratio'],
            "aum": scheme['aum'],
            "fund_manager": scheme['fund_manager'],
            "nav_date": data['last_updated'],
            "scraped_at": datetime.now().isoformat()
        })
    
    with open(scraped_file, 'w') as f:
        json.dump(scraped_data, f, indent=2)
    
    print(f"✓ Updated: {scraped_file}")
    
    # Regenerate chunks
    print("\n🧩 Regenerating chunks...")
    result = subprocess.run(
        ["python3", "src/create_real_chunks.py"],
        capture_output=True,
        text=True
    )
    if "Total REAL chunks created" in result.stdout:
        print("✓ Chunks regenerated")
    else:
        print("❌ Chunk generation failed")
        print(result.stderr)
        return
    
    # Re-index ChromaDB
    print("\n💾 Re-indexing ChromaDB...")
    import shutil
    chroma_db = Path("data/vector_db/chroma_db")
    if chroma_db.exists():
        shutil.rmtree(chroma_db)
    chroma_db.mkdir(parents=True, exist_ok=True)
    
    result = subprocess.run(
        ["python3", "src/indexing_pipeline.py"],
        capture_output=True,
        text=True
    )
    if "Phase 3 indexing completed successfully" in result.stdout:
        print("✓ ChromaDB re-indexed")
    else:
        print("❌ Indexing failed")
        print(result.stderr[-500:])
        return
    
    # Restart backend
    print("\n🚀 Restarting backend...")
    subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
    import time
    time.sleep(2)
    
    # Start backend
    subprocess.Popen(
        "export $(grep -v '^#' .env | xargs) && nohup python3 -m uvicorn src.api:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &",
        shell=True
    )
    time.sleep(4)
    
    # Test
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.json().get("status") == "healthy":
            print("✓ Backend restarted and healthy")
        else:
            print("⚠ Backend started but not healthy")
    except Exception as e:
        print(f"⚠ Backend status check failed: {e}")
    
    print("\n" + "=" * 70)
    print(" UPDATE COMPLETE")
    print("=" * 70)
    print()
    print("Test with:")
    print('  curl -X POST "http://localhost:8000/query" \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"query": "What is the NAV of Axis Flexi Cap Fund?"}\'')

if __name__ == "__main__":
    update_system()
