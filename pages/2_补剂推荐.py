import streamlit as st
import sys, os
from datetime import datetime, date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import (
    load_profile, save_chat, load_chat, clear_chat,
    get_all_brands, get_brand, add_brand,
    get_products_by_category, get_product, add_product,
    get_all_categories, get_pending_products, verify_product,
    add_rating, get_product_ratings, get_product_score_summary, like_rating
)
from ai_engine import chat_with_ollama, check_ollama_status
from supplement_data import (
    CATEGORY_CONFIG, get_categories, get_category_info,
    get_dimensions, get_goal_stack
)

st.set_page_config(page_title="补剂推荐", page_icon="💊", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@700&family=Noto+Sans+SC:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Noto Sans SC',sans-serif;}
input,textarea{color:#e8eaf0 !important;caret-color:#00f5a0 !important;}
label,.stTextInput label,.stSelectbox label,.stTextArea label,.stSlider label,.stRadio label,.stNumberInput label{color:#c8d8e8 !important;font-size:14px !important;}
[data-baseweb="menu"] li{color:#e8eaf0 !important;}
.stTabs [data-baseweb="tab"]{color:#8ca0b8 !important;}
.stTabs [aria-selected="true"]{color:#00f5a0 !important;border-bottom:2px solid #00f5a0 !important;}
.page-title{font-family:'Rajdhani',sans-serif;font-size:40px;font-weight:700;background:linear-gradient(90deg,#00f5a0,#00d9f5);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.brand-card{background:#1a2235;border:1px solid #2a3a55;border-radius:14px;padding:18px;margin-bottom:14px;transition:border-color 0.2s;}
.brand-card:hover{border-color:#00f5a0;}
.brand-name{font-size:20px;font-weight:700;color:#00f5a0;margin-bottom:4px;}
.brand-tier{display:inline-block;font-size:11px;color:#00f5a0;background:rgba(0,245,160,0.1);border:1px solid rgba(0,245,160,0.25);padding:2px 8px;border-radius:10px;margin-right:6px;letter-spacing:1px;}
.product-card{background:#1a2235;border:1px solid #2a3a55;border-radius:14px;padding:18px;margin-bottom:14px;}
.product-title{font-size:17px;color:#e8eaf0;font-weight:600;margin-bottom:4px;}
.product-brand{font-size:12px;color:#8ca0b8;margin-bottom:8px;}
.price-tag{display:inline-block;color:#ffaa3c;font-weight:700;font-size:15px;background:rgba(255,170,60,0.08);border:1px solid rgba(255,170,60,0.25);padding:3px 10px;border-radius:6px;}
.flavor-tag{display:inline-block;background:#2a3a55;border:1px solid #3a4a65;border-radius:14px;padding:2px 10px;font-size:12px;color:#c8d8e8;margin:2px;}
.score-bar{height:6px;background:#2a3a55;border-radius:3px;overflow:hidden;margin-top:4px;}
.score-fill{height:100%;background:linear-gradient(90deg,#00f5a0,#00d9f5);}
.score-row{display:flex;justify-content:space-between;font-size:13px;color:#c8d8e8;margin-bottom:6px;}
.review-card{background:#162032;border:1px solid #2a3a55;border-radius:10px;padding:12px 16px;margin:8px 0;font-size:13px;color:#e8eaf0;}
.review-user{font-size:12px;color:#00f5a0;font-weight:600;}
.review-meta{font-size:11px;color:#4a6080;}
.chat-user{background:#1e2d42;border:1px solid #2a3a55;border-radius:12px;padding:12px 16px;margin:8px 0;color:#e8eaf0;font-size:14px;}
.chat-ai{background:#162032;border:1px solid #1a3040;border-radius:12px;padding:14px 18px;margin:8px 0;color:#e8eaf0;font-size:14px;line-height:1.9;}
.stButton>button{background:linear-gradient(90deg,#00f5a0,#00d9f5);color:#0a1628 !important;font-weight:700;border:none;border-radius:8px;font-family:'Rajdhani',sans-serif;font-size:15px;width:100%;}
.cert-badge{display:inline-block;background:rgba(0,217,245,0.1);border:1px solid rgba(0,217,245,0.3);color:#00d9f5;font-size:11px;padding:2px 8px;border-radius:4px;margin:2px;}
.unverified-tag{background:rgba(255,170,60,0.1);border:1px solid rgba(255,170,60,0.3);color:#ffaa3c;font-size:11px;padding:2px 8px;border-radius:4px;}
hr{border-color:#2a3a55;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">💊 补剂中心</div>', unsafe_allow_html=True)
st.markdown('<p style="color:#8ca0b8;font-size:14px;">覆盖20+主流品牌 · 五维社区评分 · AI个性化推荐</p>', unsafe_allow_html=True)

profile = load_profile()
ollama_ok = check_ollama_status()
MODULE = "supplement"

if "supplement_messages" not in st.session_state:
    st.session_state.supplement_messages = load_chat(MODULE)

# 处理待办AI请求
if st.session_state.get("supp_pending") and ollama_ok:
    pending_q = st.session_state.pop("supp_pending")
    st.session_state.supplement_messages.append({"role":"user","content":pending_q})
    save_chat(MODULE,"user",pending_q)
    with st.spinner("AI营养师思考中..."):
        reply = chat_with_ollama(st.session_state.supplement_messages, MODULE, profile)
    st.session_state.supplement_messages.append({"role":"assistant","content":reply})
    save_chat(MODULE,"assistant",reply)
    st.rerun()

tabs = st.tabs([
    "🎯 个性化推荐",
    "🏷 品牌库",
    "📦 产品库",
    "⭐ 我要打分",
    "➕ 提交新产品",
    "🤖 AI营养师"
])

# ============ Tab 1: 个性化推荐 ============
with tabs[0]:
    if not profile:
        st.warning("⚠️ 请先在「用户档案」填写个人信息以获取个性化推荐")
    else:
        goal = profile.get("goal","健康维持")
        stack = get_goal_stack(goal)
        st.markdown(f'<div style="background:#1a2235;border:1px solid #2a3a55;border-radius:12px;padding:16px 24px;margin-bottom:24px;"><span style="color:#8ca0b8;font-size:13px;">基于目标：</span><span style="font-family:Rajdhani,sans-serif;font-size:18px;color:#00f5a0;font-weight:700;margin:0 12px;">{goal}</span><span style="color:#8ca0b8;font-size:13px;">{stack["description"]}</span></div>', unsafe_allow_html=True)

        st.markdown('<p style="font-weight:700;color:#e8eaf0;font-size:16px;">🎯 推荐核心品类</p>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, cat in enumerate(stack["core_categories"]):
            info = get_category_info(cat)
            with cols[i % 3]:
                products = get_products_by_category(category=cat)
                top_p = products[:3]
                items_html = "".join([
                    f'<div style="font-size:13px;color:#c8d8e8;margin:4px 0;">• {p["brand_name"]} - {p["series_name"][:18]}</div>'
                    for p in top_p
                ])
                st.markdown(f"""
                <div class="brand-card">
                    <div style="font-size:32px;margin-bottom:6px;">{info.get("emoji","💊")}</div>
                    <div style="font-size:18px;color:#00f5a0;font-weight:700;">{cat}</div>
                    <div style="font-size:12px;color:#8ca0b8;margin-bottom:10px;">{info.get("description","")}</div>
                    <div style="color:#ffaa3c;font-size:12px;margin-bottom:6px;">热门产品：</div>
                    {items_html}
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<p style="font-weight:700;color:#e8eaf0;font-size:16px;margin-top:16px;">➕ 进阶可选品类</p>', unsafe_allow_html=True)
        acols = st.columns(3)
        for i, cat in enumerate(stack["advanced_categories"]):
            info = get_category_info(cat)
            with acols[i % 3]:
                st.markdown(f'<div class="brand-card" style="opacity:0.75"><div style="font-size:22px">{info.get("emoji","💊")}</div><div style="font-size:15px;color:#00f5a0;font-weight:700;">{cat}</div><div style="font-size:12px;color:#8ca0b8;margin-top:6px;">{info.get("description","")}</div></div>', unsafe_allow_html=True)

# ============ Tab 2: 品牌库 ============
with tabs[1]:
    # === 品牌详情子页 ===
    if st.session_state.get("brand_detail_id"):
        target_bid = st.session_state["brand_detail_id"]
        brand_info = get_brand(target_bid)

        if st.button("← 返回品牌列表", key="back_brand_list"):
            del st.session_state["brand_detail_id"]
            st.rerun()

        if not brand_info:
            st.error("品牌未找到")
        else:
            # === 品牌头部信息 ===
            head_cols = st.columns([1, 5])
            with head_cols[0]:
                st.markdown(
                    f'<div style="font-size:80px;text-align:center;">{brand_info.get("logo_emoji","🏷")}</div>',
                    unsafe_allow_html=True
                )
            with head_cols[1]:
                head_html = (
                    f'<div style="margin-top:10px;">'
                    f'<span style="color:#00f5a0;font-weight:700;font-size:24px;">{brand_info["name_cn"]}</span>'
                    f'<span style="color:#8ca0b8;font-size:14px;margin-left:8px;">{brand_info.get("name_en","")}</span>'
                    f'</div>'
                    f'<div style="margin-top:6px;">'
                    f'<span style="color:#8ca0b8;font-size:13px;">🌍 {brand_info.get("country","—")}</span>'
                    f'<span style="background:rgba(0,245,160,0.12);color:#00f5a0;padding:2px 10px;'
                    f'border-radius:10px;font-size:11px;margin-left:12px;border:1px solid rgba(0,245,160,0.3);">'
                    f'{brand_info.get("tier","—")}</span>'
                    f'</div>'
                    f'<div style="color:#c8d8e8;font-size:14px;margin-top:10px;line-height:1.7;">'
                    f'{brand_info.get("description","")}</div>'
                )
                st.markdown(head_html, unsafe_allow_html=True)

            st.markdown("---")

            # === 该品牌下所有产品 ===
            from database import get_conn as _gc
            _conn = _gc(); _c = _conn.cursor()
            _c.execute("SELECT * FROM supp_product WHERE brand_id=? ORDER BY category, series_name",
                       (target_bid,))
            _rows = _c.fetchall()
            _cols = [d[0] for d in _c.description]
            _conn.close()
            brand_products = []
            for _r in _rows:
                _p = dict(zip(_cols, _r))
                # 解析 JSON 字段
                import json as _json
                for _kk in ["sizes","flavors","key_features","certifications","target_users"]:
                    if _p.get(_kk):
                        try: _p[_kk] = _json.loads(_p[_kk]) if isinstance(_p[_kk], str) else _p[_kk]
                        except: _p[_kk] = []
                    else:
                        _p[_kk] = []
                brand_products.append(_p)

            st.markdown(
                f'<p style="color:#e8eaf0;font-weight:700;font-size:18px;">'
                f'📦 该品牌收录的产品（{len(brand_products)} 个）</p>',
                unsafe_allow_html=True
            )

            if not brand_products:
                st.info("该品牌暂无收录产品。你可以点「+ 提交新产品」帮忙补充。")
            else:
                # 按分类分组显示
                from supplement_data import get_category_info as _gci
                _by_cat = {}
                for _p in brand_products:
                    _by_cat.setdefault(_p["category"], []).append(_p)

                for _cat_name, _ps in _by_cat.items():
                    _ci = _gci(_cat_name)
                    st.markdown(
                        f'<p style="color:#00d9f5;font-weight:700;font-size:15px;margin-top:18px;">'
                        f'{_ci.get("emoji","💊")} {_cat_name}（{len(_ps)} 个）</p>',
                        unsafe_allow_html=True
                    )
                    for _p in _ps:
                        p_score = get_product_score_summary(_p["id"])
                        score_str = f"★ {p_score['overall']:.1f}" if p_score else "未评分"
                        score_color = "#ffaa3c" if p_score else "#4a6080"

                        prod_cols = st.columns([4, 1.2, 1])
                        with prod_cols[0]:
                            verified_html = "" if _p.get("verified") else '<span style="color:#ffaa3c;font-size:11px;margin-left:6px;">⚠ 待审核</span>'
                            prod_html = (
                                f'<div style="background:#1a2235;border:1px solid #2a3a55;border-radius:10px;'
                                f'padding:12px 18px;margin:6px 0;">'
                                f'<div><span style="color:#e8eaf0;font-weight:600;font-size:14px;">{_p["series_name"]}</span>{verified_html}</div>'
                                f'<div style="color:#ffaa3c;font-size:12px;margin-top:4px;">'
                                f'💰 ¥{int(_p.get("ref_price_min") or 0)} - {int(_p.get("ref_price_max") or 0)}</div>'
                                f'</div>'
                            )
                            st.markdown(prod_html, unsafe_allow_html=True)
                        with prod_cols[1]:
                            st.markdown(
                                f'<div style="text-align:right;padding-top:14px;color:{score_color};font-weight:700;">{score_str}</div>',
                                unsafe_allow_html=True
                            )
                        with prod_cols[2]:
                            if st.button("查看 →", key=f"brand_view_{_p['id']}", use_container_width=True):
                                st.session_state["supp_detail_pid"] = _p["id"]
                                # 切换到产品库 Tab（streamlit 没法直接切 tab，但用户能看到提示）
                                del st.session_state["brand_detail_id"]
                                st.rerun()
                st.markdown('<p style="color:#8ca0b8;font-size:12px;margin-top:14px;">'
                            '💡 点击「查看 →」会跳转到「产品库」Tab 显示产品详情</p>',
                            unsafe_allow_html=True)

    # === 品牌列表页 ===
    else:
        brands = get_all_brands()
        st.markdown(f'<p style="color:#c8d8e8;">共收录 <span style="color:#00f5a0;font-weight:700;">{len(brands)}</span> 个品牌 · 点击品牌可查看其全部产品</p>', unsafe_allow_html=True)

        tier_filter = st.selectbox("按等级筛选", ["全部", "国际顶级", "国际主流", "国产主流"], key="tier_f")

        filtered = [b for b in brands if tier_filter == "全部" or b["tier"] == tier_filter]

        cols = st.columns(3)
        for i, b in enumerate(filtered):
            with cols[i % 3]:
                # 统计该品牌的产品数
                from database import get_conn as _gc
                _conn = _gc(); _c = _conn.cursor()
                _c.execute("SELECT COUNT(*) FROM supp_product WHERE brand_id=?", (b["id"],))
                _pc = _c.fetchone()[0]
                _conn.close()

                brand_html = (
                    f'<div style="background:#1a2235;border:1px solid #2a3a55;border-radius:12px;'
                    f'padding:18px 20px;margin:6px 0;min-height:200px;">'
                    f'<div style="font-size:32px;margin-bottom:6px;">{b.get("logo_emoji","🏷")}</div>'
                    f'<div style="color:#00f5a0;font-weight:700;font-size:17px;">{b["name_cn"]}</div>'
                    f'<div style="font-size:12px;color:#8ca0b8;margin-bottom:8px;">{b.get("name_en","")} · {b["country"]}</div>'
                    f'<span style="background:rgba(0,245,160,0.12);color:#00f5a0;padding:2px 10px;'
                    f'border-radius:10px;font-size:11px;border:1px solid rgba(0,245,160,0.3);">'
                    f'{b["tier"]}</span>'
                    f'<div style="font-size:13px;color:#c8d8e8;margin-top:10px;line-height:1.6;min-height:42px;">'
                    f'{b.get("description","")}</div>'
                    f'<div style="color:#ffaa3c;font-size:12px;margin-top:8px;">📦 收录 {_pc} 个产品</div>'
                    f'</div>'
                )
                st.markdown(brand_html, unsafe_allow_html=True)
                if st.button(f"查看 {b['name_cn']} →", key=f"view_brand_{b['id']}", use_container_width=True):
                    st.session_state["brand_detail_id"] = b["id"]
                    st.rerun()

# ============ Tab 3: 产品库（虎扑风） ============
with tabs[2]:
    # 如果在详情页，渲染详情
    if st.session_state.get("supp_detail_pid"):
        target_pid = st.session_state["supp_detail_pid"]
        p = get_product(target_pid)
        if not p:
            st.error("产品不存在")
            if st.button("← 返回列表"):
                del st.session_state["supp_detail_pid"]
                st.rerun()
        else:
            if st.button("← 返回列表", key="supp_back"):
                del st.session_state["supp_detail_pid"]
                st.rerun()

            # === 详情页：顶部产品信息 ===
            cat_info = get_category_info(p["category"])
            head_cols = st.columns([1, 5])
            with head_cols[0]:
                st.markdown(
                    f'<div style="font-size:80px;text-align:center;">{cat_info.get("emoji","💊")}</div>',
                    unsafe_allow_html=True
                )
            with head_cols[1]:
                head_html = (
                    f'<div style="margin-top:8px;">'
                    f'<span style="color:#00f5a0;font-weight:700;font-size:22px;">{p["brand_emoji"]} {p["brand_name"]}</span>'
                    f'</div>'
                    f'<div style="color:#e8eaf0;font-size:18px;font-weight:600;margin-top:6px;">{p["series_name"]}</div>'
                    f'<div style="color:#ffaa3c;font-size:14px;margin-top:6px;font-weight:600;">'
                    f'💰 ¥{int(p.get("ref_price_min") or 0)} - {int(p.get("ref_price_max") or 0)}</div>'
                    f'<div style="color:#8ca0b8;font-size:12px;margin-top:2px;">{p["category"]}</div>'
                )
                st.markdown(head_html, unsafe_allow_html=True)

            st.markdown("---")

            # === 评分面板（虎扑风）===
            score_summary = get_product_score_summary(p["id"])
            score_cols = st.columns([1.5, 2.5])
            with score_cols[0]:
                if score_summary:
                    overall = score_summary["overall"]
                    full = int(overall / 2)  # 10分制转5星
                    stars_str = "★" * full + "☆" * (5 - full)
                    score_panel = (
                        f'<div style="background:linear-gradient(135deg,#1a2235,#1e2945);'
                        f'border:1px solid #2a3a55;border-radius:14px;padding:22px;">'
                        f'<div style="font-family:Rajdhani,sans-serif;font-size:64px;font-weight:700;color:#ffaa3c;line-height:1;">'
                        f'{overall:.1f}</div>'
                        f'<div style="color:#8ca0b8;font-size:12px;margin-top:4px;">综合评分 · 满分 10.0</div>'
                        f'<div style="color:#ffaa3c;font-size:16px;margin-top:8px;letter-spacing:2px;">{stars_str}</div>'
                        f'<div style="color:#8ca0b8;font-size:11px;margin-top:6px;">{score_summary["count"]} 条评价</div>'
                        f'</div>'
                    )
                    st.markdown(score_panel, unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<div style="background:linear-gradient(135deg,#1a2235,#1e2945);'
                        'border:1px solid #2a3a55;border-radius:14px;padding:22px;text-align:center;">'
                        '<div style="font-size:40px;color:#4a6080;padding:20px 0;">还未评分</div>'
                        '<div style="color:#8ca0b8;font-size:11px;">「我要打分」Tab 第一个评分</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )

            with score_cols[1]:
                if score_summary:
                    dims = get_dimensions(p["category"])
                    for i, dim_name in enumerate(dims, 1):
                        score = score_summary.get(f"dim{i}", 0)
                        pct = (score / 10.0) * 100
                        bar_html = (
                            f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0;font-size:12px;">'
                            f'<span style="color:#c8d8e8;width:80px;">{dim_name}</span>'
                            f'<div style="flex:1;background:#0e1525;border-radius:4px;height:8px;overflow:hidden;">'
                            f'<div style="height:100%;background:linear-gradient(90deg,#00f5a0,#00d9f5);width:{pct}%;"></div></div>'
                            f'<span style="color:#00f5a0;font-size:11px;font-weight:600;width:42px;text-align:right;">{score:.1f}/10</span>'
                            f'</div>'
                        )
                        st.markdown(bar_html, unsafe_allow_html=True)
                else:
                    st.info("还没有评分数据")

            st.markdown("---")

            # 产品描述
            st.markdown(f'<div style="color:#c8d8e8;font-size:14px;line-height:1.8;">{p.get("description","")}</div>',
                        unsafe_allow_html=True)

            if p.get("key_features"):
                st.markdown('<p style="color:#00f5a0;font-weight:700;font-size:14px;margin-top:14px;">✓ 核心卖点</p>',
                            unsafe_allow_html=True)
                for feat in p["key_features"]:
                    st.markdown(f'<div style="color:#00f5a0;font-size:13px;margin:4px 0;">✓ {feat}</div>',
                                unsafe_allow_html=True)

            info_cols = st.columns(2)
            with info_cols[0]:
                st.markdown(f'<div style="color:#8ca0b8;font-size:13px;margin-top:10px;">🕐 服用时机：'
                            f'<span style="color:#c8d8e8;">{p.get("usage_timing","—")}</span></div>',
                            unsafe_allow_html=True)
                st.markdown(f'<div style="color:#8ca0b8;font-size:13px;">📏 推荐剂量：'
                            f'<span style="color:#c8d8e8;">{p.get("dosage","—")}</span></div>',
                            unsafe_allow_html=True)
            with info_cols[1]:
                sizes_str = " / ".join(p.get("sizes", [])) if p.get("sizes") else "—"
                st.markdown(f'<div style="color:#8ca0b8;font-size:13px;margin-top:10px;">📦 规格：'
                            f'<span style="color:#c8d8e8;">{sizes_str}</span></div>',
                            unsafe_allow_html=True)
                if p.get("flavors"):
                    flavors_str = " / ".join(p["flavors"][:6])
                    if len(p["flavors"]) > 6:
                        flavors_str += f" 等 {len(p['flavors'])} 种"
                    st.markdown(f'<div style="color:#8ca0b8;font-size:13px;">🍬 口味：'
                                f'<span style="color:#c8d8e8;">{flavors_str}</span></div>',
                                unsafe_allow_html=True)

            st.markdown("---")

            # === 💊 服用周期管理 ===
            st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">💊 我的服用周期</p>',
                        unsafe_allow_html=True)

            from database import (add_supplement_cycle, end_supplement_cycle,
                                   get_supplement_cycles, get_active_supplement_cycle)
            active_cycle = get_active_supplement_cycle(p["series_name"], p["category"])
            cycles = get_supplement_cycles(p["series_name"], p["category"])

            if active_cycle:
                # 有进行中的周期
                try:
                    days_so_far = (date.today() - datetime.strptime(active_cycle["start_date"], "%Y-%m-%d").date()).days + 1
                except:
                    days_so_far = "—"
                active_html = (
                    f'<div style="background:linear-gradient(135deg,rgba(0,245,160,0.08),rgba(0,245,160,0.02));'
                    f'border:1px solid rgba(0,245,160,0.25);border-radius:10px;padding:14px 18px;margin:8px 0;">'
                    f'<span style="color:#00f5a0;font-weight:700;">🟢 进行中</span> · 已服用 <b style="color:#00f5a0;">第 {days_so_far} 天</b>'
                    f'<div style="color:#c8d8e8;font-size:13px;margin-top:6px;">'
                    f'开始日期：{active_cycle["start_date"]} · 剂量：{active_cycle.get("dosage","—")}</div>'
                    f'</div>'
                )
                st.markdown(active_html, unsafe_allow_html=True)

                end_cols = st.columns([2, 1])
                with end_cols[0]:
                    end_note = st.text_input("结束备注（可选）",
                                              placeholder="例如：用完了一罐",
                                              key=f"end_note_{p['id']}")
                with end_cols[1]:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔚 结束本周期", key=f"end_cycle_{p['id']}",
                                 use_container_width=True):
                        end_supplement_cycle(active_cycle["id"], date.today().isoformat(), end_note)
                        st.success("已结束本周期")
                        st.rerun()
            else:
                # 没有进行中的周期 - 开始新周期
                with st.expander("➕ 开始一个新的服用周期"):
                    nc_cols = st.columns(2)
                    with nc_cols[0]:
                        new_start = st.date_input("开始日期", value=date.today(),
                                                   key=f"new_cycle_start_{p['id']}")
                    with nc_cols[1]:
                        new_dosage = st.text_input("剂量备注",
                                                    placeholder="例如：每天1勺 30g",
                                                    key=f"new_cycle_dosage_{p['id']}")
                    new_note = st.text_input("备注（可选）",
                                              placeholder="例如：训练后服用",
                                              key=f"new_cycle_note_{p['id']}")
                    if st.button("✅ 开始服用周期",
                                  key=f"start_cycle_{p['id']}",
                                  use_container_width=True, type="primary"):
                        add_supplement_cycle(
                            product_name=p["series_name"],
                            brand=p["brand_name"],
                            category=p["category"],
                            start_date=new_start.isoformat(),
                            dosage=new_dosage,
                            notes=new_note
                        )
                        st.success("✅ 已开始新周期")
                        st.rerun()

            # 历史周期
            past_cycles = [c for c in cycles if c.get("end_date")]
            if past_cycles:
                with st.expander(f"📋 历史周期（{len(past_cycles)}次）"):
                    for c in past_cycles:
                        try:
                            duration = (datetime.strptime(c["end_date"], "%Y-%m-%d").date()
                                      - datetime.strptime(c["start_date"], "%Y-%m-%d").date()).days + 1
                        except:
                            duration = "—"
                        notes_html = f'<div style="color:#8ca0b8;font-size:12px;margin-top:4px;">{c["notes"]}</div>' if c.get("notes") else ""
                        cycle_html = (
                            f'<div style="background:#1a2235;border-left:3px solid #00d9f5;'
                            f'padding:10px 14px;margin:6px 0;border-radius:6px;">'
                            f'<span style="color:#00d9f5;">{c["start_date"]} ~ {c["end_date"]}</span>'
                            f'<span style="color:#c8d8e8;margin-left:8px;">· 共 {duration} 天</span>'
                            f'{notes_html}</div>'
                        )
                        st.markdown(cycle_html, unsafe_allow_html=True)

            st.markdown("---")

            # === 评测列表（虎扑风评论流）===
            st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">💬 全部评价</p>',
                        unsafe_allow_html=True)
            ratings = get_product_ratings(p["id"], limit=50)
            if not ratings:
                st.info("还没有评价。「⭐ 我要打分」Tab 来当第一个吧！")
            else:
                for r in ratings:
                    full = int(r["overall"] / 2)
                    stars_str = "★" * full + "☆" * (5 - full)
                    flavor_str = f" · {r['flavor']}" if r.get("flavor") else ""
                    review_html = (
                        f'<div style="background:#1a2235;border:1px solid #2a3a55;border-radius:10px;'
                        f'padding:14px 18px;margin:10px 0;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
                        f'<div><span style="color:#00f5a0;font-weight:600;">👤 {r["user_name"]}</span>'
                        f'<span style="color:#ffaa3c;margin-left:8px;">{stars_str}</span>'
                        f'<span style="color:#8ca0b8;font-size:11px;margin-left:6px;">{r["overall"]:.1f}{flavor_str}</span></div>'
                        f'<span style="color:#8ca0b8;font-size:11px;">{r.get("created_at","")[:16]}</span>'
                        f'</div>'
                        f'<div style="color:#e8eaf0;font-size:13px;line-height:1.7;">{r["review"]}</div>'
                        f'</div>'
                    )
                    st.markdown(review_html, unsafe_allow_html=True)
                    if st.button(f"👍 {r['likes']}", key=f"like_{r['id']}"):
                        like_rating(r['id'])
                        st.rerun()

    # 列表页（未进入详情）
    else:
        categories = get_categories()
        available_cats = get_all_categories()
        show_cats = [c for c in categories if c in available_cats]

        c1, c2 = st.columns([2, 1])
        with c1:
            cat_filter = st.selectbox("选择品类", ["全部"] + show_cats, key="cat_filter")
        with c2:
            brand_filter = st.selectbox(
                "选择品牌",
                ["全部"] + [b["name_cn"] for b in get_all_brands()],
                key="brand_filter"
            )

        sort_opt = st.radio("排序",
                             ["默认", "评分从高到低", "价格从低到高", "评分人数最多"],
                             horizontal=True, key="supp_sort")

        if cat_filter == "全部":
            all_products = []
            for c in show_cats:
                all_products.extend(get_products_by_category(category=c))
        else:
            all_products = get_products_by_category(category=cat_filter)

        if brand_filter != "全部":
            all_products = [p for p in all_products if p["brand_name"] == brand_filter]

        # 排序
        if sort_opt == "评分从高到低":
            def _score(p):
                s = get_product_score_summary(p["id"])
                return s["overall"] if s else 0
            all_products.sort(key=_score, reverse=True)
        elif sort_opt == "价格从低到高":
            all_products.sort(key=lambda p: int(p.get("ref_price_min") or 0))
        elif sort_opt == "评分人数最多":
            def _cnt(p):
                s = get_product_score_summary(p["id"])
                return s["count"] if s else 0
            all_products.sort(key=_cnt, reverse=True)

        st.caption(f"找到 {len(all_products)} 个产品 · 点击产品卡片查看详情")
        st.markdown("---")

        # 虎扑风产品卡片列表
        for p in all_products:
            cat_info = get_category_info(p["category"])
            icon = cat_info.get("emoji","💊")
            score_summary = get_product_score_summary(p["id"])

            # 获取最新一条评价
            latest = get_product_ratings(p["id"], limit=1)
            quote = latest[0]["review"] if latest else None

            card_cols = st.columns([0.7, 4, 1.2, 1])
            with card_cols[0]:
                st.markdown(f'<div style="font-size:36px;text-align:center;padding-top:8px;">{icon}</div>',
                            unsafe_allow_html=True)
            with card_cols[1]:
                verified_html = "" if p.get("verified") else '<span style="color:#ffaa3c;font-size:11px;border:1px solid rgba(255,170,60,0.3);padding:1px 6px;border-radius:6px;margin-left:6px;">⚠ 待审核</span>'
                info_html = (
                    f'<div><span style="color:#00f5a0;font-weight:700;font-size:15px;">{p["brand_emoji"]} {p["brand_name"]}</span>{verified_html}</div>'
                    f'<div style="color:#e8eaf0;font-size:14px;font-weight:500;margin-top:2px;">{p["series_name"]}</div>'
                    f'<div style="color:#ffaa3c;font-size:12px;margin-top:4px;font-weight:600;">💰 ¥{int(p.get("ref_price_min") or 0)} - {int(p.get("ref_price_max") or 0)}</div>'
                )
                st.markdown(info_html, unsafe_allow_html=True)
                if quote:
                    quote_short = quote[:60] + ("..." if len(quote) > 60 else "")
                    st.markdown(f'<div style="color:#8ca0b8;font-size:12px;margin-top:6px;font-style:italic;">"{quote_short}"</div>',
                                unsafe_allow_html=True)
            with card_cols[2]:
                if score_summary:
                    overall = score_summary["overall"]
                    full = int(overall / 2)
                    stars_str = "★" * full + "☆" * (5 - full)
                    score_html = (
                        f'<div style="text-align:right;">'
                        f'<div style="font-family:Rajdhani,sans-serif;font-size:34px;font-weight:700;color:#ffaa3c;line-height:1;">{overall:.1f}</div>'
                        f'<div style="color:#ffaa3c;font-size:13px;margin-top:4px;letter-spacing:1px;">{stars_str}</div>'
                        f'<div style="color:#8ca0b8;font-size:11px;margin-top:2px;">{score_summary["count"]} 条评价</div>'
                        f'</div>'
                    )
                    st.markdown(score_html, unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<div style="text-align:right;padding-top:18px;">'
                        '<div style="color:#4a6080;font-size:13px;">未评分</div>'
                        '<div style="color:#8ca0b8;font-size:11px;">点进查看</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )
            with card_cols[3]:
                if st.button("查看 →", key=f"view_supp_{p['id']}", use_container_width=True):
                    st.session_state["supp_detail_pid"] = p["id"]
                    st.rerun()
            st.markdown('<hr style="margin:0;border-color:#2a3a55;">', unsafe_allow_html=True)

# ============ Tab 4: 我要打分 ============
with tabs[3]:
    st.markdown('<p style="color:#c8d8e8;font-weight:700;font-size:16px;">分享你的真实使用体验，帮助其他用户</p>', unsafe_allow_html=True)

    cat_for_rate = st.selectbox("1. 选择品类", get_all_categories(), key="rate_cat")
    products_in_cat = get_products_by_category(category=cat_for_rate)

    if not products_in_cat:
        st.info("该品类暂无产品")
    else:
        product_options = {f"{p['brand_name']} - {p['series_name']}": p for p in products_in_cat}
        selected_label = st.selectbox("2. 选择产品", list(product_options.keys()), key="rate_prod")
        selected_product = product_options[selected_label]

        flavor_opt = ["未指定"] + selected_product.get("flavors", [])
        flavor_choice = st.selectbox("3. 你使用的口味（可选）", flavor_opt, key="rate_flavor")

        st.markdown('<p style="color:#c8d8e8;font-weight:600;margin-top:16px;">4. 五维评分（1-10 分）</p>', unsafe_allow_html=True)
        dims = get_dimensions(selected_product["category"])
        scores = {}
        for i, dim_name in enumerate(dims, 1):
            scores[f"dim{i}_score"] = st.slider(dim_name, 1, 10, 7, key=f"rate_dim_{i}")

        user_name = st.text_input("你的昵称", value=profile.get("name", "匿名用户") if profile else "匿名用户", key="rate_user")
        review = st.text_area("5. 写下你的使用感受", placeholder="例如：溶解度很好，几乎没结块，口味偏甜，性价比一般...", height=100, key="rate_review")

        if st.button("✅ 提交评价", use_container_width=True, type="primary"):
            if not review.strip():
                st.error("请写一些使用感受再提交")
            else:
                add_rating({
                    "product_id": selected_product["id"],
                    "user_name": user_name or "匿名用户",
                    "flavor": flavor_choice if flavor_choice != "未指定" else "",
                    "review": review,
                    **scores
                })
                st.success("🎉 评价已提交，感谢分享！")
                st.balloons()

# ============ Tab 5: 提交新产品 ============
with tabs[4]:
    st.markdown('<p style="color:#c8d8e8;font-weight:700;font-size:16px;">没找到你在用的补剂？提交它！通过审核后将进入产品库</p>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="color:#c8d8e8;font-weight:600;">1. 品牌信息</p>', unsafe_allow_html=True)

    use_existing_brand = st.radio(
        "品牌选择",
        ["从已有品牌选择", "新增品牌"],
        horizontal=True,
        key="brand_mode"
    )

    brand_id = None
    new_brand_data = None

    if use_existing_brand == "从已有品牌选择":
        all_brands = get_all_brands()
        brand_choice = st.selectbox(
            "选择品牌",
            [f"{b['logo_emoji']} {b['name_cn']} ({b['name_en']})" for b in all_brands],
            key="exist_brand"
        )
        brand_id = all_brands[
            [f"{b['logo_emoji']} {b['name_cn']} ({b['name_en']})" for b in all_brands].index(brand_choice)
        ]["id"]
    else:
        bc1, bc2 = st.columns(2)
        with bc1:
            nb_cn = st.text_input("品牌中文名", key="nb_cn")
            nb_country = st.text_input("产地国家", key="nb_country")
        with bc2:
            nb_en = st.text_input("品牌英文名", key="nb_en")
            nb_emoji = st.text_input("品牌图标emoji（可选）", value="🏷", key="nb_emoji")
        nb_desc = st.text_area("品牌简介（一句话）", key="nb_desc")
        new_brand_data = {
            "name_cn": nb_cn, "name_en": nb_en, "country": nb_country,
            "tier": "用户提交", "description": nb_desc, "logo_emoji": nb_emoji or "🏷",
            "verified": 0
        }

    st.markdown("---")
    st.markdown('<p style="color:#c8d8e8;font-weight:600;">2. 产品信息</p>', unsafe_allow_html=True)

    pc1, pc2 = st.columns(2)
    with pc1:
        np_category = st.selectbox("品类", get_categories(), key="np_cat")
        np_series = st.text_input("系列/产品名", placeholder="例如：金标乳清", key="np_series")
        np_price_min = st.number_input("最低参考价（元）", min_value=0, value=200, key="np_pmin")
        np_price_max = st.number_input("最高参考价（元）", min_value=0, value=400, key="np_pmax")
    with pc2:
        np_subcat = st.text_input("子类型（可选）", placeholder="例如：浓缩乳清", key="np_subcat")
        np_sizes = st.text_input("规格（用 / 分隔）", placeholder="例如：2lb / 5lb", key="np_sizes")
        np_flavors = st.text_input("口味（用 / 分隔）", placeholder="例如：巧克力 / 香草 / 草莓", key="np_flavors")

    np_desc = st.text_area("产品描述", placeholder="一两句话介绍这个产品", key="np_desc")
    np_features = st.text_area("核心卖点（每行一条）", placeholder="例如：\n每勺24g蛋白\n含5.5g BCAA\nInformed-Choice认证", height=100, key="np_features")
    np_certs = st.text_input("认证标志（用 / 分隔）", placeholder="例如：Informed-Choice / BSCG", key="np_certs")

    pp1, pp2 = st.columns(2)
    with pp1:
        np_timing = st.text_input("服用时机", placeholder="训练后30分钟内", key="np_timing")
    with pp2:
        np_dosage = st.text_input("推荐剂量", placeholder="每次1勺(30g)，每日1-2次", key="np_dosage")

    np_cautions = st.text_input("注意事项（可选）", placeholder="乳糖不耐受者注意...", key="np_cautions")
    submitter = st.text_input("提交人昵称", value=profile.get("name","") if profile else "", key="np_submitter")

    if st.button("📤 提交产品（等待审核）", use_container_width=True, type="primary"):
        if not np_series.strip():
            st.error("请填写产品名")
        elif use_existing_brand == "新增品牌" and not new_brand_data.get("name_cn"):
            st.error("新增品牌时请填写品牌中文名")
        else:
            if use_existing_brand == "新增品牌":
                brand_id = add_brand(new_brand_data)

            product_data = {
                "brand_id": brand_id,
                "series_name": np_series,
                "category": np_category,
                "subcategory": np_subcat,
                "description": np_desc,
                "key_features": [f.strip() for f in np_features.split("\n") if f.strip()],
                "certifications": [c.strip() for c in np_certs.split("/") if c.strip()],
                "ref_price_min": np_price_min,
                "ref_price_max": np_price_max,
                "sizes": [s.strip() for s in np_sizes.split("/") if s.strip()],
                "flavors": [f.strip() for f in np_flavors.split("/") if f.strip()],
                "usage_timing": np_timing,
                "dosage": np_dosage,
                "cautions": np_cautions,
                "submitted_by": submitter or "匿名",
                "verified": 0,
            }
            add_product(product_data)
            st.success("🎉 产品已提交！通过审核后将在产品库可见。")
            st.balloons()

    # 待审核区域
    pending = get_pending_products()
    if pending:
        st.markdown("---")
        st.markdown(f'<p style="color:#ffaa3c;font-weight:600;">⚠️ 待审核产品（{len(pending)}）</p>', unsafe_allow_html=True)
        for p in pending:
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f'<div style="background:rgba(255,170,60,0.05);border:1px solid rgba(255,170,60,0.2);border-radius:8px;padding:10px 14px;margin:6px 0;"><b>{p["brand_name"]}</b> - {p["series_name"]}<br><span style="font-size:12px;color:#8ca0b8;">{p.get("category","")} · 提交人：{p.get("submitted_by","匿名")}</span></div>', unsafe_allow_html=True)
            with cols[1]:
                if st.button("✓ 通过", key=f"verify_{p['id']}"):
                    verify_product(p["id"])
                    st.rerun()

# ============ Tab 6: AI营养师 ============
with tabs[5]:
    if not ollama_ok:
        st.error("❌ AI 服务未启动，请打开新终端运行 `ollama serve` 后刷新")

    st.markdown('<p style="color:#c8d8e8;font-weight:700;">快速提问</p>', unsafe_allow_html=True)
    quick_qs = ["75kg增肌该选什么蛋白粉？","乳糖不耐受推荐","金标乳清和ISO100哪个好？","学生党性价比之选","减脂期补剂组合"]
    qcols = st.columns(5)
    for i, q in enumerate(quick_qs):
        with qcols[i]:
            if st.button(q, key=f"sq{i}", use_container_width=True):
                if not ollama_ok: st.error("AI未启动")
                else:
                    st.session_state["supp_pending"] = q
                    st.rerun()

    st.markdown("---")
    if st.session_state.supplement_messages:
        for msg in st.session_state.supplement_messages:
            cls = "chat-user" if msg["role"]=="user" else "chat-ai"
            icon = "🙋" if msg["role"]=="user" else "🤖"
            st.markdown(f'<div class="{cls}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#4a6080;text-align:center;padding:40px;">点击快速提问或在下方输入问题</p>', unsafe_allow_html=True)

    st.markdown("---")
    user_input = st.text_input("向AI营养师提问...", placeholder="例如：我75kg想增肌，应该补充哪些品牌的什么产品？", key="supp_input")
    b1, b2 = st.columns([4, 1])
    with b1:
        if st.button("发送", key="supp_send", use_container_width=True, type="primary"):
            if not ollama_ok: st.error("AI未启动")
            elif user_input.strip():
                st.session_state["supp_pending"] = user_input
                st.rerun()
    with b2:
        if st.button("🗑 清空", key="supp_clear", use_container_width=True):
            clear_chat(MODULE)
            st.session_state.supplement_messages = []
            st.rerun()
