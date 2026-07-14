"""
KarmaCode - 命之书 (Book of Destiny) 生成引擎
组合八字排盘 + 古籍分析 + AI解读，生成完整报告
"""

from datetime import datetime
from app.engine.bazi_calc import calculate_bazi, calculate_daily_fortune
from app.engine.analysis import full_classical_analysis


def generate_book_of_destiny(
    birth_date: str,
    birth_hour: int,
    birth_minute: int = 0,
    gender: str = "male",
    longitude: float = 120.0,
    latitude: float = 30.0,
    name: str = "",
) -> dict:
    """
    生成完整的命之书报告

    包含：
    1. 命盘总览 - 四柱八字 + 日主分析 + 五行平衡
    2. 姻缘篇 - 婚姻分析 + 古籍规则匹配
    3. 财富篇 - 财运分析 + 古籍规则匹配
    4. 先天禀赋 - 性格特质 + 五行强弱
    5. 十年大运 - 每十年运势转折
    6. 流年指南 - 当前年份详细解读
    """

    birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
    birth_dt = birth_dt.replace(hour=birth_hour, minute=birth_minute)

    # 1. 计算八字
    chart = calculate_bazi(birth_dt, birth_hour, gender, longitude, latitude)

    # 2. 古籍分析
    classical = full_classical_analysis(chart)

    # 3. 当前流年分析
    current_year = datetime.now().year
    from lunar_python import Solar
    current_dt = datetime(current_year, datetime.now().month, datetime.now().day)
    daily = calculate_daily_fortune(chart, current_dt)

    # 4. 组装报告结构
    report = {
        "meta": {
            "title": "Book of Destiny · 命之书",
            "subtitle": f"{name + ' · ' if name else ''}{chart['day_master']['char']} Master Cosmic Blueprint",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "price": "$9.99",
        },
        "chapters": [
            {
                "id": "overview",
                "title": "Chapter 1: Chart Overview · 命盘总览",
                "icon": "🌏",
                "sections": [
                    {
                        "title": "The Four Pillars",
                        "type": "chart_table",
                        "data": {
                            "year": f"{chart['pillars']['year']['stem']['char']}{chart['pillars']['year']['branch']['char']}",
                            "month": f"{chart['pillars']['month']['stem']['char']}{chart['pillars']['month']['branch']['char']}",
                            "day": f"{chart['pillars']['day']['stem']['char']}{chart['pillars']['day']['branch']['char']}",
                            "hour": f"{chart['pillars']['hour']['stem']['char']}{chart['pillars']['hour']['branch']['char']}",
                        },
                    },
                    {
                        "title": "Day Master",
                        "type": "text",
                        "content": f"{chart['day_master']['char']} ({chart['day_master']['en']}) — {chart['day_master']['element_en']} {chart['day_master']['yinyang']}",
                    },
                    {
                        "title": "Five Element Balance",
                        "type": "bar_chart",
                        "data": chart["wuxing_count"]["counts_en"],
                    },
                    {
                        "title": "Nayin (纳音)",
                        "type": "text",
                        "content": f"Year: {chart['pillars']['year']['nayin']} | Month: {chart['pillars']['month']['nayin']} | Day: {chart['pillars']['day']['nayin']} | Hour: {chart['pillars']['hour']['nayin']}",
                    },
                ],
            },
            {
                "id": "love",
                "title": "Chapter 2: Love & Marriage · 姻缘篇",
                "icon": "💑",
                "sections": [
                    {
                        "title": "Spouse Palace Analysis",
                        "type": "text",
                        "content": f"Your Day Branch ({chart['pillars']['day']['branch']['char']}) is the Spouse Palace (夫妻宫). "
                    },
                    {
                        "title": "Classical Marriage Rules",
                        "type": "findings_list",
                        "data": classical.get("marriage_analysis", {}).get("findings", []),
                    },
                ],
            },
            {
                "id": "wealth",
                "title": "Chapter 3: Wealth & Career · 财富篇",
                "icon": "💰",
                "sections": [
                    {
                        "title": "Wealth Star Analysis",
                        "type": "text",
                        "content": "Based on your chart's Ten Gods configuration."
                    },
                    {
                        "title": "Classical Wealth Rules",
                        "type": "findings_list",
                        "data": classical.get("wealth_analysis", {}).get("findings", []),
                    },
                ],
            },
            {
                "id": "character",
                "title": "Chapter 4: Innate Nature · 先天禀赋",
                "icon": "🌟",
                "sections": [
                    {
                        "title": "Day Master Personality",
                        "type": "text",
                        "content": f"As a {chart['day_master']['element_en']} Day Master, your core nature is shaped by the {chart['day_master']['element_en']} element."
                    },
                    {
                        "title": "Five Element Strengths & Weaknesses",
                        "type": "text",
                        "content": f"Dominant: {chart['wuxing_count']['dominant_en']} ({chart['wuxing_count']['counts'][chart['wuxing_count']['dominant']]} counts) | Weakest: {chart['wuxing_count']['weakest_en']}",
                    },
                    {
                        "title": "Ten Gods Profile",
                        "type": "table",
                        "data": {
                            "Year Stem": chart["shishen"]["year_stem"]["name"],
                            "Month Stem": chart["shishen"]["month_stem"]["name"],
                            "Hour Stem": chart["shishen"]["hour_stem"]["name"],
                        },
                    },
                ],
            },
            {
                "id": "dayun",
                "title": "Chapter 5: Major Luck Cycles · 十年大运",
                "icon": "📅",
                "sections": [
                    {
                        "title": "Your Life Chapters",
                        "type": "text",
                        "content": f"Your Major Luck starts at age {chart['dayun']['start_age']}. Direction: {chart['dayun']['direction']}.",
                    },
                    {
                        "title": "Decade Cycles",
                        "type": "timeline",
                        "data": chart["dayun"]["cycles"][:8],
                    },
                ],
            },
            {
                "id": "annual",
                "title": f"Chapter 6: Annual Forecast · {current_year}流年",
                "icon": "🔮",
                "sections": [
                    {
                        "title": f"Year {current_year} Energy",
                        "type": "text",
                        "content": f"Current daily energy: {daily.get('daily_shishen', 'balanced')}. Your Day Master interacts with this year's elemental energy.",
                    },
                    {
                        "title": "Key Stars",
                        "type": "tags",
                        "data": {
                            "Peach Blossom": chart["shensha"].get("桃花_Peach_Blossom", {}).get("present_in", []),
                            "Nobleman": chart["shensha"].get("天乙贵人_TianYi_Nobleman", {}).get("present_in", []),
                            "Red Luan": chart["shensha"].get("红鸾_RedLuan_Marriage", {}).get("present_in", []),
                        },
                    },
                ],
            },
        ],
        "classical_analysis": classical,
        "raw_chart": chart,
    }

    return report


def generate_book_of_destiny_markdown(report: dict) -> str:
    """将命之书报告转换为 Markdown 格式"""
    md = []
    md.append(f"# {report['meta']['title']}")
    md.append(f"## {report['meta']['subtitle']}")
    md.append(f"*Generated: {report['meta']['generated_at']}*")
    md.append("---\n")

    for chapter in report["chapters"]:
        md.append(f"## {chapter['title']}\n")
        for section in chapter["sections"]:
            md.append(f"### {section['title']}\n")
            if section["type"] == "text":
                md.append(f"{section['content']}\n")
            elif section["type"] == "table":
                md.append("| Position | Ten God |")
                md.append("|----------|---------|")
                for k, v in section.get("data", {}).items():
                    md.append(f"| {k} | {v} |")
                md.append("")
            elif section["type"] == "findings_list":
                for f in section.get("data", []):
                    icon = f.get("severity", "📋")
                    md.append(f"- {icon} **{f.get('category', '')}**: {f.get('finding', '')[:200]}")
                    if f.get("source"):
                        md.append(f"  - Source: {f['source']}")
                md.append("")
            elif section["type"] == "timeline":
                md.append("| Age | Stem | Branch | Element |")
                md.append("|-----|------|--------|---------|")
                for cycle in section.get("data", []):
                    md.append(f"| {cycle.get('age', '')} | {cycle.get('stem', '')} | {cycle.get('branch', '')} | {cycle.get('element_en', '')} |")
                md.append("")
            elif section["type"] == "chart_table":
                data = section.get("data", {})
                md.append("| Year | Month | Day | Hour |")
                md.append("|------|-------|-----|------|")
                md.append(f"| {data.get('year', '')} | {data.get('month', '')} | {data.get('day', '')} | {data.get('hour', '')} |")
                md.append("")
            elif section["type"] == "bar_chart":
                data = section.get("data", {})
                md.append("```")
                for elem, count in data.items():
                    bar = "█" * count
                    md.append(f"{elem:8s} |{bar} {count}")
                md.append("```\n")
            elif section["type"] == "tags":
                data = section.get("data", {})
                for tag, values in data.items():
                    if values:
                        md.append(f"- **{tag}**: Present in {', '.join(values)} pillar(s)")
                md.append("")

        md.append("---\n")

    md.append("\n*🔮 KarmaCode Book of Destiny — Your complete cosmic blueprint*")
    md.append("*Generated by AI based on 《三命通会》and traditional Chinese metaphysics*")
    md.append("*For entertainment and self-reflection. The stars suggest — you decide.*")

    return "\n".join(md)


if __name__ == "__main__":
    report = generate_book_of_destiny("1990-06-15", 8, 0, "female")
    md = generate_book_of_destiny_markdown(report)
    print(md[:1000])
