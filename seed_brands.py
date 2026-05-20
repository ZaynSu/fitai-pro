"""
初始化补剂品牌和产品数据
运行：python seed_brands.py
注意：所有信息为参考数据，价格仅供参考，可能与实际有出入
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import init_db, add_brand, add_product, get_all_brands, get_conn

# ============ 20个品牌定义 ============
BRANDS = [
    # === 国际主流蛋白粉/增肌（8个）===
    {"name_cn":"奥普帝蒙","name_en":"Optimum Nutrition","country":"美国","tier":"国际顶级",
     "logo_emoji":"🥇","description":"行业标杆，金标乳清是全球销量最高的乳清蛋白之一"},
    {"name_cn":"达美泰滋","name_en":"Dymatize","country":"美国","tier":"国际顶级",
     "logo_emoji":"💠","description":"ISO100水解乳清以高纯度和快速吸收闻名"},
    {"name_cn":"熊猫蛋白","name_en":"MyProtein","country":"英国","tier":"国际主流",
     "logo_emoji":"🐼","description":"欧洲销量第一，性价比突出，口味丰富"},
    {"name_cn":"肌肉科技","name_en":"MuscleTech","country":"美国","tier":"国际主流",
     "logo_emoji":"🔬","description":"白金系列广受健身人群欢迎"},
    {"name_cn":"BSN","name_en":"BSN","country":"美国","tier":"国际主流",
     "logo_emoji":"🅱️","description":"Syntha-6 多元蛋白配方独特"},
    {"name_cn":"Cellucor","name_en":"Cellucor","country":"美国","tier":"国际主流",
     "logo_emoji":"💪","description":"旗下C4预锻炼是预锻炼市场的王者"},
    {"name_cn":"ALLMAX","name_en":"ALLMAX","country":"加拿大","tier":"国际主流",
     "logo_emoji":"🍁","description":"加拿大老牌，专注运动营养"},
    {"name_cn":"GAT","name_en":"GAT Sport","country":"美国","tier":"国际主流",
     "logo_emoji":"⚙","description":"Nitraflex预锻炼广受认可"},

    # === 国产主流（4个）===
    {"name_cn":"康比特","name_en":"CPT","country":"中国","tier":"国产主流",
     "logo_emoji":"🇨🇳","description":"国产老牌运动营养，专业线和大众线都有"},
    {"name_cn":"诺特兰德","name_en":"NUTREND","country":"中国","tier":"国产主流",
     "logo_emoji":"🌟","description":"近年抖音爆款，性价比高，包装年轻化"},
    {"name_cn":"汤臣倍健","name_en":"BY-HEALTH","country":"中国","tier":"国产主流",
     "logo_emoji":"🌿","description":"国内维生素和健康营养品龙头"},
    {"name_cn":"Wonderlab","name_en":"WonderLab","country":"中国","tier":"国产主流",
     "logo_emoji":"✨","description":"代餐和功能营养品，包装时尚"},

    # === 维生素/基础营养（4个）===
    {"name_cn":"Swisse","name_en":"Swisse","country":"澳大利亚","tier":"国际主流",
     "logo_emoji":"🇦🇺","description":"澳洲健康营养品牌，TGA认证"},
    {"name_cn":"GNC","name_en":"GNC","country":"美国","tier":"国际主流",
     "logo_emoji":"🏪","description":"美国最大健康营养品零售品牌之一"},
    {"name_cn":"Nature Made","name_en":"Nature Made","country":"美国","tier":"国际主流",
     "logo_emoji":"🌳","description":"USP认证，剂量准确稳定"},
    {"name_cn":"Blackmores","name_en":"Blackmores","country":"澳大利亚","tier":"国际主流",
     "logo_emoji":"🇦🇺","description":"澳洲健康营养老牌，鱼油和维生素出名"},

    # === 预锻炼/功能（2个）===
    {"name_cn":"C4","name_en":"C4","country":"美国","tier":"国际主流",
     "logo_emoji":"💥","description":"Cellucor旗下预锻炼专线，多个口味爆款"},
    {"name_cn":"GHOST","name_en":"GHOST","country":"美国","tier":"国际主流",
     "logo_emoji":"👻","description":"高端预锻炼和补剂，口味联名创意丰富"},

    # === 植物蛋白/小众（2个）===
    {"name_cn":"Garden of Life","name_en":"Garden of Life","country":"美国","tier":"国际主流",
     "logo_emoji":"🌿","description":"有机和植物蛋白，非转基因认证"},
    {"name_cn":"Vega","name_en":"Vega","country":"加拿大","tier":"国际主流",
     "logo_emoji":"🥬","description":"专注植物蛋白和素食营养"},

    # === 国产新增本地化（3个）===
    {"name_cn":"氧气能量","name_en":"O2 Energy","country":"中国","tier":"国产主流",
     "logo_emoji":"💨","description":"新兴国货健身补剂品牌，主打 EGCG、丙氨酸等细分产品"},
    {"name_cn":"修正","name_en":"Xiuzheng","country":"中国","tier":"国产主流",
     "logo_emoji":"💊","description":"国产药企旗下营养品，价格亲民、超市/药店常见"},
    {"name_cn":"FANCL","name_en":"FANCL","country":"日本","tier":"国际主流",
     "logo_emoji":"🌸","description":"日本无添加营养品牌，胶囊小、女性用户多"},
]


# ============ 产品数据 ============
# 每个 dict 是一个产品；brand_cn 用于匹配品牌ID
PRODUCTS = [
    # ========== 奥普帝蒙 Optimum Nutrition ==========
    {"brand_cn":"奥普帝蒙","series_name":"金标乳清 Gold Standard 100% Whey","category":"乳清蛋白粉",
     "subcategory":"浓缩+分离混合","description":"行业标杆乳清蛋白，蛋白吸收均衡，溶解度优秀",
     "key_features":["每勺24g蛋白","含5.5g BCAA","Informed-Choice认证","低糖配方"],
     "certifications":["Informed-Choice","BSCG"],
     "ref_price_min":380,"ref_price_max":620,
     "sizes":["2lb (907g)","5lb (2.27kg)","10lb (4.54kg)"],
     "flavors":["双重黑巧","薄荷巧克力","曲奇奶油","法式香草","草莓","咸味焦糖","摩卡卡布奇诺","白巧克力"],
     "science_rating":5,"target_users":["增肌","减脂","健康维持"],
     "usage_timing":"训练后30分钟内/餐间","dosage":"每次1勺(约30g)，每日1-2次",
     "cautions":"乳糖不耐受者建议选分离乳清"},

    {"brand_cn":"奥普帝蒙","series_name":"金标分离乳清 Gold Standard 100% Isolate","category":"分离乳清蛋白",
     "subcategory":"高纯度分离蛋白","description":"蛋白纯度更高，乳糖含量极低，适合乳糖敏感人群",
     "key_features":["蛋白纯度>90%","几乎零脂肪","几乎零乳糖","快速吸收"],
     "certifications":["Informed-Choice"],
     "ref_price_min":520,"ref_price_max":780,
     "sizes":["1.6lb","3lb","5lb"],
     "flavors":["浓郁巧克力","香草冰激凌","草莓"],
     "science_rating":5,"target_users":["减脂","乳糖不耐","健康维持"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约27g)"},

    {"brand_cn":"奥普帝蒙","series_name":"金标肌酸 Micronized Creatine","category":"肌酸",
     "subcategory":"一水肌酸","description":"经典一水肌酸，超微粒化提高溶解度",
     "key_features":["100%纯一水肌酸","无添加剂","微粒化工艺"],
     "certifications":["Informed-Choice"],
     "ref_price_min":150,"ref_price_max":280,
     "sizes":["300g","600g","2000g"],
     "flavors":["原味无味"],
     "science_rating":5,"target_users":["增肌","运动表现"],
     "usage_timing":"训练后或随餐","dosage":"每日3-5g"},

    # ========== 达美泰滋 Dymatize ==========
    {"brand_cn":"达美泰滋","series_name":"ISO100 水解分离乳清","category":"水解乳清蛋白",
     "subcategory":"水解+分离","description":"行业知名水解蛋白，吸收最快，几乎无乳糖",
     "key_features":["每勺25g蛋白","水解工艺","几乎0乳糖0糖","Informed-Choice认证"],
     "certifications":["Informed-Choice","Gluten-Free"],
     "ref_price_min":580,"ref_price_max":880,
     "sizes":["1.6lb","3lb","5lb"],
     "flavors":["软糖熊","巧克力花生酱","曲奇奶油","巧克力","香草","草莓","奶油可可","橙子奶油"],
     "science_rating":5,"target_users":["增肌","运动表现","乳糖不耐"],
     "usage_timing":"训练后立即","dosage":"每次1勺(约30g)"},

    {"brand_cn":"达美泰滋","series_name":"Elite Whey 精英乳清","category":"乳清蛋白粉",
     "subcategory":"浓缩乳清","description":"性价比款，适合日常蛋白补充",
     "key_features":["每勺25g蛋白","BCAA 5.5g","含消化酶"],
     "certifications":[],
     "ref_price_min":280,"ref_price_max":480,
     "sizes":["2lb","5lb"],
     "flavors":["巧克力软糖","草莓奶昔","香草","花生酱奶油"],
     "science_rating":4,"target_users":["增肌","健康维持"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约35g)"},

    # ========== MyProtein 熊猫蛋白 ==========
    {"brand_cn":"熊猫蛋白","series_name":"Impact 乳清蛋白","category":"乳清蛋白粉",
     "subcategory":"浓缩乳清","description":"欧洲销量第一的蛋白粉，性价比之王，口味数量惊人",
     "key_features":["每勺21g蛋白","BCAA 4.5g","60+口味可选","Informed-Sport认证"],
     "certifications":["Informed-Sport"],
     "ref_price_min":180,"ref_price_max":520,
     "sizes":["250g","1kg","2.5kg","5kg"],
     "flavors":["天然巧克力","咸味焦糖","北海道牛奶","抹茶拿铁","蓝莓松饼","花生酱杯","摩卡","香草","草莓奶油","曲奇奶油","奇异果","树莓白巧","泰式奶茶"],
     "science_rating":4,"target_users":["增肌","减脂","健康维持","学生党"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约25g)"},

    {"brand_cn":"熊猫蛋白","series_name":"Impact 分离乳清","category":"分离乳清蛋白",
     "subcategory":"分离蛋白","description":"高蛋白低脂版本，适合控糖控脂",
     "key_features":["蛋白含量>90%","低脂低糖","Informed-Sport"],
     "certifications":["Informed-Sport"],
     "ref_price_min":280,"ref_price_max":680,
     "sizes":["1kg","2.5kg","5kg"],
     "flavors":["天然巧克力","香草","草莓奶油","咸味焦糖","抹茶"],
     "science_rating":4,"target_users":["减脂","乳糖不耐"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约25g)"},

    {"brand_cn":"熊猫蛋白","series_name":"肌酸 一水合物","category":"肌酸",
     "subcategory":"一水肌酸","description":"性价比肌酸首选",
     "key_features":["100%一水肌酸","无添加剂","Informed-Sport"],
     "certifications":["Informed-Sport"],
     "ref_price_min":80,"ref_price_max":220,
     "sizes":["250g","500g","1kg"],
     "flavors":["原味无味"],
     "science_rating":5,"target_users":["增肌","运动表现"],
     "usage_timing":"训练后/随餐","dosage":"每日3-5g"},

    # ========== 肌肉科技 MuscleTech ==========
    {"brand_cn":"肌肉科技","series_name":"白金系列 100% Whey","category":"乳清蛋白粉",
     "subcategory":"浓缩+分离","description":"经典白金乳清，包装颜值高",
     "key_features":["每勺24g蛋白","含5.5g BCAA","低糖配方"],
     "certifications":[],
     "ref_price_min":320,"ref_price_max":580,
     "sizes":["2lb","5lb"],
     "flavors":["奶油巧克力","曲奇奶油","香草","草莓"],
     "science_rating":4,"target_users":["增肌","健康维持"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约30g)"},

    {"brand_cn":"肌肉科技","series_name":"NITRO-TECH 增肌粉","category":"增肌粉",
     "subcategory":"高蛋白增肌","description":"高蛋白增肌专用，含肌酸和氨基酸",
     "key_features":["每勺30g蛋白","内含3g肌酸","6.6g BCAA"],
     "certifications":[],
     "ref_price_min":420,"ref_price_max":680,
     "sizes":["4lb","10lb"],
     "flavors":["奶油巧克力","曲奇奶油","香草","草莓","花生酱"],
     "science_rating":3,"target_users":["增肌","瘦体型增重"],
     "usage_timing":"训练后/早晨","dosage":"每次1-2勺"},

    # ========== BSN ==========
    {"brand_cn":"BSN","series_name":"Syntha-6 多元蛋白","category":"乳清蛋白粉",
     "subcategory":"多元蛋白(乳清+酪蛋白)","description":"乳清+酪蛋白混合，吸收速率分阶段，口味是行业公认顶级",
     "key_features":["每勺22g蛋白","6种蛋白来源","含消化酶","以口味闻名"],
     "certifications":[],
     "ref_price_min":350,"ref_price_max":580,
     "sizes":["2.91lb","5lb"],
     "flavors":["奶油巧克力松饼","草莓奶昔","曲奇奶油","花生酱巧克力","香草冰激凌","巧克力薄荷"],
     "science_rating":4,"target_users":["增肌","健康维持","在意口味的人"],
     "usage_timing":"训练后/餐间/睡前","dosage":"每次1勺(约47g)"},

    # ========== Cellucor ==========
    {"brand_cn":"Cellucor","series_name":"COR-Performance 乳清","category":"乳清蛋白粉",
     "subcategory":"浓缩+分离","description":"高蛋白低糖低脂，溶解度好",
     "key_features":["每勺25g蛋白","低糖低脂","快速溶解"],
     "certifications":[],
     "ref_price_min":350,"ref_price_max":520,
     "sizes":["2lb","4lb"],
     "flavors":["奶油花生酱","乳脂软糖","曲奇奶油","金色奶油焦糖","白巧覆盆子"],
     "science_rating":4,"target_users":["增肌","减脂"],
     "usage_timing":"训练后","dosage":"每次1勺(约33g)"},

    # ========== ALLMAX ==========
    {"brand_cn":"ALLMAX","series_name":"AllWhey Gold","category":"乳清蛋白粉",
     "subcategory":"浓缩乳清","description":"性价比国际款",
     "key_features":["每勺24g蛋白","BCAA 5.4g","无添加色素"],
     "certifications":[],
     "ref_price_min":260,"ref_price_max":420,
     "sizes":["2lb","5lb"],
     "flavors":["巧克力","香草","曲奇奶油","法式香草","咸味焦糖"],
     "science_rating":4,"target_users":["增肌","健康维持"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约30g)"},

    {"brand_cn":"ALLMAX","series_name":"肌酸 Creatine","category":"肌酸",
     "subcategory":"一水肌酸","description":"经典一水肌酸，纯度高",
     "key_features":["100%一水肌酸","无添加剂","药品级纯度"],
     "certifications":[],
     "ref_price_min":120,"ref_price_max":200,
     "sizes":["400g","1000g"],
     "flavors":["原味无味"],
     "science_rating":5,"target_users":["增肌","运动表现"],
     "usage_timing":"训练后","dosage":"每日3-5g"},

    # ========== GAT ==========
    {"brand_cn":"GAT","series_name":"Nitraflex 预锻炼","category":"氮泵",
     "subcategory":"高刺激预锻炼","description":"业内知名预锻炼，刺激感强，泵感和能量兼具",
     "key_features":["含咖啡因+柠檬酸西地那非合成物","含BCAA","泵感配方"],
     "certifications":[],
     "ref_price_min":280,"ref_price_max":450,
     "sizes":["30份","45份"],
     "flavors":["红西柚","蓝树莓","菠萝","水果潘趣","西瓜"],
     "science_rating":4,"target_users":["运动表现","老手玩家"],
     "usage_timing":"训练前30分钟","dosage":"每次1勺",
     "cautions":"咖啡因含量高，下午晚上避免使用，新手慎用"},

    # ========== 康比特 CPT ==========
    {"brand_cn":"康比特","series_name":"乳清蛋白粉","category":"乳清蛋白粉",
     "subcategory":"浓缩乳清","description":"国产老牌，适合入门人群",
     "key_features":["每份蛋白20g+","符合国家运动营养标准","性价比"],
     "certifications":["国食健注"],
     "ref_price_min":180,"ref_price_max":380,
     "sizes":["908g","2270g"],
     "flavors":["香草","巧克力","草莓"],
     "science_rating":3,"target_users":["健康维持","入门人群","学生党"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约30g)"},

    {"brand_cn":"康比特","series_name":"肌酸单水合物","category":"肌酸",
     "subcategory":"一水肌酸","description":"国产肌酸性价比之选",
     "key_features":["一水肌酸","无添加剂"],
     "certifications":[],
     "ref_price_min":80,"ref_price_max":180,
     "sizes":["300g","500g"],
     "flavors":["原味无味"],
     "science_rating":4,"target_users":["增肌","运动表现"],
     "usage_timing":"训练后","dosage":"每日3-5g"},

    # ========== 诺特兰德 ==========
    {"brand_cn":"诺特兰德","series_name":"分离乳清蛋白粉","category":"分离乳清蛋白",
     "subcategory":"分离蛋白","description":"抖音爆款，性价比突出，包装年轻化",
     "key_features":["蛋白含量>85%","低脂低糖","主打性价比"],
     "certifications":[],
     "ref_price_min":120,"ref_price_max":280,
     "sizes":["454g","907g"],
     "flavors":["香草","巧克力","抹茶","草莓"],
     "science_rating":3,"target_users":["健康维持","学生党","入门"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约25g)"},

    {"brand_cn":"诺特兰德","series_name":"复合维生素片","category":"复合维生素",
     "subcategory":"全面营养","description":"性价比国产复合维生素，覆盖多种营养素",
     "key_features":["含11种维生素+矿物质","每日1片"],
     "certifications":[],
     "ref_price_min":40,"ref_price_max":120,
     "sizes":["60片","120片"],
     "flavors":[],
     "science_rating":3,"target_users":["健康维持","上班族"],
     "usage_timing":"早餐后","dosage":"每日1片"},

    {"brand_cn":"诺特兰德","series_name":"鱼油软胶囊 Omega-3","category":"鱼油Omega-3",
     "subcategory":"深海鱼油","description":"国产性价比鱼油",
     "key_features":["EPA+DHA","深海鱼提取"],
     "certifications":[],
     "ref_price_min":40,"ref_price_max":120,
     "sizes":["100粒","200粒"],
     "flavors":[],
     "science_rating":3,"target_users":["健康维持","关节不适","中老年"],
     "usage_timing":"随餐","dosage":"每日1-3粒"},

    # ========== 汤臣倍健 ==========
    {"brand_cn":"汤臣倍健","series_name":"蛋白粉","category":"乳清蛋白粉",
     "subcategory":"复合蛋白","description":"国内大众蛋白粉品牌，适合非运动人群基础补充",
     "key_features":["乳清+大豆蛋白","符合国家保健食品标准"],
     "certifications":["国食健字"],
     "ref_price_min":280,"ref_price_max":580,
     "sizes":["450g","900g"],
     "flavors":["原味"],
     "science_rating":3,"target_users":["健康维持","中老年","术后恢复"],
     "usage_timing":"早晚","dosage":"每次1勺(约10g)"},

    {"brand_cn":"汤臣倍健","series_name":"多种维生素片","category":"复合维生素",
     "subcategory":"基础营养","description":"国内复合维生素经典款",
     "key_features":["含16种维生素和矿物质","男女款分别"],
     "certifications":["国食健字"],
     "ref_price_min":120,"ref_price_max":280,
     "sizes":["60片","120片"],
     "flavors":[],
     "science_rating":4,"target_users":["健康维持","上班族","中老年"],
     "usage_timing":"早餐后","dosage":"每日1片"},

    {"brand_cn":"汤臣倍健","series_name":"深海鱼油","category":"鱼油Omega-3",
     "subcategory":"深海鱼油","description":"国产鱼油大众款",
     "key_features":["EPA+DHA","深海原料"],
     "certifications":["国食健字"],
     "ref_price_min":80,"ref_price_max":180,
     "sizes":["100粒","200粒"],
     "flavors":[],
     "science_rating":3,"target_users":["健康维持","中老年"],
     "usage_timing":"随餐","dosage":"每日1-2粒"},

    # ========== Wonderlab ==========
    {"brand_cn":"Wonderlab","series_name":"代餐奶昔","category":"代餐",
     "subcategory":"小胖瓶代餐","description":"国内代餐奶昔流行款，包装时尚",
     "key_features":["每瓶约200kcal","含蛋白和膳食纤维","便携小瓶装"],
     "certifications":[],
     "ref_price_min":180,"ref_price_max":380,
     "sizes":["6瓶装","12瓶装"],
     "flavors":["生椰拿铁","海盐焦糖","抹茶","巧克力","厚乳","白桃乌龙"],
     "science_rating":3,"target_users":["减脂","上班族","学生党"],
     "usage_timing":"早餐/午餐替代","dosage":"每次1瓶"},

    # ========== Swisse ==========
    {"brand_cn":"Swisse","series_name":"复合维生素 男士/女士","category":"复合维生素",
     "subcategory":"分性别配方","description":"澳洲健康营养品代表，男女款分别",
     "key_features":["50种营养素","分性别配方","TGA认证"],
     "certifications":["澳洲TGA"],
     "ref_price_min":180,"ref_price_max":380,
     "sizes":["60片","120片"],
     "flavors":[],
     "science_rating":4,"target_users":["健康维持","上班族"],
     "usage_timing":"早餐后","dosage":"每日1片"},

    {"brand_cn":"Swisse","series_name":"深海鱼油 Omega-3","category":"鱼油Omega-3",
     "subcategory":"高浓度鱼油","description":"澳洲鱼油，EPA+DHA含量高",
     "key_features":["1500mg鱼油","含EPA+DHA","TGA认证"],
     "certifications":["澳洲TGA"],
     "ref_price_min":150,"ref_price_max":320,
     "sizes":["200粒","400粒"],
     "flavors":[],
     "science_rating":4,"target_users":["健康维持","关节不适","中老年"],
     "usage_timing":"随餐","dosage":"每日1-2粒"},

    {"brand_cn":"Swisse","series_name":"维生素D3","category":"维生素D3",
     "subcategory":"高剂量D3","description":"澳洲维生素D3",
     "key_features":["1000IU/粒","TGA认证","脂溶性"],
     "certifications":["澳洲TGA"],
     "ref_price_min":80,"ref_price_max":180,
     "sizes":["250粒","400粒"],
     "flavors":[],
     "science_rating":5,"target_users":["健康维持","室内工作者"],
     "usage_timing":"随餐","dosage":"每日1粒"},

    # ========== GNC ==========
    {"brand_cn":"GNC","series_name":"AMP 黄金分离乳清","category":"分离乳清蛋白",
     "subcategory":"分离蛋白","description":"GNC高端运动营养线",
     "key_features":["每勺25g蛋白","低糖低脂"],
     "certifications":[],
     "ref_price_min":450,"ref_price_max":780,
     "sizes":["1.6lb","4.7lb"],
     "flavors":["巧克力","香草","曲奇奶油"],
     "science_rating":4,"target_users":["增肌","减脂"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约30g)"},

    {"brand_cn":"GNC","series_name":"男士铂金多维","category":"复合维生素",
     "subcategory":"男士专用","description":"GNC经典男士复合维生素",
     "key_features":["含锌+镁+B族","男士专用配方"],
     "certifications":[],
     "ref_price_min":280,"ref_price_max":480,
     "sizes":["90片","180片"],
     "flavors":[],
     "science_rating":4,"target_users":["健康维持","男性","健身人群"],
     "usage_timing":"早餐后","dosage":"每日2片"},

    # ========== Nature Made ==========
    {"brand_cn":"Nature Made","series_name":"维生素D3 2000IU","category":"维生素D3",
     "subcategory":"高剂量D3","description":"美国USP认证维生素D3",
     "key_features":["2000IU/粒","USP认证","剂量精准"],
     "certifications":["USP"],
     "ref_price_min":80,"ref_price_max":180,
     "sizes":["100粒","220粒"],
     "flavors":[],
     "science_rating":5,"target_users":["健康维持","室内工作者"],
     "usage_timing":"随餐","dosage":"每日1粒"},

    {"brand_cn":"Nature Made","series_name":"鱼油 1200mg","category":"鱼油Omega-3",
     "subcategory":"鱼油","description":"美国USP鱼油",
     "key_features":["1200mg鱼油","EPA+DHA","USP认证"],
     "certifications":["USP"],
     "ref_price_min":120,"ref_price_max":250,
     "sizes":["100粒","200粒"],
     "flavors":[],
     "science_rating":5,"target_users":["健康维持","关节不适"],
     "usage_timing":"随餐","dosage":"每日1-2粒"},

    # ========== Blackmores ==========
    {"brand_cn":"Blackmores","series_name":"深海鱼油","category":"鱼油Omega-3",
     "subcategory":"深海鱼油","description":"澳洲鱼油老牌",
     "key_features":["1000mg鱼油","低气味","TGA认证"],
     "certifications":["澳洲TGA"],
     "ref_price_min":120,"ref_price_max":280,
     "sizes":["200粒","400粒"],
     "flavors":[],
     "science_rating":4,"target_users":["健康维持","中老年"],
     "usage_timing":"随餐","dosage":"每日1-2粒"},

    # ========== C4 ==========
    {"brand_cn":"C4","series_name":"C4 Original 原味预锻炼","category":"氮泵",
     "subcategory":"经典预锻炼","description":"全球预锻炼销量爆款，新手友好",
     "key_features":["含咖啡因150mg","含β-丙氨酸","含肌酸"],
     "certifications":[],
     "ref_price_min":180,"ref_price_max":380,
     "sizes":["30份","60份"],
     "flavors":["水果潘趣","蓝树莓","西瓜","樱桃柠檬水","橙汁","冰冻草莓"],
     "science_rating":4,"target_users":["运动表现","新手玩家"],
     "usage_timing":"训练前20-30分钟","dosage":"每次1勺",
     "cautions":"含咖啡因，下午晚上避免使用"},

    {"brand_cn":"C4","series_name":"C4 Ultimate 至尊预锻炼","category":"氮泵",
     "subcategory":"高刺激预锻炼","description":"C4高级版，刺激感更强",
     "key_features":["咖啡因300mg","泵感配方","含瓜氨酸"],
     "certifications":[],
     "ref_price_min":320,"ref_price_max":520,
     "sizes":["20份","40份"],
     "flavors":["冰冻树莓","橙子芒果","西瓜糖","蓝椰子覆盆子","酸樱桃"],
     "science_rating":4,"target_users":["运动表现","老手玩家"],
     "usage_timing":"训练前30分钟","dosage":"每次1勺",
     "cautions":"咖啡因含量高，新手减半使用"},

    # ========== GHOST ==========
    {"brand_cn":"GHOST","series_name":"GHOST Whey 乳清","category":"乳清蛋白粉",
     "subcategory":"高端浓缩+分离","description":"高端蛋白粉，与糖果品牌联名口味出名",
     "key_features":["每勺25g蛋白","联名口味","低糖"],
     "certifications":[],
     "ref_price_min":480,"ref_price_max":720,
     "sizes":["2lb"],
     "flavors":["奇巧曲奇","奇巧威化","奥利奥曲奇","花生酱奇巧","软糖蠕虫","樱桃饮料"],
     "science_rating":4,"target_users":["增肌","口味爱好者"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约35g)"},

    {"brand_cn":"GHOST","series_name":"GHOST Legend 预锻炼","category":"氮泵",
     "subcategory":"高端预锻炼","description":"高端预锻炼，配方透明，口味创新",
     "key_features":["瓜氨酸4g","β-丙氨酸3.2g","咖啡因202mg","配方透明"],
     "certifications":[],
     "ref_price_min":380,"ref_price_max":580,
     "sizes":["25份","40份"],
     "flavors":["酸糖","汽水","蓝色覆盆子","沃尔玛草莓汽水","桃子柠檬水"],
     "science_rating":4,"target_users":["运动表现","老手玩家"],
     "usage_timing":"训练前30分钟","dosage":"每次1勺"},

    # ========== Garden of Life ==========
    {"brand_cn":"Garden of Life","series_name":"Sport 有机植物蛋白","category":"植物蛋白粉",
     "subcategory":"多源植物蛋白","description":"有机认证植物蛋白，适合素食者",
     "key_features":["豌豆+糙米+大麻蛋白","NSF认证","非转基因","素食"],
     "certifications":["NSF Certified for Sport","USDA Organic","非转基因"],
     "ref_price_min":380,"ref_price_max":620,
     "sizes":["1.5lb","2.5lb"],
     "flavors":["巧克力","香草","原味"],
     "science_rating":4,"target_users":["素食者","乳糖不耐","健康维持"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约35g)"},

    # ========== Vega ==========
    {"brand_cn":"Vega","series_name":"Sport 高级植物蛋白","category":"植物蛋白粉",
     "subcategory":"多源植物蛋白","description":"专业植物蛋白品牌，NSF认证",
     "key_features":["每勺30g蛋白","豌豆+葵花籽+南瓜籽","NSF认证","素食"],
     "certifications":["NSF Certified for Sport","非转基因"],
     "ref_price_min":380,"ref_price_max":680,
     "sizes":["1.6lb","4.2lb"],
     "flavors":["巧克力","香草","莓果","花生酱","抹茶"],
     "science_rating":4,"target_users":["素食者","乳糖不耐"],
     "usage_timing":"训练后/餐间","dosage":"每次1勺(约44g)"},

    # ========== 氧气能量 O2 Energy（中国本地化）==========
    {"brand_cn":"氧气能量","series_name":"氧气能量 EGCG 绿茶提取物","category":"燃脂补剂",
     "subcategory":"绿茶提取物","description":"EGCG 是绿茶中的多酚活性成分，研究显示可适度提高代谢，减脂期辅助",
     "key_features":["每粒 EGCG 200mg","低咖啡因","素食胶囊"],
     "certifications":["第三方检测"],
     "ref_price_min":59,"ref_price_max":89,
     "sizes":["60粒","120粒"],
     "flavors":[],
     "science_rating":3,"target_users":["减脂期","咖啡因敏感者"],
     "usage_timing":"早餐前/训练前","dosage":"每天1-2粒"},
    {"brand_cn":"氧气能量","series_name":"氧气能量 β-丙氨酸","category":"β-丙氨酸",
     "subcategory":"纯粉",
     "description":"提升肌肉肌肽水平，延缓乳酸堆积，对高强度训练（8-20次范围）效果明显",
     "key_features":["每勺 3.2g β-丙氨酸","纯度 ≥99%","可与肌酸同服"],
     "certifications":["第三方纯度检测"],
     "ref_price_min":89,"ref_price_max":129,
     "sizes":["200g","400g"],
     "flavors":["原味","西瓜","蓝莓"],
     "science_rating":4,"target_users":["力量举","HIIT训练者"],
     "usage_timing":"训练前 30 分钟","dosage":"每次 3-5g，每日 1-2 次"},
    {"brand_cn":"氧气能量","series_name":"氧气能量 L-精氨酸","category":"瓜氨酸",
     "subcategory":"精氨酸/瓜氨酸",
     "description":"一氧化氮前体，提升训练泵感和血流。瓜氨酸-苹果酸吸收更佳",
     "key_features":["每勺 6g L-精氨酸","可与氮泵搭配","无刺激"],
     "certifications":["第三方检测"],
     "ref_price_min":99,"ref_price_max":149,
     "sizes":["300g"],
     "flavors":["原味","柠檬"],
     "science_rating":3,"target_users":["健美爱好者","追求泵感"],
     "usage_timing":"训练前 30 分钟","dosage":"每次 6g"},

    # ========== 康比特（新增中国本地化）==========
    {"brand_cn":"康比特","series_name":"康比特 复合维生素B族","category":"维生素B族",
     "subcategory":"B 族复合",
     "description":"B族8种维生素+生物素，运动人群和疲劳人群补充能量代谢",
     "key_features":["B1/B2/B6/B12齐全","每天1片","素食胶囊"],
     "certifications":["国食健字"],
     "ref_price_min":59,"ref_price_max":89,
     "sizes":["60片","120片"],
     "flavors":[],
     "science_rating":4,"target_users":["训练人群","上班族"],
     "usage_timing":"早餐后","dosage":"每天1片"},

    # ========== 诺特兰德（新增本地化产品）==========
    {"brand_cn":"诺特兰德","series_name":"诺特兰德 电解质水冲剂","category":"电解质",
     "subcategory":"运动电解质",
     "description":"训练中/出汗多时快速补充电解质，避免抽筋和脱水，无糖低卡",
     "key_features":["钠 280mg/钾 150mg/镁 50mg","无糖","便携包"],
     "certifications":["第三方检测"],
     "ref_price_min":49,"ref_price_max":99,
     "sizes":["30条","60条"],
     "flavors":["青柠","西瓜","蜜桃","葡萄"],
     "science_rating":4,"target_users":["训练人群","耐力运动","炎热环境"],
     "usage_timing":"训练中/训练后","dosage":"每次1条溶于水"},
    {"brand_cn":"诺特兰德","series_name":"诺特兰德 维生素B族片","category":"维生素B族",
     "subcategory":"B族复合",
     "description":"性价比 B 族片，每天1片，长期补充辅助能量代谢",
     "key_features":["8种B族","每天1片","抖音爆款"],
     "certifications":["国食健字"],
     "ref_price_min":29,"ref_price_max":59,
     "sizes":["100片","200片"],
     "flavors":[],
     "science_rating":3,"target_users":["新手","学生党"],
     "usage_timing":"早餐后","dosage":"每天1片"},

    # ========== 汤臣倍健（新增本地化产品）==========
    {"brand_cn":"汤臣倍健","series_name":"汤臣倍健 健力多氨糖软骨素","category":"关节保护",
     "subcategory":"氨糖软骨素",
     "description":"高含量氨糖软骨素，长期保护关节，运动人群和中老年常用",
     "key_features":["氨糖 750mg/天","加 Vit D","骨健康"],
     "certifications":["国食健字","蓝帽子"],
     "ref_price_min":120,"ref_price_max":280,
     "sizes":["90片","180片"],
     "flavors":[],
     "science_rating":3,"target_users":["大重量训练人群","关节不适"],
     "usage_timing":"餐后","dosage":"每天3片"},
    {"brand_cn":"汤臣倍健","series_name":"汤臣倍健 蛋白质粉","category":"乳清蛋白粉",
     "subcategory":"乳清+大豆",
     "description":"乳清+大豆蛋白复合，国民补剂，超市/药店都有",
     "key_features":["乳清+大豆混合","低糖","儿童老人皆可"],
     "certifications":["国食健字"],
     "ref_price_min":280,"ref_price_max":450,
     "sizes":["450g","600g","900g"],
     "flavors":["原味"],
     "science_rating":3,"target_users":["大众","新手","非力量训练人群"],
     "usage_timing":"早餐/训练后","dosage":"每次1勺(10g)"},

    # ========== Wonderlab（新增本地化产品）==========
    {"brand_cn":"Wonderlab","series_name":"Wonderlab 益生菌瓶","category":"代餐",
     "subcategory":"益生菌冰淇淋瓶","description":"代餐+肠道健康，包装小巧颜值高",
     "key_features":["20亿益生菌","低糖","便携小瓶"],
     "certifications":["第三方检测"],
     "ref_price_min":89,"ref_price_max":159,
     "sizes":["7瓶装","30瓶装"],
     "flavors":["原味","莓果","巧克力"],
     "science_rating":3,"target_users":["女性","减脂期","减糖"],
     "usage_timing":"早餐/餐间","dosage":"每天1-2瓶"},

    # ========== 修正（新增本地化产品）==========
    {"brand_cn":"修正","series_name":"修正 维生素D3","category":"维生素D3",
     "subcategory":"D3 软胶囊",
     "description":"性价比 D3 软胶囊，每粒 1000IU，国产药企品质",
     "key_features":["每粒 1000IU","软胶囊吸收好","药企品质"],
     "certifications":["国食健字"],
     "ref_price_min":29,"ref_price_max":59,
     "sizes":["60粒","100粒"],
     "flavors":[],
     "science_rating":4,"target_users":["大众","骨健康","睾酮补充"],
     "usage_timing":"早餐后","dosage":"每天1粒"},
    {"brand_cn":"修正","series_name":"修正 鱼油软胶囊","category":"鱼油Omega-3",
     "subcategory":"深海鱼油",
     "description":"鱼油性价比之选，EPA+DHA 含量合规，药店常见",
     "key_features":["EPA 180mg+DHA 120mg","深海鱼油","软胶囊"],
     "certifications":["国食健字"],
     "ref_price_min":49,"ref_price_max":99,
     "sizes":["100粒","200粒"],
     "flavors":[],
     "science_rating":4,"target_users":["大众","训练人群"],
     "usage_timing":"餐后","dosage":"每天1-2粒"},

    # ========== FANCL（新增本地化产品）==========
    {"brand_cn":"FANCL","series_name":"FANCL 综合维生素 30+","category":"复合维生素",
     "subcategory":"女性向多维",
     "description":"日本无添加品牌，胶囊小、女性常用",
     "key_features":["小颗粒易吞服","针对女性配比","30天分装"],
     "certifications":["日本厚生劳动省"],
     "ref_price_min":280,"ref_price_max":380,
     "sizes":["30袋"],
     "flavors":[],
     "science_rating":4,"target_users":["女性","上班族"],
     "usage_timing":"早餐后","dosage":"每天1袋"},
]


def seed_data():
    init_db()
    conn = get_conn()
    c = conn.cursor()

    # 检查是否已经初始化过
    c.execute("SELECT COUNT(*) FROM supp_brand")
    if c.fetchone()[0] > 0:
        print("⚠ 品牌数据已存在，跳过初始化（如需重新初始化请先删除 fitness_data.db）")
        conn.close()
        return

    conn.close()

    # 插入品牌
    brand_name_to_id = {}
    for b in BRANDS:
        bid = add_brand(b)
        brand_name_to_id[b["name_cn"]] = bid
        print(f"✓ 品牌：{b['name_cn']} ({b['name_en']})")

    # 插入产品
    count = 0
    for p in PRODUCTS:
        brand_id = brand_name_to_id.get(p["brand_cn"])
        if not brand_id:
            print(f"⚠ 找不到品牌：{p['brand_cn']}")
            continue
        product_data = {k: v for k, v in p.items() if k != "brand_cn"}
        product_data["brand_id"] = brand_id
        product_data["verified"] = 1
        add_product(product_data)
        count += 1
        print(f"  - {p['brand_cn']} / {p['series_name']}")

    print(f"\n✅ 完成：{len(BRANDS)} 个品牌，{count} 个产品已录入")


if __name__ == "__main__":
    seed_data()
