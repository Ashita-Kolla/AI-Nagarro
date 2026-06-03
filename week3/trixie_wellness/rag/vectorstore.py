import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "rag", "knowledge")
DB_DIR = os.path.join(BASE_DIR, "rag", "vector_stores")

DOMAINS = ["mental_health", "workplace_productivity", "crisis_support"]

class MultiDomainRAG:
    _instance = None

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.stores = {}
        self._initialize_stores()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_documents(self, domain: str):
        file_path = os.path.join(KNOWLEDGE_DIR, f"{domain}.md")
        if not os.path.exists(file_path):
            print(f"Warning: Knowledge base for {domain} not found.")
            return []
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple chunking by Markdown headers
        sections = content.split("\n## ")
        docs = []
        for i, section in enumerate(sections):
            if i > 0:
                section = "## " + section
            docs.append(Document(page_content=section.strip(), metadata={"domain": domain}))
        return docs

    def _initialize_stores(self):
        os.makedirs(DB_DIR, exist_ok=True)
        for domain in DOMAINS:
            domain_db_path = os.path.join(DB_DIR, domain)
            
            if os.path.exists(os.path.join(domain_db_path, "index.faiss")):
                # Load existing vector store
                print(f"Loading vector store for {domain}...")
                self.stores[domain] = FAISS.load_local(domain_db_path, self.embeddings, allow_dangerous_deserialization=True)
            else:
                # Create and save new vector store
                print(f"Creating vector store for {domain}...")
                docs = self._load_documents(domain)
                if docs:
                    store = FAISS.from_documents(docs, self.embeddings)
                    store.save_local(domain_db_path)
                    self.stores[domain] = store
                else:
                    self.stores[domain] = None

    def retrieve(self, domain: str, query: str, k: int = 2) -> str:
        """Retrieves top-k context for a given domain and query."""
        if domain not in self.stores or self.stores[domain] is None:
            return ""
        
        try:
            results = self.stores[domain].similarity_search(query, k=k)
            context = "\n\n".join([doc.page_content for doc in results])
            return context
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return ""

def get_rag():
    return MultiDomainRAG.get_instance()
