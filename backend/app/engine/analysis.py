"""
KarmaCode - 古籍反向分析引擎
基于《三命通会》规则库，对八字命盘进行逆向规则匹配分析
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

# ============================================================
# 加载知识库
# ============================================================

_terminology_cache = None
_rules_text_cache = None


def _load_terminology() -> dict:
    global _terminology_cache
    if _terminology_cache is None:
        path = KNOWLEDGE_DIR / "01_术语表_terminology.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                _terminology_cache = json.load(f)
    return _terminology_cache or {}


def _load_rules() -> str:
    global _rules_text_cache
    if _rules_text_cache is None:
        path = KNOWLEDGE_DIR / "02_规则库_rules.md"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                _rules_text_cache = f.read()
    return _rules_text_cache or ""


# ============================================================
# 规则匹配核心
# ============================================================

def _extract_rule_section(rules_text: str, section_header: str) -> str:
    """从规则库中提取特定章节"""
    pattern = rf"##\s+{re.escape(section_header)}.*?(?=##\s+|$)"
    match = re.search(pattern, rules_text, re.DOTALL)
    return match.group(0).strip() if match else ""


def _extract_specific_rule(rules_text: str, rule_name: str) -> str:
    """提取特定规则条目"""
    pattern = rf"\*\*规则[\d.]+\*\*.*?{re.escape(rule_name)}.*?(?=\*\*规则|\*\*#|$)"
    match = re.search(pattern, rules_text, re.DOTALL)
    if not match:
        # 尝试更宽松的匹配
        pattern2 = rf"{re.escape(rule_name)}.*?(?=\n\n|\*\*规则|$)"
        match = re.search(pattern2, rules_text, re.DOTALL)
    return match.group(0).strip() if match else ""


# ============================================================
# 婚姻分析
# ============================================================

def analyze_marriage(chart: dict) -> dict:
    """
    基于古籍规则反向分析婚姻

    检查项：
    1. 夫星/妻星纯度（官杀混杂判定）
    2. 女命八法匹配
    3. 夫妻宫分析
    4. 桃花/红鸾分析
    5. 孤辰寡宿分析
    6. 十神组合判定
    """
    rules_text = _load_rules()
    findings = []
    classical_refs = []

    pillars = chart["pillars"]
    shishen = chart["shishen"]
    shensha = chart["shensha"]
    day_master = chart["day_master"]
    gender = chart["birth_info"]["gender"]
    wuxing = chart["wuxing_count"]

    # ========== 1. 夫星/妻星纯度分析 ==========
    if gender == "female":
        # 检查官杀混杂
        has_zhengguan = False
        has_qisha = False
        for stem_pos in ["year_stem", "month_stem", "hour_stem"]:
            ss_name = shishen.get(stem_pos, {}).get("name", "")
            if ss_name == "正官":
                has_zhengguan = True
            if ss_name == "七杀":
                has_qisha = True

        # 检查藏干中的官杀
        hidden = shishen.get("hidden_stems_shishen", {})
        for pillar_name, stems in hidden.items():
            for s in stems:
                if s.get("shishen") == "正官":
                    has_zhengguan = True
                if s.get("shishen") == "七杀":
                    has_qisha = True

        if has_zhengguan and has_qisha:
            findings.append({
                "category": "官杀混杂",
                "severity": "important",
                "classical_rule": "规则1.1.1 — 夫星纯度原则",
                "finding": "Your chart shows mixed Officer (正官) and Killing (七杀) stars. The 《三命通会》states: '官煞混杂，感情复杂，易有多段感情纠葛' — when both the Direct Officer and Seven Killings appear, emotional life tends to be complex.",
                "source": "《三命通会·论女命》",
                "advice": "This doesn't mean relationships are doomed — it means you benefit from clarity about what you truly want in a partner. When one star is clearly dominant (e.g., supported by Wealth or Resource), the mixing is mitigated.",
            })
        elif has_zhengguan:
            findings.append({
                "category": "夫星清纯",
                "severity": "positive",
                "classical_rule": "规则1.1.1 — 夫星纯度原则",
                "finding": "Your chart shows pure Direct Officer (正官) energy for the husband star — this is the most auspicious configuration according to 《三命通会》: '独一位官星，无煞以杂之，俱为良妇' (a single Officer star without Killing mixed is a virtuous wife pattern).",
                "source": "《三命通会·论女命》",
            })
        elif has_qisha:
            findings.append({
                "category": "七杀为夫",
                "severity": "neutral",
                "classical_rule": "规则1.1.1",
                "finding": "Your husband star manifests as Seven Killings (七杀) rather than Direct Officer. 《三命通会》notes this brings a more intense, dynamic relationship pattern — the partner tends to be strong-willed and ambitious. The key is whether the Killing star is well-controlled (有制).",
                "source": "《三命通会·论女命》",
            })
        else:
            findings.append({
                "category": "夫星不显",
                "severity": "neutral",
                "finding": "Your husband star (官杀) does not appear prominently in the heavenly stems. It may be hidden in the earthly branches' concealed stems (藏干). 《三命通会》suggests looking to the Spouse Palace (日支) and Major Luck cycles for relationship timing.",
            })

    elif gender == "male":
        # 检查财星状况
        has_zhengcai = False
        has_piancai = False
        for stem_pos in ["year_stem", "month_stem", "hour_stem"]:
            ss_name = shishen.get(stem_pos, {}).get("name", "")
            if ss_name == "正财":
                has_zhengcai = True
            if ss_name == "偏财":
                has_piancai = True

        if has_zhengcai and has_piancai:
            findings.append({
                "category": "财星混杂",
                "severity": "important",
                "classical_rule": "规则1.2.1 — 妻星判断",
                "finding": "Your chart contains both Direct Wealth (正财, primary wife star) and Indirect Wealth (偏财, secondary). 《三命通会》warns this can create complexity in romantic life — '正偏财混杂，妻妾难明'.",
                "source": "《三命通会》",
            })
        elif has_zhengcai:
            findings.append({
                "category": "正财为妻",
                "severity": "positive",
                "finding": "Your wife star is Direct Wealth (正财) — indicating a preference for stable, committed partnerships. The 《三命通会》 says: '正财者，受我克制，为我之妻' (Direct Wealth is what I control — my wife).",
            })
        elif has_piancai:
            findings.append({
                "category": "偏财为妻",
                "severity": "neutral",
                "finding": "Your wife star manifests as Indirect Wealth (偏财) — suggesting attraction to dynamic, independent partners. The relationship may have an unconventional quality.",
            })

        # 检查比劫夺财
        has_bijie = False
        for stem_pos in ["year_stem", "month_stem", "hour_stem"]:
            ss_name = shishen.get(stem_pos, {}).get("name", "")
            if ss_name in ("比肩", "劫财"):
                has_bijie = True
        if has_bijie and (has_zhengcai or has_piancai):
            findings.append({
                "category": "比劫夺财",
                "severity": "caution",
                "classical_rule": "规则1.2.1",
                "finding": "Your chart shows Peer stars (比劫) alongside Wealth stars — 《三命通会》warns this can indicate competition for romantic partners or difficulty keeping relationships stable.",
                "source": "《三命通会》",
            })

    # ========== 2. 夫妻宫分析 ==========
    day_branch_char = pillars["day"]["branch"]["char"]
    day_branch_idx = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"].index(day_branch_char)

    # 检查夫妻宫被冲
    clashes = {"子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
               "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}
    day_clash = clashes.get(day_branch_char)
    for pillar_key in ["year", "month", "hour"]:
        if pillars[pillar_key]["branch"]["char"] == day_clash:
            findings.append({
                "category": "夫妻宫逢冲",
                "severity": "warning",
                "classical_rule": "规则1.3.2 — 日柱合婚法",
                "finding": f"Your Spouse Palace (日支 {day_branch_char}) is clashed by the {pillar_key} pillar ({day_clash}). 《三命通会》states this is a significant indicator of marriage instability: '日柱天克地冲，婚姻大忌，极难白首'. However, a clash is not a death sentence — it can also manifest as a relationship that is dynamic and transformative rather than ending.",
                "source": "《三命通会》",
            })

    # 检查夫妻宫被合
    combinations = {"子": "丑", "丑": "子", "寅": "亥", "亥": "寅", "卯": "戌", "戌": "卯",
                    "辰": "酉", "酉": "辰", "巳": "申", "申": "巳", "午": "未", "未": "午"}
    day_combo = combinations.get(day_branch_char)
    for pillar_key in ["year", "month", "hour"]:
        if pillars[pillar_key]["branch"]["char"] == day_combo:
            findings.append({
                "category": "夫妻宫逢合",
                "severity": "positive",
                "classical_rule": "规则1.3.2",
                "finding": f"Your Spouse Palace (日支 {day_branch_char}) forms a harmonious combination (合) with the {pillar_key} pillar. 《三命通会》considers this auspicious for relationships — '合多代表共同语言多，夫妻更和睦恩爱'.",
                "source": "《三命通会》",
            })

    # ========== 3. 女命八法判定 ==========
    if gender == "female":
        eight_methods = _analyze_eight_methods(chart, shishen)
        if eight_methods:
            findings.append(eight_methods)

    # ========== 4. 桃花/红鸾分析 ==========
    peach = shensha.get("桃花_Peach_Blossom", {})
    red_luan = shensha.get("红鸾_RedLuan_Marriage", {})
    solitude = shensha.get("孤辰寡宿_Solitude", {})

    if peach.get("present_in"):
        pillars_with = ", ".join(peach["present_in"])
        findings.append({
            "category": "桃花入命",
            "severity": "neutral",
            "classical_rule": "规则1.4 — 桃花/咸池规则",
            "finding": f"Peach Blossom star (桃花) appears in your {pillars_with} pillar(s). 《三命通会·论咸池》: '如生旺，则美容仪，耽酒色' — when in a strong position, it brings beauty and charisma. Context matters: in the Day or Hour pillar, it most strongly affects personal relationships.",
            "source": "《三命通会·卷二·论咸池》",
        })

    if red_luan.get("present_in"):
        findings.append({
            "category": "红鸾星动",
            "severity": "positive",
            "finding": "Red Luan (红鸾) — the marriage star — is present in your chart. In traditional timing, when annual or Major Luck energy activates this star, it signals a powerful window for commitment and weddings.",
            "source": "《三命通会》",
        })

    if solitude.get("guchen_branch") or solitude.get("guasu_branch"):
        findings.append({
            "category": "孤辰寡宿",
            "severity": "caution",
            "classical_rule": "规则1.4",
            "finding": "Your chart carries the Solitude stars (孤辰寡宿). 《三命通会》associates this with a tendency toward emotional independence — sometimes to the point of isolation. In modern terms, this is not a curse but an invitation to consciously cultivate emotional connection.",
            "source": "《三命通会》",
        })

    # ========== 5. 十神组合分析 ==========
    month_ss = shishen.get("month_stem", {}).get("name", "")

    if month_ss == "伤官":
        findings.append({
            "category": "伤官格女命",
            "severity": "caution",
            "classical_rule": "规则1.1.3 — 八法断命体系",
            "finding": "Your month pillar carries Hurting Officer (伤官). 《三命通会·论女命》 specifically warns: '伤官太重又见官，贪财破印俱不堪' — Hurting Officer can clash with the husband star (Officer), potentially causing relationship friction. However, this same energy gives you brilliant creativity and independence.",
            "source": "《三命通会·论女命》",
            "advice": "The key is channeling your independent spirit into creative or professional pursuits, rather than letting it become confrontational in relationships.",
        })

    return {
        "findings": findings,
        "summary": _generate_marriage_summary(findings, chart),
    }


def _analyze_eight_methods(chart: dict, shishen: dict) -> dict:
    """女命八法分析"""
    has_officer = False
    has_killing = False
    has_wealth = False
    has_resource = False
    has_hurting = False

    for stem_pos in ["year_stem", "month_stem", "hour_stem"]:
        ss = shishen.get(stem_pos, {}).get("name", "")
        if ss == "正官": has_officer = True
        if ss == "七杀": has_killing = True
        if ss in ("正财", "偏财"): has_wealth = True
        if ss in ("正印", "偏印"): has_resource = True
        if ss == "伤官": has_hurting = True

    if has_officer and not has_killing and has_wealth and has_resource:
        method = "纯 (Pure)"
        desc = "Your chart matches the 'Pure' (纯) pattern from the Eight Methods: a single Officer star supported by Wealth and Resource. 《三命通会》ranks this as the most auspicious female chart: '贤妻良母，夫荣子贵' — a virtuous wife with a distinguished husband and successful children."
        severity = "positive"
    elif has_officer and has_killing:
        method = "浊 (Murky)"
        desc = "Your chart aligns with the 'Murky' (浊) pattern: mixed Officer and Killing stars without clear separation. 《三命通会》notes this can indicate emotional complexity and unclear relationship patterns."
        severity = "important"
    elif has_hurting:
        method = "伤官 (Rebel Talent)"
        desc = "Your chart shows Hurting Officer (伤官) prominence — this is its own significant pattern. 《三命通会》says: '伤官太重又见官...此等女人不堪娶' — but modern interpretation sees this as independent, creative energy that needs the right partner who appreciates rather than suppresses it."
        severity = "caution"
    else:
        return None

    return {
        "category": f"女命八法: {method}",
        "severity": severity,
        "classical_rule": "规则1.1.3 — 女命八法断命体系",
        "finding": desc,
        "source": "《三命通会·论女命》",
    }


def _generate_marriage_summary(findings: list, chart: dict) -> str:
    """生成婚姻分析摘要"""
    warnings = [f for f in findings if f.get("severity") == "warning"]
    cautions = [f for f in findings if f.get("severity") in ("caution", "important")]
    positives = [f for f in findings if f.get("severity") == "positive"]

    parts = []
    if warnings:
        parts.append(f"⚠️ {len(warnings)} significant classical warning(s) detected — these deserve attention but are not deterministic.")
    if cautions:
        parts.append(f"📋 {len(cautions)} area(s) of traditional concern — awareness creates choice.")
    if positives:
        parts.append(f"✅ {len(positives)} auspicious indicator(s) per classical standards.")
    if not parts:
        parts.append("Chart shows a balanced relationship configuration by classical standards.")

    return " ".join(parts)


# ============================================================
# 财富分析
# ============================================================

def analyze_wealth(chart: dict) -> dict:
    """
    基于古籍规则反向分析财运
    """
    rules_text = _load_rules()
    findings = []
    shishen = chart["shishen"]
    wuxing = chart["wuxing_count"]
    dm_element = chart["day_master"]["element"]
    pillars = chart["pillars"]

    # ========== 1. 财星类型判断 ==========
    has_zhengcai = False
    has_piancai = False
    for stem_pos in ["year_stem", "month_stem", "hour_stem"]:
        ss = shishen.get(stem_pos, {}).get("name", "")
        if ss == "正财": has_zhengcai = True
        if ss == "偏财": has_piancai = True

    if has_zhengcai and has_piancai:
        findings.append({
            "category": "正偏财俱全",
            "severity": "positive",
            "classical_rule": "规则2.1 — 正财规则 & 规则2.2 — 偏财规则",
            "finding": "Your chart contains both Direct Wealth (正财, salary/steady income) and Indirect Wealth (偏财, windfall/investment). 《三命通会》 sees this as versatile wealth capacity: '财旺生官，富而且贵'. You have capacity for both stable earnings and opportunistic gains.",
            "source": "《三命通会·论正财/论偏财》",
        })
    elif has_zhengcai:
        findings.append({
            "category": "正财格",
            "severity": "positive",
            "classical_rule": "规则2.1 — 正财规则",
            "finding": "Your chart follows the Direct Wealth (正财) pattern. 《三命通会》 describes this as: '正财者，受我克制，为我之妻...财要得时乘旺, 自家日主有力，皆能发福' — steady, earned prosperity through consistent effort. Like a salary that grows with your career, not a lottery ticket.",
            "source": "《三命通会·论正财》",
        })
    elif has_piancai:
        findings.append({
            "category": "偏财格",
            "severity": "neutral",
            "classical_rule": "规则2.2 — 偏财规则",
            "finding": "Your chart shows Indirect Wealth (偏财) dominance. 《三命通会》 says: '偏财者，乃众人之财也...偏财好出，亦不惧藏，唯怕分夺' — capacity for windfall and business income, but watch for competition and loss. The entrepreneur's pattern.",
            "source": "《三命通会·论偏财》",
        })
    else:
        findings.append({
            "category": "财星不显",
            "severity": "neutral",
            "finding": "Wealth stars (财星) don't appear prominently in your heavenly stems. Wealth may come through hidden channels (藏干) or activated in specific Major Luck cycles. 《三命通会》 reminds us: '财为养命之源，凡人八字不可无财，但不要太多' — wealth is essential but balance matters most.",
        })

    # ========== 2. 身强身弱 vs 财旺 ==========
    # 简化判断：看日主五行的count
    dm_count = wuxing["counts"].get(dm_element, 0)
    wealth_element_map = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
    wealth_element = wealth_element_map.get(dm_element, "")
    wealth_count = wuxing["counts"].get(wealth_element, 0)

    if wealth_count >= 3 and dm_count <= 2:
        findings.append({
            "category": "财多身弱",
            "severity": "warning",
            "classical_rule": "规则2.1.1 — 正财格基本判断",
            "finding": f"Your chart shows strong Wealth energy ({wealth_count} {wealth_element}) but a relatively weaker Day Master ({dm_count} {dm_element}). 《三命通会》 calls this '财多身弱' (wealth overwhelms the self): '虽妻财丰厚，但能目视，终不得用' — like seeing treasure through a window you cannot open. Opportunities appear but the strength to grasp them may be lacking.",
            "source": "《三命通会·论正财》",
            "advice": "The ancient remedy: strengthen the Day Master through Resource (印) energy — invest in knowledge, mentorship, and self-care. When you're strong enough, the wealth will follow.",
        })
    elif dm_count >= 4 and wealth_count <= 1:
        findings.append({
            "category": "身强财弱",
            "severity": "neutral",
            "finding": "Your Day Master is strong but Wealth energy is relatively weak. 《三命通会》 would say you have the capacity to handle wealth but need the right timing (大运/流年) for it to manifest. Focus on positioning yourself so that when the Wealth cycle arrives, you're ready.",
        })

    # ========== 3. 财星藏露分析 ==========
    # 检查财星在天干还是地支藏干中
    hidden = shishen.get("hidden_stems_shishen", {})
    has_hidden_wealth = False
    for pillar_name, stems in hidden.items():
        for s in stems:
            if "财" in s.get("shishen", ""):
                has_hidden_wealth = True

    if not has_zhengcai and not has_piancai and has_hidden_wealth:
        findings.append({
            "category": "财藏地支",
            "severity": "positive",
            "classical_rule": "规则2.1.2 — 正财藏露",
            "finding": "Your wealth stars are hidden in the earthly branches (藏干). 《三命通会》 considers this auspicious: '财宜藏，藏则丰厚，露则浮荡' — hidden wealth is deep and substantial. Your prosperity may not be flashy, but it runs deep.",
            "source": "《三命通会》",
        })
    elif has_zhengcai or has_piancai:
        findings.append({
            "category": "财透天干",
            "severity": "neutral",
            "classical_rule": "规则2.1.2",
            "finding": "Your wealth stars are visible in the heavenly stems. 《三命通会》 notes: '露则浮荡' — visible wealth can be more volatile. You may earn openly but also spend visibly. The key: ensure the wealth is protected by Officer (官) or Resource (印) stars.",
            "source": "《三命通会》",
        })

    # ========== 4. 比劫夺财检查 ==========
    has_bijie = False
    for stem_pos in ["year_stem", "month_stem", "hour_stem"]:
        ss = shishen.get(stem_pos, {}).get("name", "")
        if ss in ("比肩", "劫财"):
            has_bijie = True

    if has_bijie and (has_zhengcai or has_piancai):
        findings.append({
            "category": "比劫夺财",
            "severity": "caution",
            "classical_rule": "规则2.3.2 — 财星忌讳",
            "finding": "Peer stars (比劫) coexist with Wealth stars in your chart. 《三命通会》 warns: '比劫夺财' — competition for resources, difficulty accumulating (money seems to flow out as fast as it flows in).",
            "source": "《三命通会》",
            "advice": "Consider automated savings, trusted financial advisors, and being selective about business partnerships.",
        })

    return {
        "findings": findings,
        "summary": _generate_wealth_summary(findings),
    }


def _generate_wealth_summary(findings: list) -> str:
    parts = []
    warnings = [f for f in findings if f.get("severity") == "warning"]
    positives = [f for f in findings if f.get("severity") == "positive"]
    if warnings:
        parts.append(f"⚠️ {len(warnings)} classical caution(s) about wealth management.")
    if positives:
        parts.append(f"✅ {len(positives)} auspicious wealth indicator(s).")
    return " ".join(parts) if parts else "Balanced wealth configuration."


# ============================================================
# 完整分析
# ============================================================

def full_classical_analysis(chart: dict) -> dict:
    """
    对命盘进行完整的古籍规则逆向分析
    返回所有匹配的古典规则、来源引用和建议
    """
    reading_type = "general"

    marriage = analyze_marriage(chart)
    wealth = analyze_wealth(chart)

    all_findings = {
        "marriage": marriage,
        "wealth": wealth,
    }

    # 生成一个包含所有古籍引用的文本块，可以注入到 AI prompt 中
    classical_context = _build_classical_context(all_findings, chart)

    return {
        "marriage_analysis": marriage,
        "wealth_analysis": wealth,
        "classical_context": classical_context,
        "total_findings": len(marriage["findings"]) + len(wealth["findings"]),
    }


def _build_classical_context(analysis: dict, chart: dict) -> str:
    """构建古籍上下文，用于注入AI prompt"""
    parts = []
    parts.append("## 古籍规则匹配结果 (Classical Rule Matching)\n")

    # 基本信息
    dm = chart["day_master"]
    parts.append(f"**日主**: {dm['char']} ({dm['element_en']}, {dm['yinyang']})")
    parts.append(f"**性别**: {chart['birth_info']['gender']}")
    parts.append(f"**五行**: {json.dumps(chart['wuxing_count']['counts'], ensure_ascii=False)}\n")

    # 婚姻分析
    parts.append("### 💑 婚姻古籍分析\n")
    for f in analysis["marriage"]["findings"]:
        icon = {"positive": "✅", "neutral": "📋", "caution": "⚠️", "important": "🔍", "warning": "🚩"}.get(f.get("severity", ""), "📋")
        parts.append(f"{icon} **{f['category']}**")
        parts.append(f"   {f['finding']}")
        if f.get("source"):
            parts.append(f"   📜 出处: {f['source']}")
        if f.get("advice"):
            parts.append(f"   💡 建议: {f['advice']}")
        parts.append("")

    # 财富分析
    parts.append("### 💰 财富古籍分析\n")
    for f in analysis["wealth"]["findings"]:
        icon = {"positive": "✅", "neutral": "📋", "caution": "⚠️", "warning": "🚩"}.get(f.get("severity", ""), "📋")
        parts.append(f"{icon} **{f['category']}**")
        parts.append(f"   {f['finding']}")
        if f.get("source"):
            parts.append(f"   📜 出处: {f['source']}")
        if f.get("advice"):
            parts.append(f"   💡 建议: {f['advice']}")
        parts.append("")

    parts.append("\n---\n*以上分析基于《三命通会》规则库自动匹配。请AI基于这些古籍发现进行解读，引用具体规则和出处。*")

    return "\n".join(parts)


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from app.engine.bazi_calc import calculate_bazi
    from datetime import datetime

    # 测试女命
    chart = calculate_bazi(datetime(1990, 6, 15, 8, 0), 8, "female", 120, 30)
    result = full_classical_analysis(chart)

    print("=" * 60)
    print("古籍反向分析结果")
    print("=" * 60)
    print(f"匹配到的规则发现: {result['total_findings']} 条")
    print()
    for f in result["marriage_analysis"]["findings"]:
        print(f"  [{f['severity']}] {f['category']}")
    for f in result["wealth_analysis"]["findings"]:
        print(f"  [{f['severity']}] {f['category']}")
    print()
    print(result["classical_context"][:500])
