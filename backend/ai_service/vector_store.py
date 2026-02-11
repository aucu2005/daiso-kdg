# backend/ai_service/vector_store.py
"""
ChromaDB Vector Store for Semantic Search

Uses paraphrase-multilingual-MiniLM-L12-v2 for Korean text embeddings.
This model supports 50+ languages including Korean.

Usage:
    python -m backend.ai_service.vector_store
"""

import os
import sys
from typing import List, Dict, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_PERSIST_DIR = os.path.join(PROJECT_ROOT, "backend", "database", "chroma_db")
COLLECTION_NAME = "products"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


def _get_embedding_function():
    """Get SentenceTransformer-based embedding function."""
    try:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        return SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    except ImportError:
        print(f"⚠️ sentence-transformers not available.")
        return None


class VectorStore:
    """ChromaDB wrapper for product vector search."""

    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR):
        self.persist_dir = persist_dir
        self._client = None
        self._collection = None
        self._embedding_fn = _get_embedding_function()

    def _get_client(self):
        if self._client is None:
            import chromadb
            self._client = chromadb.PersistentClient(path=self.persist_dir)
        return self._client

    def _get_collection(self):
        if self._collection is None:
            client = self._get_client()
            kwargs = {
                "name": COLLECTION_NAME,
                "metadata": {"hnsw:space": "cosine"},
            }
            if self._embedding_fn:
                kwargs["embedding_function"] = self._embedding_fn
            self._collection = client.get_or_create_collection(**kwargs)
        return self._collection

    def index_products(self, products: List[Dict], batch_size: int = 100) -> int:
        """Index products into ChromaDB."""
        collection = self._get_collection()

        # Clear existing
        try:
            existing = collection.count()
            if existing > 0:
                all_ids = collection.get()["ids"]
                if all_ids:
                    collection.delete(ids=all_ids)
                print(f"  🗑️ Cleared {existing} existing items")
        except Exception:
            pass

        total = 0
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            ids, documents, metadatas = [], [], []

            for p in batch:
                pid = str(p.get("id", ""))
                name = p.get("name", "")
                if not pid or not name:
                    continue
                ids.append(pid)
                documents.append(name)
                metadatas.append({
                    "name": name,
                    "price": int(p.get("price", 0)),
                    "rank": int(p.get("rank", 0)),
                    "category_major": str(p.get("category_major") or ""),
                    "category_middle": str(p.get("category_middle") or ""),
                    "floor": str(p.get("floor") or ""),
                    "location": str(p.get("location") or ""),
                })

            if ids:
                collection.add(ids=ids, documents=documents, metadatas=metadatas)
                total += len(ids)

        print(f"  ✅ Indexed {total} products (model: {EMBEDDING_MODEL})")
        return total

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search products by semantic similarity."""
        try:
            collection = self._get_collection()
            if collection.count() == 0:
                return []

            results = collection.query(
                query_texts=[query],
                n_results=min(top_k, collection.count()),
            )

            items = []
            if results and results["ids"] and results["ids"][0]:
                for idx, doc_id in enumerate(results["ids"][0]):
                    meta = results["metadatas"][0][idx] if results["metadatas"] else {}
                    distance = results["distances"][0][idx] if results["distances"] else 1.0
                    items.append({
                        "id": int(doc_id) if doc_id.isdigit() else doc_id,
                        "name": meta.get("name", ""),
                        "price": meta.get("price", 0),
                        "rank": meta.get("rank", 0),
                        "category_major": meta.get("category_major", ""),
                        "category_middle": meta.get("category_middle", ""),
                        "floor": meta.get("floor", ""),
                        "location": meta.get("location", ""),
                        "distance": round(distance, 4),
                    })
            return items
        except Exception as e:
            print(f"⚠️ Vector search error: {e}")
            return []

    def count(self) -> int:
        try:
            return self._get_collection().count()
        except Exception:
            return 0


# Singleton
_store_instance: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = VectorStore()
    return _store_instance


# CLI
def build_index():
    """Build ChromaDB index from SQLite products."""
    print(f"🔨 Building ChromaDB vector index (model: {EMBEDDING_MODEL})...")

    sys.path.insert(0, PROJECT_ROOT)
    from backend.database.database import get_all_products

    products = get_all_products()
    print(f"   Found {len(products)} products")

    if not products:
        print("   ❌ No products found.")
        return

    store = VectorStore()
    count = store.index_products(products)
    print(f"\n🎉 Index built! {count} products indexed")

    test_queries = ["볼펜", "매트", "충전 케이블", "미끄럼방지", "수납함"]
    print("\n📝 Quick verification:")
    for q in test_queries:
        results = store.search(q, top_k=5)
        names = [f"{r['name']}({r['distance']:.3f})" for r in results[:3]]
        print(f"   '{q}' → {names}")


if __name__ == "__main__":
    build_index()
