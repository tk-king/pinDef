from src.Pipeline import PipelineStep
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src.llm_inputs import VersionComponent
from langchain_openai import OpenAIEmbeddings
from src.DB import Component

from src.config import OPENAI_EMBEDDINGS_MODEL

class TextRag(PipelineStep):
    def __init__(self, query: VersionComponent, num_results=20, metric="similarity"):
        super().__init__()
        self.query = query
        self.embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)
        self.num_results = num_results
        self.metric = metric
        # self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.overlap)

    def step_key(self):
        return f"{self.query.version}_{self.num_results}_{self.metric}"
    
    def get_display_name(self):
        return "TextRAG"

    def invoke(self, input, c: Component):
        documents = [Document(page_content=data["text"], metadata={"page": data["page"]}) for data in input]
        
        # Generate a compliant collection name
        # Remove special characters and spaces from component name
        clean_name = ''.join(e for e in c.name if e.isalnum() or e == '_')
        # Ensure it doesn't start with numbers
        if clean_name and not clean_name[0].isalpha():
            clean_name = 'col_' + clean_name
        # Add a timestamp hash (numeric only)
        import time
        timestamp_hash = str(abs(hash(str(time.time()))))
        collection_name = f"{clean_name}_{timestamp_hash}"
        
        # Make sure name is within length limits (3-63 chars)
        if len(collection_name) < 3:
            collection_name = 'col_' + collection_name
        if len(collection_name) > 63:
            collection_name = collection_name[:60] + collection_name[-3:]
        
        # Create a client and explicitly delete any existing collection with this name
        import chromadb
        client = chromadb.Client()
        try:
            client.delete_collection(collection_name)
        except:
            pass  # Collection might not exist yet
        
        # Create a new Chroma DB with the valid collection name
        db = Chroma.from_documents(
            documents=documents, 
            embedding=self.embeddings,
            collection_name=collection_name
        )
        
        print(f"Component: {c.name}, ChromaDB size: {db._collection.count()}")
        retriever = db.as_retriever(search_type=self.metric, search_kwargs={"k": self.num_results})
        results = retriever.invoke(self.query.content)
        
        # Clean up by deleting the collection after use
        client.delete_collection(collection_name)
        
        return [{
            "text": result.page_content,
            "page": result.metadata["page"]
        } for result in results]