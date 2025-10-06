from crewai.tools import BaseTool
from typing import Type, Optional, Literal
from pydantic import BaseModel, Field
import sys
from pathlib import Path
from chroma_manager import ChromaManager
from rank_bm25 import BM25Okapi

sys.path.insert(0, str(Path(__file__).parent.parent))

class RetrievalTool(BaseModel):
    """Input schema for RetrievalTool"""
    query: str = Field(..., description="Search query to find relevant publications")
    n_results: int = Field(default=5, description="Number of results to return (1-20)")
    strategy: Literal["dense", "sparse", "hybrid"] = Field(
        default="hybrid", 
        description="Retrieval strategy: 'dense' (semantic), 'sparse' (BM25 keyword), or 'hybrid' (both combined)"
    )
    year_from: Optional[int] = Field(default=None, description="Optional: Filter by minimum year (e.g., 2020)")
    source: Optional[str] = Field(default=None, description="Optional: Filter by source ('arxiv' or 'openalex')")
    hybrid_weight: float = Field(default=0.5, description="Weight for dense vs sparse in hybrid (0.0=sparse only, 1.0=dense only)")


class RetrievalTool(BaseTool):
    name: str = "Multi-Strategy Vector Retrieval"
    description: str = """Search publications using three different retrieval strategies:
    
    1. DENSE (semantic): Neural embeddings, captures meaning and context
    2. SPARSE (BM25): Keyword-based, exact term matching  
    3. HYBRID: Combines dense + sparse for best of both worlds
    
    Returns publications with full metadata: title, authors, year, journal, DOI, quality rating.
    
    Use cases:
    - Dense: Conceptual queries 
    - Sparse: Exact terms/acronyms
    - Hybrid: Best overall results (recommended)
    
    Example: query="machine learning", n_results=5, strategy="hybrid", hybrid_weight=0.7"""
    
    args_schema: Type[BaseModel] = RetrievalTool
    
    chroma_persist_directory: str = "./chroma_db"
    _bm25_index: Optional[BM25Okapi] = None
    _bm25_documents: list = []
    _bm25_metadatas: list = []
    _chroma_manager: Optional[ChromaManager] = None
    
    def _get_chroma_manager(self):
        """Get or create ChromaManager instance (singleton pattern)"""
        if self._chroma_manager is None:
            self._chroma_manager = ChromaManager(persist_directory=self.chroma_persist_directory)
            self._chroma_manager.connect()
        return self._chroma_manager
    
    def _initialize_bm25_retriever(self):
        """Initialize BM25 index with documents from ChromaDB"""
        if self._bm25_index is not None:
            return
        
        try:
            manager = self._get_chroma_manager()
            
            collection = manager.client.get_collection(name="scientific_publications")
            
            all_data = collection.get(include=["documents", "metadatas"])
            
            if not all_data['documents']:
                return
  
            self._bm25_documents = all_data['documents']
            self._bm25_metadatas = all_data['metadatas']
            
            tokenized_corpus = [doc.lower().split() for doc in self._bm25_documents]

            self._bm25_index = BM25Okapi(tokenized_corpus)
            
        except Exception as e:
            raise Exception(f"Failed to initialize BM25 index: {e}")
    
    def _dense_retrieval(self, query: str, n_results: int, year_from: Optional[int], source: Optional[str]):
        """Dense vector search using embeddings"""
        manager = self._get_chroma_manager()

        where_filter = {}
        if year_from:
            where_filter['year'] = {'$gte': year_from}
        if source:
            where_filter['source'] = source
        
        results = manager.query_collection(
            collection_name="scientific_publications",
            query_texts=[query],
            n_results=min(n_results, 20),
            where=where_filter if where_filter else None
        )
        
        return results
    
    def _sparse_retrieval(self, query: str, n_results: int, year_from: Optional[int], source: Optional[str]):
        """Sparse BM25 keyword search"""
        self._initialize_bm25_retriever()
        
        if not self._bm25_index:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        tokenized_query = query.lower().split()
        
        bm25_scores = self._bm25_index.get_scores(tokenized_query)

        top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
        
        filtered_results = []
        for idx in top_indices:
            doc = self._bm25_documents[idx]
            metadata = self._bm25_metadatas[idx]
            score = bm25_scores[idx]
            
            if year_from and metadata.get('year', 0) < year_from:
                continue

            if source and metadata.get('source', '') != source:
                continue
            
            filtered_results.append((idx, doc, metadata, score))
            
            if len(filtered_results) >= n_results:
                break
        
        results = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        for idx, doc, metadata, score in filtered_results:
            results['ids'][0].append(f"bm25_{idx}")
            results['documents'][0].append(doc)
            results['metadatas'][0].append(metadata)
            results['distances'][0].append(1.0 / (1.0 + score) if score > 0 else 1.0)
        
        return results
    
    def _hybrid_retrieval(self, query: str, n_results: int, year_from: Optional[int], source: Optional[str], hybrid_weight: float):
        """Hybrid search combining dense and sparse"""
        dense_results = self._dense_retrieval(query, 20, year_from, source)
        
        sparse_results = self._sparse_retrieval(query, 20, year_from, source)

        combined_results = {}
        
        for idx, (doc_id, doc, metadata, distance) in enumerate(zip(
            dense_results['ids'][0],
            dense_results['documents'][0],
            dense_results['metadatas'][0],
            dense_results['distances'][0]
        )):
            dense_score = 1.0 / (1.0 + distance)
            
            doc_key = metadata.get('title', doc[:50])
            combined_results[doc_key] = {
                'document': doc,
                'metadata': metadata,
                'score': dense_score * hybrid_weight,
                'dense_rank': idx + 1,
                'sparse_rank': None
            }
        
        for idx, (doc, metadata) in enumerate(zip(
            sparse_results['documents'][0],
            sparse_results['metadatas'][0]
        )):
            sparse_score = 1.0 / (idx + 1)
            
            doc_key = metadata.get('title', doc[:50])
            
            if doc_key in combined_results:
                combined_results[doc_key]['score'] += sparse_score * (1 - hybrid_weight)
                combined_results[doc_key]['sparse_rank'] = idx + 1
            else:
                combined_results[doc_key] = {
                    'document': doc,
                    'metadata': metadata,
                    'score': sparse_score * (1 - hybrid_weight),
                    'dense_rank': None,
                    'sparse_rank': idx + 1
                }
        
        sorted_results = sorted(
            combined_results.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:n_results]
        
        results = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]],
            'scores': [[]],
            'ranks': [[]]
        }
        
        for doc_key, data in sorted_results:
            results['ids'][0].append(doc_key)
            results['documents'][0].append(data['document'])
            results['metadatas'][0].append(data['metadata'])
            results['distances'][0].append(1.0 - data['score'])
            results['scores'][0].append(data['score'])
            results['ranks'][0].append({
                'dense': data['dense_rank'],
                'sparse': data['sparse_rank']
            })
        
        return results
    
    def _run(
        self, 
        query: str, 
        n_results: int = 5, 
        strategy: str = "hybrid",
        year_from: Optional[int] = None, 
        source: Optional[str] = None,
        hybrid_weight: float = 0.5
    ) -> str:
        """Execute search with specified strategy"""
        
        try:
            if strategy == "dense":
                results = self._dense_retrieval(query, n_results, year_from, source)
                strategy_name = "DENSE (Semantic Embeddings)"
            elif strategy == "sparse":
                results = self._sparse_retrieval(query, n_results, year_from, source)
                strategy_name = "SPARSE (BM25 Keyword)"
            elif strategy == "hybrid":
                results = self._hybrid_retrieval(query, n_results, year_from, source, hybrid_weight)
                strategy_name = f"HYBRID (Dense={hybrid_weight:.0%}, Sparse={1-hybrid_weight:.0%})"
            else:
                return f"Invalid strategy: {strategy}. Use 'dense', 'sparse', or 'hybrid'."
            
            if not results or not results.get('ids') or len(results['ids'][0]) == 0:
                return f"No publications found using {strategy_name} strategy.\nTry: broader query, different strategy, or remove filters."

            formatted_results = []
            formatted_results.append(f"strategy: {strategy_name}")
            formatted_results.append(f"query: '{query}'")
            formatted_results.append(f"found {len(results['ids'][0])} publications\n")
            formatted_results.append("\n")
            
            for idx, (doc_id, document, metadata) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0]
            )):
                formatted_results.append(f"\n{idx + 1}. {metadata.get('title', 'Untitled')}\n")
                formatted_results.append(f"Authors: {metadata.get('authors', 'Unknown')}\n")
                formatted_results.append(f"Year: {metadata.get('year', 'N/A')}\n")
                formatted_results.append(f"Journal: {metadata.get('journal', 'N/A')}\n")
                
                doi = metadata.get('doi', '')
                arxiv_id = metadata.get('arxiv_id', '')
                if doi:
                    formatted_results.append(f"DOI: {doi}\n")
                if arxiv_id:
                    formatted_results.append(f"arXiv: {arxiv_id}\n")
                
                formatted_results.append(f"Source: {metadata.get('source', 'Unknown')}\n")
                
                quality = metadata.get('quality_rating', '')
                if quality:
                    formatted_results.append(f"Quality: {quality}\n")
                
                chunk_idx = metadata.get('chunk_index', 0)
                total_chunks = metadata.get('total_chunks', 1)
                formatted_results.append(f"Chunk: {chunk_idx + 1} of {total_chunks}\n")
                
                if strategy == "hybrid" and 'ranks' in results:
                    ranks = results['ranks'][0][idx]
                    rank_info = []
                    if ranks.get('dense'):
                        rank_info.append(f"Dense: #{ranks['dense']}")
                    if ranks.get('sparse'):
                        rank_info.append(f"Sparse: #{ranks['sparse']}")
                    if rank_info:
                        formatted_results.append(f"Ranking: {', '.join(rank_info)}\n")
                    
                    if 'scores' in results:
                        formatted_results.append(f"Combined Score: {results['scores'][0][idx]:.3f}\n")
  
                if idx < len(results['distances'][0]):
                    distance = results['distances'][0][idx]
                    relevance = 1 - distance if distance <= 1 else 0
                    formatted_results.append(f"Relevance: {relevance:.3f}\n")
                
                formatted_results.append(f"\nFull Chunk:\n{document}\n")
                formatted_results.append("\n")
            
            return "".join(formatted_results)
            
        except Exception as e:
            return f"Error during {strategy} retrieval: {str(e)}\nPlease check if vector store is initialized."


if __name__ == "__main__":
    tool = RetrievalTool()
    test_query = "test query"
    
