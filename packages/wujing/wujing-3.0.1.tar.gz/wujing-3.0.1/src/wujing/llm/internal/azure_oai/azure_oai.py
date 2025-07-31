from typing import Dict, List
from typing import Any
from openai import AzureOpenAI
from wujing.llm.types import ResponseModelType
from typing import Type
from pydantic import validate_call


@validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
def azure_oai(
    *,
    api_key: str,
    api_version: str,
    azure_endpoint: str,
    model: str,
    messages: List[Dict[str, str]],
    response_model: Type[ResponseModelType] | None = None,
    **kwargs: Any,
) -> str:
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
    )

    try:
        if response_model is None:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs,
            )
            return resp.choices[0].message.content
        else:
            resp = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_model,
                **kwargs,
            )
            return resp.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"Failed to send request: {e}") from e
