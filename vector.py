import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from utils import read_json
import math
# Load environment variables
load_dotenv()
# Get API Keys from .env
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Validate API keys
if not PINECONE_API_KEY or not OPENAI_API_KEY:
    raise ValueError("Missing API key(s). Check your .env file.")

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

class PineconeManager:
    """Manage Pinecone vector database operations."""
    
    def __init__(self , PINECONE_API_KEY, OPENAI_API_KEY  ):
        try: 
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=OPENAI_API_KEY)
            self.indexes = self.pc.list_indexes().names()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Pinecone: {e}")

    def create_index(self, index_name):
        """Create a Pinecone index if it doesn't exist."""
        if index_name in self.indexes:
            raise ValueError(f"Index '{index_name}' already exists.")
        
        try:
            self.pc.create_index(
                name=index_name,
                dimension=1536,
                metric="cosine",
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
            )
        except Exception as e:
            raise RuntimeError(f"Error creating index '{index_name}': {e}")

    def delete_index(self, index_name):
        """Delete an existing Pinecone index."""
        if index_name in self.indexes:
            try:
                self.pc.delete_index(index_name)
                self.indexes.remove(index_name)
            except Exception as e:
                raise RuntimeError(f"Error deleting index '{index_name}': {e}")

    def get_vector_store(self, index_name):
        """Retrieve vector store for an existing index."""
        if index_name not in self.indexes:
            raise ValueError(f"Index '{index_name}' does not exist.")
        return PineconeVectorStore.from_existing_index(index_name, self.embeddings)

    def similarity_search(self, index_name, query, top_k=4, namespace=None ):
        """Retrieve top-K most similar vectors."""
        vector_store = self.get_vector_store(index_name)
        return vector_store.similarity_search_with_score(query, k=top_k, namespace=namespace)

    def add_index(self, index_name, json_data_path, is_question_data=False):
        """Add data (chapter/questions) to Pinecone index."""
        if index_name in self.indexes:
            self.delete_index(index_name)
        
        self.create_index(index_name)
        data = read_json(json_data_path)
        docs = []

        if is_question_data:
            # Format: Questions with Answers
            for category, items in data.items():
                content= ""
                if len (items) <10 :
                    for i in items :
                        content+=f"{i['Question']}\nAnswer: {i['Answer']} \n" 
                    docs.append(
                        Document(
                            page_content=content,
                            metadata={"category": category}
                        )
                    )
                    
                    continue 
                else :        
    
                    rounded_up = math.ceil(len(items)/10)
                    items_num_in_loop=math.ceil(len(items)/rounded_up)
                    for i in range (rounded_up): 
                        content=""
                        if i == rounded_up-1: 
                            
                            
                            for i in items[(items_num_in_loop*i): ] :
                                content+=f"{i['Question']}\nAnswer: {i['Answer']} \n" 
                                docs.append(
                                Document(
                                    page_content=content,
                                    metadata={"category": category}
                                )
                            )
                        else :
                            
                            for i in items[items_num_in_loop*i-1: items_num_in_loop*(i+1) ] :
                                content+=f"this is the questiion {i['Question']}\nthis is the answer Answer: {i['Answer']} \n" 
                                docs.append(
                                Document(
                                    page_content=content,
                                    metadata={"category": category}
                                )
                            )
                                
                       
        else:
            # Format: Chapters with Headers
            history = ""
            for item in data:
                if item['content']:
                    docs.append(
                        Document(
                            page_content=item['content'],
                            metadata={"title": history if history else None, "header": item['header']}
                        )
                    )
                else:
                    history = item['header']

        # Store documents in Pinecone
        PineconeVectorStore.from_documents(docs, self.embeddings, index_name=index_name)
        print(f"Documents successfully stored in Pinecone index: {index_name}")

# Example Usage:
#manager = PineconeManager(PINECONE_API_KEY , OPENAI_API_KEY)
#print(manager.indexes)
#manager.add_index("questions3", "questions/faq_data_moc_updated.json", is_question_data=True)

#manager.add_index("chapter1", "chapters/data.json", is_question_data=False)
#print(manager.similarity_search( "questions2","كيف يمكن الإستفسار عن المجال العام والخاص للأنشطة؟"))
#print(PINECONE_API_KEY)