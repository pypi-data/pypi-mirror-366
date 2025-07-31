import hashlib
import json
from typing import Any, Literal, Type

from diskcache import FanoutCache as Cache
from pydantic import validate_call

from wujing.llm.internal.azure_oai.azure_oai import azure_oai
from wujing.llm.internal.oai.oai import oai
from wujing.llm.internal.oai_with_instructor.oai_with_instructor import oai_with_instructor
from wujing.llm.types import ResponseModelType

_CACHE_RELEVANT_PARAMS = frozenset(
    [
        "api_key",
        "api_version",
        "api_base",
        "model",
        "messages",
        "response_model",
        "formatter",
        "protocol",
        "extra_body",
        "temperature",
        "max_tokens",
    ]
)

_ALLOWED_KWARGS = frozenset(["extra_body", "temperature", "max_tokens"])


class CacheManager:
    _instances: dict[str, Cache] = {}

    @classmethod
    def get_cache(cls, directory: str) -> Cache:
        if directory not in cls._instances:
            cls._instances[directory] = Cache(directory=directory)
        return cls._instances[directory]


def _generate_cache_key(**kwargs: Any) -> str:
    """
    Generate cache key from llm_call function arguments.
    Optimized version that directly accepts parameters instead of using frame inspection.
    """
    cache_relevant_params = {}

    for param_name, value in kwargs.items():
        if param_name not in _CACHE_RELEVANT_PARAMS:
            continue

        # Special handling for api_key - hash it for security
        if param_name == "api_key" and isinstance(value, str):
            cache_relevant_params["api_key_hash"] = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
        # Special handling for response_model - use its schema or name
        elif param_name == "response_model":
            if value is None:
                cache_relevant_params[param_name] = None
            elif hasattr(value, "__name__"):
                cache_relevant_params[param_name] = value.__name__
            elif hasattr(value, "model_json_schema"):
                # For Pydantic models, use schema hash for better cache consistency
                schema_str = json.dumps(value.model_json_schema(), sort_keys=True)
                cache_relevant_params[param_name] = hashlib.sha256(schema_str.encode()).hexdigest()[:16]
            else:
                cache_relevant_params[param_name] = str(value)
        # For other parameters, handle them based on type
        else:
            cache_relevant_params[param_name] = _serialize_value(value)

    # Create cache string from the extracted parameters
    cache_str = json.dumps(cache_relevant_params, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(cache_str.encode("utf-8")).hexdigest()


def _serialize_value(value: Any) -> Any:
    """
    Serialize a value for cache key generation.
    Returns the value if it's JSON serializable, otherwise returns a string representation.
    """
    # Handle common JSON-serializable types directly
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, (list, tuple)):
        try:
            return [_serialize_value(item) for item in value]
        except (TypeError, ValueError):
            return str(value)
    elif isinstance(value, dict):
        try:
            return {k: _serialize_value(v) for k, v in value.items()}
        except (TypeError, ValueError):
            return str(value)
    else:
        # For other types, convert to string
        return str(value)


@validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
def llm_call(
    *,
    api_key: str,
    api_version: str | None = None,
    api_base: str,
    model: str,
    messages: list[dict[str, str]],
    response_model: Type[ResponseModelType] | None = None,
    formatter: Literal["prompt", "vllm", "azure"] | None = None,
    protocol: Literal["openai", "azure"] = "openai",
    cache_enabled: bool = True,
    cache_directory: str = "./.diskcache/llm_cache",
    **kwargs: Any,
) -> str:
    # 校验 kwargs 参数
    invalid_kwargs = set(kwargs.keys()) - _ALLOWED_KWARGS
    if invalid_kwargs:
        raise ValueError(f"Invalid kwargs parameters: {invalid_kwargs}. Allowed parameters are: {_ALLOWED_KWARGS}")

    if (response_model is None) != (formatter is None):
        raise ValueError("Both response_model and formatter must be either set or unset.")

    try:
        cache = CacheManager.get_cache(cache_directory) if cache_enabled else None

        if cache is not None:
            cache_key = _generate_cache_key(
                api_key=api_key,
                api_version=api_version,
                api_base=api_base,
                model=model,
                messages=messages,
                response_model=response_model,
                formatter=formatter,
                protocol=protocol,
                **kwargs,
            )

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        match protocol:
            case "openai":
                result = llm_call_with_openai(
                    api_key=api_key,
                    api_base=api_base,
                    model=model,
                    messages=messages,
                    response_model=response_model,
                    formatter=formatter,
                    **kwargs,
                )
            case "azure":
                result = llm_call_with_azure(
                    api_key=api_key,
                    api_version=api_version,
                    api_base=api_base,
                    model=model,
                    messages=messages,
                    response_model=response_model,
                    formatter=formatter,
                    **kwargs,
                )
            case _:
                raise ValueError(f"Unsupported protocol: {protocol}")

        if cache is not None:
            cache.set(cache_key, result)

        return result

    except Exception:
        raise


def llm_call_with_azure(
    *,
    api_key: str,
    api_version: str,
    api_base: str,
    model: str,
    messages: list[dict[str, str]],
    response_model: Type[ResponseModelType] | None = None,
    formatter: Literal["azure"] | None = None,
    **kwargs: Any,
):
    match formatter:
        case None | "azure":
            return azure_oai(
                azure_endpoint=api_base,
                api_key=api_key,
                api_version=api_version,
                model=model,
                messages=messages,
                response_model=response_model,
                **kwargs,
            )
        case _:
            raise ValueError(f"Unsupported formatter for Azure: {formatter}")


def llm_call_with_openai(
    *,
    api_key: str,
    api_base: str,
    model: str,
    messages: list[dict[str, str]],
    context: dict[str, Any] | None = None,
    response_model: Type[ResponseModelType] | None = None,
    formatter: Literal["prompt", "vllm"] | None = None,
    **kwargs: Any,
):
    match formatter:
        case "prompt":
            return oai_with_instructor(
                api_key=api_key,
                api_base=api_base,
                model=model,
                messages=messages,
                response_model=response_model,
                context=context,
                **kwargs,
            )
        case "vllm":
            extra_body = kwargs.get("extra_body", {})
            if not isinstance(extra_body, dict):
                raise ValueError("extra_body must be a dictionary.")

            chat_template_kwargs = extra_body.get("chat_template_kwargs", {})
            chat_template_kwargs.update({"enable_thinking": False})

            extra_body.update(
                {
                    "guided_json": response_model.model_json_schema(),
                    "chat_template_kwargs": chat_template_kwargs,
                }
            )
            kwargs["extra_body"] = extra_body
            return oai(
                api_key=api_key,
                api_base=api_base,
                model=model,
                messages=messages,
                **kwargs,
            )
        case None:
            return oai(
                api_key=api_key,
                api_base=api_base,
                model=model,
                messages=messages,
                **kwargs,
            )
        case _:
            raise ValueError(f"Unsupported formatter: {formatter}")
