import re
from pathlib import Path

from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv
import os

DATA_PATH = "data/ai_test_bug_report.txt"
COLLECTION_NAME = "internal-bug-reports"


def parse_bugs_from_txt(path: str) -> list[Document]:
    
    documents = list()
    fields = {
        "bug_number": r"Bug\s+#(\d+)",
        "title": r"Title:\s*(.+)",
        "description": r"Description:\s*(.+?)(?:\n[A-Z][\w ]+:|\Z)",
        "steps": r"Steps to Reproduce:\s*(.+?)(?:\n[A-Z][\w ]+:|\Z)",
        "environment": r"Environment:\s*(.+?)(?:\n[A-Z][\w ]+:|\Z)",
        "severity": r"Severity:\s*(.+?)(?:\n[A-Z][\w ]+:|\Z)",
        "proposed_fix": r"Proposed Fix:\s*(.+?)(?:\n[A-Z][\w ]+:|\Z)",
    }

    text_in_file = Path(path).read_text(encoding="utf-8")
    issue_entries = re.split(r"\n{2,}", text_in_file.strip())
    
    for issue in issue_entries:
        issue_in_dict = dict()
        for key, pattern in fields.items():
            match = re.search(pattern, issue, re.DOTALL)
            issue_in_dict[key] = match.group(1).strip() if match else None

        combined_text = f"{issue_in_dict["title"]}\n\n{issue_in_dict["description"]}"
        documents.append(
            Document(
                page_content=combined_text,
                metadata={"issue_number": issue_in_dict.get("bug_number"),
                          "steps": issue_in_dict.get("steps"),
                          "environment": issue_in_dict.get("environment"),
                          "severity": issue_in_dict.get("severity"),
                          "severity": issue_in_dict.get("severity"),
                          "proposed_fix": issue_in_dict.get("proposed_fix")
                        }
                )
            )
    return documents


def ingest(api_key):
    client = QdrantClient(host="localhost", port=6333)

    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

    docs = parse_bugs_from_txt(DATA_PATH)
    embeddings = OpenAIEmbeddings(api_key=api_key)

    Qdrant.from_documents(
        docs,
        embeddings,
        url="http://localhost:6333",  # or your Qdrant URL
        collection_name=COLLECTION_NAME
    )

    print(f"Ingested {len(docs)} bugs into Qdrant.")


if __name__ == "__main__":
    client = QdrantClient(host="localhost", port=6333)
    client.delete_collection(collection_name=COLLECTION_NAME)
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    ingest(api_key)
