"""
KarmaCode - AI 解读 API
支持流式和非流式解读
"""

import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import json

from app.engine.bazi_calc import calculate_bazi, calculate_daily_fortune
from app.engine.analysis import full_classical_analysis
from app.ai.prompts import (
    build_system_prompt,
    build_love_reading_prompt,
    build_wealth_reading_prompt,
    build_daily_reading_prompt,
    build_compatibility_prompt,
)
from app.ai.claude_client_v2 import MockClaudeClient, ReadingConfig

router = APIRouter()

# 使用Mock客户端(开发阶段)，生产环境切换为 ClaudeClient
USE_MOCK = os.environ.get("USE_MOCK_CLAUDE", "true").lower() == "true"
claude = MockClaudeClient()


class ReadingRequest(BaseModel):
    """解读请求"""
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD")
    birth_hour: int = Field(..., ge=0, le=23)
    birth_minute: int = Field(default=0, ge=0, le=59)
    gender: str = Field(default="male")
    reading_type: str = Field(default="general", description="解读类型: love|wealth|daily|general")
    stream: bool = Field(default=True, description="是否流式输出")
    target_date: Optional[str] = Field(default=None, description="每日运势的目标日期")


class CompatibilityRequest(BaseModel):
    """合婚请求"""
    person_a: ReadingRequest
    person_b: ReadingRequest


@router.post("/generate")
async def generate_reading(request: ReadingRequest):
    """
    生成AI解读

    支持四种解读类型：
    - love: 婚姻情感深度解读
    - wealth: 财富事业解读
    - daily: 每日运势
    - general: 综合命盘解读

    支持流式(stream=true)和非流式输出
    """
    try:
        # 1. 计算八字
        birth_dt = datetime.strptime(request.birth_date, "%Y-%m-%d")
        birth_dt = birth_dt.replace(hour=request.birth_hour, minute=request.birth_minute)

        chart = calculate_bazi(
            birth_date=birth_dt,
            birth_hour=request.birth_hour,
            gender=request.gender,
        )

        # 1.5. 古籍逆向分析
        classical = full_classical_analysis(chart)
        classical_context = classical.get("classical_context", "")

        # 2. 构建 Prompt
        system_prompt = build_system_prompt(request.reading_type)

        if request.reading_type == "love":
            user_prompt = build_love_reading_prompt(chart)
        elif request.reading_type == "wealth":
            user_prompt = build_wealth_reading_prompt(chart)
        elif request.reading_type == "daily":
            target = request.target_date or datetime.now().strftime("%Y-%m-%d")
            target_dt = datetime.strptime(target, "%Y-%m-%d")
            daily_data = calculate_daily_fortune(chart, target_dt)
            user_prompt = build_daily_reading_prompt(chart, daily_data)
        else:
            user_prompt = build_love_reading_prompt(chart)  # general defaults to love for MVP

        # 注入古籍分析上下文
        user_prompt += "\n\n---\n## Classical Rule Analysis\n"
        user_prompt += classical_context
        user_prompt += "\n\nPlease incorporate these classical findings into your interpretation. Reference specific rules from San Ming Tong Hui where applicable."

        # 3. 调用 AI
        config = ReadingConfig(
            reading_type=request.reading_type,
            stream=request.stream,
            max_tokens=2000,
        )

        if request.stream:
            async def generate():
                async for chunk in claude.generate_reading_stream(
                    system_prompt, user_prompt, config
                ):
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            # 非流式 - 直接获取完整响应（毫秒级，不经 async generator）
            full_text = claude.generate_reading_sync(
                system_prompt, user_prompt, config
            )

            return {
                "success": True,
                "data": {
                    "reading_type": request.reading_type,
                    "content": full_text,
                    "chart_summary": {
                        "day_master": f"{chart['day_master']['char']} ({chart['day_master']['element_en']})",
                        "pillars": f"{chart['pillars']['year']['stem']['char']}{chart['pillars']['year']['branch']['char']} "
                                  f"{chart['pillars']['month']['stem']['char']}{chart['pillars']['month']['branch']['char']} "
                                  f"{chart['pillars']['day']['stem']['char']}{chart['pillars']['day']['branch']['char']} "
                                  f"{chart['pillars']['hour']['stem']['char']}{chart['pillars']['hour']['branch']['char']}",
                    },
                },
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解读生成失败: {str(e)}")


@router.post("/compatibility")
async def generate_compatibility(request: CompatibilityRequest):
    """
    生成合婚解读

    分析两人八字的五行互补、夫妻宫互动、合冲关系
    """
    try:
        # 解析两人八字
        birth_a = datetime.strptime(request.person_a.birth_date, "%Y-%m-%d")
        birth_a = birth_a.replace(hour=request.person_a.birth_hour, minute=request.person_a.birth_minute)
        chart_a = calculate_bazi(birth_date=birth_a, birth_hour=request.person_a.birth_hour,
                                  gender=request.person_a.gender)

        birth_b = datetime.strptime(request.person_b.birth_date, "%Y-%m-%d")
        birth_b = birth_b.replace(hour=request.person_b.birth_hour, minute=request.person_b.birth_minute)
        chart_b = calculate_bazi(birth_date=birth_b, birth_hour=request.person_b.birth_hour,
                                  gender=request.person_b.gender)

        # 构建 Prompt
        system_prompt = build_system_prompt("compatibility")
        user_prompt = build_compatibility_prompt(chart_a, chart_b)

        config = ReadingConfig(reading_type="compatibility", stream=True)

        async def generate():
            async for chunk in claude.generate_reading_stream(
                system_prompt, user_prompt, config
            ):
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"合婚解读失败: {str(e)}")


@router.get("/types")
async def get_reading_types():
    """获取支持的解读类型"""
    return {
        "types": [
            {"id": "love", "name": "Love & Marriage", "name_cn": "婚姻情感", "description": "Deep relationship analysis"},
            {"id": "wealth", "name": "Wealth & Career", "name_cn": "财富事业", "description": "Financial destiny reading"},
            {"id": "daily", "name": "Daily Fortune", "name_cn": "每日运势", "description": "Today's energy guidance"},
            {"id": "general", "name": "General Reading", "name_cn": "综合解读", "description": "Overview of your chart"},
            {"id": "compatibility", "name": "Compatibility", "name_cn": "合婚分析", "description": "Relationship matching"},
        ]
    }
