import streamlit as st
from database import (
    init_db, load_profile,
    save_equipment_rating, get_equipment_rating,
    get_all_equipment_ratings, get_owned_equipment,
    add_equipment_journal, get_equipment_journals, delete_equipment_journal,
    list_sessions
)
from equipment_data import (
    EQUIPMENT_CATEGORIES, EQUIPMENT_BRANDS, RATING_DIMENSIONS,
    get_brands_by_category, recommend_equipment_from_notes
)
from hupu_ui import (
    HUPU_STYLE, render_list_card, render_detail_top, render_journal_card
)
from ai_engine import check_ollama_status

st.set_page_config(page_title="辅助工具", page_icon="🛡️", layout="wide")
init_db()

st.markdown(HUPU_STYLE, unsafe_allow_html=True)
st.markdown("""
<style>
.page-title{font-family:'Rajdhani',sans-serif;font-size:40px;font-weight:700;
    background:linear-gradient(90deg,#ff9d3c,#ff5757);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.rec-card{background:linear-gradient(135deg,rgba(255,87,87,0.08),rgba(255,87,87,0.03));
    border-left:3px solid #ff5757;border-radius:8px;padding:14px 18px;margin:10px 0;}
.rec-title{color:#ff5757;font-weight:700;font-size:15px;}
hr{border-color:#2a3a55;}
</style>
""", unsafe_allow_html=True)

profile = load_profile()

st.markdown('<div class="page-title">🛡️ 辅助工具</div>', unsafe_allow_html=True)
st.markdown('<p style="color:#c8d8e8;">力量训练护具 · 抓握辅助 · 恢复工具 · 全方位提升训练质量</p>', unsafe_allow_html=True)
st.markdown("---")

# ===== 详情页路由：检查 session_state =====
detail_product = st.session_state.get("equip_detail_product")
detail_category = st.session_state.get("equip_detail_category")

if detail_product and detail_category:
    # ============== 详情页 ==============
    prod = None
    for b in EQUIPMENT_BRANDS:
        if b["product_name"] == detail_product and b["category"] == detail_category:
            prod = b
            break

    if not prod:
        st.error("产品不存在")
        if st.button("← 返回列表"):
            st.session_state.pop("equip_detail_product", None)
            st.session_state.pop("equip_detail_category", None)
            st.rerun()
        st.stop()

    if st.button("← 返回列表", key="back_to_list"):
        st.session_state.pop("equip_detail_product", None)
        st.session_state.pop("equip_detail_category", None)
        st.rerun()

    saved = get_equipment_rating(detail_product, detail_category) or {}
    journals = get_equipment_journals(detail_product, detail_category)

    cat_info = EQUIPMENT_CATEGORIES.get(detail_category, {})
    avatar = cat_info.get("icon", "🔧")

    ratings_dict = {d["key"]: saved.get(d["key"], 0) for d in RATING_DIMENSIONS}

    top_html = render_detail_top(
        avatar=avatar,
        brand=prod["brand"],
        product_name=prod["product_name"],
        category=prod["category"],
        tier=prod["tier"],
        country=prod["country"],
        price_range=prod["price_range"],
        description=prod["description"],
        ratings_dict=ratings_dict,
        dimension_labels=RATING_DIMENSIONS
    )
    st.markdown(top_html, unsafe_allow_html=True)

    # 产品描述卡片（优缺点）
    pros_li = "".join(['<li>' + p + '</li>' for p in prod["pros"]])
    cons_li = "".join(['<li>' + c + '</li>' for c in prod["cons"]])
    desc_html = (
        '<div style="background:#1a2235;border:1px solid #2a3a55;border-radius:12px;'
        'padding:18px 22px;margin:12px 0;">'
        '<div style="color:#e8eaf0;font-size:14px;line-height:1.8;">' + prod["description"] + '</div>'
        '<div style="display:flex;gap:24px;margin-top:14px;">'
        '<div style="flex:1;">'
        '<div style="color:#00f5a0;font-size:13px;font-weight:700;margin-bottom:6px;">✓ 优点</div>'
        '<ul style="color:#c8d8e8;font-size:13px;margin:0;padding-left:18px;line-height:1.8;">' + pros_li + '</ul>'
        '</div>'
        '<div style="flex:1;">'
        '<div style="color:#ffaa3c;font-size:13px;font-weight:700;margin-bottom:6px;">⚠ 缺点</div>'
        '<ul style="color:#c8d8e8;font-size:13px;margin:0;padding-left:18px;line-height:1.8;">' + cons_li + '</ul>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(desc_html, unsafe_allow_html=True)

    # 评分区
    st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;margin-top:20px;">⭐ 立即评分</p>', unsafe_allow_html=True)
    st.caption("五维评分会汇总成综合评分；评分后产品也会出现在「我的评测」")

    rc = st.columns(5)
    rating_values = {}
    for i, dim in enumerate(RATING_DIMENSIONS):
        with rc[i]:
            default_val = int(saved.get(dim["key"], 0))
            rating_values[dim["key"]] = st.slider(
                dim["icon"] + " " + dim["label"],
                0, 5, default_val,
                key="rate_d_" + dim["key"]
            )

    rb1, rb2 = st.columns([1, 1])
    with rb1:
        is_owned_check = st.checkbox(
            "我拥有这个工具",
            value=bool(saved.get("is_owned")),
            key="owned_d"
        )
    with rb2:
        if st.button("💾 保存评分", use_container_width=True, type="primary", key="save_rate_d"):
            save_equipment_rating(
                category=prod["category"],
                brand=prod["brand"],
                product_name=prod["product_name"],
                ratings=rating_values,
                review="",
                is_owned=is_owned_check
            )
            st.success("✅ 评分已保存")
            st.rerun()

    # 添加日记
    st.markdown("---")
    st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">📝 写一条评测日记</p>', unsafe_allow_html=True)
    st.caption("可以多次添加，记录不同时期的使用感受")

    jc1, jc2 = st.columns([3, 1])
    with jc1:
        new_content = st.text_area(
            "本次评测内容",
            placeholder="比如：用了 30 天后，硬拉时支撑感很好...",
            height=100,
            key="new_journal_content"
        )
    with jc2:
        new_stars = st.slider("评分", 1, 5, 5, key="new_journal_stars")
        new_days = st.number_input(
            "使用天数（可选）", 0, 3650, 0,
            help="0 = 不显示天数",
            key="new_journal_days"
        )

    if st.button("➕ 添加评测", use_container_width=True, key="add_journal_btn"):
        if not new_content.strip():
            st.error("评测内容不能为空")
        else:
            add_equipment_journal(
                product_name=prod["product_name"],
                category=prod["category"],
                content=new_content.strip(),
                stars=new_stars,
                usage_days=new_days
            )
            st.success("✅ 评测已添加")
            st.rerun()

    st.markdown("---")
    if journals:
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">📋 我的评测日记 · ' + str(len(journals)) + ' 条</p>', unsafe_allow_html=True)
        for j in journals:
            jcol1, jcol2 = st.columns([10, 1])
            with jcol1:
                st.markdown(render_journal_card(j), unsafe_allow_html=True)
            with jcol2:
                if st.button("🗑️", key="del_j_" + str(j["id"]), help="删除这条评测"):
                    delete_equipment_journal(j["id"])
                    st.rerun()
    else:
        st.markdown('<div class="hp-empty">还没有评测日记，写下你的第一条使用感受吧 ✍️</div>', unsafe_allow_html=True)

else:
    # ============== 列表页（Tab） ==============
    tabs = st.tabs([
        "💡 智能推荐",
        "📚 工具品类",
        "🏷️ 品牌产品库",
        "⭐ 我的评测",
        "🤖 AI 顾问"
    ])

    # Tab1 智能推荐
    with tabs[0]:
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:18px;">💡 基于你的训练情况推荐</p>', unsafe_allow_html=True)
        st.caption("分析你最近的训练备注，推荐合适的辅助工具。")

        recent_sessions = list_sessions(limit=10)
        all_notes = ""
        for s in recent_sessions:
            if s.get("notes"):
                all_notes += s["notes"] + "\n"

        if not all_notes.strip():
            st.info("📝 还没有训练备注。完成几次训练并在备注里描述身体感受，AI 就能根据情况推荐工具。")
        else:
            recs = recommend_equipment_from_notes(all_notes)
            if recs:
                st.success("📊 根据你最近的训练情况，建议关注以下 " + str(len(recs)) + " 类工具")
                for r in recs:
                    priority_color = "#ff5757" if r["priority"] == "high" else "#ffaa3c"
                    priority_text = "强烈推荐" if r["priority"] == "high" else "建议关注"
                    ci = EQUIPMENT_CATEGORIES.get(r["category"], {})
                    icon = ci.get("icon", "🔧")
                    html = (
                        '<div class="rec-card" style="border-left-color:' + priority_color + ';">'
                        '<div class="rec-title">' + icon + ' ' + r['category'] +
                        ' <span style="color:' + priority_color + ';font-size:12px;">· ' + priority_text + '</span></div>'
                        '<div style="color:#c8d8e8;font-size:13px;margin-top:6px;line-height:1.7;">' + r['reason'] + '</div>'
                        '</div>'
                    )
                    st.markdown(html, unsafe_allow_html=True)
            else:
                st.info("✅ 根据你最近的训练备注，暂时不需要额外的辅助工具。继续保持训练！")

        if profile:
            level = profile.get("fitness_level", "新手")
            st.markdown("---")
            st.markdown('<p style="color:#e8eaf0;font-weight:700;">📌 根据你的训练水平推荐</p>', unsafe_allow_html=True)
            if "新手" in level:
                level_recs = [
                    ("护腕", "卧推、肩推时稳定手腕；新手必备"),
                    ("助力带", "硬拉、划船时辅助抓握，让目标肌肉充分发力"),
                    ("镁粉/握力", "改善握把打滑，提升训练专注度"),
                ]
            elif "初级" in level or "中级" in level:
                level_recs = [
                    ("腰部支持", "大重量硬拉/深蹲时保护腰椎"),
                    ("护膝", "膝盖支持，提供反弹助力"),
                    ("举重鞋", "改善深蹲质量"),
                    ("恢复工具", "训练量增大，需要主动恢复"),
                ]
            else:
                level_recs = [
                    ("腰部支持", "极限重量必备"),
                    ("护膝", "深蹲反弹助力"),
                    ("举重鞋", "传力效率"),
                    ("恢复工具", "专业恢复必备"),
                ]

            for cat_name, reason in level_recs:
                ci = EQUIPMENT_CATEGORIES.get(cat_name, {})
                icon = ci.get("icon", "🔧")
                html = (
                    '<div style="background:#1a2235;border-left:3px solid #00d9f5;border-radius:8px;'
                    'padding:12px 16px;margin:6px 0;">'
                    '<span style="color:#00d9f5;font-weight:600;">' + icon + ' ' + cat_name + '</span>'
                    '<span style="color:#c8d8e8;font-size:13px;margin-left:8px;">— ' + reason + '</span>'
                    '</div>'
                )
                st.markdown(html, unsafe_allow_html=True)

    # Tab2 工具品类
    with tabs[1]:
        # === 品类详情子页 ===
        if st.session_state.get("equip_cat_detail"):
            target_cat = st.session_state["equip_cat_detail"]
            cat_info = EQUIPMENT_CATEGORIES.get(target_cat, {})

            if st.button("← 返回品类列表", key="back_cat_list"):
                del st.session_state["equip_cat_detail"]
                st.rerun()

            # 品类头部
            cat_head_html = (
                f'<div style="background:linear-gradient(135deg,#1a2235,#1e2945);'
                f'border:1px solid #2a3a55;border-radius:14px;padding:22px;margin:10px 0;">'
                f'<div style="font-size:48px;">{cat_info.get("icon","🔧")}</div>'
                f'<div style="color:#ff9d3c;font-weight:700;font-size:24px;margin-top:6px;">{target_cat}</div>'
                f'<div style="color:#c8d8e8;font-size:14px;margin-top:8px;line-height:1.7;">'
                f'{cat_info.get("description","")}</div>'
                f'<div style="color:#8ca0b8;font-size:12px;margin-top:10px;font-style:italic;">'
                f'💡 {cat_info.get("when_to_use","")}</div>'
                f'</div>'
            )
            st.markdown(cat_head_html, unsafe_allow_html=True)

            # 该品类下的所有产品
            cat_products = get_brands_by_category(target_cat)
            st.markdown(
                f'<p style="color:#e8eaf0;font-weight:700;font-size:18px;margin-top:14px;">'
                f'📦 {target_cat} 收录的产品（{len(cat_products)} 个）</p>',
                unsafe_allow_html=True
            )

            if not cat_products:
                st.info("该品类暂无收录产品")
            else:
                for i, prod in enumerate(cat_products):
                    render_product_card(prod, i + 5000)

        else:
            st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:18px;">📚 8 大工具分类</p>'
                        '<p style="color:#8ca0b8;font-size:13px;">点击任意品类查看该品类下收录的所有产品</p>',
                        unsafe_allow_html=True)
            cols = st.columns(2)
            for i, (cat_name, info) in enumerate(EQUIPMENT_CATEGORIES.items()):
                with cols[i % 2]:
                    brands_count = len(get_brands_by_category(cat_name))
                    html = (
                        '<div style="background:#1a2235;border:1px solid #2a3a55;border-radius:14px;'
                        'padding:18px 22px;margin:8px 0;min-height:180px;">'
                        '<div style="font-size:28px;">' + info["icon"] + '</div>'
                        '<div style="font-weight:700;color:#ff9d3c;font-size:16px;margin:8px 0 4px;">'
                        + cat_name + '（' + str(brands_count) + ' 个产品）</div>'
                        '<div style="color:#c8d8e8;font-size:13px;line-height:1.6;">' + info["description"] + '</div>'
                        '<div style="color:#8ca0b8;font-size:12px;margin-top:8px;font-style:italic;">💡 '
                        + info["when_to_use"] + '</div>'
                        '</div>'
                    )
                    st.markdown(html, unsafe_allow_html=True)
                    if st.button(f"查看 {cat_name} 的所有产品 →",
                                 key=f"cat_btn_{cat_name}",
                                 use_container_width=True):
                        st.session_state["equip_cat_detail"] = cat_name
                        st.rerun()

    # Tab3 品牌产品库
    with tabs[2]:
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:18px;">🏷️ 品牌产品库</p>', unsafe_allow_html=True)
        st.caption("点击任意产品卡片进入详情页评分和写评测")

        fc1, fc2 = st.columns([1, 1])
        with fc1:
            cat_filter = st.selectbox(
                "分类",
                ["全部"] + list(EQUIPMENT_CATEGORIES.keys()),
                key="brand_filter_v2"
            )
        with fc2:
            tier_filter = st.selectbox(
                "档次",
                ["全部", "性价比", "中端", "中高端", "高端"],
                key="tier_filter_v2"
            )

        filtered = EQUIPMENT_BRANDS
        if cat_filter != "全部":
            filtered = [b for b in filtered if b["category"] == cat_filter]
        if tier_filter != "全部":
            filtered = [b for b in filtered if b["tier"] == tier_filter]

        st.caption("共 " + str(len(filtered)) + " 个产品")
        st.markdown("---")

        if not filtered:
            st.info("此筛选条件下暂无产品")
        else:
            for prod in filtered:
                saved = get_equipment_rating(prod["product_name"], prod["category"])
                is_owned = bool(saved and saved.get("is_owned"))

                avg_score = None
                if saved:
                    scores = [saved.get(d["key"], 0) for d in RATING_DIMENSIONS if saved.get(d["key"], 0) > 0]
                    if scores:
                        avg_score = sum(scores) / len(scores)

                journals = get_equipment_journals(prod["product_name"], prod["category"])
                latest_comment = journals[0]["content"] if journals else None

                ci = EQUIPMENT_CATEGORIES.get(prod["category"], {})
                avatar = ci.get("icon", "🔧")

                card_html = render_list_card(
                    avatar=avatar,
                    brand=prod["brand"],
                    product_name=prod["product_name"],
                    category=prod["category"],
                    tier=prod["tier"],
                    rating_score=avg_score,
                    journal_count=len(journals),
                    latest_comment=latest_comment,
                    is_owned=is_owned,
                    price_range=prod["price_range"]
                )
                st.markdown(card_html, unsafe_allow_html=True)

                if st.button(
                    "→ 查看详情和评分",
                    key="enter_detail_" + prod["product_name"],
                    use_container_width=True
                ):
                    st.session_state["equip_detail_product"] = prod["product_name"]
                    st.session_state["equip_detail_category"] = prod["category"]
                    st.rerun()

    # Tab4 我的评测
    with tabs[3]:
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:18px;">⭐ 我的工具评测</p>', unsafe_allow_html=True)

        all_ratings = get_all_equipment_ratings()
        owned_items = [r for r in all_ratings if r.get("is_owned")]

        stat1, stat2, stat3 = st.columns(3)
        with stat1:
            st.metric("已拥有", str(len(owned_items)) + " 件")
        with stat2:
            st.metric("已评分", str(len(all_ratings)) + " 个")
        with stat3:
            cats = set(r["category"] for r in owned_items)
            st.metric("收藏分类", str(len(cats)) + " 类")

        if not all_ratings:
            st.info("还没有评分。前往「品牌产品库」对你用过或想买的工具评分。")
        else:
            st.markdown("---")
            for r in all_ratings:
                scores = [r.get(d["key"], 0) for d in RATING_DIMENSIONS if r.get(d["key"], 0) > 0]
                avg = sum(scores) / len(scores) if scores else 0
                ci = EQUIPMENT_CATEGORIES.get(r["category"], {})
                avatar = ci.get("icon", "🔧")

                jj = get_equipment_journals(r["product_name"], r["category"])
                latest = jj[0]["content"] if jj else None

                prod_data = None
                for b in EQUIPMENT_BRANDS:
                    if b["product_name"] == r["product_name"]:
                        prod_data = b
                        break

                card_html = render_list_card(
                    avatar=avatar,
                    brand=r["brand"],
                    product_name=r["product_name"],
                    category=r["category"],
                    tier=prod_data["tier"] if prod_data else "中端",
                    rating_score=avg if avg > 0 else None,
                    journal_count=len(jj),
                    latest_comment=latest,
                    is_owned=bool(r.get("is_owned")),
                    price_range=prod_data["price_range"] if prod_data else None
                )
                st.markdown(card_html, unsafe_allow_html=True)
                if st.button(
                    "→ 查看详情",
                    key="my_enter_" + r["product_name"],
                    use_container_width=True
                ):
                    st.session_state["equip_detail_product"] = r["product_name"]
                    st.session_state["equip_detail_category"] = r["category"]
                    st.rerun()

    # Tab5 AI 顾问
    with tabs[4]:
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:18px;">🤖 AI 装备顾问</p>', unsafe_allow_html=True)
        st.caption("问 AI 关于辅助工具的任何问题：选购建议、使用方法、品牌对比等")

        if "equip_messages" not in st.session_state:
            st.session_state.equip_messages = []

        for msg in st.session_state.equip_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if not st.session_state.equip_messages:
            st.markdown('<p style="color:#8ca0b8;font-size:13px;font-weight:600;margin-top:8px;">💡 试试这些问题：</p>', unsafe_allow_html=True)
            qc1, qc2 = st.columns(2)
            with qc1:
                if st.button("🦺 新手需要哪些必备装备？", use_container_width=True, key="qq1"):
                    st.session_state.equip_messages.append({"role": "user", "content": "我是新手，刚开始力量训练，需要哪些必备的辅助装备？预算 500-1000 元。"})
                    st.rerun()
                if st.button("🤔 SBD 和海德的腰带有什么差别？", use_container_width=True, key="qq2"):
                    st.session_state.equip_messages.append({"role": "user", "content": "SBD 和海德的举重腰带有什么差别？我应该买哪个？"})
                    st.rerun()
            with qc2:
                if st.button("💪 卧推超过 80kg 需要护腕吗？", use_container_width=True, key="qq3"):
                    st.session_state.equip_messages.append({"role": "user", "content": "我卧推已经稳定在 80kg，需要开始用护腕吗？推荐哪款？"})
                    st.rerun()
                if st.button("🦵 膝盖受过伤，护膝怎么选？", use_container_width=True, key="qq4"):
                    st.session_state.equip_messages.append({"role": "user", "content": "我膝盖以前打篮球受过伤，做深蹲要怎么选护膝？"})
                    st.rerun()

        user_input = st.chat_input("向 AI 装备顾问提问...")
        if user_input:
            st.session_state.equip_messages.append({"role": "user", "content": user_input})
            st.rerun()

        if (st.session_state.equip_messages and
            st.session_state.equip_messages[-1]["role"] == "user"):
            with st.chat_message("assistant"):
                with st.spinner("AI 装备顾问思考中..."):
                    equip_system_msg = {
                        "role": "system",
                        "content": (
                            "你是一位拥有 10 年经验的健身装备专家。"
                            "你熟悉国际和中国市场的主流力量训练辅助工具品牌（如 SBD、Inzer、Schiek、Rehband、海德、迷宝赫、李宁、Keep 等）。\n\n"
                            "回答规范：\n"
                            "- 根据用户的训练水平、目标、预算给出针对性建议\n"
                            "- 推荐时给出 1-3 个具体品牌和型号\n"
                            "- 说明各档次的差别和适合人群\n"
                            "- 不推销，客观比较优缺点\n"
                            "- 中国用户优先考虑国内可购买的品牌\n"
                            "- 强调安全：不能光靠装备代替正确动作\n"
                            "- 全程使用中文回答"
                        )
                    }
                    messages_to_send = [{"role": m["role"], "content": m["content"]} for m in st.session_state.equip_messages]

                    import requests
                    try:
                        response = requests.post(
                            "http://localhost:11434/api/chat",
                            json={"model": "llama3", "messages": [equip_system_msg] + messages_to_send,
                                  "stream": False, "options": {"temperature": 0.7, "top_p": 0.9}},
                            timeout=120
                        )
                        response.raise_for_status()
                        reply = response.json()["message"]["content"]
                    except Exception as e:
                        reply = "❌ 无法连接到 AI 服务：" + str(e)

                    st.markdown(reply)
                    st.session_state.equip_messages.append({"role": "assistant", "content": reply})
                    st.rerun()

        if st.session_state.equip_messages:
            if st.button("🗑️ 清空对话", key="clear_equip_chat"):
                st.session_state.equip_messages = []
                st.rerun()
