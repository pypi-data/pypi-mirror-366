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

# 缓存 response_model 的 schema hash，避免重复计算
_SCHEMA_HASH_CACHE: dict[Type, str] = {}


class CacheManager:
    _instances: dict[str, Cache] = {}

    @classmethod
    def get_cache(cls, directory: str) -> Cache:
        if directory not in cls._instances:
            cls._instances[directory] = Cache(directory=directory)
        return cls._instances[directory]

    @classmethod
    def clear_cache(cls, directory: str | None = None) -> None:
        """清除指定目录的缓存，如果 directory 为 None 则清除所有缓存"""
        if directory is None:
            for cache in cls._instances.values():
                cache.clear()
        elif directory in cls._instances:
            cls._instances[directory].clear()

    @classmethod
    def get_cache_stats(cls, directory: str) -> dict[str, Any]:
        """获取缓存统计信息"""
        if directory in cls._instances:
            cache = cls._instances[directory]
            return {"size": len(cache), "volume": cache.volume(), "directory": directory}
        return {"size": 0, "volume": 0, "directory": directory}


def _generate_cache_key(**kwargs: Any) -> str:
    """
    根据 llm_call 函数参数生成缓存键。
    优化版本，直接接受参数而不使用帧检查。
    """
    cache_relevant_params = {}

    for param_name, value in kwargs.items():
        if param_name not in _CACHE_RELEVANT_PARAMS:
            continue

        # 特殊处理 api_key - 出于安全考虑进行哈希
        if param_name == "api_key" and isinstance(value, str):
            cache_relevant_params["api_key_hash"] = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
        # 特殊处理 response_model - 优先使用 schema，确保字段变化时缓存键不同
        elif param_name == "response_model":
            if value is None:
                cache_relevant_params[param_name] = None
            elif hasattr(value, "model_json_schema"):
                # 对于 Pydantic 模型，使用完整的 schema hash，确保字段变化时产生不同的缓存键
                try:
                    if value not in _SCHEMA_HASH_CACHE:
                        schema_str = json.dumps(value.model_json_schema(), sort_keys=True)
                        _SCHEMA_HASH_CACHE[value] = hashlib.sha256(schema_str.encode()).hexdigest()[:16]
                    cache_relevant_params[param_name] = _SCHEMA_HASH_CACHE[value]
                except Exception:
                    # 如果 schema 生成失败，回退到使用类名和模块名的组合
                    model_identifier = f"{getattr(value, '__module__', '')}.{getattr(value, '__name__', str(value))}"
                    cache_relevant_params[param_name] = hashlib.sha256(model_identifier.encode()).hexdigest()[:16]
            elif hasattr(value, "__name__"):
                # 对于没有 schema 的类型（如普通类），使用模块名和类名的组合，避免命名冲突
                model_identifier = f"{getattr(value, '__module__', '')}.{value.__name__}"
                cache_relevant_params[param_name] = model_identifier
            else:
                cache_relevant_params[param_name] = str(value)
        # 对于其他参数，根据类型处理
        else:
            cache_relevant_params[param_name] = _serialize_value(value)

    # 从提取的参数创建缓存字符串
    cache_str = json.dumps(cache_relevant_params, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(cache_str.encode("utf-8")).hexdigest()


def _serialize_value(value: Any) -> Any:
    """
    序列化值用于缓存键生成。
    如果值可以 JSON 序列化则返回该值，否则返回字符串表示。
    """
    # 直接处理常见的 JSON 可序列化类型
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, (list, tuple)):
        # 避免不必要的异常处理，先检查是否所有元素都可序列化
        try:
            return [_serialize_value(item) for item in value]
        except (TypeError, ValueError, RecursionError):
            return str(value)
    elif isinstance(value, dict):
        try:
            return {k: _serialize_value(v) for k, v in value.items()}
        except (TypeError, ValueError, RecursionError):
            return str(value)
    else:
        # 对于其他类型，转换为字符串
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
    cache_ttl: int | None = None,  # 缓存生存时间（秒）
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
            if cache_ttl is not None:
                cache.set(cache_key, result, expire=cache_ttl)
            else:
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


# 缓存管理便利函数
def clear_llm_cache(cache_directory: str = "./.diskcache/llm_cache") -> None:
    """清除 LLM 调用缓存"""
    CacheManager.clear_cache(cache_directory)


def get_llm_cache_stats(cache_directory: str = "./.diskcache/llm_cache") -> dict[str, Any]:
    """获取 LLM 缓存统计信息"""
    return CacheManager.get_cache_stats(cache_directory)


def cleanup_schema_cache() -> None:
    """清理 schema 缓存，释放内存"""
    global _SCHEMA_HASH_CACHE
    _SCHEMA_HASH_CACHE.clear()
