from langchain.tools import tool
from qdrant_client import QdrantClient
from langchain.embeddings import OpenAIEmbeddings

BUG_COLLECTION_NAME = "internal-bug-reports"
FEEDBACK_COLLECTION_NAME = "user-feedbacks"

@tool
def search_bug_reports(query: str) -> str:
    """Search internal bug report database using semantic vector search."""
    embeddings = OpenAIEmbeddings()
    client = QdrantClient(host="localhost", port=6333)

    vector = embeddings.embed_query(query)
    hits = client.search(
        collection_name=BUG_COLLECTION_NAME,
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

@tool
def search_user_feedbacks(query: str) -> str:
    """
    Search the 'user-feedbacks' Qdrant collection using semantic vector search.
    Returns up to 3 hits or a "no results" message.
    """
    embeddings = OpenAIEmbeddings()
    client = QdrantClient(host="localhost", port=6333)

    # 1) Embed the query
    vector = embeddings.embed_query(query)

    # 2) Run Qdrant search
    hits = client.search(
        collection_name=FEEDBACK_COLLECTION_NAME,
        query_vector=vector,
        limit=3,
        with_payload=True
    )

    if not hits:
        return "No relevant user feedbacks found."

    result = ""
    for hit in hits:
        feedback_content = hit.payload
        feedback_meta_data = feedback_content.get("metadata")

        result += f"\nFeedback #{feedback_meta_data.get('feedback_id')}: {feedback_content.get('page_content')}\n"

    return result