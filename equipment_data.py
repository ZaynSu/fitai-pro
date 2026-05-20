"""
健身辅助工具数据库
8 大分类、30+ 品牌产品
"""

# ============ 工具分类 ============
EQUIPMENT_CATEGORIES = {
    "腰部支持": {
        "icon": "🦺",
        "description": "硬拉、深蹲等大重量训练时保护腰椎，增强核心稳定",
        "when_to_use": "硬拉/深蹲 ≥ 自重 1 倍时建议使用；有腰部不适史更推荐",
        "popular_brands": ["SBD", "Inzer", "Schiek", "海德", "奥威尔", "迷宝赫"],
    },
    "护腕": {
        "icon": "💪",
        "description": "卧推、肩推时稳定手腕，减少手腕受伤风险",
        "when_to_use": "重量 ≥ 80% 1RM 推举动作时建议使用",
        "popular_brands": ["SBD", "Schiek", "Rogue", "海德", "迷宝赫", "Keep"],
    },
    "护膝": {
        "icon": "🦵",
        "description": "深蹲、腿举时保护膝关节，提供额外支持力",
        "when_to_use": "大重量深蹲（≥ 1.2 倍体重）或膝部不适时使用",
        "popular_brands": ["SBD", "Stoic", "Rehband", "海德", "迷宝赫", "李宁"],
    },
    "护肘": {
        "icon": "💪",
        "description": "卧推、推举、弯举时保护肘关节",
        "when_to_use": "网球肘、高尔夫肘历史，或大重量推举时",
        "popular_brands": ["Rehband", "SBD", "Schiek", "海德"],
    },
    "助力带": {
        "icon": "🧤",
        "description": "硬拉、划船时辅助抓握，让背部充分发力",
        "when_to_use": "硬拉、划船大重量时握力先于背部力竭",
        "popular_brands": ["Versa Gripps", "Schiek", "Harbinger", "海德", "迷宝赫"],
    },
    "镁粉/握力": {
        "icon": "✋",
        "description": "增加摩擦力，改善握力滑脱问题",
        "when_to_use": "手汗较多、握力不足时使用；液体镁粉更便携",
        "popular_brands": ["Friction Labs", "SPRI", "海德", "迷宝赫", "京东京造"],
    },
    "举重鞋": {
        "icon": "👟",
        "description": "硬底高跟设计，深蹲时改善踝关节灵活性、传递力量",
        "when_to_use": "深蹲/抓举/挺举训练，或踝关节灵活性不足",
        "popular_brands": ["Adidas Adipower", "Nike Romaleos", "Reebok Legacy Lifter", "海德"],
    },
    "恢复工具": {
        "icon": "🩹",
        "description": "筋膜枪、泡沫轴、按摩球，训练后促进恢复",
        "when_to_use": "训练后肌肉酸痛、紧绷；日常拉伸放松",
        "popular_brands": ["Hyperice", "Theragun", "Keep", "小米米家", "倍益康", "云麦"],
    },
}


# ============ 品牌产品库（约 30 个产品） ============
EQUIPMENT_BRANDS = [
    # === 腰部支持 ===
    {
        "category": "腰部支持", "brand": "SBD", "country": "🇬🇧 英国",
        "product_name": "SBD 10mm 力量举腰带",
        "price_range": "¥1500-1800",
        "description": "国际力量举认证款,IPF 比赛指定。10mm 厚牛皮,4 寸宽,前后等宽。",
        "pros": ["IPF 认证", "牛皮极致耐用", "扣子稳", "重量举/力量举通用"],
        "cons": ["价格高", "新带子需破开期", "尺码偏紧建议大一码"],
        "tier": "高端"
    },
    {
        "category": "腰部支持", "brand": "Inzer", "country": "🇺🇸 美国",
        "product_name": "Inzer Forever Lever 腰带",
        "price_range": "¥1100-1400",
        "description": "美国老牌,杠杆扣设计,一拉到位很方便。13mm 加厚版。",
        "pros": ["杠杆扣方便", "13mm 极致支撑", "耐用 10 年+"],
        "cons": ["杠杆扣不通用", "重量大", "国内购买较麻烦"],
        "tier": "高端"
    },
    {
        "category": "腰部支持", "brand": "海德 Hyder", "country": "🇨🇳 中国",
        "product_name": "海德专业举重腰带",
        "price_range": "¥180-280",
        "description": "国产性价比之选,真皮材质,7mm 厚度,适合健身房日常训练。",
        "pros": ["性价比极高", "真皮材质", "国内售后方便"],
        "cons": ["相比 SBD 略软", "仅适合中等重量", "做工细节稍逊"],
        "tier": "性价比"
    },
    {
        "category": "腰部支持", "brand": "迷宝赫", "country": "🇨🇳 中国",
        "product_name": "迷宝赫硬拉护腰",
        "price_range": "¥120-180",
        "description": "尼龙加魔术贴款,轻便,适合新手健身房使用。",
        "pros": ["轻便", "价格亲民", "魔术贴方便穿脱"],
        "cons": ["支撑力不如皮带", "大重量不推荐", "魔术贴会磨损"],
        "tier": "性价比"
    },

    # === 护腕 ===
    {
        "category": "护腕", "brand": "SBD", "country": "🇬🇧 英国",
        "product_name": "SBD 力量举护腕（中硬度）",
        "price_range": "¥380-450",
        "description": "IPF 认证,30cm 长度,弹性硬度适中。卧推、肩推神器。",
        "pros": ["IPF 认证", "支撑力强", "魔术贴牢固", "可清洗"],
        "cons": ["价格较高", "硬度需适应", "新手可能觉得过硬"],
        "tier": "高端"
    },
    {
        "category": "护腕", "brand": "Schiek", "country": "🇺🇸 美国",
        "product_name": "Schiek 1100WS 护腕",
        "price_range": "¥220-280",
        "description": "美国老牌,经典款。10cm 弹性带,适合日常训练。",
        "pros": ["弹性舒适", "耐用", "适合中等强度"],
        "cons": ["支撑力中等", "极限大重量不够"],
        "tier": "中端"
    },
    {
        "category": "护腕", "brand": "Keep", "country": "🇨🇳 中国",
        "product_name": "Keep 健身护腕",
        "price_range": "¥45-80",
        "description": "Keep 出品,通用款,日常健身房卧推、推举使用足够。",
        "pros": ["价格友好", "国内售后", "颜值高"],
        "cons": ["弹性不如进口", "极限重量不够", "做工一般"],
        "tier": "性价比"
    },
    {
        "category": "护腕", "brand": "迷宝赫", "country": "🇨🇳 中国",
        "product_name": "迷宝赫加固护腕",
        "price_range": "¥35-60",
        "description": "国产入门款,适合家用或低强度训练。",
        "pros": ["便宜", "颜色多", "新手友好"],
        "cons": ["弹力不持久", "支撑力较弱"],
        "tier": "性价比"
    },

    # === 护膝 ===
    {
        "category": "护膝", "brand": "SBD", "country": "🇬🇧 英国",
        "product_name": "SBD 7mm 护膝",
        "price_range": "¥850-980",
        "description": "国际力量举顶级款,7mm 厚护膝,深蹲反弹助力明显。",
        "pros": ["IPF 认证", "反弹助力强", "支撑性极佳"],
        "cons": ["价格高", "穿脱较费力", "夏天闷热"],
        "tier": "高端"
    },
    {
        "category": "护膝", "brand": "Rehband", "country": "🇸🇪 瑞典",
        "product_name": "Rehband 7mm 护膝",
        "price_range": "¥480-580",
        "description": "瑞典专业康复品牌,SBR 橡胶,医用级,适合膝盖恢复期。",
        "pros": ["医用级品质", "支撑+保暖", "适合康复期"],
        "cons": ["反弹助力一般", "硬度不如 SBD"],
        "tier": "中高端"
    },
    {
        "category": "护膝", "brand": "李宁", "country": "🇨🇳 中国",
        "product_name": "李宁专业运动护膝",
        "price_range": "¥120-200",
        "description": "国产专业运动品牌,5mm 厚度,适合大众健身使用。",
        "pros": ["国产品牌信赖", "性价比好", "舒适度高"],
        "cons": ["支撑性中等", "不适合极限重量"],
        "tier": "性价比"
    },
    {
        "category": "护膝", "brand": "海德 Hyder", "country": "🇨🇳 中国",
        "product_name": "海德专业护膝",
        "price_range": "¥80-150",
        "description": "性价比之选,健身房日常深蹲、腿举可用。",
        "pros": ["价格亲民", "日常够用"],
        "cons": ["支撑性一般", "耐用度中等"],
        "tier": "性价比"
    },

    # === 护肘 ===
    {
        "category": "护肘", "brand": "Rehband", "country": "🇸🇪 瑞典",
        "product_name": "Rehband 7mm 护肘",
        "price_range": "¥320-420",
        "description": "瑞典专业品牌,适合肘部不适或大重量推举训练。",
        "pros": ["医用级", "保暖+支撑", "耐用"],
        "cons": ["价格偏高", "夏天闷热"],
        "tier": "中高端"
    },
    {
        "category": "护肘", "brand": "海德 Hyder", "country": "🇨🇳 中国",
        "product_name": "海德加压护肘",
        "price_range": "¥60-120",
        "description": "国产性价比款,日常推举训练用。",
        "pros": ["价格低", "舒适"],
        "cons": ["支撑性一般"],
        "tier": "性价比"
    },

    # === 助力带 ===
    {
        "category": "助力带", "brand": "Versa Gripps", "country": "🇺🇸 美国",
        "product_name": "Versa Gripps PRO",
        "price_range": "¥580-680",
        "description": "美国专业助力带,弧形设计,无需缠绕,佩戴方便。",
        "pros": ["佩戴方便", "支撑力强", "耐用"],
        "cons": ["价格高", "适应期较长"],
        "tier": "高端"
    },
    {
        "category": "助力带", "brand": "Schiek", "country": "🇺🇸 美国",
        "product_name": "Schiek 1000PLS 助力带",
        "price_range": "¥150-220",
        "description": "经典棉质带款,需要缠绕,但是抓握感很好。",
        "pros": ["性价比好", "抓握感佳", "耐用"],
        "cons": ["需要练习缠绕", "棉质易脏"],
        "tier": "中端"
    },
    {
        "category": "助力带", "brand": "海德 Hyder", "country": "🇨🇳 中国",
        "product_name": "海德专业助力带",
        "price_range": "¥35-80",
        "description": "国产入门款,适合新手熟悉助力带使用。",
        "pros": ["价格低", "新手友好"],
        "cons": ["材质偏硬", "易磨损"],
        "tier": "性价比"
    },
    {
        "category": "助力带", "brand": "迷宝赫", "country": "🇨🇳 中国",
        "product_name": "迷宝赫硬拉助力带",
        "price_range": "¥25-60",
        "description": "最便宜入门款,健身房日常使用。",
        "pros": ["极便宜", "够用"],
        "cons": ["不耐磨", "建议半年一换"],
        "tier": "性价比"
    },

    # === 镁粉/握力 ===
    {
        "category": "镁粉/握力", "brand": "Friction Labs", "country": "🇺🇸 美国",
        "product_name": "Friction Labs 攀岩镁粉",
        "price_range": "¥150-250",
        "description": "美国攀岩界顶级镁粉,纯度高,粉质细腻不结块。",
        "pros": ["纯度极高", "持久不掉", "粉质细腻"],
        "cons": ["价格高", "国内购买较麻烦"],
        "tier": "高端"
    },
    {
        "category": "镁粉/握力", "brand": "京东京造", "country": "🇨🇳 中国",
        "product_name": "京东京造液体镁粉",
        "price_range": "¥35-60",
        "description": "国产液体镁粉,涂抹方便,飞不到衣服上。",
        "pros": ["价格亲民", "液体不飞扬", "便携"],
        "cons": ["持久度不如粉状", "需要等干"],
        "tier": "性价比"
    },
    {
        "category": "镁粉/握力", "brand": "海德 Hyder", "country": "🇨🇳 中国",
        "product_name": "海德专业镁粉",
        "price_range": "¥25-50",
        "description": "国产粉状镁粉,健身房常用款。",
        "pros": ["便宜", "好用"],
        "cons": ["容易飞扬", "需要镁粉袋"],
        "tier": "性价比"
    },

    # === 举重鞋 ===
    {
        "category": "举重鞋", "brand": "Adidas", "country": "🇩🇪 德国",
        "product_name": "Adidas Adipower III 举重鞋",
        "price_range": "¥1500-2000",
        "description": "举重鞋天花板,木质硬底,2cm 跟高,深蹲/挺举专用。",
        "pros": ["顶级品质", "传力极佳", "耐用"],
        "cons": ["价格高", "只适合大重量", "不能日常穿"],
        "tier": "高端"
    },
    {
        "category": "举重鞋", "brand": "Nike", "country": "🇺🇸 美国",
        "product_name": "Nike Romaleos 4",
        "price_range": "¥1300-1700",
        "description": "Nike 举重鞋,塑料中底,2.2cm 跟高,深蹲灵活性好。",
        "pros": ["质量好", "舒适", "颜值高"],
        "cons": ["价格高", "中底较软"],
        "tier": "高端"
    },
    {
        "category": "举重鞋", "brand": "海德 Hyder", "country": "🇨🇳 中国",
        "product_name": "海德专业举重鞋",
        "price_range": "¥280-480",
        "description": "国产举重鞋,木质硬底,深蹲/挺举入门款。",
        "pros": ["性价比之王", "够用"],
        "cons": ["质感不如进口", "尺码偏窄"],
        "tier": "性价比"
    },

    # === 恢复工具 ===
    {
        "category": "恢复工具", "brand": "Hyperice", "country": "🇺🇸 美国",
        "product_name": "Hyperice Hypervolt 2 筋膜枪",
        "price_range": "¥1800-2400",
        "description": "美国顶级筋膜枪,3 档力度,5 个枪头,安静度好。",
        "pros": ["顶级品质", "安静", "电池续航好"],
        "cons": ["价格高", "重量偏重"],
        "tier": "高端"
    },
    {
        "category": "恢复工具", "brand": "Theragun", "country": "🇺🇸 美国",
        "product_name": "Theragun Pro 4代筋膜枪",
        "price_range": "¥2800-3500",
        "description": "Theragun 招牌款,力度可调,深层放松。",
        "pros": ["顶级品质", "深层放松", "Pro 级"],
        "cons": ["价格极高", "学习曲线"],
        "tier": "高端"
    },
    {
        "category": "恢复工具", "brand": "Keep", "country": "🇨🇳 中国",
        "product_name": "Keep 筋膜枪",
        "price_range": "¥280-450",
        "description": "Keep 出品,5 档力度,4 个枪头,日常放松够用。",
        "pros": ["性价比高", "外观漂亮", "Keep 配套"],
        "cons": ["力度不如顶级", "电池续航中等"],
        "tier": "性价比"
    },
    {
        "category": "恢复工具", "brand": "小米米家", "country": "🇨🇳 中国",
        "product_name": "米家筋膜枪",
        "price_range": "¥220-380",
        "description": "米家性价比之选,简单耐用。",
        "pros": ["价格亲民", "小米生态", "做工不错"],
        "cons": ["档位少", "力度中等"],
        "tier": "性价比"
    },
    {
        "category": "恢复工具", "brand": "倍益康", "country": "🇨🇳 中国",
        "product_name": "倍益康筋膜枪 Pro",
        "price_range": "¥400-650",
        "description": "国产专业品牌,医用级,力度够,运动员常用。",
        "pros": ["专业级", "力度足", "保修好"],
        "cons": ["颜值一般", "稍重"],
        "tier": "中端"
    },
    {
        "category": "恢复工具", "brand": "TriggerPoint", "country": "🇺🇸 美国",
        "product_name": "TriggerPoint GRID 泡沫轴",
        "price_range": "¥220-320",
        "description": "美国专业泡沫轴,凹凸表面,深层放松。",
        "pros": ["专业级", "耐用", "效果好"],
        "cons": ["价格高", "初用较痛"],
        "tier": "中高端"
    },
    {
        "category": "恢复工具", "brand": "Keep", "country": "🇨🇳 中国",
        "product_name": "Keep 泡沫轴",
        "price_range": "¥45-120",
        "description": "Keep 入门泡沫轴,光滑款和凹凸款可选。",
        "pros": ["价格亲民", "颜色多"],
        "cons": ["材质偏软", "耐用度一般"],
        "tier": "性价比"
    },
]


# ============ 评分维度 ============
RATING_DIMENSIONS = [
    {"key": "protection", "label": "防护性", "icon": "🛡️"},
    {"key": "comfort", "label": "舒适度", "icon": "✨"},
    {"key": "value", "label": "性价比", "icon": "💰"},
    {"key": "durability", "label": "耐用度", "icon": "⚡"},
    {"key": "appearance", "label": "外观", "icon": "🎨"},
]


# ============ 训练备注 → 工具推荐映射 ============
def recommend_equipment_from_notes(notes: str) -> list:
    """
    根据训练备注里的关键词，推荐相关工具
    返回: [{"category": "...", "reason": "...", "priority": "high|medium"}]
    """
    if not notes:
        return []

    notes_lower = notes.lower()
    recommendations = []

    rules = [
        {
            "kws": ["腰部疼痛","腰痛","腰部不适","腰部紧绷","腰部酸","腰疼","下背痛"],
            "category": "腰部支持",
            "reason": "训练中出现腰部不适，建议使用举重腰带保护腰椎，特别是大重量硬拉/深蹲时",
            "priority": "high"
        },
        {
            "kws": ["握不住","抓不稳","前臂酸","握力不足","握力先力竭","手滑"],
            "category": "助力带",
            "reason": "握力先于目标肌肉力竭，使用助力带让背部充分发力",
            "priority": "high"
        },
        {
            "kws": ["膝盖痛","膝盖不适","膝部疼痛","膝关节"],
            "category": "护膝",
            "reason": "膝部不适，建议大重量深蹲/腿举时佩戴护膝,提供支撑和保暖",
            "priority": "high"
        },
        {
            "kws": ["手腕痛","手腕不适","手腕酸","腕关节"],
            "category": "护腕",
            "reason": "手腕不适，建议卧推/推举时佩戴护腕稳定关节",
            "priority": "high"
        },
        {
            "kws": ["肘部不适","肘痛","胳膊肘","网球肘","高尔夫肘"],
            "category": "护肘",
            "reason": "肘部不适，建议推举/弯举时佩戴护肘保护关节",
            "priority": "high"
        },
        {
            "kws": ["肌肉酸痛","肌肉紧绷","肌肉僵硬","训练后疲劳","恢复慢"],
            "category": "恢复工具",
            "reason": "训练后恢复不佳，建议使用筋膜枪/泡沫轴促进血液循环和放松",
            "priority": "medium"
        },
        {
            "kws": ["手汗","出汗多","握把滑"],
            "category": "镁粉/握力",
            "reason": "手汗导致握把打滑，建议使用镁粉或液体镁粉改善摩擦",
            "priority": "medium"
        },
        {
            "kws": ["深蹲不深","下不去","脚踝不灵活","深蹲不稳"],
            "category": "举重鞋",
            "reason": "踝关节灵活性限制深蹲质量，举重鞋的硬底高跟可改善",
            "priority": "medium"
        },
    ]

    matched_categories = set()
    for rule in rules:
        if rule["category"] in matched_categories:
            continue
        if any(kw in notes_lower for kw in rule["kws"]):
            recommendations.append({
                "category": rule["category"],
                "reason": rule["reason"],
                "priority": rule["priority"]
            })
            matched_categories.add(rule["category"])

    return recommendations


def get_brands_by_category(category: str) -> list:
    """获取某分类下所有品牌产品"""
    return [b for b in EQUIPMENT_BRANDS if b["category"] == category]
