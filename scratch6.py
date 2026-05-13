import json
with open('data/processed/chunks/all_chunks.json', 'r') as f:
    chunks = json.load(f)

for chunk in chunks:
    text = chunk.get('chunk_text', '')
    if 'Fund Manager' in text:
        lines = text.split('\n')
        for line in lines:
            if line.startswith('Scheme Name:') or line.startswith('Fund Manager:'):
                print(line)
        print("---")
