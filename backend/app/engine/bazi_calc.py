"""
KarmaCode - 八字排盘核心引擎
基于 lunar-python 库进行历法计算，自研十神/大运/神煞层
"""

from lunar_python import Solar, Lunar
from datetime import datetime
from typing import Optional
import json

# ============================================================
# 基础常量
# ============================================================

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
STEMS_EN = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
BRANCHES_EN = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]

FIVE_ELEMENTS_STEM = ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"]
FIVE_ELEMENTS_BRANCH = ["水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水"]
FIVE_ELEMENTS_EN = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]

YIN_YANG_STEM = ["阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴"]
YIN_YANG_BRANCH = ["阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴", "阳", "阴"]

# 五虎遁月干表 (年干 → 寅月天干)
WU_HU_DUN = {
    "甲": "丙", "己": "丙",
    "乙": "戊", "庚": "戊",
    "丙": "庚", "辛": "庚",
    "丁": "壬", "壬": "壬",
    "戊": "甲", "癸": "甲",
}

# 五鼠遁时干表 (日干 → 子时天干)
WU_SHU_DUN = {
    "甲": "甲", "己": "甲",
    "乙": "丙", "庚": "丙",
    "丙": "戊", "辛": "戊",
    "丁": "庚", "壬": "庚",
    "戊": "壬", "癸": "壬",
}

# 纳音表 (60甲子)
NAYIN = [
    "海中金", "炉中火", "大林木", "路旁土", "剑锋金", "山头火",
    "涧下水", "城头土", "白蜡金", "杨柳木", "泉中水", "屋上土",
    "霹雳火", "松柏木", "流年水", "砂石金", "山下火", "平地木",
    "壁上土", "金箔金", "覆灯火", "天河水", "大驿土", "钗钏金",
    "桑柘木", "大溪水", "沙中土", "天上火", "石榴木", "大海水",
]

# ============================================================
# 八字排盘
# ============================================================

def calculate_bazi(birth_date: datetime, birth_hour: int, gender: str = "male",
                   longitude: float = 120.0, latitude: float = 30.0) -> dict:
    """
    计算完整八字命盘

    Args:
        birth_date: 公历出生日期时间
        birth_hour: 出生小时 (0-23)
        gender: 'male' | 'female'
        longitude: 出生地经度 (用于真太阳时校正)
        latitude: 出生地纬度

    Returns:
        完整命盘数据
    """
    # 真太阳时校正
    true_solar_hour = _correct_true_solar_time(birth_date, birth_hour, longitude)

    # 使用 lunar-python 获取农历信息
    solar = Solar.fromYmdHms(
        birth_date.year, birth_date.month, birth_date.day,
        true_solar_hour, birth_date.minute, birth_date.second
    )
    lunar = solar.getLunar()

    # 年柱
    year_stem_idx = lunar.getYearGanIndex()
    year_branch_idx = lunar.getYearZhiIndex()
    year_stem = HEAVENLY_STEMS[year_stem_idx]
    year_branch = EARTHLY_BRANCHES[year_branch_idx]

    # 月柱 (以节气为分界)
    month_stem_idx = lunar.getMonthGanIndex()
    month_branch_idx = lunar.getMonthZhiIndex()
    month_stem = HEAVENLY_STEMS[month_stem_idx]
    month_branch = EARTHLY_BRANCHES[month_branch_idx]

    # 日柱
    day_stem_idx = lunar.getDayGanIndex()
    day_branch_idx = lunar.getDayZhiIndex()
    day_stem = HEAVENLY_STEMS[day_stem_idx]
    day_branch = EARTHLY_BRANCHES[day_branch_idx]

    # 时柱
    hour_stem_idx = lunar.getTimeGanIndex()
    hour_branch_idx = lunar.getTimeZhiIndex()
    hour_stem = HEAVENLY_STEMS[hour_stem_idx]
    hour_branch = EARTHLY_BRANCHES[hour_branch_idx]

    # 空亡
    kongwang = _calculate_kongwang(day_branch_idx)

    # 纳音
    nayin = _calculate_nayin(year_stem_idx, year_branch_idx,
                              month_stem_idx, month_branch_idx,
                              day_stem_idx, day_branch_idx,
                              hour_stem_idx, hour_branch_idx)

    # 十神
    shishen = _calculate_shishen(day_stem_idx, year_stem_idx, month_stem_idx,
                                  hour_stem_idx, year_branch_idx, month_branch_idx,
                                  day_branch_idx, hour_branch_idx)

    # 藏干
    hidden_stems = _calculate_hidden_stems(year_branch_idx, month_branch_idx,
                                            day_branch_idx, hour_branch_idx)

    # 大运
    dayun = _calculate_dayun(birth_date, lunar, gender, year_stem_idx,
                              month_stem_idx, month_branch_idx)

    # 神煞
    shensha = _calculate_shensha(day_stem_idx, year_branch_idx, month_branch_idx,
                                  day_branch_idx, hour_branch_idx, year_stem)

    # 五行统计
    wuxing_count = _count_wuxing(year_stem_idx, month_stem_idx, day_stem_idx, hour_stem_idx,
                                  year_branch_idx, month_branch_idx, day_branch_idx, hour_branch_idx)

    # 日主信息
    day_master_element = FIVE_ELEMENTS_STEM[day_stem_idx]
    day_master_yinyang = YIN_YANG_STEM[day_stem_idx]

    # 构建命盘
    chart = {
        "birth_info": {
            "solar_date": birth_date.strftime("%Y-%m-%d"),
            "solar_time": f"{birth_hour:02d}:{birth_date.minute:02d}",
            "true_solar_hour": true_solar_hour,
            "longitude": longitude,
            "lunar_date": f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}日",
            "lunar_year": lunar.getYear(),
            "lunar_month": lunar.getMonth(),
            "lunar_day": lunar.getDay(),
            "gender": gender,
            "animal": ANIMALS[year_branch_idx],
        },
        "pillars": {
            "year": {
                "stem": {"char": year_stem, "en": STEMS_EN[year_stem_idx], "element": FIVE_ELEMENTS_STEM[year_stem_idx],
                         "element_en": FIVE_ELEMENTS_EN[year_stem_idx], "yinyang": YIN_YANG_STEM[year_stem_idx]},
                "branch": {"char": year_branch, "en": BRANCHES_EN[year_branch_idx],
                           "element": FIVE_ELEMENTS_BRANCH[year_branch_idx], "animal": ANIMALS[year_branch_idx]},
                "nayin": nayin["year"],
                "hidden_stems": hidden_stems["year"],
            },
            "month": {
                "stem": {"char": month_stem, "en": STEMS_EN[month_stem_idx], "element": FIVE_ELEMENTS_STEM[month_stem_idx],
                         "element_en": FIVE_ELEMENTS_EN[month_stem_idx], "yinyang": YIN_YANG_STEM[month_stem_idx]},
                "branch": {"char": month_branch, "en": BRANCHES_EN[month_branch_idx],
                           "element": FIVE_ELEMENTS_BRANCH[month_branch_idx], "animal": ANIMALS[month_branch_idx]},
                "nayin": nayin["month"],
                "hidden_stems": hidden_stems["month"],
            },
            "day": {
                "stem": {"char": day_stem, "en": STEMS_EN[day_stem_idx], "element": FIVE_ELEMENTS_STEM[day_stem_idx],
                         "element_en": FIVE_ELEMENTS_EN[day_stem_idx], "yinyang": YIN_YANG_STEM[day_stem_idx]},
                "branch": {"char": day_branch, "en": BRANCHES_EN[day_branch_idx],
                           "element": FIVE_ELEMENTS_BRANCH[day_branch_idx], "animal": ANIMALS[day_branch_idx]},
                "nayin": nayin["day"],
                "hidden_stems": hidden_stems["day"],
            },
            "hour": {
                "stem": {"char": hour_stem, "en": STEMS_EN[hour_stem_idx], "element": FIVE_ELEMENTS_STEM[hour_stem_idx],
                         "element_en": FIVE_ELEMENTS_EN[hour_stem_idx], "yinyang": YIN_YANG_STEM[hour_stem_idx]},
                "branch": {"char": hour_branch, "en": BRANCHES_EN[hour_branch_idx],
                           "element": FIVE_ELEMENTS_BRANCH[hour_branch_idx], "animal": ANIMALS[hour_branch_idx]},
                "nayin": nayin["hour"],
                "hidden_stems": hidden_stems["hour"],
            },
        },
        "day_master": {
            "char": day_stem,
            "en": STEMS_EN[day_stem_idx],
            "element": day_master_element,
            "element_en": FIVE_ELEMENTS_EN[day_stem_idx],
            "yinyang": day_master_yinyang,
        },
        "shishen": shishen,
        "dayun": dayun,
        "shensha": shensha,
        "wuxing_count": wuxing_count,
        "kongwang": kongwang,
    }

    return chart


def _correct_true_solar_time(birth_date: datetime, birth_hour: int,
                               longitude: float) -> int:
    """真太阳时校正"""
    # 北京时间 (120°E) 与出生地经度的时差
    minute_offset = (longitude - 120) * 4
    total_minutes = birth_hour * 60 + birth_date.minute + minute_offset
    corrected_hour = total_minutes / 60
    corrected_hour = corrected_hour % 24
    return int(round(corrected_hour))


def _calculate_kongwang(day_branch_idx: int) -> dict:
    """计算空亡"""
    # 旬空表：每旬两位地支为空亡
    xun_kong = {
        0: [9, 10], 1: [9, 10],   # 甲子旬 → 戌亥
        2: [11, 0], 3: [11, 0],   # 甲寅旬 → 子丑
        4: [1, 2], 5: [1, 2],     # 甲辰旬 → 寅卯
        6: [3, 4], 7: [3, 4],     # 甲午旬 → 辰巳
        8: [5, 6], 9: [5, 6],     # 甲申旬 → 午未
        10: [7, 8], 11: [7, 8],   # 甲戌旬 → 申酉
    }
    group = day_branch_idx % 12
    kw_indices = xun_kong.get(group, [])
    return {
        "branches": [EARTHLY_BRANCHES[i] for i in kw_indices],
        "branches_en": [BRANCHES_EN[i] for i in kw_indices],
    }


def _calculate_nayin(year_si, year_bi, month_si, month_bi,
                      day_si, day_bi, hour_si, hour_bi) -> dict:
    """计算纳音五行"""
    def get_nayin(stem_idx, branch_idx):
        nayin_idx = (stem_idx + branch_idx) // 2 % 30
        return NAYIN[nayin_idx]

    return {
        "year": get_nayin(year_si, year_bi),
        "month": get_nayin(month_si, month_bi),
        "day": get_nayin(day_si, day_bi),
        "hour": get_nayin(hour_si, hour_bi),
    }


def _calculate_hidden_stems(yb_idx, mb_idx, db_idx, hb_idx) -> dict:
    """计算地支藏干"""
    # 地支藏干表
    HIDDEN = [
        ["癸"],                    # 子
        ["己", "癸", "辛"],        # 丑
        ["甲", "丙", "戊"],        # 寅
        ["乙"],                    # 卯
        ["戊", "乙", "癸"],        # 辰
        ["丙", "戊", "庚"],        # 巳
        ["丁", "己"],              # 午
        ["己", "丁", "乙"],        # 未
        ["庚", "壬", "戊"],        # 申
        ["辛"],                    # 酉
        ["戊", "辛", "丁"],        # 戌
        ["壬", "甲"],              # 亥
    ]
    return {
        "year": HIDDEN[yb_idx],
        "month": HIDDEN[mb_idx],
        "day": HIDDEN[db_idx],
        "hour": HIDDEN[hb_idx],
    }


def _calculate_shishen(day_stem_idx, ys, ms, hs, yb, mb, db, hb) -> dict:
    """计算十神"""
    def get_shishen(day_idx, other_idx):
        diff = (other_idx - day_idx) % 10
        yinyang_same = (day_idx % 2) == (other_idx % 2)

        SHISHEN_MAP = {
            (0, True): "比肩", (0, False): "劫财",
            (1, False): "食神", (1, True): "伤官",
            (2, True): "偏财", (2, False): "正财",
            (3, False): "正官", (3, True): "七杀",
            (4, True): "偏印", (4, False): "正印",
            (5, False): "劫财", (5, True): "比肩",
            (6, True): "伤官", (6, False): "食神",
            (7, False): "正财", (7, True): "偏财",
            (8, True): "七杀", (8, False): "正官",
            (9, False): "正印", (9, True): "偏印",
        }
        return SHISHEN_MAP.get((diff, yinyang_same), "未知")

    SHISHEN_EN = {
        "比肩": "Parallel (BiJian)",
        "劫财": "Rob Wealth (JieCai)",
        "食神": "Eating God (ShiShen)",
        "伤官": "Hurting Officer (ShangGuan)",
        "偏财": "Indirect Wealth (PianCai)",
        "正财": "Direct Wealth (ZhengCai)",
        "正官": "Direct Officer (ZhengGuan)",
        "七杀": "Seven Killings (QiSha)",
        "偏印": "Indirect Resource (PianYin)",
        "正印": "Direct Resource (ZhengYin)",
    }

    result = {}
    for name, idx in [("year_stem", ys), ("month_stem", ms), ("hour_stem", hs),
                       ("year_branch", yb), ("month_branch", mb),
                       ("day_branch", db), ("hour_branch", hb)]:
        ss = get_shishen(day_stem_idx, idx)
        result[name] = {"name": ss, "en": SHISHEN_EN.get(ss, "Unknown")}

    # 对地支藏干也算十神
    hidden_stems = _calculate_hidden_stems(yb, mb, db, hb)
    result["hidden_stems_shishen"] = {}
    for pillar, stems in hidden_stems.items():
        result["hidden_stems_shishen"][pillar] = []
        for s in stems:
            s_idx = HEAVENLY_STEMS.index(s)
            ss = get_shishen(day_stem_idx, s_idx)
            result["hidden_stems_shishen"][pillar].append({
                "stem": s, "shishen": ss, "shishen_en": SHISHEN_EN.get(ss, "Unknown")
            })

    return result


def _calculate_dayun(birth_date, lunar, gender, year_stem_idx,
                      month_stem_idx, month_branch_idx) -> dict:
    """计算大运"""
    year_stem = HEAVENLY_STEMS[year_stem_idx]
    yinyang_nian = YIN_YANG_STEM[year_stem_idx]  # 阳年 or 阴年

    # 顺排/逆排
    if (yinyang_nian == "阳" and gender == "male") or (yinyang_nian == "阴" and gender == "female"):
        direction = "forward"  # 顺排
    else:
        direction = "reverse"  # 逆排

    # 计算起运岁数
    # 使用 lunar-python 获取起运信息
    try:
        yun = lunar.getTime().getDaYun()
        start_age = yun.getStartAge() if direction == "forward" else yun.getStartAge()
        # lunar-python 直接提供大运列表
        dayun_list = []
        yun_names = yun.getDaYun() if hasattr(yun, 'getDaYun') else []

        # 手动计算大运
        dayun_list = _compute_dayun_manual(month_stem_idx, month_branch_idx,
                                            direction, start_age)
    except Exception:
        # 降级：手动计算
        start_age = _compute_start_age(lunar, birth_date, direction)
        dayun_list = _compute_dayun_manual(month_stem_idx, month_branch_idx,
                                            direction, start_age)

    return {
        "start_age": start_age,
        "direction": direction,
        "direction_en": "Forward (顺排)" if direction == "forward" else "Reverse (逆排)",
        "cycles": dayun_list,
    }


def _compute_start_age(lunar, birth_date, direction) -> int:
    """计算起运岁数"""
    try:
        # 找到最近的上一个或下一个节气
        jieqi = lunar.getJieQi()
        # 简化：从 lunar-python 获取节令信息
        prev_jq = lunar.getPrevJieQi()
        next_jq = lunar.getNextJieQi()

        if direction == "forward":
            # 顺排：找下一个节气
            target_date = next_jq.getSolar()
        else:
            # 逆排：找上一个节气
            target_date = prev_jq.getSolar()

        # 计算天数差
        from datetime import datetime
        birth_dt = datetime(birth_date.year, birth_date.month, birth_date.day)
        target_dt = datetime(target_date.getYear(), target_date.getMonth(), target_date.getDay())
        diff_days = abs((target_dt - birth_dt).days)

        # 三天为一岁
        age = max(1, round(diff_days / 3))
        return age
    except Exception:
        return 5  # 默认值


def _compute_dayun_manual(month_stem_idx, month_branch_idx,
                            direction, start_age) -> list:
    """手动计算大运列表"""
    cycles = []
    current_stem = month_stem_idx
    current_branch = month_branch_idx

    for i in range(8):  # 8步大运，80年
        if direction == "forward":
            current_stem = (current_stem + 1) % 10
            current_branch = (current_branch + 1) % 12
        else:
            current_stem = (current_stem - 1) % 10
            current_branch = (current_branch - 1) % 12

        age_start = start_age + i * 10
        cycles.append({
            "order": i + 1,
            "age": f"{age_start} - {age_start + 9}",
            "age_start": age_start,
            "age_end": age_start + 9,
            "stem": HEAVENLY_STEMS[current_stem],
            "stem_en": STEMS_EN[current_stem],
            "branch": EARTHLY_BRANCHES[current_branch],
            "branch_en": BRANCHES_EN[current_branch],
            "element": FIVE_ELEMENTS_STEM[current_stem],
            "element_en": FIVE_ELEMENTS_EN[current_stem],
            "nayin": NAYIN[(current_stem + current_branch) // 2 % 30],
        })

    return cycles


def _calculate_shensha(day_stem_idx, yb, mb, db, hb, year_stem) -> dict:
    """计算常用神煞"""
    result = {}

    # 天乙贵人
    tianyi_map = {
        "甲": [6, 8], "戊": [6, 8], "庚": [6, 8],  # 丑未
        "乙": [0, 10], "己": [0, 10],              # 子申
        "丙": [10, 2], "丁": [10, 2],               # 亥酉
        "辛": [3, 5], "壬": [3, 5], "癸": [3, 5],  # 卯巳
    }
    tianyi_positions = tianyi_map.get(day_stem_idx if isinstance(day_stem_idx, str)
                                       else HEAVENLY_STEMS[day_stem_idx], [])

    # 桃花 (咸池)
    taohua_map = {
        0: 3, 1: 3, 3: 3,   # 申子辰 → 酉
        4: 6, 5: 6, 7: 6,   # 巳酉丑 → 午
        8: 9, 9: 9, 11: 9,  # 亥卯未 → 子
        2: 0, 6: 0, 10: 0,  # 寅午戌 → 卯 (修正：亥卯未见子，申子辰见酉，寅午戌见卯，巳酉丑见午)
    }

    # 贵人
    all_branches = [yb, mb, db, hb]
    branch_names = ["year", "month", "day", "hour"]
    result["天乙贵人_TianYi_Nobleman"] = {
        "present_in": [branch_names[i] for i, b in enumerate(all_branches) if b in tianyi_positions],
        "description": "The most auspicious star — brings benefactors and rescues from danger",
    }

    # 桃花
    day_branch = db
    peach_idx = None
    for key_idx in [0, 1, 2]:  # Check by groups
        group = [0, 4, 8]  # 申子辰, 巳酉丑, 亥卯未, 寅午戌
        # 简化查找
        pass

    # 简化桃花计算
    peach_map = {
        0: 3, 4: 6, 8: 9,  # 申子辰→酉, 巳酉丑→午, 亥卯未→子
        2: 0, 6: 0, 10: 0,  # 寅午戌→卯
    }
    # 以日支查桃花
    peach_blossom = peach_map.get(db)

    result["桃花_Peach_Blossom"] = {
        "branch": EARTHLY_BRANCHES[peach_blossom] if peach_blossom is not None else None,
        "branch_en": BRANCHES_EN[peach_blossom] if peach_blossom is not None else None,
        "present_in": [branch_names[i] for i, b in enumerate(all_branches) if b == peach_blossom],
        "description": "Romance and charm star — indicates attractiveness and romantic opportunities",
    }

    # 驿马
    yima_map = {0: 2, 4: 10, 8: 6, 2: 10, 6: 6, 10: 2}  # 简化
    yima = yima_map.get(db)
    result["驿马_YiMa_Travel"] = {
        "branch": EARTHLY_BRANCHES[yima] if yima is not None else None,
        "present_in": [branch_names[i] for i, b in enumerate(all_branches) if b == yima],
        "description": "Travel and movement star — indicates mobility, relocation, or busy lifestyle",
    }

    # 羊刃
    yangren_map_stem = {
        0: 3, 1: 2, 2: 6, 3: 5, 4: 6,  # 甲卯,乙寅,丙午,丁巳,戊午
        5: 5, 6: 9, 7: 8, 8: 0, 9: 11,  # 己巳,庚酉,辛申,壬子,癸亥
    }
    yangren = yangren_map_stem.get(day_stem_idx)
    result["羊刃_YangBlade"] = {
        "branch": EARTHLY_BRANCHES[yangren] if yangren is not None else None,
        "present_in": [branch_names[i] for i, b in enumerate(all_branches) if b == yangren],
        "description": "Extreme strength point — extraordinary willpower but risk of injuries",
    }

    # 红鸾
    hongluan_map = {0: 3, 1: 2, 2: 6, 3: 5, 4: 6, 5: 5, 6: 9, 7: 8, 8: 0, 9: 11}
    hongluan = hongluan_map.get(db)
    result["红鸾_RedLuan_Marriage"] = {
        "branch": EARTHLY_BRANCHES[hongluan] if hongluan is not None else None,
        "present_in": [branch_names[i] for i, b in enumerate(all_branches) if b == hongluan],
        "description": "Marriage star — indicates timing of romantic commitment and weddings",
    }

    # 孤辰寡宿
    guchen_map = {10: 2, 4: 6, 6: 2, 0: 6, 8: 10}  # 简化
    guasu_map = {10: 0, 4: 8, 6: 0, 0: 8, 8: 4}
    guchen = guchen_map.get(db)
    guasu = guasu_map.get(db)

    result["孤辰寡宿_Solitude"] = {
        "guchen_branch": EARTHLY_BRANCHES[guchen] if guchen is not None else None,
        "guasu_branch": EARTHLY_BRANCHES[guasu] if guasu is not None else None,
        "description": "Tendency toward emotional solitude or late marriage",
    }

    return result


def _count_wuxing(ys, ms, ds, hs, yb, mb, db, hb) -> dict:
    """统计五行分布"""
    stem_elements = [FIVE_ELEMENTS_STEM[ys], FIVE_ELEMENTS_STEM[ms],
                     FIVE_ELEMENTS_STEM[ds], FIVE_ELEMENTS_STEM[hs]]
    branch_elements = [FIVE_ELEMENTS_BRANCH[yb], FIVE_ELEMENTS_BRANCH[mb],
                       FIVE_ELEMENTS_BRANCH[db], FIVE_ELEMENTS_BRANCH[hb]]

    all_elements = stem_elements + branch_elements
    count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for e in all_elements:
        count[e] += 1

    wuxing_en = {"木": "Wood", "火": "Fire", "土": "Earth", "金": "Metal", "水": "Water"}
    return {
        "counts": count,
        "counts_en": {wuxing_en[k]: v for k, v in count.items()},
        "dominant": max(count, key=count.get),
        "dominant_en": wuxing_en[max(count, key=count.get)],
        "weakest": min(count, key=count.get),
        "weakest_en": wuxing_en[min(count, key=count.get)],
        "balanced": max(count.values()) - min(count.values()) <= 2,
    }


def get_current_dayun(chart: dict, current_age: int) -> dict:
    """根据当前年龄获取所处大运"""
    for cycle in chart["dayun"]["cycles"]:
        if cycle["age_start"] <= current_age <= cycle["age_end"]:
            return cycle
    return None


def calculate_daily_fortune(chart: dict, target_date: datetime) -> dict:
    """计算指定日期的流日运势"""
    solar = Solar.fromYmd(target_date.year, target_date.month, target_date.day)
    lunar = solar.getLunar()

    day_stem_idx = lunar.getDayGanIndex()
    day_branch_idx = lunar.getDayZhiIndex()
    flow_day_stem = HEAVENLY_STEMS[day_stem_idx]
    flow_day_branch = EARTHLY_BRANCHES[day_branch_idx]

    # 日主
    day_master_char = chart["day_master"]["char"]
    dm_idx = HEAVENLY_STEMS.index(day_master_char)

    # 流日十神
    diff = (day_stem_idx - dm_idx) % 10
    yinyang_same = (dm_idx % 2) == (day_stem_idx % 2)
    SHISHEN_MAP = {
        (0, True): "比肩", (0, False): "劫财",
        (1, False): "食神", (1, True): "伤官",
        (2, True): "偏财", (2, False): "正财",
        (3, False): "正官", (3, True): "七杀",
        (4, True): "偏印", (4, False): "正印",
        (5, False): "劫财", (5, True): "比肩",
        (6, True): "伤官", (6, False): "食神",
        (7, False): "正财", (7, True): "偏财",
        (8, True): "七杀", (8, False): "正官",
        (9, False): "正印", (9, True): "偏印",
    }
    daily_shishen = SHISHEN_MAP.get((diff, yinyang_same), "未知")

    # 日柱与流日的关系
    my_day_branch_idx = HEAVENLY_STEMS.index(chart["pillars"]["day"]["stem"]["char"])
    # 天克地冲检测
    is_tiankedichong = False
    if (dm_idx + 6) % 10 == day_stem_idx:  # 天干相克
        day_chart_branch = chart["pillars"]["day"]["branch"]["char"]
        day_chart_branch_idx = EARTHLY_BRANCHES.index(day_chart_branch)
        if (day_chart_branch_idx + 6) % 12 == day_branch_idx:  # 地支相冲
            is_tiankedichong = True

    # 伏吟检测
    is_fuyin = (flow_day_stem == chart["pillars"]["day"]["stem"]["char"] and
                flow_day_branch == chart["pillars"]["day"]["branch"]["char"])

    # 每日宜忌建议
    SUGGESTIONS = {
        "正财": {"auspicious": ["Handle finances", "Sign contracts", "Shopping"], "caution": ["Major study sessions"]},
        "偏财": {"auspicious": ["Business deals", "Investment review", "Networking"], "caution": ["Gambling", "Lending money"]},
        "正官": {"auspicious": ["Career tasks", "Report to superiors", "Official matters"], "caution": ["High-risk investments"]},
        "七杀": {"auspicious": ["Competitive activities", "Take on challenges"], "caution": ["Arguments", "Risky ventures"]},
        "正印": {"auspicious": ["Study", "Planning", "Seek advice", "Health checkup"], "caution": ["Overthinking", "Laziness"]},
        "偏印": {"auspicious": ["Research", "Specialized study", "Solitude"], "caution": ["Overthinking", "Social withdrawal"]},
        "食神": {"auspicious": ["Creative work", "Dining out", "Learning new skills"], "caution": ["Overindulgence"]},
        "伤官": {"auspicious": ["Innovation", "Self-expression", "Artistic pursuits"], "caution": ["Challenging authority", "Harsh words"]},
        "比肩": {"auspicious": ["Social gatherings", "Exchange ideas"], "caution": ["Investing", "Signing contracts", "Lending money"]},
        "劫财": {"auspicious": ["Socializing", "Teamwork"], "caution": ["All financial decisions", "Major purchases"]},
    }

    suggestion = SUGGESTIONS.get(daily_shishen, {"auspicious": ["Go with the flow"], "caution": ["Major decisions"]})

    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "flow_day": {"stem": flow_day_stem, "branch": flow_day_branch},
        "daily_shishen": daily_shishen,
        "is_tiankedichong": is_tiankedichong,
        "is_fuyin": is_fuyin,
        "suggestions": suggestion,
        "energy_level": "high" if is_tiankedichong else ("low" if is_fuyin else "normal"),
    }


# ============================================================
# 简单测试
# ============================================================

if __name__ == "__main__":
    # 测试：1985年3月15日 早上8点 男
    test_date = datetime(1985, 3, 15, 8, 0, 0)
    chart = calculate_bazi(test_date, 8, "male", 120, 30)
    print(json.dumps(chart, ensure_ascii=False, indent=2))
