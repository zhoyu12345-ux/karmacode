"""
KarmaCode - FateTell风格 AI 解读引擎 v2
现代化、共情化、具象化的命理分析
"""

import re
import json
import os
from typing import AsyncGenerator
from dataclasses import dataclass


@dataclass
class ReadingConfig:
    reading_type: str
    stream: bool = True
    max_tokens: int = 2000
    temperature: float = 0.7


# ============================================================
# 五行人格画像（更现代的描述）
# ============================================================

ELEMENT_PROFILES = {
    "Wood": {
        "essence": "You're the person people go to when they need growth. Like a tree that keeps reaching upward no matter how hard the wind blows — that's you. You don't just adapt to change; you ARE the change.",
        "gift": "Vision. You see possibilities where others see problems.",
        "shadow": "Sometimes you grow in too many directions at once. Not every branch needs to reach the sun.",
        "love": "In love, you're the gardener — always nurturing, always growing. But gardens need pruning too. The right partner isn't the one who lets you grow wild; it's the one who knows which branches to trim.",
        "work": "You thrive in roles where you can create, teach, or build something that outlasts you. Boring routines feel like cages to you.",
        "quote": "\"A tree doesn't rush toward the sun — it simply grows, one patient ring at a time.\"",
    },
    "Fire": {
        "essence": "When you walk into a room, people feel it. You carry a warmth that's magnetic, a spark that's contagious. You're the flame — and everyone wants to sit by your fire.",
        "gift": "Passion. You don't do anything halfway.",
        "shadow": "Flames that burn brightest burn out fastest. You need people who remind you to rest.",
        "love": "You love the way fire loves — intensely, completely, transforming everything it touches. The risk? Burning through relationships when the initial spark fades. Your soulmate isn't the hottest flame — it's the one that keeps you warm through the longest nights.",
        "work": "You need work that matters. If it doesn't light you up, you'll find something else that does.",
        "quote": "\"A fire's purpose isn't to burn forever — it's to ignite everything it touches.\"",
    },
    "Earth": {
        "essence": "In a world of chaos, you're the mountain. People lean on you because you're solid. You don't chase trends or drama — you build things that last.",
        "gift": "Stability. You're the anchor in every storm.",
        "shadow": "Mountains are strong, but they don't move easily. Sometimes you hold on too long.",
        "love": "You love the way mountains love — deeply, quietly, forever. You don't need grand gestures; you need someone who shows up, day after day, year after year. The right partner for you doesn't complete you — they stand beside you, another mountain in the range.",
        "work": "You're built for the long game. Finance, real estate, healthcare, education — fields where trust compounds over decades.",
        "quote": "\"A mountain isn't built in a day — it's carved by time, wind, and patience.\"",
    },
    "Metal": {
        "essence": "You have a mind like a blade — it cuts through noise and gets to what matters. People respect you before they like you, and they're usually right to.",
        "gift": "Clarity. You see the truth when others are tangled in feelings.",
        "shadow": "Blades that never bend eventually break. Softness isn't weakness.",
        "love": "You love with integrity, not drama. You're not the type for messy entanglements — you want a partnership with clear terms, mutual respect, and quiet devotion. Your ideal match is someone who can soften your edges without dulling your edge.",
        "work": "Law, engineering, finance, technology — anywhere precision matters, you belong.",
        "quote": "\"True strength isn't never bending — it's bending and returning true.\"",
    },
    "Water": {
        "essence": "You're deep. While others skim the surface, you're exploring depths they don't even know exist. Your intuition is your compass, and it rarely steers you wrong.",
        "gift": "Wisdom. You understand things without needing them explained.",
        "shadow": "Depth without direction becomes an ocean without shores. You need anchors.",
        "love": "You love like water — adapting, flowing, filling every space. You're the most emotionally intelligent partner someone could ask for. But water needs a container — someone who gives your flowing nature a shape, a shoreline, a home.",
        "work": "Research, psychology, arts, writing — anywhere that rewards depth over speed.",
        "quote": "\"Water is the softest thing in the world, yet it can carve through mountains and reshape continents.\"",
    },
}


class FateTellMockClient:
    """FateTell风格的Mock AI客户端 — 现代、共情、具象"""

    async def generate_reading_stream(self, system_prompt: str, user_prompt: str,
                                        config: ReadingConfig = ReadingConfig("general")) -> AsyncGenerator[str, None]:
        import asyncio
        chart_data = self._parse_chart_from_prompt(user_prompt)

        if config.reading_type == "love":
            text = self._generate_love_reading(chart_data)
        elif config.reading_type == "wealth":
            text = self._generate_wealth_reading(chart_data)
        elif config.reading_type == "daily":
            text = self._generate_daily_sign(chart_data)
        elif config.reading_type == "compatibility":
            text = self._generate_compat_reading(chart_data)
        else:
            text = self._generate_general_reading(chart_data)

        text += self._format_classical_footnotes(chart_data)

        for char in text:
            yield char
            await asyncio.sleep(0.0005)

    def generate_reading_sync(self, system_prompt: str, user_prompt: str,
                                config: ReadingConfig = ReadingConfig("general")) -> str:
        chart_data = self._parse_chart_from_prompt(user_prompt)

        if config.reading_type == "love":
            text = self._generate_love_reading(chart_data)
        elif config.reading_type == "wealth":
            text = self._generate_wealth_reading(chart_data)
        elif config.reading_type == "daily":
            text = self._generate_daily_sign(chart_data)
        elif config.reading_type == "compatibility":
            text = self._generate_compat_reading(chart_data)
        else:
            text = self._generate_general_reading(chart_data)

        return text + self._format_classical_footnotes(chart_data)

    # ============================================================
    # 数据解析（从旧版沿用）
    # ============================================================

    def _parse_chart_from_prompt(self, prompt: str) -> dict:
        data = {
            "dm_char": "?", "dm_element": "Unknown", "dm_yinyang": "", "dm_en": "",
            "year_pillar": "??", "month_pillar": "??", "day_pillar": "??", "hour_pillar": "??",
            "animal": "", "gender": "", "dominant_element": "", "weakest_element": "",
            "month_shishen": "", "hour_shishen": "", "day_branch": "", "start_age": "",
            "elements": {}, "classical_findings": [],
        }

        m = re.search(r'Day Master:\s*\*?\*?(\S+)\s*\((\w+),\s*(\w+)\)', prompt)
        if m:
            data["dm_char"] = m.group(1).strip().replace("*", "")
            data["dm_element"] = m.group(2).strip()
            data["dm_yinyang"] = m.group(3).strip() if len(m.groups()) > 2 else ""

        for pillar_name, key in [("Year:", "year_pillar"), ("Month:", "month_pillar"),
                                  ("Day:", "day_pillar"), ("Hour:", "hour_pillar")]:
            p = re.search(rf'{pillar_name}\s*\*?\*?(\S\S)', prompt)
            if p: data[key] = p.group(1)
        if len(data.get("day_pillar", "")) >= 2:
            data["day_branch"] = data["day_pillar"][1]

        gm = re.search(r'Gender:\s*(\w+)', prompt)
        if gm: data["gender"] = gm.group(1)
        am = re.search(r'Zodiac:\s*\*?\*?(\w+)', prompt)
        if am: data["animal"] = am.group(1)
        sm = re.search(r'start_age["\']?\s*:\s*(\d+)', prompt)
        if sm: data["start_age"] = sm.group(1)

        for e in ["Wood", "Fire", "Earth", "Metal", "Water"]:
            em = re.search(rf'"{e}":\s*(\d+)', prompt)
            if em: data["elements"][e] = int(em.group(1))
        dm_match = re.search(r'Dominant:\s*\*?\*?(\w+)', prompt)
        if dm_match: data["dominant_element"] = dm_match.group(1)
        wk_match = re.search(r'Weakest:\s*\*?\*?(\w+)', prompt)
        if wk_match: data["weakest_element"] = wk_match.group(1)
        ms_match = re.search(r'Month Stem:\s*\*?\*?(\S+)', prompt)
        if ms_match: data["month_shishen"] = ms_match.group(1)

        return data

    def _get_profile(self, element: str) -> dict:
        return ELEMENT_PROFILES.get(element, ELEMENT_PROFILES["Earth"])

    # ============================================================
    # 全新FateTell风格解读
    # ============================================================

    def _generate_general_reading(self, d: dict) -> str:
        p = self._get_profile(d["dm_element"])
        dm = d["dm_char"]
        el = d["dm_element"]
        dom = d.get("dominant_element", el)
        weak = d.get("weakest_element", "Unknown")
        yp, mp, dp, hp = d.get("year_pillar", "??"), d.get("month_pillar", "??"), d.get("day_pillar", "??"), d.get("hour_pillar", "??")
        animal = d.get("animal", "Unknown")
        age = d.get("start_age", "?")
        is_female = (d.get("gender", "") == "female")

        gender_intro = ""
        if is_female:
            gender_intro = "I can feel the depth of what you're searching for. The ancient Chinese sages believed a woman's chart is like a river — its course is set at birth, but how it flows depends on the landscape it travels through."
        else:
            gender_intro = "I understand why you're here. The ancient masters believed a man's chart is like a mountain — its foundation is fixed at birth, but what you build on it? That's entirely yours to decide."

        elems_desc = ", ".join([f"{e}: {c}" for e, c in d.get("elements", {}).items()]) if d.get("elements") else "a balanced constitution"

        return f"""
{gender_intro}

---

### 🎭 Who You Are

Your Day Master is **{dm} ({el})**. {p["essence"]}

Your chart carries {elems_desc}. Your natural strength flows through **{dom}** — this is your superpower. But your growth edge? It lives in **{weak}** — the energy that challenges you the most is also the one that will transform you the most.

Here's the thing ancient Chinese metaphysics understood that Western psychology is only now catching up to: **your greatest gift and your greatest challenge are the same energy, just expressed differently.**

### 🐉 The Animal That Walks With You

Born in the Year of the **{animal}**, you carry an archetype that's been recognized across thousands of years of Chinese civilization. The {animal} isn't just a zodiac sign — it's a lens through which the world perceives you, and through which you perceive yourself.

### 📊 Your Life's Architecture

```
Year  → {yp}  (Ancestry, childhood)
Month → {mp}  (Career foundation, parents)
Day   → {dp}  ⭐ YOUR CORE SELF
Hour  → {hp}  (Hidden depths, later life)
```

### 🌙 The Path Forward

> {p["quote"]}

{p["shadow"]} And that's okay. Awareness is the first step toward integration.

Your Major Luck begins around age **{age}** — the cosmic clockwork doesn't start ticking until then. Before that, you're learning the rules of your own game. After that? You start playing for real.

### 💭 A Question to Sit With

*If you could fully embody your {weak} energy for one day — what would that day look like?*

---
*KarmaCode · Your stars suggest. You decide.*
"""

    def _generate_love_reading(self, d: dict) -> str:
        p = self._get_profile(d["dm_element"])
        dm = d["dm_char"]
        el = d["dm_element"]
        db = d.get("day_branch", "?")
        ms = d.get("month_shishen", "")
        animal = d.get("animal", "")
        is_female = (d.get("gender", "") == "female")

        # 夫妻宫具体描述
        SPOUSE_PALACE = {
            "子": "Your love lives in Water Rat territory — quick-witted, deeply intuitive. You need a partner who can keep up with your mind, not just your heart.",
            "丑": "Your Spouse Palace is Ox earth — steady, patient, built for the long haul. You don't fall fast, but when you fall, it's forever. Loyalty isn't a choice for you; it's your default setting.",
            "寅": "Tiger Wood energy lives in your Spouse Palace. You need a partner who brings passion and courage — someone who makes life feel like an adventure, not a routine.",
            "卯": "Rabbit Wood blooms in your relationship zone. You're a romantic at your core — beauty, art, and tenderness aren't luxuries for you; they're relationship requirements.",
            "辰": "Dragon Earth guards your Spouse Palace. You're drawn to power and presence — your ideal partner has ambition that matches your own. Together, you're a force.",
            "巳": "Fire Snake coils in your relationship house. Intensity is your love language. You don't do surface-level connections — when you commit, it's soul-deep or not at all.",
            "午": "Fire Horse gallops through your love zone. Freedom and passion aren't opposites for you — they're the same thing. The right partner runs beside you, not in front of you.",
            "未": "Earth Goat nurtures your relationships. You love through care — cooking meals, remembering details, being the soft place to land. Your partner must appreciate quiet devotion.",
            "申": "Metal Monkey sharpens your romantic instincts. You need intellectual chemistry — a partner who challenges your mind will capture your heart.",
            "酉": "Metal Rooster refines your love life. Standards matter to you. You'd rather wait for the right person than settle — and when they arrive, you'll know.",
            "戌": "Earth Dog protects your relationship house. Loyalty is your non-negotiable. Love, for you, is a vow — not a feeling that comes and goes.",
            "亥": "Water Pig flows through your love zone. You love with an almost childlike openness — generous, trusting, seeing the best in your partner even when they can't see it themselves.",
        }
        spouse_desc = SPOUSE_PALACE.get(db, f"Your Spouse Palace reflects your intimate relationship patterns.")

        # 性别特定分析
        if is_female:
            gender_section = f"""
### 👰 Your Love Story

{dm} women with {el} energy carry a specific kind of power in relationships. {p["love"]}

I'll be honest with you — your chart shows patterns that the ancient masters would study carefully. But here's what they didn't write in the old texts: a chart isn't a cage. It's a map. And you get to choose the route.

The partner who's right for you isn't necessarily the richest, the most successful, or the most conventionally attractive. It's the one whose presence makes you feel **more yourself, not less**.
"""
        else:
            gender_section = f"""
### 🤵 Your Love Story

{dm} men with {el} energy bring something rare to relationships. {p["love"]}

The ancient texts talk about a man's wife star (妻星) — but here's the modern translation: you're not looking for someone to complete you. You're looking for someone whose presence adds a dimension to your life that wasn't there before.

In the Five Element framework, {p["love"][:80]}...

The partner who's right for you? Someone whose elemental nature balances yours — not by being your opposite, but by filling the spaces you didn't know were empty.
"""

        return f"""
### 💑 Love & You

I know why you clicked this tab. Love — real, lasting, soul-level connection — is the thing we all want and the thing that scares us most. So let's look at what your chart actually says, without the mystical filter.

{spouse_desc}

{gender_section}

### 🏠 Where Love Lives: Your Spouse Palace ({db})

In BaZi, the Day Branch isn't just your spouse's "room" in your chart — it's the entire architecture of your intimate life. Yours carries {db} energy, which means...

{spouse_desc}

### 💎 The Kind of Person Who Fits

Based on your elemental makeup, you'll feel most at home with someone who carries **{p.get('gift', 'complementary')}** energy. This isn't about zodiac compatibility or star sign matching — it's about elemental chemistry.

When {el} meets its complementary element, something clicks. Conversations flow. Silences feel comfortable. You don't have to explain yourself — they just get it.

### 🌸 Timing

The ancient texts speak of "Peach Blossom years" — windows when the cosmic energy aligns for love. Pay attention when your Spouse Palace ({db}) receives supporting energy from the annual cycle. These aren't random — they're when the universe is most receptive to your romantic intentions.

### 🌙 The Wisdom

> {p["quote"]}

The best love isn't the one that's easiest. It's the one where both people grow — sometimes together, sometimes individually, but always toward more authentic versions of themselves.

### 💭 A Question

*What would change if you approached your love life less like a problem to solve, and more like a garden to tend?*

---
*KarmaCode · Ancient wisdom, modern understanding.*
"""

    def _generate_wealth_reading(self, d: dict) -> str:
        p = self._get_profile(d["dm_element"])
        dm = d["dm_char"]
        el = d["dm_element"]
        dom = d.get("dominant_element", el)
        weak = d.get("weakest_element", "Unknown")

        # 财星判断
        ms = d.get("month_shishen", "")
        if "财" in ms:
            wealth_note = f"Your month stem carries {ms} — the wealth star is prominent in your chart. The ancient texts say people with this configuration 'see money as their servant, not their master.'"
        else:
            wealth_note = "Your wealth stars may not shout from the mountaintop, but they're present in your chart's architecture. This isn't a sign of poverty — it's a sign that wealth comes to you through structure, not spectacle."

        return f"""
### 💰 You & Money

Let's talk about the thing everyone thinks about but few feel comfortable discussing openly.

{wealth_note}

### 🏔️ Your Money DNA

As a **{dm} ({el})** Day Master, your relationship with money is shaped by elemental physics. {p.get("essence", "")[:200]}

{p.get("work", "")}

### 📊 The Architecture of Your Wealth

Your dominant element is **{dom}**. This shapes the kind of work that feels effortless — the sort where you lose track of time and produce your best results without feeling drained.

Meanwhile, **{weak}** is your growth edge. Developing this energy — through skills, relationships, or simply awareness — could unlock income streams you haven't yet imagined.

### 🎯 What This Means, Practically

The ancient text 《三命通会》 says: *"财为养命之源 — Wealth is the source that nourishes life."*

But it also warns: wealth must match the Day Master's strength. If you chase money against your elemental nature, exhaustion follows. If you align your work with your element, prosperity follows naturally.

### 💡 The Takeaway

> {p["quote"]}

Your wealth path isn't about chasing trends or copying someone else's strategy. It's about doing work that feels so natural to you that the money becomes secondary — and paradoxically, that's exactly when it arrives.

### 💭 A Question

*If money weren't a concern for one year, what would you spend your days doing? The answer is your wealth compass.*

---
*KarmaCode · Prosperity follows purpose.*
"""

    def _generate_daily_sign(self, d: dict) -> str:
        """日签风格 — FateTell 式每日能量卡片"""
        import random

        dm = d["dm_char"]
        el = d["dm_element"]
        p = self._get_profile(el)

        # 随机生成能量指数（模拟）
        energy_score = random.randint(55, 92)
        lucky_color = random.choice(["Crimson", "Jade Green", "Gold", "Deep Blue", "Amber", "Violet"])
        lucky_number = random.randint(1, 9)
        lucky_direction = random.choice(["East", "Southeast", "South", "North", "West"])

        # 日签短语
        SIGNS = [
            {"title": "🌅 Still Waters", "msg": "Today is not for pushing. It's for positioning. The wave is coming — be ready, not busy.", "vibe": "Reflective"},
            {"title": "⚡ Lightning Strike", "msg": "An insight today will change everything. Pay attention to thoughts that arrive fully formed — they're not random.", "vibe": "Revelatory"},
            {"title": "🌿 Gentle Growth", "msg": "Progress today won't look like progress. Watering seeds never does. Trust the invisible work.", "vibe": "Nurturing"},
            {"title": "🗻 Steady Ground", "msg": "Today rewards consistency. Not brilliance. Not luck. Just showing up and doing the thing you said you'd do.", "vibe": "Grounded"},
            {"title": "🦋 Small Shift", "msg": "One tiny change today changes everything three months from now. You'll know what it is when you see it.", "vibe": "Transformative"},
        ]
        sign = random.choice(SIGNS)

        return f"""
```
┌──────────────────────────────────┐
│         TODAY'S ENERGY            │
│                                  │
│     🔮 Energy Score: {energy_score}/100      │
│     🎨 Color: {lucky_color}               │
│     🔢 Number: {lucky_number}                     │
│     🧭 Direction: {lucky_direction}          │
│                                  │
└──────────────────────────────────┘
```

### {sign["title"]}

*{sign["msg"]}*

**Vibe: {sign["vibe"]}**

---

### 🌤 Your Cosmic Weather

As a **{dm} ({el})** Day Master, today's energy interacts with your core nature in a specific way. {p.get("essence", "")[:150]}

### ✅ Lean Into

- Tasks that require **sustained focus** rather than quick pivots
- Conversations you've been putting off — today's energy supports honest dialogue
- One small step toward something that scares you

### ⚠️ Gently Avoid

- Impulsive financial decisions — sit on it for 24 hours
- Arguments about things that won't matter next week
- Overcommitting — today's a "quality over quantity" kind of day

---

> *"The day's design is set at dawn. Your first hour shapes the rest."*

**Today's invitation:** Notice one moment of unexpected beauty, and let it be enough.

---
*KarmaCode · Daily Sign*
"""

    def _generate_compat_reading(self, d: dict) -> str:
        p = self._get_profile(d["dm_element"])
        dm = d["dm_char"]
        el = d["dm_element"]
        return f"""
### 🤝 Compatibility

Analyzing two charts together is like reading a duet — the notes each person plays matter less than the harmony between them.

Your **{dm} ({el})** nature brings specific energy to any relationship. The question isn't "are they a good match on paper" — it's "does this combination create more light than heat?"

### The Three Types of Connection

**🌿 Nurturing** — One person's element feeds the other's. Like rain on fertile soil. These relationships feel naturally supportive.

**⚔️ Transformative** — One element challenges the other. Like a blade against a whetstone. These relationships sharpen both people — but can also wear them down if there isn't mutual respect.

**☯️ Balancing** — Each person's excess is the other's deficiency. The rarest connection. Two people who literally complete each other's elemental equation.

### What Actually Matters

The ancient masters looked beyond zodiac signs to three things:
1. **Day Branch harmony** — Do your Spouse Palaces clash or embrace?
2. **Elemental complement** — Does each person's "too much" get balanced by the other's "not enough"?
3. **Timing alignment** — Do your Major Luck cycles support commitment at the same time?

> {p["quote"]}

Some of the best partnerships weren't predicted by charts. They were built by two people who decided, every day, to choose each other.

---
*KarmaCode · The stars suggest. Love decides.*
"""

    def _format_classical_footnotes(self, d: dict) -> str:
        """简洁的古籍脚注"""
        return ""


# 导出为 MockClaudeClient 兼容接口
MockClaudeClient = FateTellMockClient
