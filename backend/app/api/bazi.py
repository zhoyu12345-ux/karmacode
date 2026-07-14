"""
KarmaCode - 八字排盘 API
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.engine.bazi_calc import calculate_bazi, calculate_daily_fortune

router = APIRouter()


class BaziRequest(BaseModel):
    """八字排盘请求"""
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD", example="1990-06-15")
    birth_hour: int = Field(..., ge=0, le=23, description="出生小时 0-23", example=8)
    birth_minute: int = Field(default=0, ge=0, le=59, description="出生分钟", example=0)
    gender: str = Field(default="male", pattern="^(male|female)$", description="性别")
    longitude: float = Field(default=120.0, description="出生地经度", example=116.4)
    latitude: float = Field(default=30.0, description="出生地纬度", example=39.9)


class DailyFortuneRequest(BaseModel):
    """每日运势请求"""
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD")
    birth_hour: int = Field(..., ge=0, le=23)
    birth_minute: int = Field(default=0, ge=0, le=59)
    gender: str = Field(default="male")
    target_date: str = Field(..., description="目标日期 YYYY-MM-DD")


@router.post("/calculate")
async def calculate_bazi_api(request: BaziRequest):
    """
    计算八字命盘

    输入公历出生日期和时间，返回完整八字命盘：
    - 四柱八字（年柱、月柱、日柱、时柱）
    - 十神
    - 藏干
    - 纳音
    - 大运
    - 神煞
    - 五行统计
    """
    try:
        birth_dt = datetime.strptime(request.birth_date, "%Y-%m-%d")
        birth_dt = birth_dt.replace(hour=request.birth_hour, minute=request.birth_minute)

        chart = calculate_bazi(
            birth_date=birth_dt,
            birth_hour=request.birth_hour,
            gender=request.gender,
            longitude=request.longitude,
            latitude=request.latitude,
        )

        return {
            "success": True,
            "data": chart,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"日期格式错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"排盘计算失败: {str(e)}")


@router.post("/daily-fortune")
async def calculate_daily_api(request: DailyFortuneRequest):
    """
    计算每日运势

    输入八字信息和目标日期，返回当日的：
    - 流日干支
    - 当日十神能量主题
    - 宜忌建议
    - 特殊信号（天克地冲、伏吟等）
    """
    try:
        birth_dt = datetime.strptime(request.birth_date, "%Y-%m-%d")
        birth_dt = birth_dt.replace(hour=request.birth_hour, minute=request.birth_minute)
        target_dt = datetime.strptime(request.target_date, "%Y-%m-%d")

        chart = calculate_bazi(
            birth_date=birth_dt,
            birth_hour=request.birth_hour,
            gender=request.gender,
        )

        daily_data = calculate_daily_fortune(chart, target_dt)

        return {
            "success": True,
            "data": daily_data,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"每日运势计算失败: {str(e)}")


@router.get("/animal/{year}")
async def get_zodiac(year: int):
    """根据年份获取生肖"""
    animals = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
               "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
    animals_cn = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    idx = (year - 4) % 12
    return {"year": year, "animal": animals[idx], "animal_cn": animals_cn[idx]}
