"""
训练助手工具
- parse_ai_plan_smart: 智能解析多日训练计划，按天分组
- parse_ai_plan: 兼容老接口，返回单一动作列表
- check_injury_risk / get_nutrition_advice / progressive_overload_tip
"""
import re


# ============ 常见 AI 翻译错字纠正表 ============
TYPO_FIXES = {
    # 器械名称
    "哑铲": "哑铃",
    "亚铃": "哑铃",
    "亚玲": "哑铃",
    "哑玲": "哑铃",
    "扛铃": "杠铃",
    "杠玲": "杠铃",
    "杠零": "杠铃",
    "壶玲": "壶铃",
    "壶零": "壶铃",
    "史密斯机": "史密斯架",
    "史密斯机器": "史密斯架",
    # 动作名错字
    "深躯": "深蹲",
    "深蹭": "深蹲",
    "硬来": "硬拉",
    "硬力": "硬拉",
    "罗玛尼亚": "罗马尼亚",
    "保加里亚": "保加利亚",
    "卧堆": "卧推",
    "推剧": "推举",
    "推具": "推举",
    "弯距": "弯举",
    "划装": "划船",
    "下垃": "下拉",
    "提中": "提踵",
    # 部位名错字
    "肱二投": "肱二头",
    "肱三投": "肱三头",
    "胸不": "胸部",
    "背不": "背部",
    "腿不": "腿部",
    "肩不": "肩部",
}


def fix_typos(text: str) -> str:
    """修正AI生成内容中的常见错字"""
    if not text:
        return text
    for wrong, right in TYPO_FIXES.items():
        text = text.replace(wrong, right)
    return text


# ============ 关键词配置 ============
ACTION_KEYWORDS = [
    # 下肢
    "深蹲","硬拉","蹲","腿举","蹬腿","弓步","保加利亚","哈克","前蹲","后蹲",
    "高脚杯","罗马尼亚","RDL","腿屈伸","腿弯举","提踵","髋外展","髋内收","臀冲","臀推","臀桥",
    # 上肢推
    "卧推","推举","推胸","肩推","推","夹胸","飞鸟","三头","下压","臂屈伸","颈后","过头",
    # 上肢拉
    "划船","下拉","引体","弯举","二头","面拉","耸肩","屈臂","拉力","拉绳","拉",
    # 肩
    "侧平举","前平举","后束","三角","反向飞鸟","侧向提举","提举","侧抬","前抬","侧举","前举","前提","抬举",
    # 核心
    "卷腹","仰卧起坐","平板支撑","俄罗斯转体","悬挂举腿","举腿","山羊挺身","罗马椅","支撑",
    # 器械修饰词
    "杠铃","哑铃","壶铃","史密斯","绳索","拉索","龙门架","坐姿","站姿","俯身","上斜","下斜","平板","T杠",
    # 自重
    "俯卧撑","深蹲跳","波比","登山者",
    # 通用动作词
    "蹲举","划","伸展","伸","飞",
]

SKIP_KEYWORDS = [
    "热身","拉伸","放松","休息","组间","建议","注意","提示",
    "胸部和","背部和","腿部和","肩部和","手臂和",
    "训练日","可选","替换",
    "完成后","完成指定","完成时","保持","专注于","确保",
    "从一个","根据你","组间休息","使用","冷却",
]

# 周几映射（中文 -> 0-6）
WEEKDAY_MAP = {
    "周一":0,"星期一":0,"礼拜一":0,"周1":0,"第一天":0,"第1天":0,"day1":0,"day 1":0,
    "周二":1,"星期二":1,"礼拜二":1,"周2":1,"第二天":1,"第2天":1,"day2":1,"day 2":1,
    "周三":2,"星期三":2,"礼拜三":2,"周3":2,"第三天":2,"第3天":2,"day3":2,"day 3":2,
    "周四":3,"星期四":3,"礼拜四":3,"周4":3,"第四天":3,"第4天":3,"day4":3,"day 4":3,
    "周五":4,"星期五":4,"礼拜五":4,"周5":4,"第五天":4,"第5天":4,"day5":4,"day 5":4,
    "周六":5,"星期六":5,"礼拜六":5,"周6":5,"第六天":5,"第6天":5,"day6":5,"day 6":5,
    "周日":6,"周天":6,"星期日":6,"星期天":6,"礼拜日":6,"礼拜天":6,"周7":6,"第七天":6,"第7天":6,"day7":6,"day 7":6,
}

# 部位关键词（按优先级）
MUSCLE_PATTERNS = [
    ("胸+三头", ["胸", "三头"]),
    ("背+二头", ["背", "二头"]),
    ("胸+肩", ["胸", "肩"]),
    ("背+肩", ["背", "肩"]),
    ("肩+臂", ["肩", "臂"]),
    ("肩+腹", ["肩", "腹"]),
    ("肩+核心", ["肩", "核心"]),
    ("腿+肩", ["腿", "肩"]),
    ("腿+臀", ["腿", "臀"]),
    ("胸", ["胸部", "胸肌", "胸"]),
    ("背", ["背部", "背"]),
    ("腿", ["腿部", "腿"]),
    ("肩", ["肩部", "肩"]),
    ("臂", ["手臂", "臂"]),
    ("臀", ["臀"]),
    ("核心", ["腹", "核心"]),
    ("全身", ["全身"]),
]


def _detect_weekday(line: str):
    """识别这一行是否是某天的标题，返回 (weekday_index, is_rest, muscle_group) 或 None"""
    line_lower = line.lower().strip()
    # 去除标点干扰
    line_clean = re.sub(r'[【】\[\]（）\(\)：:。.,，、]', ' ', line_lower)

    # 必须是较短的标题行（动作行通常包含组数次数）
    if re.search(r'\d+\s*组', line) and re.search(r'\d+\s*[次秒下个]', line):
        return None  # 是动作行，不是标题

    # 匹配周几
    matched_widx = None
    for keyword, widx in WEEKDAY_MAP.items():
        if keyword in line_clean:
            matched_widx = widx
            break

    if matched_widx is None:
        return None

    # 是否是休息日
    is_rest = any(kw in line for kw in ["休息", "Rest", "rest", "REST"])

    # 提取部位
    muscle = "未指定"
    if not is_rest:
        for label, parts in MUSCLE_PATTERNS:
            if all(p in line for p in parts):
                muscle = label
                break

    return (matched_widx, is_rest, muscle)


def _parse_exercise_line(line: str):
    """解析单行动作，返回 dict 或 None"""
    if not line or len(line) < 4:
        return None
    if line.startswith(("-", "·", "•", "—", "*", "◦", "○")):
        return None
    if any(kw in line for kw in SKIP_KEYWORDS):
        return None

    # 必须含动作关键词
    if not any(kw in line for kw in ACTION_KEYWORDS):
        return None

    # 必须含组数+次数
    m_sets = re.search(r'(\d+)\s*组', line)
    m_reps = re.search(r'(\d+(?:[\-～~至到]\d+)?)\s*(?:次|下|个|rep|秒|分钟|分)', line, re.IGNORECASE)
    m_xy = re.search(r'(\d+)\s*[xX×\*]\s*(\d+(?:[\-～~]\d+)?)', line)

    sets, reps, reps_unit = None, None, "次"

    if m_sets and m_reps:
        sets = int(m_sets.group(1))
        reps = m_reps.group(1).replace("～","-").replace("~","-").replace("至","-").replace("到","-")
        unit_match = re.search(r'(?:次|下|个|秒|分钟|分)', m_reps.group(0))
        if unit_match:
            u = unit_match.group(0)
            if u in ("秒","分钟","分"):
                reps_unit = u
    elif m_sets and m_xy:
        sets = int(m_sets.group(1))
        reps = m_xy.group(2).replace("～","-").replace("~","-")
        after_xy = line[m_xy.end():m_xy.end()+8]
        if re.search(r'秒|分钟|分', after_xy):
            reps_unit = "秒" if "秒" in after_xy else "分钟"
    elif m_xy and not m_sets:
        sets = int(m_xy.group(1))
        reps = m_xy.group(2).replace("～","-").replace("~","-")
    else:
        return None

    if sets < 1 or sets > 10:
        return None

    reps_display = f"{reps}{reps_unit}" if reps_unit != "次" else reps

    # 清理动作名
    name = line
    name = re.sub(r'^\s*[\d①②③④⑤⑥⑦⑧⑨⑩\.、\)\-—\s]+', '', name)
    name = re.split(r'[：:]', name)[0]
    name = re.sub(r'\d+\s*组.*$', '', name)
    name = re.sub(r'\d+\s*[xX×]\s*\d+.*$', '', name)
    name = re.sub(r'[\(（].*?[\)）]', '', name)
    name = re.sub(r'[，,。.\s]+$', '', name).strip()

    # 自动纠错
    name = fix_typos(name)

    if len(name) < 2 or len(name) > 25:
        return None

    return {
        "name": name,
        "sets": sets,
        "reps": reps_display,
        "weight": "",
        "notes": "",
    }


def parse_ai_plan_smart(ai_text: str) -> dict:
    """
    智能解析：识别按天分组的训练计划
    返回:
    {
      "plan_type": "weekly" 或 "single",
      "days_data": {
        0: {"muscle_group": "胸+三头", "is_rest": False, "exercises": [...]},
        1: {"muscle_group": "背+二头", "is_rest": False, "exercises": [...]},
        ...
      } 或 {"single": {...}}
    }
    """
    lines = ai_text.split("\n")

    # 第一遍扫描：识别天数标题及对应的部位/休息状态
    day_markers = []  # [(line_index, weekday_index, is_rest, muscle_group)]
    for i, line in enumerate(lines):
        info = _detect_weekday(line.strip())
        if info is not None:
            widx, is_rest, muscle = info
            day_markers.append((i, widx, is_rest, muscle))

    # 第二遍扫描：把动作分配给最近的一个day marker
    if not day_markers:
        # 没有任何天标题 → 当作单日计划
        exercises = []
        seen_names = set()
        for line in lines:
            ex = _parse_exercise_line(line.strip())
            if ex and ex["name"] not in seen_names:
                exercises.append(ex)
                seen_names.add(ex["name"])
        if not exercises:
            return {"plan_type": "single", "days_data": {}}
        # 推断单日部位
        muscle = _guess_muscle_from_exercises(exercises)
        return {
            "plan_type": "single",
            "days_data": {
                "single": {
                    "muscle_group": muscle,
                    "is_rest": False,
                    "exercises": exercises,
                }
            }
        }

    # 有多天标题 → 按天分配动作
    days_data = {}

    for marker_i, (line_idx, widx, is_rest, muscle) in enumerate(day_markers):
        # 这一天的动作范围：当前marker到下一个marker之间
        next_line_idx = day_markers[marker_i + 1][0] if marker_i + 1 < len(day_markers) else len(lines)

        if is_rest:
            # 休息日，无动作
            days_data[widx] = {
                "muscle_group": "休息",
                "is_rest": True,
                "exercises": [],
            }
        else:
            day_exercises = []
            seen = set()
            for j in range(line_idx + 1, next_line_idx):
                ex = _parse_exercise_line(lines[j].strip())
                if ex and ex["name"] not in seen:
                    day_exercises.append(ex)
                    seen.add(ex["name"])

            # 如果识别的部位是"未指定"，根据动作推断
            if muscle == "未指定" and day_exercises:
                muscle = _guess_muscle_from_exercises(day_exercises)

            days_data[widx] = {
                "muscle_group": muscle,
                "is_rest": False,
                "exercises": day_exercises,
            }

    # 检查是否真的是周计划（至少2天有内容）
    valid_days = [d for d in days_data.values() if d["exercises"] or d["is_rest"]]
    if len(valid_days) >= 2:
        # 补全缺失的天数为休息日
        for w in range(7):
            if w not in days_data:
                days_data[w] = {
                    "muscle_group": "休息",
                    "is_rest": True,
                    "exercises": [],
                }
        # 转字符串key（json兼容）
        days_data_str = {str(k): v for k, v in days_data.items()}
        return {"plan_type": "weekly", "days_data": days_data_str}
    else:
        # 只有1天 → 当单日计划
        if days_data:
            first_day = list(days_data.values())[0]
            return {
                "plan_type": "single",
                "days_data": {"single": first_day}
            }
        return {"plan_type": "single", "days_data": {}}


def _guess_muscle_from_exercises(exercises: list) -> str:
    """根据动作列表推断主要部位（加权评分版）"""
    if not exercises:
        return "未指定"
    text = " ".join([e.get("name","") for e in exercises])

    # 用计数器代替简单集合 - 每个部位累计权重
    scores = {"胸": 0, "背": 0, "腿": 0, "肩": 0, "二头": 0, "三头": 0, "核心": 0, "臀": 0}

    # 强信号关键词（每出现一次+2分）
    strong_signals = {
        "胸": ["卧推","推胸","夹胸","胸"],
        "背": ["下拉","划船","引体","背"],
        "腿": ["深蹲","腿举","蹬腿","腿屈伸","腿弯举","弓步"],
        "肩": ["肩推","侧平举","前平举","侧抬","前抬","推举"],
        "二头": ["弯举","二头"],
        "三头": ["三头","下压","臂屈伸","颈后"],
        "核心": ["卷腹","平板","支撑","举腿","俄罗斯转体","核心"],
        "臀": ["臀冲","臀桥","臀推"],
    }
    # 弱信号关键词（每出现一次+1分，可能多部位）
    weak_signals = {
        "背": ["硬拉","面拉"],  # 硬拉也算腿但更主要是背
        "腿": ["硬拉","臀桥","臀冲"],  # 复合动作
        "胸": ["飞鸟","俯卧撑"],
    }

    for muscle, kws in strong_signals.items():
        for kw in kws:
            scores[muscle] += text.count(kw) * 2

    for muscle, kws in weak_signals.items():
        for kw in kws:
            scores[muscle] += text.count(kw)

    # 过滤掉得分太低的部位（只保留 >= 2 分的主导部位）
    detected = {m for m, s in scores.items() if s >= 2}

    if not detected:
        return "未指定"
    if len(detected) == 1:
        return detected.pop()

    # 常见组合
    if "胸" in detected and "三头" in detected: return "胸+三头"
    if "背" in detected and "二头" in detected: return "背+二头"
    if "肩" in detected and "核心" in detected: return "肩+核心"
    if "腿" in detected and "肩" in detected: return "腿+肩"
    if "腿" in detected and "臀" in detected: return "腿+臀"
    if "胸" in detected and "肩" in detected and "三头" in detected: return "胸+肩+三头"

    # 4+ 个部位才算全身（之前是3个，太宽松）
    if len(detected) >= 4:
        return "全身"

    # 2-3 个部位 → 按得分排序取前2个
    top2 = sorted(detected, key=lambda m: -scores[m])[:2]
    return "+".join(top2)


def parse_ai_plan(ai_text: str) -> list:
    """兼容老接口：扁平化返回所有动作"""
    result = parse_ai_plan_smart(ai_text)
    all_ex = []
    for day in result["days_data"].values():
        all_ex.extend(day.get("exercises", []))
    return all_ex


# ============ 伤病预警 ============
def check_injury_risk(profile: dict, exercises: list, session_notes: str = "") -> list:
    """
    检查伤病预警
    :param profile: 用户档案（包含历史 health_conditions）
    :param exercises: 当次训练的动作列表
    :param session_notes: 用户本次训练的备注（实时反馈，最重要）
    :return: 预警消息列表
    """
    warnings = []
    if not exercises and not session_notes:
        return warnings

    health = (profile.get("health_conditions") if profile else "" or "").lower()
    if health == "无":
        health = ""
    notes = (session_notes or "").lower()
    exercise_names = " ".join([e.get("name", "") for e in (exercises or [])])

    # ========= 第一类：备注里的实时不适信号（最重要）=========
    # 识别 "部位 + 不适词" 的组合
    body_part_signals = {
        "肩": ["肩","肩膀","三角肌","肩袖","锁骨"],
        "腰": ["腰","腰部","下背","腰椎","椎间盘"],
        "膝": ["膝","膝盖","膝关节","髌骨","半月板"],
        "腿": ["腿","大腿","小腿","后腿","前腿","股四头","股二头","腘绳","腿后","腿前","腘窝","小腿肚"],
        "臀": ["臀","屁股","臀部","梨状肌"],
        "肘": ["肘","胳膊肘","肘关节"],
        "腕": ["腕","手腕","腕关节"],
        "踝": ["踝","脚踝","跟腱"],
        "脚": ["脚底","脚趾","足弓"],
        "颈": ["颈","脖子","颈椎"],
        "髋": ["髋","胯","胯部"],
        "背": ["上背","背部","背"],
        "胸": ["胸口","胸部"],
        "手臂": ["手臂","胳膊","二头","三头","肱二头","肱三头"],
    }
    discomfort_signals = {
        "异响": ["异响","咔嗒","咯吱","响声","咯咯","嘎吱","弹响","响"],
        "疼痛": ["疼","痛","刺痛","剧痛","酸痛得厉害"],
        "抽搐": ["抽搐","抽筋","痉挛","抽筋","肌肉抽"],
        "不适": ["不适","难受","酸胀","紧绷","僵硬","卡住","不舒服","不太舒服","酸","胀","累得不行","发紧"],
        "受伤": ["受伤","扭伤","拉伤","闪到","拉到","闪了"],
        "麻木": ["发麻","麻木","刺麻","有点麻","麻"],
    }

    # 把备注按标点拆成短句，按句子分析（避免跨句误判）
    sentences = re.split(r'[，。；！？,;!?\n]', notes)
    sentences = [s.strip() for s in sentences if s.strip()]

    reported = set()  # 已经报过的 (部位+不适类型) 组合避免重复
    for sentence in sentences:
        for body, body_kws in body_part_signals.items():
            if not any(kw in sentence for kw in body_kws):
                continue
            for disc_type, disc_kws in discomfort_signals.items():
                if not any(kw in sentence for kw in disc_kws):
                    continue
                key = (body, disc_type)
                if key in reported:
                    continue
                reported.add(key)
                # 根据严重程度生成对应预警
                if disc_type == "异响":
                    warnings.append(
                        f"🚨 训练备注中提到「{body}部出现异响」。\n"
                        f"建议：① **立即停止该动作**，异响可能是关节、肌腱、滑膜出现问题的信号 "
                        f"② 24-48小时内观察是否伴随疼痛或活动受限 "
                        f"③ 如反复出现或加重，强烈建议**前往「伤病筛查」详细描述症状**或就医检查 "
                        f"④ 下次训练前充分热身，避免该动作或减重 50%"
                    )
                elif disc_type == "疼痛":
                    warnings.append(
                        f"🚨 训练备注中提到「{body}部疼痛」。\n"
                        f"建议：① **立即停止训练该部位** ② 应用 RICE 原则（休息+冰敷+加压+抬高） "
                        f"③ 24小时内观察，如疼痛持续或加重请就医 "
                        f"④ 强烈建议**前往「伤病筛查」详细描述症状**，让 AI 康复师给出针对性建议"
                    )
                elif disc_type == "受伤":
                    warnings.append(
                        f"🚨 训练备注中显示**{body}部疑似受伤**。\n"
                        f"立即措施：① 停止训练 ② RICE 原则（休息+冰敷15分钟+加压包扎+抬高） "
                        f"③ **如有明显肿胀、关节变形、无法承重，请立即就医** "
                        f"④ 前往「伤病筛查」获取详细康复建议"
                    )
                elif disc_type == "麻木":
                    warnings.append(
                        f"🚨 训练备注中提到「{body}部麻木」。\n"
                        f"⚠ 这可能是神经压迫或循环问题的信号。建议：① 立即停止训练 "
                        f"② 检查训练姿势是否压迫到神经 ③ **如麻木持续超过30分钟或伴随其他症状请就医**"
                    )
                elif disc_type == "抽搐":
                    warnings.append(
                        f"🚨 训练备注中提到「{body}部抽搐/痉挛」。\n"
                        f"原因可能是：① **电解质失衡**（钠/钾/镁/钙不足）② 训练强度过大或脱水 "
                        f"③ 肌肉过度疲劳 ④ 热身不充分。\n"
                        f"立即措施：① 停止训练 ② 缓慢拉伸抽搐肌肉 ③ 按摩放松 "
                        f"④ 补充含电解质的水或运动饮料 ⑤ 注意保暖。\n"
                        f"建议：今后训练前充分热身，训练中适量饮水，可考虑补充镁/钾。"
                        f"如反复发作，请前往「伤病筛查」或就医检查"
                    )
                else:
                    warnings.append(
                        f"⚠ 训练备注中提到「{body}部{disc_type}」。\n"
                        f"建议：① 评估严重程度 ② 减少该部位训练强度 "
                        f"③ 训练前后做针对性拉伸和按摩 ④ 如持续 3 天以上请前往「伤病筛查」"
                    )

    # 备注里有通用伤病词但没匹配到部位
    if not warnings and notes:
        general_signs = ["拉伤","扭伤","受伤","严重疼痛","剧痛"]
        if any(kw in notes for kw in general_signs):
            warnings.append(
                f"🚨 训练备注显示有伤病信号。\n"
                f"建议：① 立即停止训练 ② **前往「伤病筛查」详细描述症状**让 AI 评估 ③ 如严重请就医"
            )

    # ========= 第二类：档案里的预存健康状况 + 当次动作匹配 =========
    if health:
        risk_rules = [
            {"keywords":["膝","半月板","髌骨","膝关节"],
             "exercise_match":["深蹲","蹲","弓步","腿举","蹬腿","跳"],
             "msg":"⚠ 档案显示有膝部问题，今天的训练包含蹲类动作。建议：① 充分热身 ② 重量减少20-30%　③ 控制下蹲深度不低于平行 ④ 训练后冰敷15分钟"},
            {"keywords":["腰","椎间盘","腰肌劳损","腰椎"],
             "exercise_match":["硬拉","深蹲","划船","弯举","俯身"],
             "msg":"⚠ 档案显示有腰部问题。建议：① 全程保持核心收紧 ② 避免负重过大 ③ 硬拉类改用六角杆或换为臀冲 ④ 训练前做猫牛式激活"},
            {"keywords":["肩","肩袖","肩周炎","冈上肌"],
             "exercise_match":["卧推","推举","引体","侧平举","过顶"],
             "msg":"⚠ 档案显示有肩部问题。建议：① 训练前做肩关节灵活性练习 ② 减少过顶推举重量 ③ 卧推减少下放幅度 ④ 增加肩袖肌群激活"},
            {"keywords":["肘","网球肘","高尔夫肘"],
             "exercise_match":["弯举","下压","引体","俯卧撑"],
             "msg":"⚠ 档案显示有肘部问题。建议：① 减小重量 ② 训练前佩戴肘部护具 ③ 避免直杆弯举改用曲杆或哑铃 ④ 训练后冰敷"},
            {"keywords":["心","高血压","心脏"],
             "exercise_match":[],
             "msg":"⚠ 档案显示有心血管问题。请注意：① 避免憋气 ② 控制重量在中等强度 ③ 组间充分休息 ④ 出现胸闷立即停止"},
            {"keywords":["糖尿病"],
             "exercise_match":[],
             "msg":"⚠ 糖尿病人群训练注意：① 训练前后监测血糖 ② 携带糖块 ③ 避免空腹训练"},
        ]
        for rule in risk_rules:
            if any(kw in health for kw in rule["keywords"]):
                if not rule["exercise_match"] or any(em in exercise_names for em in rule["exercise_match"]):
                    warnings.append(rule["msg"])

    return warnings


# ============ 营养建议 ============
def get_nutrition_advice(target_muscle: str, exercises: list) -> dict:
    target_muscle = target_muscle or ""
    exercise_names = " ".join([e.get("name", "") for e in (exercises or [])])
    combined = (target_muscle + " " + exercise_names).lower()
    advice = {"post_workout": [], "supplements": []}
    is_leg = any(kw in combined for kw in ["腿","深蹲","硬拉","蹲","腿举","蹬腿","臀"])
    is_chest = any(kw in combined for kw in ["胸","卧推","飞鸟","夹胸","俯卧撑"])
    is_back = any(kw in combined for kw in ["背","引体","划船","下拉","硬拉"])
    is_chest_shoulder = is_chest or any(kw in combined for kw in ["肩","推举","侧平举","前平举"])
    advice["post_workout"].append("训练后 30 分钟黄金窗口期内补充蛋白+碳水")
    advice["supplements"].append({"category":"乳清蛋白粉","reason":"训练后立即补充20-30g蛋白质促进肌肉合成","priority":"core"})
    if is_leg or is_back:
        advice["supplements"].append({"category":"肌酸","reason":"大肌群训练后补充5g肌酸帮助恢复","priority":"core"})
        advice["post_workout"].append("大肌群训练后建议补充快碳（香蕉/葡萄糖）+ 慢碳（米饭/燕麦）")
    if is_chest_shoulder:
        advice["supplements"].append({"category":"鱼油Omega-3","reason":"上肢推类动作对肩关节有压力，Omega-3可减少炎症","priority":"advanced"})
    advice["supplements"].append({"category":"BCAA/EAA","reason":"减少肌肉分解，加速恢复","priority":"advanced"})
    advice["supplements"].append({"category":"ZMA","reason":"睡前补充改善睡眠质量，促进恢复","priority":"advanced"})
    return advice


# ============ 渐进超负荷 ============
def progressive_overload_tip(history_sessions: list, exercise_name: str) -> str:
    if not history_sessions:
        return ""
    recent_records = []
    for s in history_sessions[:5]:
        for ex in s.get("exercises_data", []):
            if ex.get("name") == exercise_name:
                for set_log in ex.get("set_logs", []):
                    if set_log.get("done") and set_log.get("actual_weight"):
                        recent_records.append({
                            "weight": set_log["actual_weight"],
                            "reps": set_log.get("actual_reps", 0),
                            "date": s.get("session_date"),
                        })
    if len(recent_records) < 2:
        return ""
    weights = [r["weight"] for r in recent_records[:3]]
    reps = [r["reps"] for r in recent_records[:3]]
    if len(set(weights)) == 1 and len(set(reps)) == 1:
        new_weight = weights[0] * 1.05
        return f"💡 {exercise_name} 已稳定在 {weights[0]}kg×{reps[0]}次连续3次，建议下次尝试 {new_weight:.1f}kg 或增加2次"
    return ""
