from typing import Literal


providers = {
    "dashscope": {
        "api_id": "dashscope",
        "default_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "deepseek-ai": {"api_id": "deepseek", "default_url": "https://api.deepseek.com/v1"},
    "tencent-cloud": {
        "api_id": "tencent",
        "default_url": "https://api.hunyuan.cloud.tencent.com/v1",
    },
    "moonshot-ai": {
        "api_id": "moonshot",
        "default_url": "https://api.moonshot.cn/v1",
    },
    "zhipu-ai": {
        "api_id": "zhipu",
        "default_url": "https://open.bigmodel.cn/api/paas/v4/",
    },
    "minimax": {
        "api_id": "minimax",
        "default_url": "https://api.minimaxi.com/v1",
    },
    "vllm": {
        "api_id": "vllm",
        "default_url": "http://localhost:8080/v1",
    },
    "ollama": {
        "api_id": "ollama",
        "default_url": "http://localhost:11434/v1",
    },
}


provider_list = Literal[
    "deepseek-ai",
    "dashscope",
    "tencent-cloud",
    "moonshot-ai",
    "zhipu-ai",
    "minimax",
    "vllm",
    "ollama",
    "custom",
]


def _get_provider_with_model(model: str) -> provider_list:
    if "deepseek" in model.lower():
        return "deepseek-ai"
    elif "qwen" in model.lower():
        return "dashscope"
    elif "hunyuan" in model.lower():
        return "tencent-cloud"
    elif "kimi" in model.lower():
        return "moonshot-ai"
    elif "glm" in model.lower():
        return "zhipu-ai"
    elif "minimax" in model.lower():
        return "minimax"
    else:
        return "custom"



provider_emb_list=Literal[
    "dashscope",
    "zhipu-ai",
    "ollama",
    "vllm",
    "custom"
]