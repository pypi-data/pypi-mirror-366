import pytest
from pydantic import BaseModel


@pytest.fixture(scope="session")
def volces():
    return ("https://ark.cn-beijing.volces.com/api/v3", "3a6615d7-fbfa-4a5e-a675-ad2f43d8985f", "deepseek-v3-250324")


@pytest.fixture(scope="session")
def vllm():
    return ("http://127.0.0.1:8002/v1", "sk-xylx1.t!@#", "Qwen3-235B-A22B-Instruct-2507")


@pytest.fixture(scope="session")
def azure():
    return ("https://gpt-4-rdg.openai.azure.com", "f095296765e144dba561f8dc3506e4d7", "2025-01-01-preview", "gpt-4.1")


@pytest.fixture(scope="session")
def model():
    return "deepseek-v3-250324"


@pytest.fixture(scope="session")
def messages():
    return [{"role": "user", "content": "Hello, how are you?"}]


class ResponseModel(BaseModel):
    content: str

@pytest.fixture(scope="session", params=[ResponseModel])
def response_model(request):
    return request.param
