from pgvector.django import CosineDistance
from mechanic.models import KnowledgeDocument
from .embedding_service import generate_query_embedding


def search_knowledge(query, limit=5, max_distance=0.65):
    """
    Search PostgreSQL vector DB using cosine similarity.
    Filters by max_distance threshold (Cosine distance: 0 = identical, 1 = orthogonal).
    """
    # 1. Generate query embedding
    query_embedding = generate_query_embedding(query)

    if not query_embedding:
        print("[RAG WARNING] Query embedding returned empty or None.")
        return []

    # 2. Vector distance query
    documents = (
        KnowledgeDocument.objects
        .filter(embedding__isnull=False)
        .annotate(
            distance=CosineDistance("embedding", query_embedding)
        )
        .filter(distance__lte=max_distance)  # Only keep relevant matches
        .order_by("distance")[:limit]
    )

    results = []
    for doc in documents:
        results.append({
            "id": doc.id,
            "title": doc.title,
            "category": doc.category,
            "content": doc.content,
            "source": doc.source,
            "distance": float(doc.distance)
        })

    # 3. Corrected Debug Prints (iterating over `results` dict list)
    print("\n--- RAG SEARCH DEBUG ---")
    print(f"Query: '{query}'")
    print(f"Documents found count: {len(results)}")
    for idx, doc in enumerate(results):
        print(f" [{idx + 1}] Title: {doc['title']} | Category: {doc['category']} | Distance: {doc['distance']:.4f}")
    print("------------------------\n")

    return results


def build_context(results):
    """
    Convert retrieved documents into formatted context for Gemini.
    """
    if not results:
        return "No relevant mechanic knowledge was found in the database."

    context_parts = []
    for index, result in enumerate(results, start=1):
        context_parts.append(
            f"--- SOURCE {index} ---\n"
            f"Title: {result['title']}\n"
            f"Category: {result['category']}\n"
            f"Information:\n{result['content']}\n"
        )

    return "\n\n".join(context_parts)