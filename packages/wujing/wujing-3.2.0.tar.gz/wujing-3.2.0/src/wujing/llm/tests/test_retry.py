from wujing.llm.retry import create_clean_model
from pydantic import BaseModel


def test_create_clean_model():
    """测试创建干净模型的功能"""

    class TestModel(BaseModel):
        name: str
        age: int

    # 创建干净模型
    clean_model = create_clean_model(TestModel)

    # 验证干净模型的类型
    assert isinstance(clean_model, type)
