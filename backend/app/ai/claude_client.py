"""
KarmaCode - Claude API 客户端封装
支持流式输出和RAG增强
"""

import os
import json
import re
from typing import AsyncGenerator, Optional
from dataclasses import dataclass

import httpx


@dataclass
class ReadingConfig:
    """解读配置"""
    reading_type: str
    stream: bool = True
    max_tokens: int = 2000
    temperature: float = 0.7


class ClaudeClient:
    """Claude API 客户端"""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.anthropic.com"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.base_url = base_url
        self.api_version = "2023-06-01"

    async def generate_reading_stream(self, system_prompt: str, user_prompt: str,
                                        config: ReadingConfig = ReadingConfig("general")) -> AsyncGenerator[str, None]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json",
        }

        payload = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/v1/messages",
                                     headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            if event.get("type") == "content_block_delta":
                                delta = event.get("delta", {})
                                if "text" in delta:
                                    yield delta["text"]
                        except json.JSONDecodeError:
                            continue


def create_claude_client() -> ClaudeClient:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    return ClaudeClient(api_key=api_key)


# ============================================================
# 数据感知 Mock Client —— 根据实际命盘生成个性化解读
# ============================================================

# 五行人格描述模板
ELEMENT_PERSONAS = {
    "Wood": {
        "nature": "the pioneer, reaching upward like a tall tree toward sunlight",
        "strength": "vision, growth, and adaptability",
        "challenge": "scattered energy — too many branches, not enough roots",
        "partner_ideal": "Metal — someone decisive who can prune your wild branches into focused form",
        "career_fit": "innovation, education, environmental fields, creative leadership",
        "wealth_style": "grows wealth organically, like a forest expanding season by season",
        "quote": "A tree does not rush — it simply grows toward the light, one ring at a time.",
    },
    "Fire": {
        "nature": "the flame — warm, radiant, and impossible to ignore",
        "strength": "passion, charisma, and transformative energy",
        "challenge": "burnout — giving so much light that you forget to refuel",
        "partner_ideal": "Water — someone deep and calm who can cool your intensity without extinguishing your spark",
        "career_fit": "entertainment, public speaking, coaching, technology, creative arts",
        "wealth_style": "wealth comes in bursts — like a bonfire, not a candle",
        "quote": "A fire's purpose is not to last forever, but to ignite everything it touches.",
    },
    "Earth": {
        "nature": "the mountain — steady, nurturing, and deeply grounded",
        "strength": "stability, reliability, and the ability to nurture others",
        "challenge": "resistance to change — mountains are strong but slow to move",
        "partner_ideal": "Wood — someone energetic who can bring life to your stable terrain",
        "career_fit": "finance, real estate, healthcare, education, management",
        "wealth_style": "slow and steady accumulation — the mountain does not hurry, yet it reaches the sky",
        "quote": "A mountain is not built in a day — it is carved by time, wind, and patience.",
    },
    "Metal": {
        "nature": "the sword — precise, principled, and beautifully structured",
        "strength": "discipline, integrity, and the ability to cut through confusion",
        "challenge": "rigidity — a sword that cannot bend will eventually break",
        "partner_ideal": "Fire — someone warm who can soften your edges and remind you that perfection is not the goal",
        "career_fit": "law, engineering, finance, military, technology, jewelry/design",
        "wealth_style": "earned through skill and precision — like a master craftsman's finest work",
        "quote": "True strength is not the blade that never bends, but the one that bends and returns true.",
    },
    "Water": {
        "nature": "the ocean — deep, wise, and endlessly adaptable",
        "strength": "wisdom, intuition, and the ability to flow around any obstacle",
        "challenge": "depth without direction — an ocean without shores becomes aimless",
        "partner_ideal": "Earth — someone stable who can give your flowing nature a shoreline to call home",
        "career_fit": "research, writing, psychology, arts, diplomacy, exploration",
        "wealth_style": "flows like a river — sometimes a trickle, sometimes a flood, always finding its way",
        "quote": "Water is the softest thing, yet it can penetrate mountains and shape continents.",
    },
}

# 十神对婚姻的解读模板
SHISHEN_LOVE = {
    "正官": "You carry the Direct Officer as a prominent influence — drawn to partners who embody integrity, responsibility, and quiet authority. You're not looking for a whirlwind romance; you're looking for someone worth building a life with.",
    "七杀": "The Seven Killings star brings intensity to your love life. You're attracted to strong, ambitious partners — people with edge and drive. The challenge is distinguishing passion from chaos.",
    "正财": "Direct Wealth shapes your approach to relationships — you value stability, loyalty, and practical compatibility. Love, for you, is something you build, not something you fall into.",
    "偏财": "Indirect Wealth energy makes you charming and magnetic — you draw people in effortlessly. The gift is charisma; the lesson is commitment.",
    "食神": "The Eating God blesses you with warmth and creativity in love. You express affection through acts of care — cooking a meal, planning a surprise, making your partner feel cherished.",
    "伤官": "Hurting Officer energy gives you a sharp wit and irresistible charm — but it can also make you restless in settled relationships. Your lesson: passion needs peace to grow roots.",
    "正印": "Direct Resource makes you nurturing and deeply caring. In relationships, you're the safe harbor — the one who listens, supports, and protects.",
    "偏印": "Indirect Resource gives you a unique, almost mystical allure. You connect deeply — but sometimes retreat into your inner world, leaving your partner outside.",
    "比肩": "Parallel energy makes you independent — you want a partner who walks beside you as an equal, not someone who leads or follows.",
    "劫财": "Rob Wealth brings competitive fire — even in love. You're drawn to exciting people, but watch the tendency to turn partnership into rivalry.",
}


class MockClaudeClient:
    """数据感知的Mock Claude客户端"""

    async def generate_reading_stream(self, system_prompt: str, user_prompt: str,
                                        config: ReadingConfig = ReadingConfig("general")) -> AsyncGenerator[str, None]:
        import asyncio

        # 从 user_prompt 中提取实际数据
        chart_data = self._parse_chart_from_prompt(user_prompt)

        if config.reading_type == "love":
            text = self._generate_love_reading(chart_data)
        elif config.reading_type == "wealth":
            text = self._generate_wealth_reading(chart_data)
        elif config.reading_type == "daily":
            text = self._generate_daily_reading(chart_data, user_prompt)
        elif config.reading_type == "compatibility":
            text = self._generate_compat_reading(chart_data)
        else:
            text = self._generate_general_reading(chart_data)

        # 追加古籍分析段落
        classical_section = self._format_classical_section(chart_data)
        text += classical_section

        for char in text:
            yield char
            await asyncio.sleep(0.001)  # 加速测试

    def generate_reading_sync(self, system_prompt: str, user_prompt: str,
                               config: ReadingConfig = ReadingConfig("general")) -> str:
        """
        同步方式生成完整解读文本（非流式）。
        直接返回完整字符串，不经过 async generator，响应速度从 ~30s 降至毫秒级。
        """
        chart_data = self._parse_chart_from_prompt(user_prompt)

        if config.reading_type == "love":
            text = self._generate_love_reading(chart_data)
        elif config.reading_type == "wealth":
            text = self._generate_wealth_reading(chart_data)
        elif config.reading_type == "daily":
            text = self._generate_daily_reading(chart_data, user_prompt)
        elif config.reading_type == "compatibility":
            text = self._generate_compat_reading(chart_data)
        else:
            text = self._generate_general_reading(chart_data)

        # 追加古籍分析段落
        classical_section = self._format_classical_section(chart_data)
        text += classical_section

        return text

    def _parse_chart_from_prompt(self, prompt: str) -> dict:
        """从用户prompt中提取命盘关键数据"""
        data = {
            "dm_char": "?",
            "dm_element": "Unknown",
            "dm_yinyang": "",
            "dm_en": "",
            "year_pillar": "??",
            "month_pillar": "??",
            "day_pillar": "??",
            "hour_pillar": "??",
            "year_nayin": "",
            "month_nayin": "",
            "day_nayin": "",
            "hour_nayin": "",
            "animal": "",
            "gender": "",
            "dominant_element": "",
            "weakest_element": "",
            "month_shishen": "",
            "hour_shishen": "",
            "day_branch": "",
            "day_branch_animal": "",
            "start_age": "",
            "elements": {},
        }

        # 提取 Day Master
        m = re.search(r'Day Master:\s*\*\*([^\*]+)\*\*\s*\(([^,]+),\s*(\w+)\)', prompt)
        if not m:
            m = re.search(r'Day Master:\s*([^(]+)\s*\(([^,]+),\s*(\w+)\)', prompt)
        if not m:
            m = re.search(r'Day Master:\s*\*?\*?(\S+)\s*\((\w+),\s*(\w+)\)', prompt)
        if m:
            data["dm_char"] = m.group(1).strip().replace("*", "")
            data["dm_element"] = m.group(2).strip()
            data["dm_yinyang"] = m.group(3).strip() if len(m.groups()) > 2 else ""

        # 提取四柱
        pillars_match = re.search(r'Year:\s*\*?\*?(\S{2}).*?\(.*?(\S+)', prompt)
        if pillars_match:
            data["year_pillar"] = pillars_match.group(1)

        # 更稳健的四柱提取
        for pillar_name, key in [("Year:", "year_pillar"), ("Month:", "month_pillar"),
                                  ("Day:", "day_pillar"), ("Hour:", "hour_pillar")]:
            p = re.search(rf'{pillar_name}\s*\*?\*?(\S\S)', prompt)
            if p:
                data[key] = p.group(1)

        # 提取纳音
        for nayin_name, key in [("Year:", "year_nayin"), ("Month:", "month_nayin"),
                                 ("Day:", "day_nayin"), ("Hour:", "hour_nayin")]:
            n = re.search(rf'{nayin_name}.*?\(.*?,\s*(\S+)\)', prompt)
            if n:
                data[key] = n.group(1)

        # 提取日支（从day_pillar中取第二个字）
        if len(data.get("day_pillar", "")) >= 2:
            data["day_branch"] = data["day_pillar"][1]

        # 提取十神
        m_ss = re.search(r'Month Stem:\s*\*?\*?(\S+)', prompt)
        if m_ss:
            data["month_shishen"] = m_ss.group(1)
        h_ss = re.search(r'Hour Stem:\s*\*?\*?(\S+)', prompt)
        if h_ss:
            data["hour_shishen"] = h_ss.group(1)

        # 提取五行
        elements_match = re.search(r'"(\w+)":\s*(\d+)', prompt)
        if elements_match:
            for e in ["Wood", "Fire", "Earth", "Metal", "Water"]:
                em = re.search(rf'"{e}":\s*(\d+)', prompt)
                if em:
                    data["elements"][e] = int(em.group(1))

        # Dominant / Weakest
        dm_match = re.search(r'Dominant:\s*\*?\*?(\w+)', prompt)
        if dm_match:
            data["dominant_element"] = dm_match.group(1)
        wk_match = re.search(r'Weakest:\s*\*?\*?(\w+)', prompt)
        if wk_match:
            data["weakest_element"] = wk_match.group(1)

        # 性别
        gm = re.search(r'Gender:\s*(\w+)', prompt)
        if gm:
            data["gender"] = gm.group(1)

        # 生肖
        am = re.search(r'Zodiac:\s*\*?\*?(\w+)', prompt)
        if am:
            data["animal"] = am.group(1)

        # 起运年龄
        sm = re.search(r'start_age["\']?\s*:\s*(\d+)', prompt)
        if sm:
            data["start_age"] = sm.group(1)

        # 提取古籍分析发现
        data["classical_findings"] = []
        finding_pattern = re.finditer(
            r'([✅📋⚠️🔍🚩])\s*\*\*([^*]+)\*\*\s*\n\s+(.*?)(?=\n\n|\n[✅📋⚠️🔍🚩]|\n###|\Z)',
            prompt, re.DOTALL
        )
        seen = set()
        for match in finding_pattern:
            icon = match.group(1)
            category = match.group(2).strip()
            detail = match.group(3).strip()
            if category not in seen:
                seen.add(category)
                data["classical_findings"].append({
                    "icon": icon,
                    "category": category,
                    "detail": detail[:300],
                })

        return data

    def _get_persona(self, element: str) -> dict:
        return ELEMENT_PERSONAS.get(element, ELEMENT_PERSONAS["Earth"])

    def _format_classical_section(self, d: dict) -> str:
        """格式化古籍分析段落"""
        findings = d.get("classical_findings", [])
        if not findings:
            return ""

        lines = []
        lines.append("\n---\n")
        lines.append("### 📜 Classical Analysis (Based on San Ming Tong Hui)\n")
        lines.append("*The following patterns were identified in your chart using rules from the ancient text 《三命通会》:*\n")

        marriage_findings = [f for f in findings if any(kw in f.get("category", "") for kw in
            ["官杀", "夫星", "正财为妻", "偏财为妻", "比劫夺财", "桃花", "红鸾", "孤辰", "夫妻宫", "女命八法", "伤官格"])]
        wealth_findings = [f for f in findings if any(kw in f.get("category", "") for kw in
            ["正财格", "偏财格", "财多身弱", "身强财弱", "财藏", "财透", "财星"])]

        if marriage_findings:
            lines.append("**Love & Marriage:**\n")
            for f in marriage_findings:
                lines.append(f"- {f['icon']} **{f['category']}**: {f['detail'][:200]}")
            lines.append("")

        if wealth_findings:
            lines.append("**Wealth & Career:**\n")
            for f in wealth_findings:
                lines.append(f"- {f['icon']} **{f['category']}**: {f['detail'][:200]}")
            lines.append("")

        lines.append("*These classical observations are derived from centuries of pattern recognition in Chinese metaphysics. They describe tendencies, not destinies.*\n")

        return "\n".join(lines)

    # ============================================================
    # 个性化解读生成
    # ============================================================

    def _generate_general_reading(self, d: dict) -> str:
        p = self._get_persona(d["dm_element"])
        dm = d["dm_char"]
        el = d["dm_element"]
        dom = d.get("dominant_element", el)
        weak = d.get("weakest_element", "Unknown")
        yp = d.get("year_pillar", "??")
        mp = d.get("month_pillar", "??")
        dp = d.get("day_pillar", "??")
        hp = d.get("hour_pillar", "??")
        animal = d.get("animal", "Unknown")
        age = d.get("start_age", "?")
        gender = d.get("gender", "")
        is_female = (gender == "female")

        elems_desc = ", ".join([f"{e}: {c}" for e, c in d.get("elements", {}).items()]) if d.get("elements") else "balanced distribution"

        # 性别特定的关系提示
        if is_female:
            gender_note = f"""
### 💑 Your Life Path as a Woman

The 《三命通会·论女命》 offers specific guidance for women's charts. Your husband star (夫星) and children star (子星) are the two pillars of traditional female destiny analysis. In modern terms, this translates to: your partnerships and what you create in the world (whether children, projects, or legacy) are the twin measures of a life well-lived.

The ancient text urges women to look for **clarity (清)** and **harmony (和)** in their charts — not perfection, but balance. Your {el} Day Master brings its own unique gifts to this equation."""
        else:
            gender_note = f"""
### 💑 Your Life Path as a Man

In traditional BaZi, a man's chart is read through the lens of career (官星) and wealth (财星) — the two pillars of worldly achievement. But 《三命通会》also reminds us that the wife star (妻星 = 财星) is equally important: '财为养命之源' — wealth nourishes life, and the wife star IS the wealth star in a man's chart.

Your {el} Day Master shapes how you pursue both career and relationship. The ancient wisdom suggests: the man who builds only his career builds half a life. The man who nurtures both his work AND his home builds a complete one."""

        return f"""
## 🌏 Your Cosmic Blueprint

### Your Day Master: **{dm} ({el})**

You were born under the sign of **{dm} ({el})** — {p["nature"]}. In the grand tapestry of elemental personalities, yours is the energy of {p["strength"]}.

Your BaZi chart reveals the four pillars of your destiny:

| | Year | Month | Day ⭐ | Hour |
|---|---|---|---|---|
| **Pillar** | {yp} | {mp} | **{dp}** | {hp} |

### 🎋 Your Elemental Story

Your Five Element distribution tells a unique story — **{elems_desc}**. Your dominant element is **{dom}**, while **{weak}** appears least in your chart. This pattern suggests that {p["challenge"]}.

**What this means in daily life:** The energy of {dom} comes naturally to you — it's your default mode. But consciously cultivating **{weak}** energy could unlock new dimensions of your personality. Think of it as cross-training for the soul.
{gender_note}

### 🐉 Your Chinese Zodiac

Born in the Year of the **{animal}**, you carry its spirit — its strengths, its instincts, and its unique way of moving through the world. The {animal} meets the {el} element, creating a distinctive blend of earthbound instinct and cosmic energy.

### 📅 Your Life Chapters

Your Major Luck (大运) begins around age **{age}** — this is when your life's larger rhythms start to reveal themselves. Each decade brings a new elemental influence, reshaping your priorities, challenges, and opportunities.

### 🌙 The Path Forward

Your cosmic blueprint is not a cage — it is a map. The elements that dominate show your natural gifts; the elements that recede show your growth edges. Ancient wisdom reminds us:

> *"知命者不怨天，知己者不怨人" — Those who understand destiny don't blame heaven; those who know themselves don't blame others.*

### 💭 Reflection

*What would change if you treated your "{weak}" qualities not as weaknesses, but as invitations to grow?*

---
*🔮 This reading is based on traditional Chinese metaphysical frameworks and is offered for entertainment and self-reflection. It does not constitute professional advice. The stars suggest — you decide.*
"""

    def _generate_love_reading(self, d: dict) -> str:
        p = self._get_persona(d["dm_element"])
        dm = d["dm_char"]
        el = d["dm_element"]
        dp = d.get("day_pillar", "??")
        db = d.get("day_branch", "?")
        ms = d.get("month_shishen", "your chart pattern")
        animal = d.get("animal", "Unknown")
        gender = d.get("gender", "")
        is_female = (gender == "female")

        # 日支夫妻宫解读
        BRANCH_LOVE = {
            "子": "carries Water Rat energy — intelligent, adaptable, and deeply intuitive in matters of the heart",
            "丑": "holds Earth Ox energy — steady, loyal, and quietly devoted. Love here is slow, deep, and forever",
            "寅": "resonates with Wood Tiger energy — bold, passionate, fiercely protective",
            "卯": "blooms with Wood Rabbit energy — gentle, artistic, and romantic, seeking beauty in partnership",
            "辰": "anchors in Earth Dragon energy — magnetic, ambitious, drawn to partners with presence and purpose",
            "巳": "burns with Fire Snake energy — intense, mysterious, and deeply selective",
            "午": "blazes with Fire Horse energy — passionate, free-spirited, seeking love that feels like adventure",
            "未": "nurtures with Earth Goat energy — warm, caring, and drawn to gentle souls",
            "申": "sharpens with Metal Monkey energy — witty, clever, attracted to stimulating minds",
            "酉": "refines with Metal Rooster energy — elegant, discerning, holding love to high standards",
            "戌": "guards with Earth Dog energy — loyal, protective, believing love is a vow",
            "亥": "flows with Water Pig energy — open-hearted, generous, loving with childlike purity",
        }
        branch_reading = BRANCH_LOVE.get(db, f"colors your experience of intimacy and partnership")

        # 性别特定的十神分析
        ss_desc = SHISHEN_LOVE.get(ms, "")

        # ====== 女性解读 ======
        if is_female:
            # 夫星分析
            husband_analysis = ""
            if ms in ("正官", "七杀"):
                husband_analysis = f"Your **{ms}** appearing in the month stem directly shapes your husband star (夫星). The 《三命通会·论女命》teaches: '妇人何利？利在夫星。夫利，其妇必利' — a woman's fortune is tied to her husband star's quality. When the husband star is well-placed and supported, the relationship becomes a source of strength and elevation."
            elif ms == "伤官":
                husband_analysis = "Your **Hurting Officer (伤官)** in the month stem creates a classic dynamic noted in 《三命通会》: '伤官太重又见官...此等女人不堪娶'. In modern terms, this means you have a fiercely independent spirit that can sometimes clash with traditional relationship expectations. The key is finding a partner who values your fire rather than trying to extinguish it."
            elif ms in ("正印", "偏印"):
                husband_analysis = "Your **Resource star (印星)** in the month position suggests you attract partners who support and nurture you. 《三命通会》sees this as auspicious: the Resource star protects and strengthens the Day Master, allowing you to thrive in partnership."
            else:
                husband_analysis = f"The placement of your **{ms}** in the month stem colors how you experience partnership. The 《三命通会》advises looking to your Day Branch (夫妻宫) and Major Luck cycles for relationship timing and quality."

            return f"""
## 💑 Your Love Blueprint

### 🌸 Your Feminine Nature in Love

Your Day Master is **{dm} ({el})** — {p["nature"]}. As a woman with this elemental constitution, you bring {p["strength"]} to your relationships. The 《三命通会》would describe you as someone whose romantic destiny is shaped by the quality of your husband star (夫星).

{husband_analysis}

### 🏠 Your Spouse Palace: {db}

Your Spouse Palace (夫妻宫) {branch_reading}. In a woman's chart, the Day Branch is where the husband "lives" — its quality directly affects marital happiness. {ss_desc}

### 💎 Your Ideal Partner

According to the Five Element framework, you're naturally drawn to partners who embody **{p["partner_ideal"].split('—')[0].strip()}** energy. {p["partner_ideal"]}

As a woman born in the Year of the **{animal}**, you bring a unique blend of instinct and cosmic energy. The 《三命通会》advises that the best match is not necessarily the most exciting one — it's the one where you can be fully yourself without diminishing your light.

### 🌸 When Love Blossoms

Your Major Luck cycles reveal natural windows for love and marriage. Pay special attention to years when your husband star (正官/七杀) or Spouse Palace ({db}) receives harmonious energy. In traditional BaZi, the arrival of the **Peach Blossom (桃花)** or **Red Luan (红鸾)** in annual or luck cycles signals powerful moments for romantic commitment.

### 🌙 Relationship Wisdom

{p["challenge"]} As a woman carrying {el} energy, this invites reflection: are you allowing yourself to receive as well as give? The healthiest partnerships are ecosystems, not hierarchies.

> *"金风玉露一相逢，便胜却人间无数" — When golden wind meets jade dew, it surpasses all earthly encounters.*

### 💭 Reflection

*What kind of partner would make you feel safe enough to be both strong AND soft?*

---
*🔮 This reading is based on traditional Chinese metaphysical frameworks and is offered for entertainment and self-reflection. It does not constitute professional advice. The stars suggest — you decide.*
"""
        # ====== 男性解读 ======
        else:
            # 妻星分析
            wife_analysis = ""
            if ms in ("正财", "偏财"):
                wife_analysis = f"Your **{ms}** appearing in the month stem directly shapes your wife star (妻星). 《三命通会》states: '正财者，受我克制，为我之妻' — the Direct Wealth is what the Day Master controls, representing the wife. A well-placed wife star promises a supportive, capable partner who brings practical value to your life."
            elif ms in ("比肩", "劫财"):
                wife_analysis = "Your **Peer star (比劫)** in the month stem creates a dynamic noted in 《三命通会》: when peer stars are strong and the wife star is weak, relationships may face competition or instability. The ancient remedy: develop your career and character (官星) to protect and stabilize your romantic life."
            elif ms == "食神":
                wife_analysis = "Your **Eating God (食神)** in the month position gives you warmth and charm in love. 《三命通会》sees this as auspicious for family life — the Eating God generates Wealth (wife star), suggesting your natural creativity and warmth will attract a loving partner."
            else:
                wife_analysis = f"The placement of your **{ms}** in the month stem influences how you approach commitment. 《三命通会》advises men to look at the strength of their Wealth star (财星) and Day Master to assess marriage prospects."

            return f"""
## 💑 Your Love Blueprint

### 🌳 Your Masculine Nature in Love

Your Day Master is **{dm} ({el})** — {p["nature"]}. As a man with this elemental constitution, you bring {p["strength"]} to your relationships. In traditional BaZi, a man's marriage fortune is read through his wife star (妻星), which is the Wealth element (财星) in his chart.

{wife_analysis}

### 🏠 Your Spouse Palace: {db}

Your Spouse Palace (夫妻宫) {branch_reading}. In a man's chart, the Day Branch is where his wife "resides" — a harmonious spouse palace promises a peaceful home life. {ss_desc}

### 💎 Your Ideal Partner

According to the Five Element framework, your ideal partner carries **{p["partner_ideal"].split('—')[0].strip()}** energy. {p["partner_ideal"]}

As a man born in the Year of the **{animal}**, you project a distinct presence. The 《三命通会》advises: '财宜藏，藏则丰厚' — the best wife is not necessarily the most visible or flashy one, but the one whose value runs deep and steady.

### 🌸 When Love Blossoms

The Major Luck cycles reveal when your wife star receives support — these are the natural windows for commitment and marriage. In traditional practice, years when your Wealth star (财星) is strong or when the Peach Blossom (桃花) appears in favorable positions mark powerful opportunities for finding or deepening love.

### 🌙 Relationship Wisdom

{p["challenge"]} As a man carrying {el} energy, this invites reflection: are you building a partnership, or just providing for one? The strongest relationships are those where you offer not just stability, but presence.

> *"君子爱财，取之有道" — The noble person seeks value through proper channels. The same is true of love.*

### 💭 Reflection

*What would change if you approached love not as something to acquire, but as something to cultivate — like a garden that needs daily tending?*

---
*🔮 This reading is based on traditional Chinese metaphysical frameworks and is offered for entertainment and self-reflection. It does not constitute professional advice. The stars suggest — you decide.*
"""

    def _generate_wealth_reading(self, d: dict) -> str:
        p = self._get_persona(d["dm_element"])
        dm = d["dm_char"]
        el = d["dm_element"]
        dom = d.get("dominant_element", el)
        weak = d.get("weakest_element", "Unknown")
        mp = d.get("month_pillar", "??")

        return f"""
## 💰 Your Wealth Architecture

### 🏔️ Your Money DNA

Your Day Master **{dm} ({el})** shapes your relationship with wealth. {p["wealth_style"]}

The ancient text *San Ming Tong Hui* (三命通会) teaches: *"财为养命之源"* — Wealth is the source that nourishes life. But it also warns: wealth must match the strength of the Day Master. Your {el} nature suggests a specific approach to prosperity — not someone else's path, but your own.

### 📊 Your Elemental Wealth Map

Your dominant element is **{dom}** — this is your natural economic advantage. It shapes the kind of work that feels effortless and the opportunities that gravitate toward you. Meanwhile, **{weak}** energy is your growth area — developing this could unlock income streams you haven't yet imagined.

**Your wealth style:** {p["wealth_style"]}

### 🎯 Career Alchemy

Based on your elemental profile, here are directions where your natural gifts can translate into prosperity:

- **{dom}-aligned work** comes easily — lean into this as your foundation
- **{weak}-building activities** expand your range — invest in developing this capacity
- The balance between them is where true mastery (and sustainable wealth) lives

{p["career_fit"]} — these fields align naturally with your elemental constitution.

### 💡 Eastern Wealth Wisdom

> *"君子爱财，取之有道" — The noble person loves wealth, but acquires it through proper channels.*

Your chart confirms this: sustainable prosperity comes through alignment, not force. When your work matches your element, wealth follows naturally. When you chase money against your nature, exhaustion follows instead.

### 💭 Reflection

*If money were no object, what would you still choose to do every day? The answer points to your true wealth path — and paradoxically, the path where prosperity is most likely to find you.*

---
*🔮 This reading is offered for self-reflection. Your financial decisions remain entirely your own.*
"""

    def _generate_daily_reading(self, d: dict, prompt: str) -> str:
        dm = d["dm_char"]
        el = d["dm_element"]
        p = self._get_persona(el)

        # 从prompt提取当日十神
        ss_match = re.search(r"Today's Energy Type:\s*\*?\*?(\S+)", prompt)
        daily_ss = ss_match.group(1) if ss_match else "balanced"

        # 当日宜忌
        DAILY_TIPS = {
            "正财": ("Handle finances, sign contracts, make purchases", "Intensive study, risky speculation"),
            "偏财": ("Business networking, investment review, socializing", "Gambling, lending large sums"),
            "正官": ("Career tasks, official matters, responsible communication", "High-risk ventures, challenging authority"),
            "七杀": ("Competitive activities, taking initiative, physical training", "Arguments, reckless decisions"),
            "正印": ("Study, planning, seeking mentorship, health checkups", "Overthinking, excessive dependence on others"),
            "偏印": ("Deep research, spiritual practice, solitude", "Social withdrawal, conspiracy thinking"),
            "食神": ("Creative expression, enjoying good food, learning", "Overindulgence, laziness"),
            "伤官": ("Innovation, artistic work, authentic self-expression", "Harsh criticism, rebellion without cause"),
            "比肩": ("Teamwork, social gatherings, sharing ideas", "Major investments, signing contracts"),
            "劫财": ("Building alliances, collaborative projects", "All financial decisions, lending money"),
        }

        tips = DAILY_TIPS.get(daily_ss, ("Follow your intuition", "Major life decisions"))
        auspicious, caution = tips

        return f"""
## 🔮 Your Day Ahead

### Today's Cosmic Weather

*"When {daily_ss} energy visits, the day takes on a distinct character."*

Today's energy is **{daily_ss}** — interacting with your **{dm} ({el})** Day Master. {p["nature"]}

### 🌟 Flourish

- **{auspicious.split(',')[0].strip()}** — today's energy supports this naturally
- {auspicious.split(',')[1].strip() if ',' in auspicious else "Follow what feels aligned"}

### ⚠️ Gentle Caution

- **{caution.split(',')[0].strip()}** — best saved for another day
- {caution.split(',')[1].strip() if ',' in caution else "Trust your instincts"}

### 💫 Your Mantra

> *"顺其自然，为所当为" — Flow with nature; do what must be done.*

Today is not about forcing outcomes. It's about sensing the energy and moving with it, not against it.

---
*🔮 Daily energy check — a compass, not a cage. How you use the day is always your choice.*
"""

    def _generate_compat_reading(self, d: dict) -> str:
        dm = d["dm_char"]
        el = d["dm_element"]
        p = self._get_persona(el)

        return f"""
## 🤝 Your Cosmic Chemistry

### The Element Dance

When two charts meet, the Five Elements tell the first story. It's not about "good match" or "bad match" — it's about the unique alchemy that happens when two elemental constitutions interact.

Your Day Master **{dm} ({el})** — {p["nature"]} — brings specific energy to any relationship. The question is: does the other person's element nourish, challenge, or balance yours?

### Three Types of Cosmic Connection

**🌿 Nourishing (相生):** One person's element generates the other's — like Water feeding Wood. These relationships feel naturally supportive, like rain on fertile soil.

**⚔️ Challenging (相克):** One element controls another — like Metal cutting Wood. These relationships are intense and transformative. They can be the forge where both people become stronger, or the fire that consumes. The difference is **mutual respect**.

**☯️ Balancing:** Each person's excess is the other's deficiency. This is the rarest and most powerful connection — two people who literally complete each other's elemental equation.

### 🔍 What to Look For

When analyzing compatibility, the ancient masters looked beyond the surface:
1. **Day Branch harmony** — do your Spouse Palaces clash or embrace?
2. **Five Element complement** — does Person A's excess get balanced by Person B's deficiency?
3. **Shared timing** — do your Major Luck cycles align?

### 🌙 The Wisdom

> *"有缘千里来相会，无缘对面不相逢" — Fate brings together those who are meant to meet, no matter the distance.*

Some of the best partnerships are the ones that challenge us. The question isn't whether it's easy — it's whether it's worth it. The ancient sages believed that the strongest marriages weren't the ones with no conflicts, but the ones where each person's "excess" was tempered by the other's "deficiency."

### 💭 Reflection

*What's one way your partner's difference has actually made you better? And one way your difference has made them better?*

---
*🔮 Compatibility insights for self-reflection, not life decisions. Every relationship is what you make it.*
"""
