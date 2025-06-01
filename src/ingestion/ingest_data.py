import re
from pathlib import Path

from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv
import os

BUG_DATA_PATH = "data/ai_test_bug_report.txt"
BUG_COLLECTION_NAME = "internal-bug-reports"

FEEDBACK_DATA_PATH = "data/ai_test_user_feedback.txt"
FEEDBACK_COLLECTION_NAME = "user-feedbacks"

def parse_bugs_from_txt(path: str) -> list[Document]:
    
    documents = list()
    pattern_map = {
        "bug_number": r"Bug\s+#(?P<bug_number>\d+)",
        "title": r"Title:\s*(?P<title>.+)",
        "description": r"Description:\s*(?P<description>.+?)(?=\n[A-Z][a-zA-Z ]+?:|\Z)",
        "steps": r"Steps to Reproduce:\s*(?P<steps>(?:\d+\..+\n?)+)",
        "environment": r"Environment:\s*(?P<environment>.+)",
        "severity": r"Severity:\s*(?P<severity>.+)",
        "proposed_fix": r"Proposed Fix:\s*(?P<proposed_fix>.+)",
    }

    text_in_file = Path(path).read_text(encoding="utf-8")
    issue_entries = re.split(r"\n{2,}", text_in_file.strip())
    
    for issue in issue_entries:
        issue_in_dict = dict()
        for key, pattern in pattern_map.items():
            match = re.search(pattern, issue, re.MULTILINE)
            issue_in_dict[key] = match.group(1).strip() if match else None
        combined_text = f"{issue_in_dict["title"]}. {issue_in_dict["description"]}"
        documents.append(
            Document(
                page_content=combined_text,
                metadata=issue_in_dict
                )
            )
    return documents

def parse_feedbacks_from_txt(path: str) -> list[Document]:
    documents: list[Document] = []
    feedback_pattern = re.compile(r"^Feedback\s+#(?P<id>\d+):\s*(?P<text>.+)$")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Skip the very first line
    for line in lines[1:]:
        if not line.strip():
            continue  # ignore blank lines
        m = feedback_pattern.match(line)
        if m:
            fid = m.group("id")
            text = m.group("text").strip()
            doc = Document(
                page_content=text,
                metadata={"feedback_id": fid}
            )
            documents.append(doc)
        else:
            continue

    return documents

def ingest(api_key):
    embeddings = OpenAIEmbeddings(api_key=api_key)
    client = QdrantClient(host="localhost", port=6333)

    if BUG_COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=BUG_COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

    if FEEDBACK_COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=FEEDBACK_COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
    # ingest bug information
    # docs = parse_bugs_from_txt(BUG_DATA_PATH)

    # Qdrant.from_documents(
    #     docs,
    #     embeddings,
    #     url="http://localhost:6333",
    #     collection_name=BUG_COLLECTION_NAME
    # )

    # print(f"Ingested {len(docs)} bugs into Qdrant.")

    # ingest feedback information
    docs = parse_feedbacks_from_txt(FEEDBACK_DATA_PATH)

    Qdrant.from_documents(
        docs,
        embeddings,
        url="http://localhost:6333",
        collection_name=FEEDBACK_COLLECTION_NAME
    )

    print(f"Ingested {len(docs)} feeds into Qdrant.")


if __name__ == "__main__":
    # client = QdrantClient(host="localhost", port=6333)
    # client.delete_collection(collection_name=COLLECTION_NAME)
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    ingest(api_key)
