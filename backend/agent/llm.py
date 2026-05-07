"""
LLM client wrapper using OpenAI SDK with GenSpark proxy.
Supports GENSPARK_TOKEN, OPENAI_API_KEY, or ~/.genspark_llm.yaml config.
"""
import os
from typing import Any, Optional

from dotenv import load_dotenv

try:
    from langfuse.openai import OpenAI
except ModuleNotFoundError:
    from openai import OpenAI

load_dotenv()


def get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)

    return OpenAI(api_key=api_key)


def chat(
    system,
    user,
    model="gpt-4o-mini",
    max_completion_tokens=2000,
    trace_name: str = "agent-llm-call",
    metadata: Optional[dict[str, Any]] = None,
):
    client = get_client()

    kwargs = dict(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_completion_tokens,
    )
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def chat_with_history(
    system: str,
    messages: list,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_completion_tokens: int = 2000,
    trace_name: str = "agent-chat-response",
    metadata: Optional[dict[str, Any]] = None,
) -> str:
    client = get_client()
    all_messages = [{"role": "system", "content": system}] + messages

    kwargs = dict(
        model=model,
        messages=all_messages,
        temperature=temperature,
        max_tokens=max_completion_tokens,
    )
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
