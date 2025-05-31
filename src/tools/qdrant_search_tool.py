from langchain.tools import tool
from qdrant_client import QdrantClient
from langchain.embeddings import OpenAIEmbeddings

COLLECTION_NAME = "internal-bug-reports"

@tool
def search_bug_reports(query: str) -> str:
    """Search internal bug report database using semantic vector search."""
    embeddings = OpenAIEmbeddings()
    client = QdrantClient(host="localhost", port=6333)

    vector = embeddings.embed_query(query)
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=3,
        with_payload=True
    )

    if not hits:
        return "No relevant bug reports found."
    result = ""
    for hit in hits:
        bug_content = hit.payload
        bug_meta_data = bug_content.get("metadata")
        result += f"\nBug #{bug_meta_data.get('bug_number')}: {bug_meta_data.get('title')}\n{bug_content.get('page_content')}\n"

    return result.strip()
