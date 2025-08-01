# ruff: noqa: E501, RUF001, UP007, D417, G004
from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING, List, Optional

import tiktoken
from llama_index.core.agent.workflow import (
    AgentOutput,
    FunctionAgent,
    ToolCallResult,
)
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

if TYPE_CHECKING:
    from .client import CRFAPIClient
    from .warehouse import Warehouse

# Configure logging
logger = logging.getLogger(__name__)


def dict_to_markdown(data, depth=0) -> str:
    md_lines = []
    indent = "  " * depth
    bullet = "-" if depth == 0 else "*"

    # Add current node's name and description
    name = data.get("name", "Unnamed")
    description = data.get("description", "")
    md_lines.append(f"{indent}{bullet} **{name}**")
    if description:
        md_lines.append(f"{indent}  {description}")
    # Recurse into children if any
    md_lines.extend(dict_to_markdown(child, depth + 1) for child in data.get("children", []))

    return "\n".join(md_lines)


SYSTEM_PROMPT = """

You are an expert with deep knowledge about {project_brief}.
────────────────────────────────
MISSION  :  WHAT YOU COVER

You are tasked with answering questions in your area of expertise describe above.
You will use the **Knowledge Warehouse** to find relevant information and provide accurate,
citation-backed answers.

All answers must draw on the **Knowledge Warehouse** .
**Query the warehouse exclusively with the provided tool.**

If a tool returns an empty list, do not reuse the same tool with a similar query.
Instead, use the other tool if relevant.

In any case, always indicate explicitely if your answer is not grounded on the content of the Warehouse and comes only from a general knowledge ([Model Knowledge]).

---------------------------------------
ORGANISATION OF KNOWLEDGE WAREHOUSE

You have access to a **Knowledge Warehouse** about {project_brief} that is organised around the
 following dimensions:
{tag_structure}

────────────────────────────────
ADDITIONAL INSTRUCTIONS  :

{additional_instructions}

────────────────────────────────
CITATION RULES - NO EXCEPTIONS
1. Every factual or regulatory statement needs a citation.
2. Format citations exactly as `[Reference <ID>]`. For example, `[Reference 5]`
   • Multiple sources: `[Reference <ID1>][Reference <ID2>]`. For example, `[Reference 5][Reference 6]`
3. The ID (ID1, ID2, etc.) is a natural number (1,2,3, etc.) found in the field "id" of a result item
4. If the warehouse lacks a direct source, cite `[Model Knowledge]`.
5. Place citations **inline, immediately after the sentence *or list item* they support**.
   • **For bullet/numbered lists, append the citation to *each* item, never as a block at the end.**
   • Example (partial list of mandatory label elements):
     - Name and address of the Responsible Person [Reference 5]
     - Nominal content (weight/volume) [Reference 6]

────────────────────────────────
ANSWERING METHOD
1. **Analyse the query**
   • Break it into parts and detect key topics to adress
    • Identify from the structure the type of dimensions and the associated values that are relevant
     to the query
    • Split the user query into sub-questions if needed, to ensure all dimensions - values are c
    overed.

2. **Gather evidence**
   • Reformulate the search if helpful and split it into various queries to the Knowledge Warehouse.
   • Use the warehouse tool to pull slightly more data than needed, then filter for relevance.
   • Capture **every** requested dimension (annex, limit, condition, etc.).

3. **Write the answer**
   • Address every sub-question or implicit request.
   • As much as possible, provide a quantitative answer supported by the warehouse.
   • Insert citations inline (see rules above).
   • **Exhaustive-list rule:**
     - If the user's words (e.g. "all", "complete", "exhaustive list") demand exhaustivity, return
     the *entire* list in one response—no truncation, no "let me know if you need more."
     - Provide *only* the fields requested.
       • Example: "List all chemical names that benefit from exemptions for
       hair-care products" → output **just the chemical names**, one per line/bullet, each with its own citation.
  • If the user asks for a list of all the chemicals in the warehouse, return the entire list.
   • For other requests, be precise **and concise**—include only what is relevant.

────────────────────────────────
GOAL
Deliver clear, legally accurate, citation-backed answers that prioritise **exhaustivity** where
demanded and **brevity** everywhere else.
"""


class KnowledgeAssistant:
    """Knowledge Assistant for the Knowledge Warehouse."""

    def __init__(
        self,
        llm_model_id: str,
        crf_client: CRFAPIClient,
        warehouse: Warehouse,
        tools: Optional[List[str]] = None,
        additional_instructions: str | None = None,
        reasoning_tree_ids: Optional[List[str]] = None,
    ):
        """
        Initialize the Knowledge Assistant.

        Args:
            llm_model_id: The LLM model ID to use (eg: gpt-4o-mini)
            crf_client: The CRF client instance
            project_id: The Warehouse ID
            warehouse: The warehouse client api object instance of Warehouse
            tools: The tools to use (eg: [SemanticSearchOnChunksTool(), SemanticSearchOnObjectsTool(enriched_with_chunks=True)])
            additional_instructions: The additional instructions to use (eg: "Answer in a concise way, in French.") that will be added to the system prompt
            reasoning_tree_ids: The IDs of the reasoning trees to use

        """
        logger.info(f"Initializing Knowledge Assistant with model: {llm_model_id}")

        # Store the CRF client
        self.crf_client = crf_client

        # Get the warehouse
        self.warehouse = warehouse
        self.project_id = self.warehouse.id
        self.project_brief = self.warehouse.business_brief

        # Prepare the assistant prompt
        # Build reasoning tree markdown if needed
        self.reasoning_tree_ids = reasoning_tree_ids or []

        md = ""
        if self.reasoning_tree_ids:
            extractor_list = self.warehouse.list_tag_extractors()
            reasoning_trees = [t for t in extractor_list if t["id"] in self.reasoning_tree_ids]
            for tag in reasoning_trees:
                md += dict_to_markdown(tag["tagging_tree"])
                md += "\n\n"

        self.additional_instructions = (
            additional_instructions if additional_instructions else "NO ADDITIONAL INSTRUCTIONS"
        )
        self.assistant_prompt = SYSTEM_PROMPT.format(
            project_brief=self.project_brief,
            tag_structure=md,
            additional_instructions=self.additional_instructions,
        )

        # Initialize the LLM
        self.llm_model_id = llm_model_id
        self.token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model(llm_model_id).encode
        )
        self.init_used_token()
        self.callback_manager = CallbackManager([self.token_counter])

        self.llm = OpenAI(model=llm_model_id, callback_manager=self.callback_manager)

        # Initialize the tools
        self.tools = tools or []
        self.function_tools = []
        for tool in self.tools:
            tool.set_assistant(self)
            self.function_tools.append(
                FunctionTool.from_defaults(
                    name=tool.tool_name,
                    description=tool.tool_description,
                    fn=tool.tool_function(),
                )
            )

        # Initialize the agent
        self.agent: FunctionAgent = FunctionAgent(
            name="Knowledge Assistant",
            description="A chat assistant that can answer questions about the knowledge warehouse.",
            tools=self.function_tools,
            llm=self.llm,
            system_prompt=self.assistant_prompt,
        )

        # Initializing the cache for links replacement
        self.cache_kw = []

        # Initializing the tool call history
        self.tool_call_history = []

        # Initializing the chat history
        self.chat_history = []

        logger.info("Knowledge Assistant initialization complete")

    # ===== TOOL CALL HISTORY =====
    def get_tool_call_history(self):
        """Get the tool call history."""
        return self.tool_call_history

    def log_tool_call(self, tool_name: str, params: dict, results: dict):
        """Add a tool call to the tool call history."""
        self.tool_call_history.append(
            {
                "tool_name": tool_name,
                "params": params,
                "results": results,
            }
        )

    # ===== CHAT =====
    def _run_agent(self, query: str):  # noqa: C901
        # Chat with the agent (including tool calls)
        async def async_generator():
            handler = self.agent.run(query, chat_history=self.chat_history.copy())
            async for event in handler.stream_events():
                yield event

        # Create a new event loop for this generator if there is no running one
        new_loop = False
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, safe to create a new one
            new_loop = True
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            # Convert async generator to sync
            async_gen = async_generator()
            while True:
                event = loop.run_until_complete(async_gen.__anext__())
                if isinstance(event, AgentOutput):
                    # Log agent output
                    self.delta_chat_history.append(event.response)
                if isinstance(event, ToolCallResult):
                    # Log tool call result
                    message = ChatMessage(
                        role="tool",
                        content=event.tool_output.content,
                        additional_kwargs={
                            "tool_call_id": event.tool_id,
                            "name": event.tool_output.tool_name,
                        },
                    )
                    self.delta_chat_history.append(message)

        except StopAsyncIteration:
            pass
        except Exception:
            logger.exception("Error during agent execution")
        finally:
            if new_loop:
                pending_tasks = asyncio.all_tasks(loop)
                if pending_tasks:
                    try:
                        loop.run_until_complete(
                            asyncio.wait_for(
                                asyncio.gather(*pending_tasks, return_exceptions=True), timeout=3.0
                            )
                        )
                    except Exception:
                        logger.exception("Error during task cleanup")

                loop.close()
        assistant_messages = [
            message for message in self.delta_chat_history if message.role == "assistant"
        ]
        if assistant_messages:
            return assistant_messages[-1]
        return None

    async def _run_async_agent(self, query: str):
        """Async version of _run_agent that works in an async context."""
        try:
            # Chat with the agent (including tool calls)
            handler = self.agent.run(query, chat_history=self.chat_history.copy())
            async for event in handler.stream_events():
                if isinstance(event, AgentOutput):
                    # Log agent output
                    self.delta_chat_history.append(event.response)
                if isinstance(event, ToolCallResult):
                    # Log tool call result
                    message = ChatMessage(
                        role="tool",
                        content=event.tool_output.content,
                        additional_kwargs={
                            "tool_call_id": event.tool_id,
                            "name": event.tool_output.tool_name,
                        },
                    )
                    self.delta_chat_history.append(message)
        except Exception:
            logger.exception("Error during async agent execution")

        assistant_messages = [
            message for message in self.delta_chat_history if message.role == "assistant"
        ]
        if assistant_messages:
            return assistant_messages[-1]
        return None

    def chat(self, query: str):
        """Chat with the assistant."""
        self.delta_chat_history = [ChatMessage(role="user", content=query)]
        response = self._run_agent(query)
        self.chat_history.extend(self.delta_chat_history)
        content = ""
        if response:
            content = response.content if response and hasattr(response, "content") else ""
        return self.replace_findings_with_links(content)

    async def achat(self, query: str):
        """Async chat with the assistant."""
        self.delta_chat_history = [ChatMessage(role="user", content=query)]
        response = await self._run_async_agent(query)
        self.chat_history.extend(self.delta_chat_history)
        content = ""
        if response:
            content = response.content if response and hasattr(response, "content") else ""
        return self.replace_findings_with_links(content)

    # ===== TOKEN COUNTER =====

    def init_used_token(self):
        """RAZ of the used tokens counters."""
        self.input_token_count_so_far = 0
        self.output_token_count_so_far = 0

    def get_used_tokens(self):
        """Get the used tokens since the last call to this method."""
        used_tokens_input = (
            self.token_counter.prompt_llm_token_count - self.input_token_count_so_far
        )
        used_tokens_output = (
            self.token_counter.completion_llm_token_count - self.output_token_count_so_far
        )
        self.input_token_count_so_far = self.token_counter.prompt_llm_token_count
        self.output_token_count_so_far = self.token_counter.completion_llm_token_count
        return used_tokens_input, used_tokens_output

    # ===== CACHE and Reference management =====
    def store_in_cache(self, results):
        """
        Store the results in the cache.

        The cache is used to store the results tool calls.
        It is used to replace the [Reference ####] with the corresponding links.
        We use the uuid of the object, if available, to uniquely identify it and avoid duplicates.
        We add a unique "id" field to the result so that the Agent to reference the object like [Reference <ID>]
        """
        uuids = {obj["uuid"] for obj in self.cache_kw if "uuid" in obj}
        last_id = max((obj["id"] for obj in self.cache_kw), default=0)
        for result in results:
            # Do not add the same object twice (if the uuid is not present, we add the object)
            uuid = result.get("uuid")
            if uuid in uuids:
                continue
            last_id += 1
            result["id"] = last_id
            self.cache_kw.append(result)
            if uuid:
                uuids.add(uuid)

    def replace_findings_with_links(self, text: str):
        """Replace all occurrences of [Reference ####] with links."""
        try:
            # Extract all IDs from the text
            id_matches = re.findall(r"\[Reference (.+?)\]", text)
            # Replace the IDs with the corresponding links
            for current_id in id_matches:
                # Remove the < and > from the ID if any
                clean_id = current_id.strip("<>")
                result = [obj for obj in self.cache_kw if str(obj["id"]) == str(clean_id)]
                if len(result) == 0:
                    continue
                # Use the most recent result if multiple matches (data integrity issue)
                result = result[-1]
                reference_url = result.get("reference_url")
                if reference_url:
                    text = text.replace(
                        f"[Reference {current_id}]",
                        f" *[Ref {result['id']}]({reference_url})* ",
                    )
                else:
                    text = text.replace(f"[Reference {current_id}]", "")
        except Exception:
            logger.exception("Unexpected error occurred while extracting link for finding")
        return text
