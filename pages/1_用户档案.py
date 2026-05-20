import streamlit as st
from datetime import datetime, date, timedelta
from database import (
    save_profile, load_profile,
    save_advanced_profile, load_advanced_profile, clear_advanced_profile,
    get_menstrual_cycle, save_menstrual_cycle, delete_menstrual_cycle,
    get_recent_menstrual_logs, add_menstrual_log, predict_period_dates
)

st.set_page_config(page_title="用户档案", page_icon="👤", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@700&family=Noto+Sans+SC:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Noto Sans SC',sans-serif;}
input,textarea{color:#e8eaf0 !important; caret-color:#00f5a0 !important;}
label,.stTextInput label,.stNumberInput label,.stSelectbox label,.stTextArea label,.stSlider label{color:#c8d8e8 !important;font-size:14px !important;}
[data-baseweb="menu"] li{color:#e8eaf0 !important;}
.page-title{font-family:'Rajdhani',sans-serif;font-size:40px;font-weight:700;background:linear-gradient(90deg,#00f5a0,#00d9f5);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.section-label{font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#4a6080;margin:20px 0 8px;}
.saved-card{background:#1a2235;border:1px solid #2a3a55;border-radius:14px;padding:20px 24px;}
.saved-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #2a3a55;font-size:14px;color:#e8eaf0;}
.saved-row:last-child{border-bottom:none;}
.saved-key{color:#8ca0b8;}
.saved-val{color:#00f5a0;font-weight:500;}
.period-card{background:linear-gradient(135deg,rgba(255,121,180,0.08),rgba(255,121,180,0.03));
    border:1px solid rgba(255,121,180,0.3);border-radius:14px;padding:20px 24px;margin-top:16px;}
.period-title{color:#ff79b4;font-weight:700;font-size:16px;}
.period-info{color:#c8d8e8;font-size:13px;margin-top:8px;line-height:1.8;}
.privacy-locked{background:#1a2235;border:1px solid #2a3a55;border-radius:14px;padding:32px 24px;text-align:center;}
hr{border-color:#2a3a55;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">👤 用户档案</div>', unsafe_allow_html=True)
st.markdown('<p>完善档案后，AI 将根据你的情况提供个性化建议</p>', unsafe_allow_html=True)
st.markdown("---")

existing = load_profile()
col_form, col_preview = st.columns([3,2])

with col_form:
    st.markdown('<div class="section-label">基本信息</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        name = st.text_input("姓名", value=existing.get("name","") if existing else "")
    with c2:
        gender = st.selectbox("性别", ["男","女","其他"],
            index=["男","女","其他"].index(existing["gender"]) if existing and existing.get("gender") in ["男","女","其他"] else 0)
    c3,c4,c5 = st.columns(3)
    with c3:
        age = st.number_input("年龄", min_value=10, max_value=100, value=int(existing["age"]) if existing and existing.get("age") else 25)
    with c4:
        height = st.number_input("身高(cm)", min_value=100.0, max_value=250.0, step=0.5, value=float(existing["height"]) if existing and existing.get("height") else 170.0)
    with c5:
        weight = st.number_input("体重(kg)", min_value=30.0, max_value=300.0, step=0.5, value=float(existing["weight"]) if existing and existing.get("weight") else 65.0)
    if height>0 and weight>0:
        bmi = weight/((height/100)**2)
        bmi_label = "偏瘦" if bmi<18.5 else "正常" if bmi<24 else "超重" if bmi<28 else "肥胖"
        bmi_color = "#00d9f5" if bmi<18.5 else "#00f5a0" if bmi<24 else "#ffa500" if bmi<28 else "#ff5757"
        st.markdown(f'<p style="font-size:13px;">BMI：<span style="color:{bmi_color};font-weight:700;">{bmi:.1f}（{bmi_label}）</span></p>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">训练目标</div>', unsafe_allow_html=True)
    goal_opts = ["增肌","减脂","运动表现提升","健康维持","康复恢复"]
    goal = st.selectbox("主要目标", goal_opts, index=goal_opts.index(existing["goal"]) if existing and existing.get("goal") in goal_opts else 0)
    level_opts = ["新手（运动不足1年）","初级（1-2年）","中级（3-5年）","高级（5年以上）"]
    fitness_level = st.selectbox("训练水平", level_opts, index=level_opts.index(existing["fitness_level"]) if existing and existing.get("fitness_level") in level_opts else 0)

    st.markdown('<div class="section-label">健康信息</div>', unsafe_allow_html=True)
    health = st.text_area("健康状况/疾病史", value=existing.get("health_conditions","") if existing else "", placeholder="例如：高血压、膝关节损伤... 没有则填「无」", height=80)
    diet = st.text_area("饮食限制/过敏", value=existing.get("dietary_restrictions","") if existing else "", placeholder="例如：乳糖不耐受、素食... 没有则填「无」", height=60)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 保存基本档案", use_container_width=True, type="primary"):
        if not name.strip():
            st.error("请填写姓名")
        else:
            save_profile({"name":name,"age":age,"gender":gender,"height":height,"weight":weight,
                "goal":goal,"fitness_level":fitness_level,"health_conditions":health,"dietary_restrictions":diet})
            st.success("✅ 档案已保存！")
            st.rerun()

with col_preview:
    st.markdown('<div class="section-label">当前档案预览</div>', unsafe_allow_html=True)
    if existing:
        bmi_val = existing["weight"]/((existing["height"]/100)**2) if existing.get("height") and existing.get("weight") else 0
        rows = [("姓名",existing.get("name","—")),("年龄/性别",f'{existing.get("age","—")}岁/{existing.get("gender","—")}'),
                ("身高/体重",f'{existing.get("height","—")}cm/{existing.get("weight","—")}kg'),
                ("BMI",f"{bmi_val:.1f}"),("目标",existing.get("goal","—")),
                ("训练水平",existing.get("fitness_level","—")),("健康状况",existing.get("health_conditions","—")),
                ("饮食限制",existing.get("dietary_restrictions","—"))]
        rows_html="".join([f'<div class="saved-row"><span class="saved-key">{k}</span><span class="saved-val">{v}</span></div>' for k,v in rows])
        st.markdown(f'<div class="saved-card">{rows_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#4a6080;text-align:center;margin-top:40px;">尚未保存档案</p>', unsafe_allow_html=True)


# ===== 进阶档案区块（基础档案保存后才显示）=====
if existing:
    st.markdown("---")
    adv = load_advanced_profile() or {}

    has_adv = any(adv.get(k) for k in [
        "body_fat_pct","muscle_mass","fat_free_mass","visceral_fat","bone_mass","bmr",
        "chest_cm","waist_cm","hip_cm","left_thigh_cm","right_thigh_cm",
        "left_arm_cm","right_arm_cm","left_calf_cm","right_calf_cm"
    ])
    adv_emoji = "✅" if has_adv else "➕"
    adv_status = "已填写" if has_adv else "未填写"
    st.markdown(
        f'<p style="color:#00d9f5;font-weight:700;font-size:20px;">'
        f'📊 进阶档案 <span style="color:#8ca0b8;font-size:13px;font-weight:400;">{adv_emoji} {adv_status}</span></p>',
        unsafe_allow_html=True
    )
    st.caption("填写体测数据后，AI 训练师会更精准地为你设计训练计划。所有数据可选填，建议有体脂秤或体检数据后再填。")

    with st.expander("📊 展开/填写 进阶档案", expanded=False):
        # === 体测数据 ===
        st.markdown('<div class="section-label">体测数据（来自体脂秤或体检报告）</div>', unsafe_allow_html=True)
        adv_c1, adv_c2, adv_c3 = st.columns(3)
        with adv_c1:
            body_fat = st.number_input(
                "体脂率 (%)", min_value=0.0, max_value=80.0, step=0.1,
                value=float(adv.get("body_fat_pct") or 0),
                help="女性正常范围：21-31%；男性：10-22%",
                key="adv_bf"
            )
            muscle_mass = st.number_input(
                "肌肉量 (kg)", min_value=0.0, max_value=200.0, step=0.1,
                value=float(adv.get("muscle_mass") or 0),
                help="肌肉重量",
                key="adv_mm"
            )
            fat_free = st.number_input(
                "去脂体重 (kg)", min_value=0.0, max_value=200.0, step=0.1,
                value=float(adv.get("fat_free_mass") or 0),
                help="去掉脂肪后的体重",
                key="adv_ffm"
            )
        with adv_c2:
            visceral = st.number_input(
                "内脏脂肪等级", min_value=0, max_value=30, step=1,
                value=int(adv.get("visceral_fat") or 0),
                help="正常范围：1-9，10+ 偏高",
                key="adv_vf"
            )
            bone_mass = st.number_input(
                "骨盐量 (kg)", min_value=0.0, max_value=10.0, step=0.1,
                value=float(adv.get("bone_mass") or 0),
                help="骨骼无机物总量",
                key="adv_bm"
            )
            bmr = st.number_input(
                "基础代谢 (kcal)", min_value=0, max_value=5000, step=10,
                value=int(adv.get("bmr") or 0),
                help="静息状态下每日消耗",
                key="adv_bmr"
            )
        with adv_c3:
            water_pct = st.number_input(
                "体内水分 (%)", min_value=0.0, max_value=100.0, step=0.1,
                value=float(adv.get("body_water_pct") or 0),
                help="正常范围：女50-55%，男60-65%",
                key="adv_water"
            )
            measured_at = st.date_input(
                "测量日期",
                value=date.today() if not adv.get("measured_at") else (
                    datetime.strptime(adv["measured_at"], "%Y-%m-%d").date()
                    if isinstance(adv.get("measured_at"), str) else date.today()
                ),
                key="adv_measured"
            )

        st.markdown('<div class="section-label">围度数据（厘米）</div>', unsafe_allow_html=True)
        cir1, cir2, cir3 = st.columns(3)
        with cir1:
            chest_cm = st.number_input("胸围", min_value=0.0, max_value=200.0, step=0.5,
                                        value=float(adv.get("chest_cm") or 0), key="adv_chest")
            left_arm = st.number_input("左上臂围", min_value=0.0, max_value=80.0, step=0.5,
                                        value=float(adv.get("left_arm_cm") or 0), key="adv_larm")
            left_thigh = st.number_input("左大腿围", min_value=0.0, max_value=100.0, step=0.5,
                                          value=float(adv.get("left_thigh_cm") or 0), key="adv_lthigh")
            left_calf = st.number_input("左小腿围", min_value=0.0, max_value=80.0, step=0.5,
                                         value=float(adv.get("left_calf_cm") or 0), key="adv_lcalf")
        with cir2:
            waist_cm = st.number_input("腰围", min_value=0.0, max_value=200.0, step=0.5,
                                        value=float(adv.get("waist_cm") or 0), key="adv_waist")
            right_arm = st.number_input("右上臂围", min_value=0.0, max_value=80.0, step=0.5,
                                         value=float(adv.get("right_arm_cm") or 0), key="adv_rarm")
            right_thigh = st.number_input("右大腿围", min_value=0.0, max_value=100.0, step=0.5,
                                           value=float(adv.get("right_thigh_cm") or 0), key="adv_rthigh")
            right_calf = st.number_input("右小腿围", min_value=0.0, max_value=80.0, step=0.5,
                                          value=float(adv.get("right_calf_cm") or 0), key="adv_rcalf")
        with cir3:
            hip_cm = st.number_input("臀围", min_value=0.0, max_value=200.0, step=0.5,
                                      value=float(adv.get("hip_cm") or 0), key="adv_hip")
            st.markdown(
                '<div style="color:#8ca0b8;font-size:12px;line-height:1.7;margin-top:12px;'
                'background:rgba(0,217,245,0.06);border-left:3px solid #00d9f5;padding:10px 14px;border-radius:6px;">'
                '💡 围度测量建议：<br>'
                '• 上臂：自然下垂，最粗处<br>'
                '• 大腿：最粗处，通常臀线下方<br>'
                '• 小腿：最粗处<br>'
                '• 早晨空腹测量更准确'
                '</div>',
                unsafe_allow_html=True
            )

        adv_notes = st.text_area(
            "备注（可选）",
            value=adv.get("notes","") or "",
            placeholder="例如：测量条件、数据来源（体脂秤型号/医院体检等）",
            height=60, key="adv_notes"
        )

        adv_btn_c1, adv_btn_c2 = st.columns(2)
        with adv_btn_c1:
            if st.button("💾 保存进阶档案", use_container_width=True, type="primary", key="save_adv"):
                save_advanced_profile({
                    "body_fat_pct": body_fat or None,
                    "muscle_mass": muscle_mass or None,
                    "fat_free_mass": fat_free or None,
                    "visceral_fat": visceral or None,
                    "bone_mass": bone_mass or None,
                    "bmr": bmr or None,
                    "body_water_pct": water_pct or None,
                    "chest_cm": chest_cm or None,
                    "waist_cm": waist_cm or None,
                    "hip_cm": hip_cm or None,
                    "left_thigh_cm": left_thigh or None,
                    "right_thigh_cm": right_thigh or None,
                    "left_arm_cm": left_arm or None,
                    "right_arm_cm": right_arm or None,
                    "left_calf_cm": left_calf or None,
                    "right_calf_cm": right_calf or None,
                    "measured_at": measured_at.isoformat(),
                    "notes": adv_notes,
                })
                st.success("✅ 进阶档案已保存！AI 教练下次给出训练计划时会优先参考这些数据。")
                st.balloons()
                import time
                time.sleep(1.5)
                st.rerun()
        with adv_btn_c2:
            if st.button("🗑️ 清空进阶档案", use_container_width=True, key="clear_adv"):
                if st.session_state.get("confirm_clear_adv"):
                    clear_advanced_profile()
                    st.session_state.pop("confirm_clear_adv", None)
                    st.success("已清空")
                    st.rerun()
                else:
                    st.session_state["confirm_clear_adv"] = True
                    st.warning("再次点击以确认清空")

    # ===== 进阶档案预览（如果已有数据）=====
    if has_adv:
        adv_preview_items = []
        if adv.get("body_fat_pct"): adv_preview_items.append(("体脂率", f"{adv['body_fat_pct']}%"))
        if adv.get("muscle_mass"): adv_preview_items.append(("肌肉量", f"{adv['muscle_mass']} kg"))
        if adv.get("fat_free_mass"): adv_preview_items.append(("去脂体重", f"{adv['fat_free_mass']} kg"))
        if adv.get("visceral_fat"): adv_preview_items.append(("内脏脂肪", f"{adv['visceral_fat']} 级"))
        if adv.get("bone_mass"): adv_preview_items.append(("骨盐量", f"{adv['bone_mass']} kg"))
        if adv.get("bmr"): adv_preview_items.append(("基础代谢", f"{adv['bmr']} kcal"))
        if adv.get("chest_cm"): adv_preview_items.append(("胸围", f"{adv['chest_cm']} cm"))
        if adv.get("waist_cm"): adv_preview_items.append(("腰围", f"{adv['waist_cm']} cm"))
        if adv.get("hip_cm"): adv_preview_items.append(("臀围", f"{adv['hip_cm']} cm"))

        if adv_preview_items:
            preview_html = '<div style="background:#1a2235;border:1px solid #2a3a55;border-radius:14px;padding:16px 20px;margin-top:10px;">'
            preview_html += '<div style="color:#00d9f5;font-weight:700;font-size:14px;margin-bottom:10px;">📊 当前进阶数据</div>'
            preview_html += '<div style="display:flex;flex-wrap:wrap;gap:14px;">'
            for k, v in adv_preview_items:
                preview_html += (
                    f'<div style="background:rgba(0,217,245,0.06);border-radius:8px;'
                    f'padding:6px 12px;font-size:13px;">'
                    f'<span style="color:#8ca0b8;">{k}：</span>'
                    f'<span style="color:#00d9f5;font-weight:600;">{v}</span></div>'
                )
            preview_html += '</div></div>'
            st.markdown(preview_html, unsafe_allow_html=True)


# ===== 经期管理模块（仅女性显示）=====
if existing and existing.get("gender") == "女":
    st.markdown("---")
    st.markdown('<p style="color:#ff79b4;font-weight:700;font-size:20px;">🌸 经期管理</p>', unsafe_allow_html=True)
    st.caption("经期数据有隐私保护。一键安排训练时会自动避开经期，经期前后 3 天会询问你身体状态。")

    cycle_data = get_menstrual_cycle()
    has_pin = bool(cycle_data and cycle_data.get("privacy_pin"))

    # ===== 隐私模式：解锁验证 =====
    if has_pin and not st.session_state.get("period_unlocked"):
        st.markdown("""
        <div class="privacy-locked">
            <div style="font-size:48px;">🔒</div>
            <div style="color:#ff79b4;font-weight:700;font-size:18px;margin:12px 0;">经期数据已加密</div>
            <div style="color:#c8d8e8;font-size:13px;">输入 4 位数字密码解锁查看详情</div>
        </div>
        """, unsafe_allow_html=True)
        pl1, pl2, pl3 = st.columns([1, 2, 1])
        with pl2:
            pin_input = st.text_input("4 位数字密码", type="password", max_chars=4, key="period_pin_input")
            if st.button("🔓 解锁", use_container_width=True, type="primary"):
                if pin_input == cycle_data.get("privacy_pin"):
                    st.session_state["period_unlocked"] = True
                    st.success("✅ 已解锁")
                    st.rerun()
                else:
                    st.error("❌ 密码错误")
        with st.expander("忘记密码？"):
            st.warning("出于隐私保护，密码无法找回。如忘记密码，可清除所有经期数据后重新设置。")
            if st.button("🗑️ 清除所有经期数据（不可恢复）", key="forget_pin_clear"):
                if st.session_state.get("confirm_clear_period"):
                    delete_menstrual_cycle()
                    st.session_state.pop("confirm_clear_period", None)
                    st.session_state.pop("period_unlocked", None)
                    st.success("已清除所有经期数据")
                    st.rerun()
                else:
                    st.session_state["confirm_clear_period"] = True
                    st.warning("再次点击确认清除")
    else:
        # ===== 解锁后或未设密码：显示完整经期模块 =====
        period_tab1, period_tab2, period_tab3 = st.tabs(["⚙️ 设置", "📅 经期记录", "🔮 预测日历"])

        with period_tab1:
            pc1, pc2 = st.columns(2)
            with pc1:
                today = date.today()
                default_last = today - timedelta(days=14)
                if cycle_data and cycle_data.get("last_start_date"):
                    try:
                        default_last = datetime.strptime(cycle_data["last_start_date"], "%Y-%m-%d").date()
                    except: pass
                last_start = st.date_input(
                    "上次月经开始日期",
                    value=default_last,
                    max_value=today,
                    key="period_last_start")
            with pc2:
                cycle_length = st.number_input(
                    "平均周期长度（天）",
                    min_value=21, max_value=45,
                    value=cycle_data.get("cycle_length") if cycle_data else 28,
                    help="正常范围 21-35 天，平均 28 天",
                    key="period_cycle_len")

            pc3, pc4 = st.columns(2)
            with pc3:
                period_length = st.number_input(
                    "平均月经持续天数",
                    min_value=2, max_value=10,
                    value=cycle_data.get("period_length") if cycle_data else 5,
                    help="正常范围 3-7 天",
                    key="period_len")
            with pc4:
                auto_avoid = st.checkbox(
                    "一键安排训练时自动避开经期",
                    value=bool(cycle_data.get("auto_avoid")) if cycle_data else True,
                    help="勾选后，一键安排月历训练时经期日期会自动设为休息日",
                    key="period_auto_avoid")

            # 隐私密码设置 - 简化逻辑
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p style="color:#8ca0b8;font-size:13px;font-weight:600;">🔒 隐私保护（可选）</p>', unsafe_allow_html=True)
            pin_current = cycle_data.get("privacy_pin") if cycle_data else None

            if pin_current:
                st.info("🔐 当前已设置 4 位数字密码")
                ps1, ps2 = st.columns(2)
                with ps1:
                    new_pin_input = st.text_input(
                        "修改密码（留空则保留原密码）",
                        type="password", max_chars=4, key="period_change_pin",
                        placeholder="4位数字")
                with ps2:
                    if st.button("🗑️ 取消密码保护", use_container_width=True, key="remove_pin"):
                        from database import get_conn
                        conn = get_conn(); c = conn.cursor()
                        c.execute("UPDATE menstrual_cycle SET privacy_pin=NULL WHERE user_id=1")
                        conn.commit(); conn.close()
                        st.success("密码已取消")
                        st.rerun()
            else:
                new_pin_input = st.text_input(
                    "设置 4 位数字密码（留空表示不启用）",
                    type="password", max_chars=4, key="period_create_pin",
                    placeholder="4位数字",
                    help="设置后下次进入需输入密码才能查看经期详情")

            st.markdown("<br>", unsafe_allow_html=True)
            sv1, sv2 = st.columns(2)
            with sv1:
                if st.button("💾 保存经期设置", use_container_width=True, type="primary", key="save_period"):
                    # 直接在按钮回调最开头显示 - 确认按钮被点击
                    _debug_box = st.empty()
                    _debug_box.info("🔄 正在保存…")

                    try:
                        # 用 session_state 直接读取输入框值，更可靠
                        raw_pin = ""
                        if pin_current:
                            raw_pin = st.session_state.get("period_change_pin", "") or ""
                        else:
                            raw_pin = st.session_state.get("period_create_pin", "") or ""
                        raw_pin = raw_pin.strip()

                        # 决定要保存的 PIN
                        pin_to_save = pin_current
                        if raw_pin:
                            if len(raw_pin) == 4 and raw_pin.isdigit():
                                pin_to_save = raw_pin
                            else:
                                _debug_box.empty()
                                st.error(f"❌ 密码必须是 4 位数字（当前输入 {len(raw_pin)} 位）")
                                st.stop()

                        # 处理 last_start
                        if not last_start:
                            _debug_box.empty()
                            st.error("❌ 请选择上次月经开始日期")
                            st.stop()

                        save_menstrual_cycle(
                            last_start_date=last_start.isoformat(),
                            cycle_length=int(cycle_length),
                            period_length=int(period_length),
                            auto_avoid=int(bool(auto_avoid)),
                            privacy_pin=pin_to_save,
                            notes=(cycle_data.get("notes") if cycle_data else "") or ""
                        )
                        _debug_box.empty()
                        st.success(f"✅ 经期设置已保存（上次开始：{last_start.isoformat()}，周期：{cycle_length}天，持续：{period_length}天）")
                        st.balloons()

                        # 如果有密码 → 2 秒后自动锁回去
                        import time
                        if pin_to_save:
                            st.info("🔒 2 秒后自动锁定界面...")
                            time.sleep(2)
                            st.session_state.pop("period_unlocked", None)
                            st.rerun()
                        else:
                            time.sleep(1)
                            st.rerun()
                    except Exception as _err:
                        _debug_box.empty()
                        st.error(f"❌ 保存失败：{type(_err).__name__}: {_err}")
                        import traceback
                        st.code(traceback.format_exc(), language="python")
            with sv2:
                if st.button("🗑️ 清除所有经期数据", use_container_width=True, key="clear_period_all"):
                    if st.session_state.get("confirm_clear_period_all"):
                        delete_menstrual_cycle()
                        st.session_state.pop("confirm_clear_period_all", None)
                        st.session_state.pop("period_unlocked", None)
                        st.success("已清除所有经期数据")
                        st.rerun()
                    else:
                        st.session_state["confirm_clear_period_all"] = True
                        st.warning("再次点击以确认清除")

        with period_tab2:
            st.markdown('<p style="color:#c8d8e8;font-size:13px;">📝 实际经期记录会让预测更准确。每次经期开始/结束时记录一下。</p>', unsafe_allow_html=True)
            lc1, lc2 = st.columns(2)
            with lc1:
                log_start = st.date_input("本次开始日期", value=date.today(), key="log_start_date")
            with lc2:
                log_end = st.date_input("本次结束日期（如已结束）", value=date.today(), key="log_end_date")
            log_notes = st.text_input("备注（可选）", placeholder="如：量较多、伴随痛经...", key="log_notes")

            if st.button("➕ 记录这次经期", use_container_width=True, key="add_period_log"):
                add_menstrual_log(
                    start_date=log_start.isoformat(),
                    end_date=log_end.isoformat() if log_end >= log_start else None,
                    notes=log_notes
                )
                st.success("✅ 已记录")
                st.rerun()

            st.markdown("---")
            logs = get_recent_menstrual_logs(limit=12)
            if logs:
                st.markdown('<p style="color:#e8eaf0;font-weight:700;">最近 12 次记录</p>', unsafe_allow_html=True)
                for log in logs:
                    end_str = f" ~ {log['end_date']}" if log.get('end_date') else " ~ (进行中)"
                    note_str = f" · {log['notes']}" if log.get('notes') else ""
                    st.markdown(
                        f'<div style="background:#1a2235;border-left:3px solid #ff79b4;padding:10px 16px;'
                        f'margin:6px 0;border-radius:6px;color:#c8d8e8;font-size:13px;">'
                        f'🌸 {log["start_date"]}{end_str}{note_str}</div>',
                        unsafe_allow_html=True)
            else:
                st.info("还没有经期记录")

        with period_tab3:
            if cycle_data and cycle_data.get("last_start_date"):
                period_dates = predict_period_dates(weeks_ahead=8)
                future_dates = sorted([d for d in period_dates if d >= date.today()])
                if future_dates:
                    # 分组成连续的经期段
                    ranges = []
                    cur_start = future_dates[0]
                    cur_end = future_dates[0]
                    for d in future_dates[1:]:
                        if (d - cur_end).days == 1:
                            cur_end = d
                        else:
                            ranges.append((cur_start, cur_end))
                            cur_start = cur_end = d
                    ranges.append((cur_start, cur_end))

                    st.markdown('<p style="color:#e8eaf0;font-weight:700;">未来 8 周预测</p>', unsafe_allow_html=True)
                    st.caption("📌 这只是基于平均周期的预测，实际可能有 ±2-3 天浮动。每次记录实际经期会让预测更准。")
                    for ri, (rs, re_) in enumerate(ranges):
                        days_from_now = (rs - date.today()).days
                        if days_from_now < 0:
                            tag = "进行中"
                            color = "#ff79b4"
                        elif days_from_now == 0:
                            tag = "今天开始"
                            color = "#ff79b4"
                        elif days_from_now <= 7:
                            tag = f"{days_from_now} 天后"
                            color = "#ffaa3c"
                        else:
                            tag = f"{days_from_now} 天后"
                            color = "#8ca0b8"
                        st.markdown(
                            f'<div style="background:#1a2235;border:1px solid #2a3a55;padding:12px 18px;'
                            f'margin:6px 0;border-radius:8px;color:#c8d8e8;font-size:14px;">'
                            f'🌸 第 {ri+1} 次预测：<b>{rs.strftime("%m月%d日")}</b> ~ <b>{re_.strftime("%m月%d日")}</b> '
                            f'<span style="float:right;color:{color};font-weight:600;">{tag}</span></div>',
                            unsafe_allow_html=True)
                else:
                    st.info("尚无未来经期预测，请先在「设置」Tab 完善信息")
            else:
                st.info("请先在「设置」Tab 填写上次月经开始日期")
