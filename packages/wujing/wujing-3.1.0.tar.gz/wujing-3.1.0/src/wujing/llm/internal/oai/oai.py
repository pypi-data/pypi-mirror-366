from typing import Dict, List, Any

from openai import OpenAI


def oai(
    *,
    api_key: str,
    api_base: str,
    model: str,
    messages: List[Dict[str, str]],
    **kwargs: Any,
) -> str:
    client = OpenAI(
        api_key=api_key,
        base_url=api_base,
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        return resp.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"Failed to send request: {e}") from e
