"""
补剂品类配置 + 评分维度配置
"""

# ============ 品类定义 ============
# 每个品类有独立的5个评分维度
CATEGORY_CONFIG = {
    "乳清蛋白粉": {
        "emoji": "🥛",
        "description": "训练后蛋白质补充，增肌/减脂期必备",
        "dimensions": ["口味", "溶解度", "性价比", "吸收效率", "成分纯净度"],
        "science_rating": 5,
    },
    "分离乳清蛋白": {
        "emoji": "💎",
        "description": "蛋白纯度高于90%，几乎不含乳糖和脂肪",
        "dimensions": ["口味", "溶解度", "性价比", "纯度", "适合乳糖不耐"],
        "science_rating": 5,
    },
    "水解乳清蛋白": {
        "emoji": "⚡",
        "description": "吸收速度最快，适合训练后即时补充",
        "dimensions": ["吸收速度", "口味", "性价比", "纯度", "肠胃舒适度"],
        "science_rating": 5,
    },
    "酪蛋白": {
        "emoji": "🌙",
        "description": "缓慢释放蛋白质，适合睡前或长时间空腹",
        "dimensions": ["饱腹感", "口味", "性价比", "缓释效果", "成分纯净度"],
        "science_rating": 4,
    },
    "增肌粉": {
        "emoji": "💪",
        "description": "高热量高碳水，适合瘦体型增肌人群",
        "dimensions": ["增重效果", "口味", "性价比", "肠胃负担", "营养均衡"],
        "science_rating": 3,
    },
    "植物蛋白粉": {
        "emoji": "🌱",
        "description": "豌豆/糙米/大麻蛋白，适合素食者和乳糖不耐",
        "dimensions": ["口感", "溶解度", "性价比", "蛋白氨基酸完整性", "肠胃友好度"],
        "science_rating": 4,
    },
    "肌酸": {
        "emoji": "🔋",
        "description": "提升爆发力和训练容量，最有科学依据的补剂之一",
        "dimensions": ["纯度", "溶解度", "性价比", "效果显著度", "肠胃舒适度"],
        "science_rating": 5,
    },
    "BCAA/EAA": {
        "emoji": "🧬",
        "description": "支链/必需氨基酸，训练中补充防分解",
        "dimensions": ["氨基酸配比", "口味", "溶解度", "性价比", "实际效果"],
        "science_rating": 3,
    },
    "氮泵": {
        "emoji": "🚀",
        "description": "训练前补充，提升精力、专注力和泵感",
        "dimensions": ["起效速度", "能量持续", "口味", "性价比", "刺激强度"],
        "science_rating": 4,
    },
    "瓜氨酸": {
        "emoji": "💉",
        "description": "前体氨基酸，提升一氧化氮、改善血流和泵感",
        "dimensions": ["泵感效果", "纯度", "口味", "性价比", "肠胃舒适度"],
        "science_rating": 4,
    },
    "谷氨酰胺": {
        "emoji": "🛡",
        "description": "辅助恢复和免疫力支持",
        "dimensions": ["恢复效果", "纯度", "性价比", "口味", "肠胃友好度"],
        "science_rating": 3,
    },
    "β-丙氨酸": {
        "emoji": "⚙️",
        "description": "延缓肌肉酸痛，提升高强度耐力",
        "dimensions": ["效果", "纯度", "性价比", "刺痛感接受度", "组合使用便利度"],
        "science_rating": 4,
    },
    "HMB": {
        "emoji": "🧪",
        "description": "亮氨酸代谢产物，减少肌肉分解，新手期效果更明显",
        "dimensions": ["效果", "纯度", "性价比", "吞服感", "副作用"],
        "science_rating": 3,
    },
    "燃脂补剂": {
        "emoji": "🔥",
        "description": "促进代谢和脂肪燃烧",
        "dimensions": ["燃脂效果", "副作用", "性价比", "安全性", "持续耐受度"],
        "science_rating": 2,
    },
    "L-肉碱": {
        "emoji": "💧",
        "description": "辅助脂肪运输与代谢",
        "dimensions": ["效果显著度", "口味", "性价比", "副作用", "吸收效率"],
        "science_rating": 2,
    },
    "维生素D3": {
        "emoji": "☀️",
        "description": "提升睾酮、骨骼、免疫力",
        "dimensions": ["吸收率", "剂量准确", "性价比", "品牌信任度", "副作用"],
        "science_rating": 5,
    },
    "鱼油Omega-3": {
        "emoji": "🐟",
        "description": "抗炎、关节、心血管",
        "dimensions": ["EPA/DHA含量", "新鲜度", "性价比", "鱼腥味", "胶囊吞服感"],
        "science_rating": 5,
    },
    "复合维生素": {
        "emoji": "🌈",
        "description": "全面基础营养保障",
        "dimensions": ["营养全面性", "吸收率", "性价比", "吞服感", "副作用"],
        "science_rating": 4,
    },
    "ZMA": {
        "emoji": "💤",
        "description": "锌+镁+B6，改善睡眠与恢复",
        "dimensions": ["睡眠改善", "恢复效果", "性价比", "副作用", "吞服感"],
        "science_rating": 3,
    },
    "蛋白棒": {
        "emoji": "🍫",
        "description": "便携蛋白零食",
        "dimensions": ["口味", "口感", "性价比", "蛋白含量", "低糖低脂"],
        "science_rating": 3,
    },
    "代餐": {
        "emoji": "🥤",
        "description": "减脂期热量控制",
        "dimensions": ["饱腹感", "口味", "性价比", "营养均衡", "便利性"],
        "science_rating": 3,
    },
    "维生素B族": {
        "emoji": "💛",
        "description": "能量代谢、神经系统、皮肤健康",
        "dimensions": ["剂量准确", "吸收率", "性价比", "副作用", "吞服感"],
        "science_rating": 4,
    },
    "电解质": {
        "emoji": "💧",
        "description": "训练中补充钠钾镁钙，避免抽筋和脱水",
        "dimensions": ["电解质配比", "口味", "性价比", "溶解度", "吸收速度"],
        "science_rating": 4,
    },
    "关节保护": {
        "emoji": "🦴",
        "description": "氨糖软骨素，保护关节软骨",
        "dimensions": ["效果", "成分含量", "性价比", "吞服感", "副作用"],
        "science_rating": 3,
    },
    "护肝": {
        "emoji": "🌿",
        "description": "高强度训练或补剂使用期间的肝脏保护",
        "dimensions": ["效果", "成分透明度", "性价比", "副作用", "起效时间"],
        "science_rating": 2,
    },
}


def get_categories():
    return list(CATEGORY_CONFIG.keys())


def get_category_info(category):
    return CATEGORY_CONFIG.get(category, {
        "emoji": "💊",
        "description": "",
        "dimensions": ["维度1", "维度2", "维度3", "维度4", "维度5"],
        "science_rating": 3,
    })


def get_dimensions(category):
    info = get_category_info(category)
    return info.get("dimensions", ["维度1", "维度2", "维度3", "维度4", "维度5"])


# ============ 目标推荐组合（保留用于个性化推荐）============
GOAL_STACKS = {
    "增肌": {
        "core_categories": ["乳清蛋白粉", "肌酸", "维生素D3"],
        "advanced_categories": ["氮泵", "ZMA", "鱼油Omega-3", "维生素B族"],
        "description": "以蛋白质合成和力量提升为核心",
    },
    "减脂": {
        "core_categories": ["分离乳清蛋白", "鱼油Omega-3", "复合维生素"],
        "advanced_categories": ["L-肉碱", "BCAA/EAA", "电解质", "维生素B族"],
        "description": "保留肌肉、提高代谢、减少炎症",
    },
    "运动表现": {
        "core_categories": ["肌酸", "氮泵", "β-丙氨酸"],
        "advanced_categories": ["瓜氨酸", "BCAA/EAA", "维生素D3", "电解质"],
        "description": "最大化力量输出和训练容量",
    },
    "健康维持": {
        "core_categories": ["维生素D3", "鱼油Omega-3", "复合维生素"],
        "advanced_categories": ["乳清蛋白粉", "ZMA", "维生素B族"],
        "description": "基础营养保障和整体健康",
    },
    "康复恢复": {
        "core_categories": ["鱼油Omega-3", "维生素D3", "谷氨酰胺"],
        "advanced_categories": ["乳清蛋白粉", "复合维生素", "ZMA", "关节保护"],
        "description": "减少炎症、加速组织修复",
    },
}


def get_goal_stack(goal):
    for key in GOAL_STACKS:
        if key in goal or goal in key:
            return GOAL_STACKS[key]
    return GOAL_STACKS["健康维持"]
