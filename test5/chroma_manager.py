import chromadb
from chromadb.config import Settings
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaManager:
    """Manages ChromaDB vector database operations"""
    
    def __init__(self, persist_directory="./chroma_db"):
        """
        Initialize ChromaDB client with persistent storage
        
        Args:
            persist_directory: Path to store the ChromaDB database
        """
        self.persist_directory = persist_directory
        self.client = None
        
    def connect(self):
        """Initialize ChromaDB client"""
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            return True
        except Exception as e:
            raise
    
    def list_collections(self):
        """
        List all collections in the database
        
        Returns:
            List of collection names
        """
        try:
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            logger.info(f"Found {len(collection_names)} collections: {collection_names}")
            return collection_names
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def create_publications_collection(
        self,
        collection_name="scientific_publications",
        distance_metric="l2",
        drop_if_exists=False
    ):
        """
        Create a collection for storing scientific publications with embeddings
        
        Args:
            collection_name: Name of the collection
            distance_metric: Distance metric ("l2", "cosine", "ip")
            drop_if_exists: If True, drop existing collection with same name
            
        Returns:
            Collection object
        """
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "hnsw:space": distance_metric,
                    "description": f"Collection for scientific publications"
                }
            )
            
            logger.info(f"Created/Retrieved collection '{collection_name}' with {distance_metric} distance metric")
            logger.info(f"   Metadata fields: paper_id, title, authors, year, journal, abstract")
            
            return collection
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def get_collection_info(self, collection_name):
        """
        Get information about a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection information
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            
            info = {
                "name": collection.name,
                "count": count,
                "metadata": collection.metadata,
            }
            
            logger.info(f"Collection info for '{collection_name}':")
            logger.info(f"   Documents: {count}")
            logger.info(f"   Metadata: {collection.metadata}")
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    def chunk_text(
        self,
        text,
        chunk_size=1000,
        chunk_overlap=200,
        separators=None
    ):
        """
        Chunk text using RecursiveCharacterTextSplitter
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            separators: List of separators to use (default: ["\\n\\n", "\\n", " ", ""])
            
        Returns:
            List of text chunks
        """
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
        )
        
        chunks = text_splitter.split_text(text)
        logger.info(f"Split text into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
        
        return chunks
    
    def chunk_documents(
        self,
        documents,
        chunk_size=1000,
        chunk_overlap=200
    ):
        """
        Chunk multiple documents
        
        Args:
            documents: List of documents to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of tuples (doc_index, chunk_text)
        """
        all_chunks = []
        
        for doc_idx, doc in enumerate(documents):
            chunks = self.chunk_text(doc, chunk_size, chunk_overlap)
            for chunk in chunks:
                all_chunks.append((doc_idx, chunk))
        
        logger.info(f"Chunked {len(documents)} documents into {len(all_chunks)} total chunks")
        
        return all_chunks
    
    def add_documents(
        self,
        collection_name,
        documents,
        metadatas,
        ids,
        embeddings=None
    ):
        """
        Add documents to a collection
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique IDs for documents
            embeddings: Optional pre-computed embeddings (ChromaDB can auto-generate)
        """
        try:
            collection = self.client.get_or_create_collection(name=collection_name)
            
            if embeddings:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
            else:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            
            logger.info(f"Added {len(documents)} documents to '{collection_name}'")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def add_chunked_documents(
        self,
        collection_name,
        documents,
        metadatas,
        base_ids,
        chunk_size=1000,
        chunk_overlap=200
    ):
        """
        Chunk documents and add them to collection with proper metadata
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts to chunk
            metadatas: List of metadata dicts for each document
            base_ids: List of base IDs for each document
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
        """
        try:
            chunked_docs = []
            chunked_metadatas = []
            chunked_ids = []
            
            for doc_idx, (doc, metadata, base_id) in enumerate(zip(documents, metadatas, base_ids)):
                chunks = self.chunk_text(doc, chunk_size, chunk_overlap)
                
                for chunk_idx, chunk in enumerate(chunks):
                    chunked_docs.append(chunk)
                    
                    
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = chunk_idx
                    chunk_metadata['total_chunks'] = len(chunks)
                    chunk_metadata['base_id'] = base_id
                    chunked_metadatas.append(chunk_metadata)
                    
                    
                    chunked_ids.append(f"{base_id}_chunk_{chunk_idx}")
            
            
            self.add_documents(
                collection_name=collection_name,
                documents=chunked_docs,
                metadatas=chunked_metadatas,
                ids=chunked_ids
            )
            
            logger.info(f"Added {len(documents)} documents as {len(chunked_docs)} chunks to '{collection_name}'")
            
        except Exception as e:
            logger.error(f"Failed to add chunked documents: {e}")
            raise
    
    def query_collection(
        self,
        collection_name,
        query_texts,
        n_results=10,
        where=None
    ):
        """
        Query a collection for similar documents
        
        Args:
            collection_name: Name of the collection
            query_texts: List of query texts
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Query results
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where
            )
            
            logger.info(f"Found {len(results['ids'][0])} results for query")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query collection: {e}")
            return {}


def main():
    manager = ChromaManager(persist_directory="./chroma_db")
    
    try:
        manager.connect()
        
        print("\nExisting collections:")
        collections = manager.list_collections()
        if collections:
            for col in collections:
                print(f"{col}")
        else:
            print("(none)")

        print("\nCreating 'scientific_publications' collection...")
        try:
            collection = manager.create_publications_collection(
                collection_name="scientific_publications",
                distance_metric="l2",
                drop_if_exists=False
            )
        except Exception:
            pass
        
        collections = manager.list_collections()
        for col in collections:
            print(f"{col}")
        
        print("\nCollection details:")
        info = manager.get_collection_info("scientific_publications")
        print(f"Name: {info.get('name')}")
        print(f"Documents: {info.get('count')}")
        print(f"Metadata: {info.get('metadata')}")
        
        print("\nSetup complete!")
        
    except Exception as e:
        print(f"\nError: {e}")
    
if __name__ == "__main__":
    main()
