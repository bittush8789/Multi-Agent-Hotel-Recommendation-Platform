import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
from app.config import settings

class VectorStoreService:
    def __init__(self):
        # Initialize ChromaDB client based on settings (HTTP or Persistent)
        if settings.CHROMA_HOST:
            self.client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        else:
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        
        # Use default MiniLM-L6-v2 embedding function provided by Chroma
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Create/Get collection
        self.collection = self.client.get_or_create_collection(
            name="hotel_reviews",
            embedding_function=self.embedding_function
        )

    def add_reviews(self, hotel_name: str, reviews: List[str]):
        """Adds a list of guest reviews for a specific hotel to ChromaDB."""
        if not reviews:
            return

        documents = []
        metadatas = []
        ids = []

        for idx, review in enumerate(reviews):
            documents.append(review)
            metadatas.append({"hotel_name": hotel_name})
            # Generate a unique ID based on hotel and index
            clean_hotel_name = hotel_name.lower().replace(" ", "_")
            ids.append(f"{clean_hotel_name}_review_{idx}")

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_hotel_reviews(self, hotel_name: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top semantically relevant reviews for a specific hotel.
        If no items exist or collection is empty, returns empty list.
        """
        try:
            # Query collection with filter on hotel_name metadata
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where={"hotel_name": hotel_name}
            )
            
            # Reformat results
            insights = []
            if results and results.get("documents"):
                documents = results["documents"][0]
                metadatas = results["metadatas"][0] if results.get("metadatas") else []
                distances = results["distances"][0] if results.get("distances") else []
                
                for idx, doc in enumerate(documents):
                    insights.append({
                        "text": doc,
                        "distance": distances[idx] if idx < len(distances) else 0.0
                    })
            return insights
        except Exception as e:
            # Safe recovery if querying fails
            return []

    def clear_database(self):
        """Clears all documents in the collection for resetting database."""
        try:
            self.client.delete_collection(name="hotel_reviews")
            self.collection = self.client.get_or_create_collection(
                name="hotel_reviews",
                embedding_function=self.embedding_function
            )
        except Exception:
            pass

# Export vector store service instance
vector_store_service = VectorStoreService()
