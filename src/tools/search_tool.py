from langchain.tools import tool
from qdrant_client import QdrantClient
from langchain_community.embeddings import OpenAIEmbeddings

BUG_COLLECTION_NAME = "internal-bug-reports"
FEEDBACK_COLLECTION_NAME = "user-feedbacks"

@tool
def search_bug_reports(query: str) -> dict:
    """search information in bug reports. Searches internal bug reports by semantic meaning from user query."""
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
    result = dict()
    for hit in hits:
        bug_content = hit.payload
        bug_meta_data = bug_content.get("metadata")
        bug_meta_data["content"] = bug_content.get('page_content')
        bug_number = bug_meta_data.pop('bug_number')
        result[bug_number] = bug_meta_data

    return result

@tool
def search_user_feedbacks(query: str) -> dict:
    """search information in user feedback reports. Searches user feedback reports by semantic meaning from user query."""
    embeddings = OpenAIEmbeddings()
    client = QdrantClient(host="localhost", port=6333)

    vector = embeddings.embed_query(query)
    hits = client.search(
        collection_name=FEEDBACK_COLLECTION_NAME,
        query_vector=vector,
        limit=3,
        with_payload=True
    )

    if not hits:
        return "No relevant user feedbacks found."

    result = dict()
    for hit in hits:
        feedback_content = hit.payload
        feedback_meta_data = feedback_content.get("metadata")
        feedback_meta_data["content"] = feedback_content.get('page_content')
        feedback_id = feedback_meta_data.pop('feedback_id')
        result[feedback_id] = feedback_meta_data

    return result