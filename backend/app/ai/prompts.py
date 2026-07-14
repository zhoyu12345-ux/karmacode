"""
KarmaCode - AI Prompt 模板
基于知识库规则 + 风格语料，构建Claude System Prompt
"""

import json
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

# ============================================================
# 加载知识库
# ============================================================

def load_knowledge() -> dict:
    """加载知识库三件套"""
    knowledge = {}

    # 术语表
    terms_path = KNOWLEDGE_DIR / "01_术语表_terminology.json"
    if terms_path.exists():
        with open(terms_path, "r", encoding="utf-8") as f:
            knowledge["terminology"] = json.load(f)

    # 规则库
    rules_path = KNOWLEDGE_DIR / "02_规则库_rules.md"
    if rules_path.exists():
        with open(rules_path, "r", encoding="utf-8") as f:
            knowledge["rules"] = f.read()

    # 风格语料
    style_path = KNOWLEDGE_DIR / "03_风格语料_style_corpus.md"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            knowledge["style"] = f.read()

    return knowledge


# ============================================================
# System Prompt 构建
# ============================================================

def build_system_prompt(reading_type: str = "general") -> str:
    """
    构建Claude System Prompt

    Args:
        reading_type: 'love' | 'wealth' | 'daily' | 'general' | 'compatibility'
    """
    knowledge = load_knowledge()

    base_prompt = f"""You are KarmaCode, an AI guide specializing in Chinese BaZi (Eight Characters / Four Pillars of Destiny) divination. Your role is to help users understand themselves through the lens of Eastern wisdom — combining the depth of ancient Chinese metaphysics with modern psychological insight.

## Your Identity
- You are warm, wise, and poetic — like a sage who speaks the language of modern people
- You NEVER claim absolute predictions. Use language like "suggests," "tends to indicate," "many people with this pattern find..."
- Every challenging reading MUST be followed by constructive guidance
- You bridge Eastern concepts with Western frameworks (psychology, personality theory, life coaching)

## Core Knowledge Base
You have access to the following knowledge from the classic text "三命通会" (San Ming Tong Hui) and modern scholarship:

### Key Terminology
{json.dumps(knowledge.get('terminology', {}).get('categories', {}).get('十神_Ten_Gods', {}), ensure_ascii=False, indent=2)}

### Core Rules Reference
{knowledge.get('rules', '')[:3000]}

## Style Guidelines
{knowledge.get('style', '')[:2000]}

## Critical Rules
1. **NEVER** use fear-based language (no "destined to," "will definitely," "cursed")
2. **ALWAYS** provide both the Eastern concept AND a Western equivalent
3. **ALWAYS** end with a reflective question or empowering statement
4. Use natural imagery (water=flow, mountain=stability, wind=change) to make concepts accessible
5. For marriage/love readings: be especially gentle and nuanced — this is emotionally sensitive
6. Include a brief disclaimer at the end that this is for self-reflection, not professional advice

## Response Format
Structure your response with clear sections using markdown. Be generous with emojis for visual warmth (but not excessive). Use the exact styling patterns from the Style Corpus.

## Language
Primary output language: English (targeting a global, English-speaking audience)
Include the original Chinese characters for key terms in parentheses, e.g., "Direct Officer (正官, ZhengGuan)"
"""

    # 根据解读类型添加特定指令
    type_specific = {
        "love": """
## Love & Marriage Focus
- Analyze the Husband/Wife Star (夫妻星) and Spouse Palace (夫妻宫)
- Apply the "Eight Methods for Female Charts" (女命八法) where relevant
- Check Peach Blossom (桃花) positioning and timing
- Provide relationship timing windows based on Major Luck (大运) and Annual cycles
- If analyzing compatibility: apply Five Element complementarity principles
- Be especially warm and non-judgmental — love is universal and sacred
""",
        "wealth": """
## Wealth & Career Focus
- Analyze Direct Wealth (正财) and Indirect Wealth (偏财) stars
- Apply the core principle: "财为养命之源" (Wealth nourishes life)
- Check if the Day Master is strong enough to "carry" the wealth
- Identify wealth windows in Major Luck cycles
- Distinguish between earned income vs. unexpected fortune patterns
- Give practical, modern career advice linked to the elemental analysis
""",
        "daily": """
## Daily Fortune Focus
- Analyze today's energy based on the Day Stem's relationship to the user's Day Master
- Use the 十神 (Ten Gods) framework for practical daily guidance
- Provide specific auspicious/inauspicious activities
- Check for special signals: 天克地冲 (Heaven-Clash Earth-Rush), 伏吟, 三合
- Keep it brief, actionable, and uplifting
- One reflective quote or proverb to carry through the day
""",
        "general": """
## Comprehensive Reading Focus
- Give an overview of the user's Day Master nature and core personality
- Touch on the most prominent patterns in their chart
- Identify the dominant Five Element and its implications
- Provide a high-level view of current Major Luck phase
- Hint at love and wealth themes without going too deep (those are separate readings)
""",
        "compatibility": """
## Compatibility Reading Focus
- Analyze both persons' Day Masters and their Five Element relationship
- Check Day Branch (Spouse Palace) interactions — harmonious or clashing?
- Apply Five Element complementarity: does each person's excess get balanced by the other's deficiency?
- Count harmonious combinations (合) vs. clashes (冲)
- Check if each person's "problem element" is the other's "beneficial element"
- Give an honest but kind assessment
- Remember: even challenging matches can work with awareness and effort
""",
    }

    base_prompt += type_specific.get(reading_type, type_specific["general"])
    base_prompt += """

## Disclaimer
Include this at the end of every reading:

---
*🔮 This reading is based on traditional Chinese metaphysical frameworks and is offered for entertainment and self-reflection. It does not constitute professional advice (medical, legal, financial, or psychological). Your life choices remain entirely in your own hands. The stars may suggest — you decide.*
"""

    return base_prompt


# ============================================================
# 用户消息模板
# ============================================================

def build_love_reading_prompt(chart: dict) -> str:
    """构建婚恋解读的user prompt"""
    dm = chart["day_master"]
    pillars = chart["pillars"]
    shishen = chart["shishen"]
    shensha = chart["shensha"]
    dayun = chart["dayun"]
    wuxing = chart["wuxing_count"]
    gender = chart["birth_info"]["gender"]

    gender_en = "female" if gender == "female" else "male"
    spouse_star = "Husband Star (正官/七杀)" if gender == "female" else "Wife Star (正财)"

    return f"""Please give me a detailed Love & Marriage reading based on my BaZi chart.

## My Chart Data

**Basic Info:**
- Gender: {gender_en}
- Day Master: {dm["char"]} ({dm["element_en"]}, {dm["yinyang"]})
- Birth: {chart["birth_info"]["solar_date"]}, {chart["birth_info"]["lunar_date"]}
- Chinese Zodiac: {chart["birth_info"]["animal"]}

**Four Pillars:**
- Year: {pillars["year"]["stem"]["char"]}{pillars["year"]["branch"]["char"]} ({pillars["year"]["stem"]["element_en"]} {pillars["year"]["stem"]["en"]}, {pillars["year"]["nayin"]})
- Month: {pillars["month"]["stem"]["char"]}{pillars["month"]["branch"]["char"]} ({pillars["month"]["stem"]["element_en"]} {pillars["month"]["stem"]["en"]}, {pillars["month"]["nayin"]})
- Day: {pillars["day"]["stem"]["char"]}{pillars["day"]["branch"]["char"]} ({pillars["day"]["stem"]["element_en"]} {pillars["day"]["stem"]["en"]}, {pillars["day"]["nayin"]}) — **SPOUSE PALACE**
- Hour: {pillars["hour"]["stem"]["char"]}{pillars["hour"]["branch"]["char"]} ({pillars["hour"]["stem"]["element_en"]} {pillars["hour"]["stem"]["en"]}, {pillars["hour"]["nayin"]})

**Ten Gods (十神) - Key for Spouse Analysis ({spouse_star}):**
- Year Stem: {shishen["year_stem"]["name"]}
- Month Stem: {shishen["month_stem"]["name"]}
- Hour Stem: {shishen["hour_stem"]["name"]}
- Day Branch (Spouse Palace): {shishen["day_branch"]["name"]}

**Special Stars Related to Love:**
- Peach Blossom (桃花): {json.dumps(shensha.get('桃花_Peach_Blossom', {}), ensure_ascii=False)}
- Red Luan (红鸾): {json.dumps(shensha.get('红鸾_RedLuan_Marriage', {}), ensure_ascii=False)}
- Solitude Stars (孤辰寡宿): {json.dumps(shensha.get('孤辰寡宿_Solitude', {}), ensure_ascii=False)}
- Nobleman (天乙贵人): {json.dumps(shensha.get('天乙贵人_TianYi_Nobleman', {}), ensure_ascii=False)}

**Five Element Balance:**
{json.dumps(wuxing["counts_en"], ensure_ascii=False)}
Dominant: {wuxing["dominant_en"]}, Weakest: {wuxing["weakest_en"]}

**Major Luck (大运) Timelines:**
{json.dumps(dayun["cycles"][:5], ensure_ascii=False, indent=2)}

---

Please analyze:
1. My relationship nature based on my Day Master and Spouse Palace
2. What kind of partner would complement my chart (Five Element harmony)
3. Timing — when am I most likely to meet someone significant or get married?
4. What should I be aware of in relationships based on my chart patterns?
5. A reflective question for me to ponder about love

Use the poetic, warm style. Bridge Eastern concepts with Western understanding.
"""


def build_wealth_reading_prompt(chart: dict) -> str:
    """构建财富解读的user prompt"""
    dm = chart["day_master"]
    pillars = chart["pillars"]
    shishen = chart["shishen"]
    dayun = chart["dayun"]
    wuxing = chart["wuxing_count"]

    return f"""Please give me a detailed Wealth & Career reading based on my BaZi chart.

## My Chart Data

**Day Master:** {dm["char"]} ({dm["element_en"]}, {dm["yinyang"]})

**Four Pillars:**
- Year: {pillars["year"]["stem"]["char"]}{pillars["year"]["branch"]["char"]} ({pillars["year"]["nayin"]})
- Month: {pillars["month"]["stem"]["char"]}{pillars["month"]["branch"]["char"]} ({pillars["month"]["nayin"]})
- Day: {pillars["day"]["stem"]["char"]}{pillars["day"]["branch"]["char"]} ({pillars["day"]["nayin"]})
- Hour: {pillars["hour"]["stem"]["char"]}{pillars["hour"]["branch"]["char"]} ({pillars["hour"]["nayin"]})

**Ten Gods - Key for Wealth Analysis:**
- Year Stem: {shishen["year_stem"]["name"]}
- Month Stem: {shishen["month_stem"]["name"]}
- Hour Stem: {shishen["hour_stem"]["name"]}

**Five Elements:** {json.dumps(wuxing["counts_en"], ensure_ascii=False)}
Dominant: {wuxing["dominant_en"]}, Weakest: {wuxing["weakest_en"]}

**Major Luck Cycles:**
{json.dumps(dayun["cycles"][:5], ensure_ascii=False, indent=2)}

---

Please analyze:
1. My wealth nature — steady earner or fortune seeker?
2. The strength of my Day Master — can I "carry" wealth?
3. Wealth timing windows in my Major Luck cycles
4. Career direction aligned with my elemental strengths
5. One piece of Eastern wealth wisdom for me

Be practical and modern — connect to actual career and financial concepts.
"""


def build_daily_reading_prompt(chart: dict, daily_data: dict) -> str:
    """构建每日运势的user prompt"""
    dm = chart["day_master"]

    return f"""Please give me a brief daily fortune reading.

## My Day Master
{dm["char"]} ({dm["element_en"]})

## Today's Energy
- Date: {daily_data["date"]}
- Flow Day: {daily_data["flow_day"]["stem"]}{daily_data["flow_day"]["branch"]}
- Today's Energy Type: {daily_data["daily_shishen"]}
- Special Signals: {"⚠️ Heaven-Clash Earth-Rush (天克地冲) - be extra careful!" if daily_data["is_tiankedichong"] else ("🔄 FuYin (伏吟) - expect a reflective, possibly frustrating day" if daily_data["is_fuyin"] else "Normal day")}

## Suggestions
- Auspicious: {json.dumps(daily_data["suggestions"]["auspicious"], ensure_ascii=False)}
- Caution: {json.dumps(daily_data["suggestions"]["caution"], ensure_ascii=False)}

---

Please provide:
1. A poetic one-line summary of today's cosmic energy
2. Practical advice for the day (2-3 actionable tips)
3. One thing to watch out for
4. An inspiring quote or proverb to carry through the day

Keep it short and uplifting. Think "morning meditation" length — not a full reading.
"""


def build_compatibility_prompt(chart_a: dict, chart_b: dict) -> str:
    """构建合婚解读的user prompt"""
    return f"""Please analyze the compatibility between two people based on their BaZi charts.

## Person A
- Day Master: {chart_a["day_master"]["char"]} ({chart_a["day_master"]["element_en"]})
- Day Pillar: {chart_a["pillars"]["day"]["stem"]["char"]}{chart_a["pillars"]["day"]["branch"]["char"]}
- Dominant Element: {chart_a["wuxing_count"]["dominant_en"]}
- Weakest Element: {chart_a["wuxing_count"]["weakest_en"]}
- Animal: {chart_a["birth_info"]["animal"]}

## Person B
- Day Master: {chart_b["day_master"]["char"]} ({chart_b["day_master"]["element_en"]})
- Day Pillar: {chart_b["pillars"]["day"]["stem"]["char"]}{chart_b["pillars"]["day"]["branch"]["char"]}
- Dominant Element: {chart_b["wuxing_count"]["dominant_en"]}
- Weakest Element: {chart_b["wuxing_count"]["weakest_en"]}
- Animal: {chart_b["birth_info"]["animal"]}

---

Please analyze:
1. The elemental dance between them (generate/control cycle)
2. Are their Day Branches harmonious or clashing?
3. What does each person bring to balance the other?
4. Potential growth edges in this relationship
5. Overall compatibility score and summary

Be honest but kind. Every relationship has strengths AND challenges.
"""
