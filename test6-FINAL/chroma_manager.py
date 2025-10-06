import chromadb
from chromadb.config import Settings
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaManager:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        
    def connect(self):
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            return True
        except Exception as e:
            raise
    
    def list_collections(self):
        try:
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            logger.info(f"Found {len(collection_names)} collections: {collection_names}")
            return collection_names
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    def create_publications_collection(self, collection_name="scientific_publications", distance_metric="l2", drop_if_exists=False):
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "hnsw:space": distance_metric,
                    "description": f"Collection for scientific publications"
                }
            )
            
            logger.info(f"Created/Retrieved collection '{collection_name}' with {distance_metric} distance metric")
            logger.info(f"Metadata fields: paper_id, title, authors, year, journal, abstract")
            
            return collection
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def get_collection_info(self, collection_name):
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

    def chunk_text(self, text, chunk_size=1000, chunk_overlap=200, separators=None):
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

    def chunk_documents(self, documents, chunk_size=1000, chunk_overlap=200):
        all_chunks = []
        
        for doc_idx, doc in enumerate(documents):
            chunks = self.chunk_text(doc, chunk_size, chunk_overlap)
            for chunk in chunks:
                all_chunks.append((doc_idx, chunk))
        
        logger.info(f"Chunked {len(documents)} documents into {len(all_chunks)} total chunks")
        
        return all_chunks

    def add_documents(self, collection_name, documents, metadatas, ids, embeddings=None):
        try:
            # Get or create collection if it doesn't exist
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

    def add_chunked_documents(self, collection_name, documents, metadatas, base_ids, chunk_size=1000, chunk_overlap=200):
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

    def query_collection(self, collection_name, query_texts, n_results=10, where=None):
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
       
        try:
            collection = manager.create_publications_collection(
                collection_name="scientific_publications",
                distance_metric="l2",
                drop_if_exists=False
            )
        except Exception:
            pass
        
        print("\nCollections after creation:")
        collections = manager.list_collections()
        for col in collections:
            print(f"{col}")
        
        info = manager.get_collection_info("scientific_publications")
        print(f"Name: {info.get('name')}")
        print(f"Documents: {info.get('count')}")
        print(f"Metadata: {info.get('metadata')}")
    
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
