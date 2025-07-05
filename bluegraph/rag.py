import asyncio
import nest_asyncio

import logging
from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

from . import api

nest_asyncio.apply()

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

async def initialize_rag(path):
    rag = LightRAG(
        working_dir=path,
        chunk_token_size=800,
        llm_model_func=api.sync_vivogpt,
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: api.embedding(texts),
        ),
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag

def main(path):
    # Initialize RAG instance
    return asyncio.run(initialize_rag(path))