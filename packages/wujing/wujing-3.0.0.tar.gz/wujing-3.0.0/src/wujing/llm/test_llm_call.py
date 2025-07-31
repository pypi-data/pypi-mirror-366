from rich import print as rprint

from wujing.llm.llm_call import llm_call


def test_llm_call_with_openai_prompt(volces, messages, response_model):
    resp = llm_call(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        messages=messages,
        protocol="openai",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        messages=messages,
        response_model=response_model,
        protocol="openai",
        formatter="prompt",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_with_openai_vllm(vllm, messages, response_model):
    resp = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        protocol="openai",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        response_model=response_model,
        protocol="openai",
        formatter="vllm",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_with_azure(azure, messages, response_model):
    resp = llm_call(
        api_key=azure[1],
        api_version=azure[2],
        api_base=azure[0],
        model=azure[3],
        messages=messages,
        protocol="azure",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=azure[1],
        api_version=azure[2],
        api_base=azure[0],
        model=azure[3],
        messages=messages,
        response_model=response_model,
        protocol="azure",
        formatter="azure",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")
