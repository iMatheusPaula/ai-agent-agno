from agno.knowledge.json import JSONKnowledgeBase
from agno.vectordb.pgvector import PgVector

cardapio = JSONKnowledgeBase(
    path="cardapio.json",
    # Table name: ai.json_documents
    vector_db=PgVector(
        table_name="json_documents",
        db_url="postgresql+psycopg://ai:ai@pgvector:5432/ai",
    ),
)
