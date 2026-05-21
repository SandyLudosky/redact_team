import re
import os
import asyncio
from colorama import Fore, Style

import aiofiles
import aiohttp
from typing import List
from pathlib import Path
from autogen_core.memory import Memory, MemoryContent, MemoryMimeType
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
from autogen_ext.models.openai import OpenAIChatCompletionClient

from autogen_core.memory import Memory, MemoryContent, MemoryMimeType


class SimpleDocumentIndexer:
    """Basic document indexer for AutoGen Memory."""

    def __init__(self, memory: Memory, chunk_size: int = 100, file_path: str = "") -> None:
        self.memory = memory
        self.chunk_size = chunk_size
        self.file_path = file_path

    def _load_data(self, file_path) -> str:
        with open(file_path, "r") as f:
            guidelines = f.read()
            return guidelines

    def _split_text(self, text: str) -> List[str]:
        """Split text into fixed-size chunks."""
        chunks: list[str] = []
        # Just split text into fixed-size chunks
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i : i + self.chunk_size]
            chunks.append(chunk.strip())
        return chunks

    async def index_documents(self) -> int:
        """Index documents into memory."""
        total_chunks = 0

        content = self._load_data(self.file_path)
        
        print(f"{Fore.GREEN}Loaded {self.file_path}{Style.RESET_ALL}")
        chunks = self._split_text(content)
        print(f"{Fore.YELLOW}Split content into {len(chunks)} chunks (chunk size: {self.chunk_size} characters){Style.RESET_ALL}")
        total_chunks += len(chunks)

        for i, chunk in enumerate(chunks):
            await self.memory.add(
                MemoryContent(
                    content=chunk, mime_type=MemoryMimeType.TEXT, metadata={"text": chunk, "chunk_index": i}
                )
            )
            print(f"Indexing chunk {i + 1}/{len(chunks)}'")
        return total_chunks

# Initialize vector memory
rag_memory = ChromaDBVectorMemory(
    config=PersistentChromaDBVectorMemoryConfig(
        collection_name="publishing_guidelines",
        persistence_path=os.path.join(str(Path.home()), ".chromadb"),
        k=3,  # Return top 3 results
        score_threshold=0.4,  # Minimum similarity score
    )
)

class MemoryWrapper(Memory):
    def __init__(self, vector_memory):
        self.vector_memory = vector_memory

    async def add(self, content: MemoryContent):
        return await self.vector_memory.add(content)

    async def query(self, query: str, **kwargs):
        return await self.vector_memory.query(query, **kwargs)
    
    async def retrieve_all(self):
        """
        Retrieve all documents from the vector store using a broad query.
        """
        results = await self.memory.query(
            query="*",   # broad query
            k=1000       # large enough to include all chunks
        )
        return results
        
# Index Documents
async def index_documents() -> None:
    await rag_memory.clear()  # Clear existing memory
    indexer = SimpleDocumentIndexer(memory=rag_memory, chunk_size=150, file_path="guidelines.txt")
    chunks: int = await indexer.index_documents()
    print(f"Indexed {chunks} chunks from guidelines.txt")

if __name__ == "__main__":
    asyncio.run(index_documents())