
import asyncio
import os
from pyexpat.errors import messages

from dotenv import load_dotenv
from colorama import Fore
from autogen_agentchat.agents import AssistantAgent

from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_agentchat.agents import UserProxyAgent
from mem0 import MemoryClient

from fastapi import FastAPI
from pydantic import BaseModel

from utils import generate_image, pretty_stream, tavily_search_tool, spell_checker_tool
from rag import MemoryWrapper, rag_memory

load_dotenv(override=True)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = MemoryClient(api_key=os.getenv("MEM0_KEY"))
session_memory = ListMemory()


# Init
app = FastAPI(
    title="AI Agent API",
    description="API for LLM agents with tools (search, spellcheck, image)",
    version="1.0.0"
)

prompt_researcher = """
You are a research analyst.

Validate and enrich the content.
Your role:
- Validate facts
- Add missing insights
- Use tavily_search when information may be outdated or factual
- Give the results of your research (source and conclusions) in a clear and structured way (bullet points, sections, etc.)

Output:
- Improved version of the content with factual enrichment

Output format:
When research is complete, write:  ✅ RESEARCH COMPLETE
"""

prompt_editor1 = """

You are a professional editor working for a publishing company.

Write a high-quality structured article.

Your role:
- Write high-quality, engaging, and structured content
- Use clear sections and educational tone
- Make it publication-ready (book/article level)
- If it's ready → respond ONLY with: ✅ DRAFT READY FOR REVIEW

Rules:
- Be clear and pedagogical
- Use examples when helpful
- Avoid spelling mistakes

Write a high-quality article.

Output format:
When the copy is ready, write : ✅ DRAFT READY FOR REVIEW
"""


prompt_editor2 = """

You are a senior writer working for a publishing company.

Improve clarity and fix grammar using spell_checker_tool.

Your role:
- Improve clarity and structure
- Fix grammar and spelling using spell_checker_tool
- If it's ready → respond ONLY with: EDITED

Rules:
- ALWAYS call spell_checker_tool before returning final answer

Output format:
When the review is complete, write : ✅ READY FOR REVIEW
"""

prompt_reviewer = """
You are a publishing reviewer.


Your role:
- Evaluate content quality
- If it's ready → respond ONLY with: APPROVE or REJECT
- Otherwise → give clear improvement feedback

Following guidelines strictly: {guidelines}

Review the content.

If good:
STATUS: APPROVE

If not:
STATUS: REJECT

IMPORTANT:
Return ONLY the status line.
"""

prompt_reviewer = """
You are a senior publishing reviewer and quality controller.

Your role:
- Evaluate content quality
- Decide if the article is ready for publication
- Follow the evaluation guidelines strictly
- Indicate every step of your evaluation process along with guideline application. Be transparent and detailed in your reasoning.

---

## EVALUATION GUIDELINES

{guidelines}

---

## Instructions

- Carefully review the provided content against ALL guidelines.
- Do NOT ignore any criterion.
- Be strict and consistent in your evaluation.

---

## Decision Rules

- If ALL criteria are satisfied:
    → Respond ONLY with: APPROVE

- If ANY criterion fails:
    → Respond ONLY with: REJECT

---

Output format:
When evaluation is complete, write 

If good:
✅  REVIEW COMPLETE - APPROVE

If not:
❌ REJECT - NEEDS IMPROVEMENT
"""

prompt_image = """
You are an illustrator for a publishing company.

Generate an illustration prompt from the content.

OUTPUT FORMAT:
{
  "status": "IMAGE",
  "prompt": "<image description>"
}

Your role:
- Generate a high-quality illustration prompt based on the content
- The style should match a book illustration or editorial artwork
"""

# Define a model client. You can use other model client that implements
# the `ChatCompletionClient` interface.
model = OpenAIChatCompletionClient(
  model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY"),
)


researcher = AssistantAgent(
    "researcher",
    model_client=model,
    system_message=prompt_researcher,
    tools=[tavily_search_tool],
    memory=[session_memory]
)

editor1 = AssistantAgent("editor", model_client=model, system_message=prompt_editor1, tools=[spell_checker_tool], memory=[session_memory],)

editor2 = AssistantAgent(
    "senior_editor",
    model_client=model,
    system_message=prompt_editor2,
    tools=[spell_checker_tool],
    memory=[session_memory]
)

reviewer = AssistantAgent(
    "reviewer",
    model_client=model,
    system_message=prompt_reviewer,
    memory=[rag_memory],
)

illustrator = AssistantAgent(
    "illustrator",
    model_client=model,
    system_message=prompt_image,
)

user_proxy = UserProxyAgent("user_proxy")


# Build the graph
builder = DiGraphBuilder()

builder.add_node(researcher)
builder.add_node(editor1)
builder.add_node(editor2)
builder.add_node(reviewer)
builder.add_node(illustrator)

# Flow simple (aucune condition)
builder.add_edge(researcher, editor1)
builder.add_edge(editor1, editor2)
builder.add_edge(editor2, reviewer)
builder.add_edge(reviewer, illustrator)

builder.set_entry_point(researcher)

# Build and validate the graph
graph = builder.build()

# Create the flow
flow = GraphFlow([researcher, editor1, editor2, reviewer, illustrator], graph=graph)

class InputRequest(BaseModel):
    input: str
# Use `asyncio.run(...)` and wrap the below in a async function when running in a script.

@app.post("/run")
async def run(request: InputRequest):
    try:
        results = client.search(request.input, filters={"user_id": "rag_memory"}, limit=5)
        
        stream = flow.run_stream(
            task=f"{request.input}\n\nPrevious related information:\n{results}"
        )
        summary = await pretty_stream(stream)

        messages = [
            {"role": "user", "content": request.input},   # ← was undefined `user_input`
            {"role": "assistant", "content": summary}
        ]
        client.add(messages, user_id="rag_memory")

        return {"summary": summary}                        # ← always return a dict

    except Exception as e:                                 # ← single except block
        print(Fore.RED + f"Error: {str(e)}" + Fore.RESET)
        return JSONResponse(status_code=500, content={"error": str(e)})


# Entry point
if __name__ == "__main__":
    while True:
        user_input = input(f"\n👤 {Fore.CYAN}Enter your task: {Fore.RESET} ")
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting...")
            break
        asyncio.run(run(user_input))





