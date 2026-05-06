"""
LLM client wrapper using OpenAI SDK with GenSpark proxy.
Supports GENSPARK_TOKEN, OPENAI_API_KEY, or ~/.genspark_llm.yaml config.
"""
import os
from openai import OpenAI

def get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    return OpenAI(api_key=api_key)

def chat(system, user, model="gpt-4o-mini", max_completion_tokens=2000):
    client = get_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_completion_tokens=max_completion_tokens,
    )

    return response.choices[0].message.content


def chat_with_history(
    system: str,
    messages: list,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_completion_tokens: int = 2000,
) -> str:
    client = get_client()
    all_messages = [{"role": "system", "content": system}] + messages
    response = client.chat.completions.create(
        model=model,
        messages=all_messages,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
    )
    return response.choices[0].message.content
