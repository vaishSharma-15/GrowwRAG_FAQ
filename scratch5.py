import sys
import os
sys.path.append(os.path.abspath('.'))

from src.vector_db import ChromaVectorDB

vector_db = ChromaVectorDB(persist_directory="data/vector_db/chroma_db")
vector_db.connect()
print("CURRENT COLLECTION ID:", vector_db.collection.id)
