import os
import litellm
from litellm import completion


def test_moon():
    # 设置 Moonshot AI API 密钥
    os.environ["MOONSHOT_API_KEY"] = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    messages = [{"content": "Hello, how are you?", "role": "user"}]

    # Moonshot call with correct configuration
    response = completion(
        model="moonshot/kimi-k2-0711-preview",
        messages=messages,
        api_base="https://api.moonshot.cn/v1",  # 添加正确的 API 端点
        api_key=os.environ["MOONSHOT_API_KEY"]  # 显式传递 API 密钥
    )

    # 打印完整的响应对象
    print("完整响应对象:")
    print(response)
    print("\n" + "="*50 + "\n")

    # 打印响应内容
    print("AI 回复:")
    print(response.choices[0].message.content)
    print("\n" + "="*50 + "\n")

    # 打印使用统计
    print("使用统计:")
    print(f"总 token 数: {response.usage.total_tokens}")
    print(f"输入 token 数: {response.usage.prompt_tokens}")
    print(f"输出 token 数: {response.usage.completion_tokens}")