
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).parent
KB_DIR = BASE_DIR / "knowledge_base"

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

documents = []
sources = []

for file in KB_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    # Simple paragraph-based chunking
    for chunk in text.split("\n\n"):
        chunk = chunk.strip()
        if chunk:
            documents.append(chunk)
            sources.append(file.name)

index = None
if documents:
    embeddings = model.encode(documents, normalize_embeddings=True)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)


def search_knowledge(question: str, top_k: int = 3):
    if index is None or not documents:
        return []

    query_embedding = model.encode(
        [question], normalize_embeddings=True
    )
    scores, indices = index.search(
        query_embedding, min(top_k, len(documents))
    )

    results = []
    for score, i in zip(scores[0], indices[0]):
        if i >= 0 and float(score) >= 0.30:
            results.append({
                "source": sources[i],
                "content": documents[i],
                "score": round(float(score), 3),
            })

    return results
