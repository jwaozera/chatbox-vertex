import os
import chromadb
import uuid
from chromadb.utils import embedding_functions

class RAGManager:
    def __init__(self, persistence_path='chroma_db'):
        self.client = chromadb.PersistentClient(path=persistence_path)
        # Using default embedding function (all-MiniLM-L6-v2) which downloads automatically
        # For better privacy/offline, we might want a local one, but default is fine for now.
        self.collection = self.client.get_or_create_collection(name="context_memory")

    def add_document(self, text, source="user_input", metadata=None):
        if not text or not text.strip():
            return
        
        # Simple chunking logic (can be improved)
        chunk_size = 500
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = []
        for _ in chunks:
            meta = {"source": source}
            if metadata:
                meta.update(metadata)
            metadatas.append(meta)

        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        return len(chunks)

    def query_context(self, query, n_results=3):
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            # Flatten results
            if results and results['documents']:
                return results['documents'][0] # Returns list of strings
            return []
        except Exception as e:
            print(f"RAG Error: {e}")
            return []

    def clear(self):
        self.client.delete_collection("context_memory")
        self.collection = self.client.get_or_create_collection(name="context_memory")
