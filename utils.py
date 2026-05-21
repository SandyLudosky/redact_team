import os
import json
import requests
from typing import Optional, Dict, Any
from spellchecker import SpellChecker
from tavily import TavilyClient
from rich.console import Console
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from dotenv import load_dotenv

from openai import OpenAI
import json
import base64

load_dotenv(override=True)

console = Console()
client = OpenAI()
spell = SpellChecker()
tavily = TavilyClient(api_key=os.getenv("TAVILY_KEY"))

# Initialize user memory
session_memory = ListMemory()

def get_status(msg):
    try:
        return json.loads(msg["content"]).get("status")
    except:
        return None
    
def spell_checker_tool(text: str) -> str:
    corrected = []
    for w in text.split():
        c = spell.correction(w)
        corrected.append(c if c else w)
    return " ".join(corrected)


def tavily_search_tool(query: str) -> str:
    response = tavily.search(query=query, search_depth="advanced", max_results=3)

    results = []
    for r in response["results"]:
        results.append(f"{r['title']}\n{r['content']}\n")

    return "\n".join(results)

def user_memory_tool(content: str, memory: ListMemory) -> str:
    memory.add(MemoryContent(content=content, mime_type=MemoryMimeType.TEXT))
    return "User input has been added to memory."


file_path = "image.png"
MODEL = "gpt-4.1-mini"

def generate_image(input):
    """Generates an image based on the provided description and saves it as output.png."""
    response = client.responses.create(
        model=MODEL,
        input=f"Generate an image based on the following description: {input}",
        tools=[{"type": "image_generation"}],
    )
    
    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]

    if image_data:
        image_base64 = image_data[0]
        image_bytes = base64.b64decode(image_base64)
   
        with open(file_path, "wb") as f:
            f.write(image_bytes)    
            
            return file_path
            

async def pretty_stream(stream):

    async for event in stream:

        if isinstance(event, TextMessage):
            role = event.source.upper()
            content = event.content.strip()

            if role == "USER":
                console.print(f"\n[bold yellow]👤 USER[/bold yellow] {content}")

            elif role == "WRITER":
                console.print(f"\n[bold cyan]✍️ WRITER[/bold cyan]\n{content}")

            elif role == "RESEARCHER":
                console.print(f"\n[bold blue]🔎 RESEARCHER[/bold blue]\n{content}")

            elif role == "EDITOR":
                console.print(f"\n[bold magenta]📝 EDITOR[/bold magenta]\n{content}")

            elif role == "REVIEWER":
                console.print(f"\n[bold green]👤 REVIEWER[/bold green]\n{content}")

        elif isinstance(event, TaskResult):
            console.print("\n[bold green]🏁 FINAL RESULT[/bold green]\n")
            for msg in event.messages:
                console.print(f"[bold]{msg.source.upper()}:[/bold] {msg.content}")
                return generate_summary(msg.content)
                


def generate_summary(content):
        response = client.responses.create(
            model="gpt-3.5-turbo",
            input=f"Summarize the following text in one sentence:{content}",
        )
        return response.output_text