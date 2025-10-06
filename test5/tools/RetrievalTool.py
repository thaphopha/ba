from crewai.tools import BaseTool
from typing import Type, Optional, Literal
from pydantic import BaseModel, Field, field_validator
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


    @field_validator('year_from', mode='before')
    @classmethod
    def validate_year_from(cls, v):
        """Handle LLM passing 'None' as string"""
        if isinstance(v, str) and v.lower() == "none":
            return None
        return v
    
    @field_validator('source', mode='before')
    @classmethod  
    def validate_source(cls, v):
        """Handle LLM passing 'None' as string"""
        if isinstance(v, str) and v.lower() == "none":
            return None
        return v


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

            collection = manager.client.get_or_create_collection(name="scientific_publications")

            
            all_data = collection.get(include=["documents", "metadatas"])
            
            if not all_data['documents']:
                return
            
            
            self._bm25_documents = all_data['documents']
            self._bm25_metadatas = all_data['metadatas']
            
            # Tokenize documents for BM25 (simple whitespace tokenization)
            tokenized_corpus = [doc.lower().split() for doc in self._bm25_documents]
            
            # Initialize BM25 index
            self._bm25_index = BM25Okapi(tokenized_corpus)
            
        except Exception as e:
            raise Exception(f"Failed to initialize BM25 index: {e}")
    
    def _dense_retrieval(self, query: str, n_results: int, year_from: Optional[int], source: Optional[str]):
        """Dense vector search using embeddings"""
        manager = self._get_chroma_manager()
        
        # Build metadata filter
        where_filter = {}
        if year_from:
            where_filter['year'] = {'$gte': year_from}
        if source:
            where_filter['source'] = source
        
        # Query with dense embeddings
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
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get BM25 scores for all documents
        bm25_scores = self._bm25_index.get_scores(tokenized_query)
        
        # Get top documents with scores
        top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
        
        # FILTERS
        filtered_results = []
        for idx in top_indices:
            doc = self._bm25_documents[idx]
            metadata = self._bm25_metadatas[idx]
            score = bm25_scores[idx]
            
            # Year filter
            if year_from and metadata.get('year', 0) < year_from:
                continue
            
            # Source filter
            if source and metadata.get('source', '') != source:
                continue
            
            filtered_results.append((idx, doc, metadata, score))
            
            # Stop once we have enough results
            if len(filtered_results) >= n_results:
                break
        
        # Format results to match ChromaDB structure
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
            # Convert BM25 score to distance (higher score = lower distance)
            results['distances'][0].append(1.0 / (1.0 + score) if score > 0 else 1.0)
        
        return results
    
    def _hybrid_retrieval(self, query: str, n_results: int, year_from: Optional[int], source: Optional[str], hybrid_weight: float):
        """Hybrid search combining dense and sparse"""
        # Get dense results
        dense_results = self._dense_retrieval(query, 20, year_from, source)
        
        # Get sparse results
        sparse_results = self._sparse_retrieval(query, 20, year_from, source)
        
        # Combine and rerank based on hybrid_weight
        combined_results = {}
        
        # Add dense results with weight
        for idx, (doc_id, doc, metadata, distance) in enumerate(zip(
            dense_results['ids'][0],
            dense_results['documents'][0],
            dense_results['metadatas'][0],
            dense_results['distances'][0]
        )):
            # Normalize distance to score (lower distance = higher score)
            dense_score = 1.0 / (1.0 + distance)
            
            doc_key = metadata.get('title', doc[:50])
            combined_results[doc_key] = {
                'document': doc,
                'metadata': metadata,
                'score': dense_score * hybrid_weight,
                'dense_rank': idx + 1,
                'sparse_rank': None
            }
        
        # Add sparse results with weight
        for idx, (doc, metadata) in enumerate(zip(
            sparse_results['documents'][0],
            sparse_results['metadatas'][0]
        )):
            # BM25 rank-based score (higher rank = lower score)
            sparse_score = 1.0 / (idx + 1)
            
            doc_key = metadata.get('title', doc[:50])
            
            if doc_key in combined_results:
                # Document in both - combine scores
                combined_results[doc_key]['score'] += sparse_score * (1 - hybrid_weight)
                combined_results[doc_key]['sparse_rank'] = idx + 1
            else:
                # Document only in sparse
                combined_results[doc_key] = {
                    'document': doc,
                    'metadata': metadata,
                    'score': sparse_score * (1 - hybrid_weight),
                    'dense_rank': None,
                    'sparse_rank': idx + 1
                }
        
        # Sort by combined score
        sorted_results = sorted(
            combined_results.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:n_results]
        
        # Format results
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
            results['distances'][0].append(1.0 - data['score'])  # Convert score back to distance
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
            # Handle LLM passing "None" as string instead of null
            if isinstance(year_from, str) and year_from.lower() == "none":
                year_from = None
            if isinstance(source, str) and source.lower() == "none":
                source = None
                
            # Execute based on strategy
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
            
            # Format results
            formatted_results = []
            formatted_results.append(f"SEARCH STRATEGY: {strategy_name}")
            formatted_results.append(f"QUERY: '{query}'")
            formatted_results.append(f"Found {len(results['ids'][0])} publications\n")
            formatted_results.append("=" * 80 + "\n")
            
            for idx, (doc_id, document, metadata) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0]
            )):
                formatted_results.append(f"\n{idx + 1}. {metadata.get('title', 'Untitled')}\n")
                formatted_results.append(f"   Authors: {metadata.get('authors', 'Unknown')}\n")
                formatted_results.append(f"   Year: {metadata.get('year', 'N/A')}\n")
                formatted_results.append(f"   Journal: {metadata.get('journal', 'N/A')}\n")
                
                # Add identifiers
                doi = metadata.get('doi', '')
                arxiv_id = metadata.get('arxiv_id', '')
                if doi:
                    formatted_results.append(f"   DOI: {doi}\n")
                if arxiv_id:
                    formatted_results.append(f"   arXiv: {arxiv_id}\n")
                
                formatted_results.append(f"   Source: {metadata.get('source', 'Unknown')}\n")
                
                quality = metadata.get('quality_rating', '')
                if quality:
                    formatted_results.append(f"   Quality: {quality}\n")
                
                # Add chunk info
                chunk_idx = metadata.get('chunk_index', 0)
                total_chunks = metadata.get('total_chunks', 1)
                formatted_results.append(f"   Chunk: {chunk_idx + 1} of {total_chunks}\n")
                
                # Strategy-specific info
                if strategy == "hybrid" and 'ranks' in results:
                    ranks = results['ranks'][0][idx]
                    rank_info = []
                    if ranks.get('dense'):
                        rank_info.append(f"Dense: #{ranks['dense']}")
                    if ranks.get('sparse'):
                        rank_info.append(f"Sparse: #{ranks['sparse']}")
                    if rank_info:
                        formatted_results.append(f"   Ranking: {', '.join(rank_info)}\n")
                    
                    if 'scores' in results:
                        formatted_results.append(f"   Combined Score: {results['scores'][0][idx]:.3f}\n")
                
                # Add distance/relevance
                if idx < len(results['distances'][0]):
                    distance = results['distances'][0][idx]
                    relevance = 1 - distance if distance <= 1 else 0
                    formatted_results.append(f"   Relevance: {relevance:.3f}\n")
                
                # Add full chunk content
                formatted_results.append(f"\n   Full Chunk:\n   {document}\n")
                formatted_results.append("-" * 80 + "\n")
            
            return "".join(formatted_results)
            
        except Exception as e:
            return f"Error during {strategy} retrieval: {str(e)}\nPlease check if vector store is initialized."


# For standalone testing
if __name__ == "__main__":
    print("\nTesting Multi-Strategy Retrieval Tool\n")
    print("=" * 80)
    
    tool = RetrievalTool()
    
    test_query = "context management"
    
    print("\n1. DENSE ONLY")
    print("-" * 80)
    result = tool._run(query=test_query, n_results=3, strategy="dense")
    print(result)
    
    print("\n\n2. SPARSE ONLY (BM25)")
    print("-" * 80)
    result = tool._run(query=test_query, n_results=3, strategy="sparse")
    print(result)
    
    print("\n\n3. HYBRID (50/50)")
    print("-" * 80)
    result = tool._run(query=test_query, n_results=3, strategy="hybrid", hybrid_weight=0.5)
    print(result)
