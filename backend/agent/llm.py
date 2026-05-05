"""
LLM client wrapper using OpenAI SDK with GenSpark proxy.
Supports GENSPARK_TOKEN, OPENAI_API_KEY, or ~/.genspark_llm.yaml config.
"""
import os
from openai import OpenAI

def _load_config():
    """Load API key and base URL — priority: GSK_TOKEN > GENSPARK_TOKEN > OPENAI_API_KEY > yaml."""
    # GSK_TOKEN is the primary token for GenSpark sandbox
    api_key = (
        os.environ.get("GSK_TOKEN")
        or os.environ.get("GENSPARK_TOKEN")
        or os.environ.get("OPENAI_API_KEY")
    )
    base_url = os.environ.get(
        "OPENAI_BASE_URL",
        "https://www.genspark.ai/api/llm_proxy/v1"
    )
    # Fallback: read from yaml config
    if not api_key:
        try:
            import yaml
            cfg_path = os.path.expanduser("~/.genspark_llm.yaml")
            with open(cfg_path) as f:
                cfg = yaml.safe_load(f)
            raw_key = cfg.get("openai", {}).get("api_key", "")
            if raw_key.startswith("${") and raw_key.endswith("}"):
                var_name = raw_key[2:-1]
                api_key = os.environ.get(var_name, "")
            else:
                api_key = raw_key
            base_url = cfg.get("openai", {}).get("base_url", base_url)
        except Exception:
            pass
    return api_key, base_url

def get_client() -> OpenAI:
    api_key, base_url = _load_config()
    return OpenAI(api_key=api_key, base_url=base_url)

def chat(
    system: str,
    user: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_completion_tokens: int = 4000,
) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
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
