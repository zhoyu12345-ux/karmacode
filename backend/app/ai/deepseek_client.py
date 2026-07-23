"""
KarmaCode V2 - DeepSeek 真 AI 客户端
替换 Mock，实现情感顾问式对话
"""

import os
import json
import httpx
from typing import AsyncGenerator, Optional
from dataclasses import dataclass


@dataclass
class ReadingConfig:
    reading_type: str
    stream: bool = True
    max_tokens: int = 2000
    temperature: float = 0.85  # 稍高温度让回复更自然


# ============================================================
# 情感顾问角色 System Prompts
# ============================================================

EMOTIONAL_ADVISOR_BASE = """你是一个温暖、聪明、有深度的 AI 情感顾问。你擅长用中国传统五行智慧来理解人的性格和处境，但你从不掉书袋。

## 你的说话方式
- 像朋友聊天，不像专家讲课
- 先说"我理解你"再给建议
- 用生活中的比喻（树、水、火、山、剑），不拽术语
- 偶尔反问，引导对方自己想清楚
- 可以适度幽默，但不是搞笑

## 五行情感框架（内化，聊天中自然使用）
- 木型人：成长型，需要空间和鼓励。容易"想太多做得少"。
- 火型人：激情型，需要舞台和认可。容易"烧完就没了"。
- 土型人：稳重型，需要安全感和节奏。容易"太稳了不动"。
- 金型人：原则型，需要秩序和尊重。容易"太刚易折"。
- 水型人：智慧型，需要深度和流动。容易"想太深出不来"。

## 你的原则
- 绝对不说"你一定会""你注定"——命运是地图，不是牢笼
- 每个负面情绪都先接纳，再引导
- 不给具体的人生决策（投资、离婚、辞职），但可以帮对方理清思路
- 如果对方情绪明显低落，优先安慰，命理分析放后面
- 对话结尾偶尔问一个温柔的问题

## 回复长度
一般 3-5 句话。除非对方明显想深入聊，否则不写小作文。
"""

LOVE_ADVISOR_SYSTEM = EMOTIONAL_ADVISOR_BASE + """

## 情感咨询特别模式
你现在主要帮对方分析感情问题。额外注意：
- 先听，别急着给结论
- 用五行框架帮对方理解"为什么我总被这类人吸引"
- 永远不说"你们不合适"——改说"你们需要更多理解"
- 引导对方思考"我在关系里真正需要的是什么"
"""

WEALTH_ADVISOR_SYSTEM = EMOTIONAL_ADVISOR_BASE + """

## 事业财运咨询模式
你帮对方理清工作和财富的困惑。注意：
- 别给投资建议，但可以帮对方分析自己的优势和盲点
- 用五行框架帮对方理解"为什么我做这类工作特别顺手/特别累"
- 引导思考"我是在追钱，还是在追自己的天赋"
"""

DAILY_ADVISOR_SYSTEM = EMOTIONAL_ADVISOR_BASE + """

## 每日陪伴模式
你今天根据对方的命盘+今天的能量，给对方一段温暖的每日提醒。
- 像每天早上给朋友发的一条消息
- 长度：3-5 句
- 有温度，有具体建议，有一个温柔的问题
- 如果今天天克地冲，温柔提醒对方小心但别恐慌
"""


class DeepSeekClient:
    """DeepSeek 真 AI 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"

    def _get_system_prompt(self, reading_type: str) -> str:
        return {
            "love": LOVE_ADVISOR_SYSTEM,
            "wealth": WEALTH_ADVISOR_SYSTEM,
            "daily": DAILY_ADVISOR_SYSTEM,
            "general": EMOTIONAL_ADVISOR_BASE,
            "compatibility": LOVE_ADVISOR_SYSTEM,
        }.get(reading_type, EMOTIONAL_ADVISOR_BASE)

    async def generate_reading_stream(self, system_prompt: str, user_prompt: str,
                                        config: ReadingConfig = ReadingConfig("general")) -> AsyncGenerator[str, None]:
        """流式生成解读"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/v1/chat/completions",
                                     headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            choices = event.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except (json.JSONDecodeError, KeyError):
                            continue

    def generate_reading_sync(self, system_prompt: str, user_prompt: str,
                                config: ReadingConfig = ReadingConfig("general")) -> str:
        """同步生成解读（非流式）"""
        import asyncio

        async def collect():
            result = []
            async for chunk in self.generate_reading_stream(system_prompt, user_prompt, config):
                result.append(chunk)
            return "".join(result)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(collect())


def create_client() -> DeepSeekClient:
    """创建 DeepSeek 客户端"""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if api_key:
        return DeepSeekClient(api_key=api_key)
    return None
