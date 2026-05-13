import sys
import os
sys.path.append(os.path.abspath('.'))

from src.vector_db import ChromaVectorDB
from src.indexing_pipeline import IndexingPipeline

# Initialize and reset Vector DB
vector_db = ChromaVectorDB(persist_directory="data/vector_db/chroma_db")
vector_db.reset_collection()

# Run indexing pipeline
pipeline = IndexingPipeline()
pipeline.run()
