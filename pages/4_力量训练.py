import streamlit as st
import sys, os
import json
from datetime import datetime, date, timedelta
import calendar

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    load_profile, save_chat, load_chat, clear_chat,
    save_plan, list_plans, get_plan, update_plan, delete_plan,
    add_schedule, get_schedules_by_date, get_schedules_in_range,
    update_schedule_status, update_schedule_time, mark_schedule_notified,
    delete_schedule, get_due_schedules, check_adjacent_muscle,
    start_session, update_session, finish_session,
    get_session, get_today_session, list_sessions, delete_session,
    get_setting, set_setting
)
from ai_engine import chat_with_ollama, check_ollama_status
from training_helpers import (
    parse_ai_plan_smart, check_injury_risk,
    get_nutrition_advice, progressive_overload_tip
)

WEEKDAY_NAMES = ["周一","周二","周三","周四","周五","周六","周日"]

# ===== 自愈：清理因之前 bug 导致的坏 checkbox state =====
# 如果有 keep_-xxxx_x_x 这种带负号 hash 的旧 state，全部清掉避免下次崩
_stale_keys = [k for k in list(st.session_state.keys()) if k.startswith("keep_") or k.startswith("bulk_default_") or k.startswith("bulk_request_")]
if _stale_keys and not st.session_state.get("_cleaned_stale_keep"):
    # 只在第一次访问页面时清理
    for k in _stale_keys:
        try:
            del st.session_state[k]
        except: pass
    st.session_state["_cleaned_stale_keep"] = True


# ============ 公共函数：渲染动作编辑器 ============
def _render_exercises_editor(day, prefix):
    """day 是 dict ref，直接修改其 exercises 列表"""
    import streamlit as st
    exes = day.setdefault("exercises", [])
    st.markdown('<p style="color:#c8d8e8;font-size:13px;margin-top:8px;">动作列表：</p>', unsafe_allow_html=True)
    for i, ex in enumerate(exes):
        col_n, col_s, col_r, col_w, col_x = st.columns([3, 1, 1.5, 1.5, 0.5])
        with col_n:
            ex["name"] = st.text_input("名称", value=ex.get("name",""),
                key=f"{prefix}_n_{i}", label_visibility="collapsed")
        with col_s:
            ex["sets"] = st.number_input("组",
                min_value=1, max_value=20,
                value=int(ex.get("sets", 3) or 3),
                key=f"{prefix}_s_{i}", label_visibility="collapsed")
        with col_r:
            ex["reps"] = st.text_input("次", value=str(ex.get("reps","10")),
                key=f"{prefix}_r_{i}", label_visibility="collapsed",
                placeholder="次")
        with col_w:
            ex["weight"] = st.text_input("kg",
                value=str(ex.get("weight","") or ""),
                key=f"{prefix}_w_{i}", label_visibility="collapsed",
                placeholder="kg")
        with col_x:
            if st.button("✕", key=f"{prefix}_del_{i}"):
                exes.pop(i)
                st.rerun()

    if st.button("➕ 添加动作", key=f"{prefix}_add", use_container_width=True):
        exes.append({"name":"新动作","sets":3,"reps":"10","weight":"","notes":""})
        st.rerun()


st.set_page_config(page_title="力量训练", page_icon="🏋️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@700&family=Noto+Sans+SC:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Noto Sans SC',sans-serif;}
input,textarea{color:#e8eaf0 !important;caret-color:#00d9f5 !important;}
label{color:#c8d8e8 !important;font-size:14px !important;}
[data-baseweb="menu"] li{color:#e8eaf0 !important;}
.stTabs [data-baseweb="tab"]{color:#8ca0b8 !important;}
.stTabs [aria-selected="true"]{color:#00d9f5 !important;border-bottom:2px solid #00d9f5 !important;}
.page-title{font-family:'Rajdhani',sans-serif;font-size:40px;font-weight:700;
    background:linear-gradient(90deg,#00d9f5,#7b61ff);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.chat-user{background:#1e2d42;border:1px solid #2a3a55;border-radius:12px;padding:12px 16px;margin:8px 0;color:#e8eaf0;font-size:14px;}
.chat-ai{background:#162032;border:1px solid #1a3040;border-radius:12px;padding:14px 18px;margin:8px 0;color:#e8eaf0;font-size:14px;line-height:1.9;}
.plan-card{background:#1a2235;border:1px solid #2a3a55;border-radius:14px;padding:16px;margin-bottom:12px;}
.plan-name{font-family:'Rajdhani',sans-serif;font-size:20px;color:#00d9f5;font-weight:700;}
.plan-meta{font-size:12px;color:#8ca0b8;margin-top:4px;}
.exercise-row{background:#162032;border:1px solid #2a3a55;border-radius:8px;padding:10px 14px;margin:6px 0;color:#e8eaf0;}
.alert-card{background:rgba(255,170,87,0.1);border:1px solid rgba(255,170,87,0.35);
    border-radius:12px;padding:16px 20px;color:#ffcc80;font-size:14px;line-height:1.7;}
.success-card{background:rgba(0,245,160,0.1);border:1px solid rgba(0,245,160,0.35);
    border-radius:12px;padding:16px 20px;color:#7fffc8;font-size:14px;line-height:1.7;}
.warning-card{background:rgba(255,99,99,0.1);border:1px solid rgba(255,99,99,0.4);
    border-radius:12px;padding:14px 18px;color:#ff9999;font-size:14px;line-height:1.7;}
.cal-day{background:#1a2235;border:1px solid #2a3a55;border-radius:8px;
    padding:6px;min-height:90px;font-size:11px;}
.cal-day-today{border-color:#00d9f5;background:rgba(0,217,245,0.06);}
.cal-day-rest{background:rgba(140,160,184,0.05);border-color:#3a4a65;}
.cal-day-num{font-weight:700;color:#c8d8e8;font-size:13px;}
.cal-event{background:rgba(0,217,245,0.15);border-left:3px solid #00d9f5;
    padding:3px 6px;margin-top:3px;border-radius:3px;font-size:10px;color:#7fdfff;
    overflow:hidden;text-overflow:ellipsis;}
.cal-event-rest{background:rgba(140,160,184,0.1);border-left:3px solid #8ca0b8;
    color:#8ca0b8;}
.due-banner{background:linear-gradient(90deg,rgba(0,217,245,0.15),rgba(123,97,255,0.15));
    border:2px solid #00d9f5;border-radius:12px;padding:18px 24px;margin-bottom:16px;}
.muscle-tag{display:inline-block;padding:3px 10px;border-radius:12px;font-size:12px;
    background:rgba(0,245,160,0.12);color:#00f5a0;border:1px solid rgba(0,245,160,0.3);
    margin-right:6px;}
.rest-tag{display:inline-block;padding:3px 10px;border-radius:12px;font-size:12px;
    background:rgba(140,160,184,0.15);color:#8ca0b8;border:1px solid rgba(140,160,184,0.3);}
hr{border-color:#2a3a55;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🏋️ 力量训练</div>', unsafe_allow_html=True)
profile = load_profile()
ollama_ok = check_ollama_status()

# ===================== 提醒检查 =====================
due_schedules = get_due_schedules()

# 经期前后 3 天询问（仅女性用户、有训练日程时）
if profile and profile.get("gender") == "女" and due_schedules:
    from database import is_near_period, add_menstrual_log, update_menstrual_log_end, get_recent_menstrual_logs
    today_dt = date.today()
    period_status = is_near_period(today_dt)

    if period_status and not st.session_state.get(f"period_dismissed_{today_dt.isoformat()}"):
        # 经期内 - 是否仍要训练
        if period_status == "in_period":
            st.warning(
                f"🌸 **今天处于预测经期内**\n\n"
                f"建议：根据自己身体状态决定是否训练。如经期反应较强烈（痛经、头晕、量大），"
                f"建议休息或只做轻度瑜伽/拉伸。如状态良好，可降低训练强度（重量减少 30%）继续。"
            )
            pcc1, pcc2 = st.columns(2)
            with pcc1:
                if st.button("✅ 我确认，今天休息", use_container_width=True, key="period_confirm_rest"):
                    # 跳过所有今天的训练日程
                    for sch in due_schedules:
                        update_schedule_status(sch['id'], 'skipped')
                        mark_schedule_notified(sch['id'])
                    st.session_state[f"period_dismissed_{today_dt.isoformat()}"] = True
                    st.success("好好休息～")
                    st.rerun()
            with pcc2:
                if st.button("💪 状态良好，照常训练", use_container_width=True, key="period_continue_train"):
                    st.session_state[f"period_dismissed_{today_dt.isoformat()}"] = True
                    st.rerun()

        # 经期前 1-3 天 - 询问是否已开始
        elif period_status.startswith("pre_"):
            days = period_status.split("_")[1]
            st.info(
                f"🌸 **预测经期将在 {days} 天内开始**\n\n"
                f"如果你的经期已经开始（提前了），点下面按钮记录并自动调整后续训练计划；"
                f"如未开始，可继续训练但可考虑降低强度。"
            )
            pcc1, pcc2 = st.columns(2)
            with pcc1:
                if st.button("🌸 经期已经开始（今天）", use_container_width=True, key="period_started_today"):
                    add_menstrual_log(start_date=today_dt.isoformat(), notes="提前开始")
                    for sch in due_schedules:
                        update_schedule_status(sch['id'], 'skipped')
                        mark_schedule_notified(sch['id'])
                    st.session_state[f"period_dismissed_{today_dt.isoformat()}"] = True
                    st.success("已记录。今天的训练已自动改为休息～")
                    st.rerun()
            with pcc2:
                if st.button("还没开始，继续训练", use_container_width=True, key="period_not_started"):
                    st.session_state[f"period_dismissed_{today_dt.isoformat()}"] = True
                    st.rerun()

        # 经期后 1-3 天 - 询问是否已结束
        elif period_status.startswith("post_"):
            days = period_status.split("_")[1]
            st.info(
                f"🌸 **预测经期已结束 {days} 天**\n\n"
                f"如果经期还没结束（延后了），点下面按钮记录；"
                f"如已结束，建议本周训练强度从轻量开始逐步恢复。"
            )
            pcc1, pcc2 = st.columns(2)
            with pcc1:
                if st.button("🌸 经期还没结束", use_container_width=True, key="period_still_ongoing"):
                    # 更新最近一条 log 的结束日期为 today + 几天
                    logs = get_recent_menstrual_logs(limit=1)
                    if logs and not logs[0].get("end_date"):
                        # 还没设置结束日期 - 不动，等用户后续记录
                        pass
                    for sch in due_schedules:
                        update_schedule_status(sch['id'], 'skipped')
                        mark_schedule_notified(sch['id'])
                    st.session_state[f"period_dismissed_{today_dt.isoformat()}"] = True
                    st.success("已记录，今天休息～")
                    st.rerun()
            with pcc2:
                if st.button("已结束，继续训练", use_container_width=True, key="period_ended"):
                    # 把最近一条 log 的 end_date 设为 today - days
                    logs = get_recent_menstrual_logs(limit=1)
                    if logs and not logs[0].get("end_date"):
                        try:
                            ended_at = today_dt - timedelta(days=int(days))
                            update_menstrual_log_end(logs[0]["id"], ended_at.isoformat())
                        except: pass
                    st.session_state[f"period_dismissed_{today_dt.isoformat()}"] = True
                    st.rerun()

if due_schedules:
    for sch in due_schedules:
        di = sch.get("day_info", {})
        if di.get("is_rest"):
            continue  # 休息日不弹提醒
        muscle = di.get("muscle_group", "训练")
        with st.container():
            st.markdown(f"""
            <div class="due-banner">
                <div style="font-size:13px;color:#8ca0b8;letter-spacing:2px;">⏰ 训练提醒</div>
                <div style="font-size:22px;font-weight:700;color:#00d9f5;margin:6px 0;">
                    {sch.get('plan_name','训练')} · {sch['schedule_time']}
                </div>
                <div style="font-size:13px;color:#c8d8e8;">
                    今天练：<span class="muscle-tag">{muscle}</span> · 该开始训练了！
                </div>
            </div>
            """, unsafe_allow_html=True)
            cb1, cb2, cb3 = st.columns(3)
            with cb1:
                if st.button("✅ 开始训练", key=f"due_start_{sch['id']}", use_container_width=True, type="primary"):
                    mark_schedule_notified(sch['id'])
                    st.session_state["jump_schedule_id"] = sch['id']
                    st.success("✅ 请切换到下方「🎯 今日训练」Tab 开始训练")
                    st.rerun()
            with cb2:
                if st.button("⏰ 推迟30分钟", key=f"due_delay_{sch['id']}", use_container_width=True):
                    try:
                        # 用原训练时间作为基准加30分钟
                        h, m = sch['schedule_time'].split(":")
                        h_int, m_int = int(h), int(m)
                        # 加30分钟，处理跨小时
                        total_minutes = h_int * 60 + m_int + 30
                        new_h = (total_minutes // 60) % 24
                        new_m = total_minutes % 60
                        new_time_str = f"{new_h:02d}:{new_m:02d}"
                        update_schedule_time(sch['id'], new_time_str)
                        st.success(f"已推迟到 {new_time_str}")
                        st.rerun()
                    except Exception as _e:
                        st.error(f"推迟失败：{_e}")
            with cb3:
                if st.button("❌ 跳过", key=f"due_skip_{sch['id']}", use_container_width=True):
                    update_schedule_status(sch['id'], 'skipped')
                    mark_schedule_notified(sch['id'])
                    st.success("已跳过今天的训练")
                    st.rerun()

tabs = st.tabs([
    "🤖 AI训练计划",
    "📋 计划模板库",
    "📅 训练日历",
    "🎯 今日训练",
    "💚 AI联动建议",
    "📈 进步曲线"
])

# =================================================================
# Tab1: AI训练计划
# =================================================================
with tabs[0]:
    MODULE = "training"
    if "training_messages" not in st.session_state:
        st.session_state.training_messages = load_chat(MODULE)
    if not ollama_ok:
        st.error("❌ AI 服务未启动")

    if st.session_state.get("train_pending") and ollama_ok:
        pending_q = st.session_state.pop("train_pending")
        st.session_state.training_messages.append({"role":"user","content":pending_q})
        save_chat(MODULE, "user", pending_q)
        with st.spinner("AI教练思考中..."):
            reply = chat_with_ollama(st.session_state.training_messages, MODULE, profile)
        st.session_state.training_messages.append({"role":"assistant","content":reply})
        save_chat(MODULE, "assistant", reply)
        st.rerun()

    st.markdown('<p style="font-weight:700;color:#e8eaf0;">快速生成计划</p>', unsafe_allow_html=True)
    plan_qs = ["给我一个本周训练计划","胸肌训练计划","背部训练计划","腿部训练计划",
               "全身力量3天/周","减脂有氧+力量计划","只有哑铃怎么练？","解释渐进超负荷"]
    pc = st.columns(4)
    for i, q in enumerate(plan_qs):
        with pc[i%4]:
            if st.button(q, key=f"tq{i}", use_container_width=True):
                if not ollama_ok: st.error("AI未启动")
                else:
                    st.session_state["train_pending"] = q
                    st.rerun()

    st.markdown("---")
    for msg in st.session_state.training_messages:
        cls = "chat-user" if msg["role"]=="user" else "chat-ai"
        icon = "🙋" if msg["role"]=="user" else "🤖"
        st.markdown(f'<div class="{cls}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    # 保存最新AI计划
    if st.session_state.training_messages:
        last_msg = st.session_state.training_messages[-1]
        if last_msg["role"] == "assistant":
            st.markdown("---")
            st.markdown('<p style="color:#00f5a0;font-weight:700;">💾 把最新AI计划保存到模板库</p>', unsafe_allow_html=True)

            # ===== 直接内联解析 - 绕过模块缓存 =====
            import re as _re_inline

            _AK = ["深蹲","硬拉","蹲","腿举","蹬腿","弓步","保加利亚","哈克","前蹲","后蹲",
                "高脚杯","罗马尼亚","RDL","腿屈伸","腿弯举","提踵","髋外展","髋内收","臀冲","臀推","臀桥",
                "卧推","推举","推胸","肩推","推","夹胸","飞鸟","三头","下压","臂屈伸","颈后","过头",
                "划船","下拉","引体","弯举","二头","面拉","耸肩","屈臂","拉力","拉绳","拉",
                "侧平举","前平举","后束","三角","反向飞鸟","侧向提举","提举","侧抬","前抬","侧举","前举","前提","抬举","提起","提",
                "卷腹","仰卧起坐","平板支撑","俄罗斯转体","悬挂举腿","举腿","山羊挺身","罗马椅","支撑",
                "杠铃","哑铃","壶铃","史密斯","绳索","拉索","龙门架","坐姿","站姿","俯身","上斜","下斜","平板","T杠",
                "俯卧撑","深蹲跳","波比","登山者",
                "蹲举","划","伸展","伸","飞",
                # 英文动作名
                "squat","lunge","bench","press","row","curl","extension","fly","raise","pulldown","pullup","pull-up",
                "deadlift","plank","push","press","crunch"]

            _SK = ["热身","拉伸","放松","休息","组间","建议","注意","提示",
                "胸部和","背部和","腿部和","肩部和","手臂和",
                "训练日","可选","替换","好好休息","好好恢复",
                "完成后","完成指定","完成时","保持","专注于","确保",
                "从一个","根据你","组间休息","使用","冷却","cool-down","warm-up"]

            _WD = {
                "周一":0,"星期一":0,"礼拜一":0,"第一天":0,"第1天":0,"day1":0,"day 1":0,"monday":0,
                "周二":1,"星期二":1,"礼拜二":1,"第二天":1,"第2天":1,"day2":1,"day 2":1,"tuesday":1,
                "周三":2,"星期三":2,"礼拜三":2,"第三天":2,"第3天":2,"day3":2,"day 3":2,"wednesday":2,
                "周四":3,"星期四":3,"礼拜四":3,"第四天":3,"第4天":3,"day4":3,"day 4":3,"thursday":3,
                "周五":4,"星期五":4,"礼拜五":4,"第五天":4,"第5天":4,"day5":4,"day 5":4,"friday":4,
                "周六":5,"星期六":5,"礼拜六":5,"第六天":5,"第6天":5,"day6":5,"day 6":5,"saturday":5,
                "周日":6,"周天":6,"星期日":6,"星期天":6,"礼拜日":6,"礼拜天":6,"第七天":6,"第7天":6,"day7":6,"day 7":6,"sunday":6,
            }

            def _parse_line_inline(line):
                """内联版动作解析"""
                line = line.strip()
                if not line or len(line) < 4:
                    return None
                # 去除markdown标记
                line_clean = line.lstrip("*-·•—◦○ ").rstrip("*").strip()
                if any(kw in line_clean for kw in _SK):
                    return None

                # 必须含动作关键词（中英文不区分大小写）
                line_lower = line_clean.lower()
                if not any(kw.lower() in line_lower for kw in _AK):
                    return None

                # 提取组数次数
                m_sets = _re_inline.search(r'(\d+)\s*(?:组|sets?)', line_clean, _re_inline.IGNORECASE)
                m_reps = _re_inline.search(r'(\d+(?:[\-～~至到]\d+)?)\s*(?:次|下|个|reps?|秒|seconds?|分钟|分)', line_clean, _re_inline.IGNORECASE)
                m_xy = _re_inline.search(r'(\d+)\s*[xX×\*]\s*(\d+(?:[\-～~]\d+)?)', line_clean)

                sets, reps, reps_unit = None, None, "次"

                if m_sets and m_reps:
                    sets = int(m_sets.group(1))
                    reps = m_reps.group(1).replace("～","-").replace("~","-").replace("至","-").replace("到","-")
                    u_match = _re_inline.search(r'(?:次|下|个|秒|seconds?|分钟|分|reps?)', m_reps.group(0), _re_inline.IGNORECASE)
                    if u_match:
                        u = u_match.group(0).lower()
                        if u in ("秒","seconds","second"): reps_unit = "秒"
                        elif u in ("分钟","分"): reps_unit = "分钟"
                elif m_sets and m_xy:
                    sets = int(m_sets.group(1))
                    reps = m_xy.group(2).replace("～","-").replace("~","-")
                    after = line_clean[m_xy.end():m_xy.end()+15].lower()
                    if "秒" in after or "second" in after: reps_unit = "秒"
                elif m_xy and not m_sets:
                    sets = int(m_xy.group(1))
                    reps = m_xy.group(2).replace("～","-").replace("~","-")
                else:
                    return None

                if sets < 1 or sets > 10:
                    return None

                reps_display = f"{reps}{reps_unit}" if reps_unit != "次" else reps

                name = line_clean
                name = _re_inline.sub(r'^\s*[\d①②③④⑤⑥⑦⑧⑨⑩\.、\)\-—\s]+', '', name)
                name = _re_inline.split(r'[：:]', name)[0]
                name = _re_inline.sub(r'\d+\s*(?:组|sets?).*$', '', name, flags=_re_inline.IGNORECASE)
                name = _re_inline.sub(r'\d+\s*[xX×]\s*\d+.*$', '', name)
                name = _re_inline.sub(r'[\(（].*?[\)）]', '', name)
                name = _re_inline.sub(r'[，,。.\s]+$', '', name).strip()

                # 自动纠错（防止哑铲、扛铃等AI翻译错字）
                _typo_fixes = {
                    "哑铲":"哑铃","亚铃":"哑铃","亚玲":"哑铃","哑玲":"哑铃",
                    "扛铃":"杠铃","杠玲":"杠铃","杠零":"杠铃",
                    "壶玲":"壶铃","壶零":"壶铃",
                    "深躯":"深蹲","深蹭":"深蹲","硬来":"硬拉","硬力":"硬拉",
                    "罗玛尼亚":"罗马尼亚","保加里亚":"保加利亚",
                    "卧堆":"卧推","推剧":"推举","推具":"推举",
                    "弯距":"弯举","划装":"划船","下垃":"下拉","提中":"提踵",
                    "肱二投":"肱二头","肱三投":"肱三头",
                    "胸不":"胸部","背不":"背部","腿不":"腿部","肩不":"肩部",
                }
                for _wrong, _right in _typo_fixes.items():
                    name = name.replace(_wrong, _right)

                if len(name) < 2 or len(name) > 30:
                    return None

                return {"name":name, "sets":sets, "reps":reps_display, "weight":"", "notes":""}

            def _detect_day_inline(line):
                """内联版日期标题识别"""
                line = line.strip()
                # 去markdown
                line_clean = line.replace("**","").replace("*","")
                # 如果是动作行（含组数次数），不当标题
                if _re_inline.search(r'\d+\s*(?:组|sets?)', line_clean, _re_inline.IGNORECASE) and \
                   _re_inline.search(r'\d+\s*(?:次|下|个|reps?|秒)', line_clean, _re_inline.IGNORECASE):
                    return None

                line_lower = line_clean.lower()
                matched_widx = None
                for kw, widx in _WD.items():
                    if kw.lower() in line_lower:
                        matched_widx = widx
                        break
                if matched_widx is None:
                    return None

                is_rest = any(kw in line for kw in ["休息","Rest","rest","REST","off"])

                muscle = "未指定"
                if not is_rest:
                    # 部位识别 - 用加权评分（每个关键词+1），最高分的优先
                    part_keywords = {
                        "胸": ["胸","chest"],
                        "背": ["背","back"],
                        "腿": ["腿","leg"],
                        "臀": ["臀","屁股","glute"],
                        "肩": ["肩","shoulder"],
                        "三头": ["三头","triceps"],
                        "二头": ["二头","biceps"],
                        "核心": ["腹","核心","abs","core"],
                    }
                    scores = {}
                    for part, kws in part_keywords.items():
                        for kw in kws:
                            if kw in line_lower:
                                scores[part] = scores.get(part, 0) + 1
                    # 用加号串接 ≤ 2 个，超过取得分最高的 2 个
                    if scores:
                        sorted_parts = sorted(scores.items(), key=lambda x: -x[1])
                        if len(sorted_parts) <= 2:
                            muscle = "+".join([p for p, _ in sorted_parts])
                        else:
                            # 3+ 部位 - 取前两个，不轻易判"全身"
                            muscle = "+".join([p for p, _ in sorted_parts[:2]])
                return (matched_widx, is_rest, muscle)

            # 用内联函数重新解析
            _content = last_msg["content"]
            _lines = _content.split("\n")

            _day_markers = []
            for _i, _l in enumerate(_lines):
                _info = _detect_day_inline(_l)
                if _info:
                    _day_markers.append((_i, _info[0], _info[1], _info[2]))

            # 判断：用户问的是单日训练还是周计划？
            _user_msgs_check = [m["content"] for m in st.session_state.training_messages if m["role"] == "user"]
            _user_last_q = _user_msgs_check[-1] if _user_msgs_check else ""

            # 用户明确说"一天/单日/某天"训练 → 强制单日
            _force_single = any(kw in _user_last_q for kw in [
                "一天","单日","当天","今天","明天","一次","一日",
                "一天训练","一日训练","单日训练","当天训练","今日训练","明日训练"
            ])

            # 真正的周计划：天标题 ≥ 2 个 且 用户没说"一天"
            _is_real_weekly = len(_day_markers) >= 2 and not _force_single

            if _is_real_weekly:
                # 周计划
                _days_data = {}
                for _mi, (_li, _widx, _rest, _muscle) in enumerate(_day_markers):
                    _next_li = _day_markers[_mi+1][0] if _mi+1 < len(_day_markers) else len(_lines)
                    if _rest:
                        _days_data[_widx] = {"muscle_group":"休息","is_rest":True,"exercises":[]}
                    else:
                        _exes = []
                        _seen = set()
                        for _j in range(_li+1, _next_li):
                            _ex = _parse_line_inline(_lines[_j])
                            if _ex and _ex["name"] not in _seen:
                                _exes.append(_ex)
                                _seen.add(_ex["name"])
                        _days_data[_widx] = {"muscle_group":_muscle,"is_rest":False,"exercises":_exes}
                # 补齐7天
                for _w in range(7):
                    if _w not in _days_data:
                        _days_data[_w] = {"muscle_group":"休息","is_rest":True,"exercises":[]}
                _days_data_str = {str(k):v for k,v in _days_data.items()}
                # 判断是否真的有动作
                _valid = any(d["exercises"] for d in _days_data_str.values())
                if _valid:
                    plan_type = "weekly"
                    days_data = _days_data_str
                else:
                    plan_type = "single"
                    days_data = {}
            else:
                # 单日（包括用户问"一天"训练 或 只有1个天标题/没天标题的情况）
                _exes = []
                _seen = set()
                for _l in _lines:
                    _ex = _parse_line_inline(_l)
                    if _ex and _ex["name"] not in _seen:
                        _exes.append(_ex)
                        _seen.add(_ex["name"])
                if _exes:
                    plan_type = "single"
                    # 部位推断：先看 AI 回复+用户最近消息的标题关键词，再看动作内容
                    _all_text = last_msg["content"]
                    # 也参考用户最近的提问
                    _user_msgs = [m["content"] for m in st.session_state.training_messages if m["role"] == "user"]
                    if _user_msgs:
                        _all_text = _user_msgs[-1] + "\n" + _all_text

                    _muscle = "未指定"

                    # ===== 策略1：从用户提问+AI 标题里直接计数部位关键词 =====
                    # 这是最可靠的信号：用户问"臀腿训练" → 文本里有"臀"和"腿"
                    _part_kws = {
                        "胸": ["胸"],
                        "背": ["背"],
                        "腿": ["腿","股四头","股二头","腘绳"],
                        "臀": ["臀","屁股"],
                        "肩": ["肩","三角肌"],
                        "二头": ["二头","肱二头"],
                        "三头": ["三头","肱三头"],
                        "核心": ["核心","腹肌","卷腹"],
                        "手臂": ["手臂","胳膊"],
                    }

                    # 只在用户提问 + AI 前 800 字（通常包含计划标题和介绍）里数
                    _user_q = _user_msgs[-1] if _user_msgs else ""
                    _title_zone = _user_q + "\n" + last_msg["content"][:800]
                    _title_scores = {}
                    for _p, _kws in _part_kws.items():
                        for _kw in _kws:
                            _title_scores[_p] = _title_scores.get(_p, 0) + _title_zone.count(_kw)

                    # 过滤掉得分=0的
                    _title_scores = {k: v for k, v in _title_scores.items() if v > 0}

                    if _title_scores:
                        # 取得分最高的 1-2 个
                        _sorted = sorted(_title_scores.items(), key=lambda x: -x[1])
                        if len(_sorted) == 1:
                            _muscle = _sorted[0][0]
                        else:
                            top1_score = _sorted[0][1]
                            top2_score = _sorted[1][1]
                            # 第二名只要 ≥ 第一名 25% 就算组合
                            # 修正：放宽门槛，避免 (2, 1) 这种被判单部位
                            if top2_score >= 1 and top2_score >= top1_score * 0.25:
                                _muscle = f"{_sorted[0][0]}+{_sorted[1][0]}"
                            else:
                                _muscle = _sorted[0][0]

                    # ===== 策略2：fallback - 用动作名识别 =====
                    if _muscle == "未指定":
                        _scores = {"胸":0,"背":0,"腿":0,"肩":0,"二头":0,"三头":0,"核心":0,"臀":0}
                        _ex_text = " ".join([e["name"] for e in _exes])
                        _strong = {
                            "胸":["卧推","推胸","夹胸"],
                            "背":["下拉","划船","引体"],
                            "腿":["深蹲","腿举","蹬腿","腿屈伸","腿弯举","弓步"],
                            "肩":["肩推","侧平举","前平举","侧抬","前抬"],
                            "二头":["弯举"],
                            "三头":["三头下压","臂屈伸","颈后"],
                            "核心":["卷腹","平板支撑","俄罗斯转体","悬挂举腿","山羊挺身"],
                            "臀":["臀冲","臀桥","臀推"],
                        }
                        for _m, _kws in _strong.items():
                            for _kw in _kws:
                                _scores[_m] += _ex_text.count(_kw)
                        _detected = [(m, s) for m, s in _scores.items() if s >= 1]
                        if _detected:
                            _sorted = sorted(_detected, key=lambda x: -x[1])
                            # 3+ 个部位都至少检测到一次动作 → 真正的"全身训练"
                            if len(_sorted) >= 3:
                                _muscle = "全身"
                            elif len(_sorted) == 1:
                                _muscle = _sorted[0][0]
                            else:
                                _muscle = f"{_sorted[0][0]}+{_sorted[1][0]}"

                    days_data = {"single":{"muscle_group":_muscle,"is_rest":False,"exercises":_exes}}
                else:
                    plan_type = "single"
                    days_data = {}

            parsed = {"plan_type":plan_type, "days_data":days_data}
            # ===== 内联解析结束 =====

            # 统计总动作数
            total_ex = sum(len(d.get("exercises", [])) for d in days_data.values())

            # ===== 调试信息 =====
            with st.expander("🔧 调试信息（识别失败时点开查看）", expanded=False):
                st.write(f"**plan_type:** `{plan_type}`")
                st.write(f"**days_data 键:** `{list(days_data.keys())}`")
                st.write(f"**总动作数:** `{total_ex}`")
                st.write(f"**识别到的天标题数:** `{len(_day_markers)}`")

                # 显示识别路径
                if plan_type == "single":
                    sd = days_data.get("single", {})
                    st.write(f"**识别到的部位:** `{sd.get('muscle_group', '未指定')}`")

                    # 重新跑一遍部位推断显示中间值
                    _user_msgs_dbg = [m["content"] for m in st.session_state.training_messages if m["role"] == "user"]
                    _last_user_q = _user_msgs_dbg[-1] if _user_msgs_dbg else "(无)"
                    _title_zone_dbg = (_user_msgs_dbg[-1] if _user_msgs_dbg else "") + "\n" + last_msg["content"][:800]

                    st.write(f"**用户最后一句提问:** `{_last_user_q[:100]}`")
                    st.write(f"**AI回复前 200 字:** `{last_msg['content'][:200]}`")

                    _part_kws_dbg = {
                        "胸": ["胸"], "背": ["背"],
                        "腿": ["腿","股四头","股二头","腘绳"], "臀": ["臀","屁股"],
                        "肩": ["肩","三角肌"], "二头": ["二头","肱二头"],
                        "三头": ["三头","肱三头"], "核心": ["核心","腹肌","卷腹"],
                        "手臂": ["手臂","胳膊"],
                    }
                    _title_scores_dbg = {}
                    for _p, _kws in _part_kws_dbg.items():
                        for _kw in _kws:
                            _title_scores_dbg[_p] = _title_scores_dbg.get(_p, 0) + _title_zone_dbg.count(_kw)
                    _title_scores_dbg = {k: v for k, v in _title_scores_dbg.items() if v > 0}
                    st.write(f"**部位关键词得分:** `{_title_scores_dbg}`")

                    # 显示动作列表
                    if sd.get("exercises"):
                        st.write("**识别到的动作:**")
                        for ex in sd["exercises"]:
                            st.write(f"  - {ex['name']} ({ex['sets']}组 × {ex['reps']})")

                st.write("**完整解析结果:**")
                st.json(parsed)
            # ===== 调试信息结束 =====

            if total_ex > 0:
                if plan_type == "weekly":
                    train_days = sum(1 for d in days_data.values() if not d.get("is_rest"))
                    rest_days = sum(1 for d in days_data.values() if d.get("is_rest"))
                    st.markdown(f'<p style="color:#c8d8e8;font-size:13px;">📅 一周计划：<b style="color:#00f5a0;">{train_days}</b> 个训练日 · <b style="color:#8ca0b8;">{rest_days}</b> 个休息日 · 共 <b style="color:#00f5a0;">{total_ex}</b> 个动作</p>', unsafe_allow_html=True)

                    with st.expander(f"👀 查看一周分配详情"):
                        for w in range(7):
                            d = days_data.get(str(w), {})
                            if d.get("is_rest"):
                                st.markdown(f'<div class="exercise-row">{WEEKDAY_NAMES[w]} · <span class="rest-tag">休息日</span></div>', unsafe_allow_html=True)
                            elif d.get("exercises"):
                                st.markdown(f'<div class="exercise-row">{WEEKDAY_NAMES[w]} · <span class="muscle-tag">{d.get("muscle_group", "训练")}</span></div>', unsafe_allow_html=True)
                                for ex in d["exercises"]:
                                    _clean_n = ex["name"].replace("**","").replace("*","").strip()
                                    st.markdown(f'<div style="margin-left:24px;font-size:13px;color:#c8d8e8;padding:3px 0;">· {_clean_n} - {ex["sets"]}组 × {ex["reps"]}</div>', unsafe_allow_html=True)
                else:
                    single_day = days_data.get("single", {})
                    st.markdown(f'<p style="color:#c8d8e8;font-size:13px;">📋 单日计划 · 部位：<b style="color:#00f5a0;">{single_day.get("muscle_group","未指定")}</b> · 共 <b style="color:#00f5a0;">{total_ex}</b> 个动作</p>', unsafe_allow_html=True)
                    with st.expander(f"👀 查看动作列表"):
                        for ex in single_day.get("exercises", []):
                            _clean_n = ex["name"].replace("**","").replace("*","").strip()
                            st.markdown(f'<div class="exercise-row">· {_clean_n} - {ex["sets"]}组 × {ex["reps"]}</div>', unsafe_allow_html=True)

                # 清理 days_data 中所有动作名的 markdown 标记（保存前清洗）
                for _dv in days_data.values():
                    for _ex in _dv.get("exercises", []):
                        _ex["name"] = _ex["name"].replace("**","").replace("*","").strip()

                # 基于最后一条AI消息的内容长度做key，每次AI更新都重置输入框
                _msg_hash = str(hash(last_msg["content"]))[:8]
                _name_key = f"save_plan_name_{_msg_hash}"
                _type_key = f"save_plan_type_{_msg_hash}"

                # ===== 自定义编辑：勾选要保留的动作 =====
                with st.expander("✏️ 自定义计划（勾选要保留的动作）", expanded=False):
                    st.caption("不勾的动作保存时会被剔除。适合不喜欢某个动作、或想精简训练量。")

                    # 用 generation 让 checkbox 完全重建（绕开 streamlit 的"key已存在"限制）
                    _gen_key = f"bulk_gen_{_msg_hash}"
                    _default_key = f"bulk_default_{_msg_hash}"
                    if _gen_key not in st.session_state:
                        st.session_state[_gen_key] = 0
                    if _default_key not in st.session_state:
                        st.session_state[_default_key] = True

                    _generation = st.session_state[_gen_key]
                    _default_checked = st.session_state[_default_key]

                    # 按钮放上面，方便操作
                    _cb_c1, _cb_c2 = st.columns(2)
                    with _cb_c1:
                        if st.button("☑ 全部勾选", key=f"all_check_{_msg_hash}_g{_generation}",
                                     use_container_width=True):
                            st.session_state[_default_key] = True
                            st.session_state[_gen_key] = _generation + 1
                            st.rerun()
                    with _cb_c2:
                        if st.button("☐ 全部取消", key=f"none_check_{_msg_hash}_g{_generation}",
                                     use_container_width=True):
                            st.session_state[_default_key] = False
                            st.session_state[_gen_key] = _generation + 1
                            st.rerun()

                    st.markdown("---")

                    if plan_type == "weekly":
                        for _widx_str, _day in days_data.items():
                            if _day.get("is_rest") or not _day.get("exercises"):
                                continue
                            try:
                                _w_int = int(_widx_str)
                                _wname = ["周一","周二","周三","周四","周五","周六","周日"][_w_int]
                            except: _wname = f"第{_widx_str}天"
                            st.markdown(
                                f'<p style="color:#00d9f5;font-weight:700;font-size:14px;margin-top:10px;">'
                                f'{_wname}（{_day.get("muscle_group","训练")}）</p>',
                                unsafe_allow_html=True
                            )
                            for _ei, _ex in enumerate(_day["exercises"]):
                                # key 带 generation -> 全选/取消时创建全新 widget
                                _ck_key = f"keep_{_msg_hash}_g{_generation}_{_widx_str}_{_ei}"
                                st.checkbox(
                                    f'{_ex["name"]} · {_ex["sets"]}组 × {_ex["reps"]}',
                                    value=_default_checked,
                                    key=_ck_key
                                )
                    else:
                        _sd = days_data.get("single", {})
                        if _sd.get("exercises"):
                            for _ei, _ex in enumerate(_sd["exercises"]):
                                _ck_key = f"keep_{_msg_hash}_g{_generation}_single_{_ei}"
                                st.checkbox(
                                    f'{_ex["name"]} · {_ex["sets"]}组 × {_ex["reps"]}',
                                    value=_default_checked,
                                    key=_ck_key
                                )

                sp1, sp2 = st.columns(2)
                with sp1:
                    new_plan_name = st.text_input(
                        "计划名称",
                        value=f"AI计划_{datetime.now().strftime('%m%d_%H%M')}",
                        key=_name_key)
                with sp2:
                    _default_type_idx = 1 if plan_type == "weekly" else 0
                    plan_type_choice = st.radio(
                        "计划类型",
                        ["single", "weekly"],
                        format_func=lambda x: "📋 单日计划" if x == "single" else "📅 一周计划",
                        index=_default_type_idx,
                        horizontal=True, key=_type_key)

                if st.button("💾 保存为计划模板", type="primary", use_container_width=True):
                    # 先根据勾选过滤动作
                    filtered_days = {}
                    # 读取当前 generation 的 checkbox 状态
                    _read_gen = st.session_state.get(f"bulk_gen_{_msg_hash}", 0)
                    if plan_type == "weekly":
                        for _widx_str, _day in days_data.items():
                            if _day.get("is_rest"):
                                filtered_days[_widx_str] = dict(_day)
                                continue
                            kept = []
                            for _ei, _ex in enumerate(_day.get("exercises", [])):
                                _ck_key = f"keep_{_msg_hash}_g{_read_gen}_{_widx_str}_{_ei}"
                                if st.session_state.get(_ck_key, True):
                                    kept.append(_ex)
                            new_day = dict(_day)
                            new_day["exercises"] = kept
                            # 如果一天动作被清空，标记为休息
                            if not kept:
                                new_day["is_rest"] = True
                                new_day["muscle_group"] = "休息"
                            filtered_days[_widx_str] = new_day
                    else:
                        _sd = days_data.get("single", {})
                        kept = []
                        for _ei, _ex in enumerate(_sd.get("exercises", [])):
                            _ck_key = f"keep_{_msg_hash}_g{_read_gen}_single_{_ei}"
                            if st.session_state.get(_ck_key, True):
                                kept.append(_ex)
                        filtered_days = {"single": {**_sd, "exercises": kept}}

                    # 检查是否还有动作
                    _has_any = any(d.get("exercises") for d in filtered_days.values())
                    if not _has_any:
                        st.error("❌ 没有勾选任何动作，无法保存。请至少勾选一个动作。")
                    else:
                        # 如果用户改了类型，需要转换 days_data
                        final_days_data = filtered_days
                        if plan_type_choice != plan_type:
                            if plan_type_choice == "single":
                                # weekly → single：合并所有训练日动作
                                all_ex = []
                                seen_names = set()
                                for d in filtered_days.values():
                                    if not d.get("is_rest"):
                                        for ex in d.get("exercises", []):
                                            if ex["name"] not in seen_names:
                                                all_ex.append(ex)
                                                seen_names.add(ex["name"])
                                final_days_data = {"single": {
                                    "muscle_group": "全身",
                                    "is_rest": False,
                                    "exercises": all_ex
                                }}
                            else:
                                # single → weekly：把单日内容放到周一，其余休息
                                sd = filtered_days.get("single", {})
                                final_days_data = {
                                    "0": {"muscle_group": sd.get("muscle_group", "训练"),
                                          "is_rest": False, "exercises": sd.get("exercises", [])}
                                }
                                for w in range(1, 7):
                                    final_days_data[str(w)] = {"muscle_group": "休息", "is_rest": True, "exercises": []}

                        save_plan(
                            plan_name=new_plan_name,
                            description=last_msg["content"][:200],
                            plan_type=plan_type_choice,
                            days_data=final_days_data,
                            source="AI"
                        )
                        # 统计删了多少
                        _orig_count = total_ex
                        _final_count = sum(len(d.get("exercises", [])) for d in final_days_data.values())
                        if _orig_count > _final_count:
                            st.success(f"✅ 已保存「{new_plan_name}」（共 {_final_count} 个动作，删除了 {_orig_count - _final_count} 个）")
                        else:
                            st.success(f"✅ 已保存「{new_plan_name}」（共 {_final_count} 个动作）")
                        st.balloons()
            else:
                st.warning("⚠️ AI回复中没识别出训练动作，请重新让AI生成更明确的计划")

    st.markdown("---")
    user_input = st.text_input("向AI教练提问...", placeholder="例如：我是新手，每周练3天，目标增肌", key="train_input")
    b1, b2 = st.columns([4,1])
    with b1:
        if st.button("发送", key="train_send", use_container_width=True, type="primary"):
            if not ollama_ok: st.error("AI未启动")
            elif user_input.strip():
                st.session_state["train_pending"] = user_input
                st.rerun()
    with b2:
        if st.button("🗑 清空对话", key="train_clear", use_container_width=True):
            clear_chat(MODULE)
            st.session_state.training_messages = []
            st.rerun()


# =================================================================
# Tab2: 计划模板库
# =================================================================
with tabs[1]:
    st.markdown('<p style="color:#c8d8e8;font-weight:700;font-size:16px;">你的训练计划模板</p>', unsafe_allow_html=True)

    plans = list_plans()
    op1, op2 = st.columns([3, 1])
    with op2:
        if st.button("➕ 手动新建", use_container_width=True, type="primary", key="new_plan_btn"):
            st.session_state["editing_plan_id"] = "new"
            st.session_state["editing_plan_type"] = "single"
            st.session_state["editing_days_data"] = {"single": {"muscle_group":"胸","is_rest":False,"exercises":[]}}
            st.rerun()

    # 编辑模式
    if st.session_state.get("editing_plan_id"):
        editing_id = st.session_state["editing_plan_id"]
        is_new = editing_id == "new"

        if not is_new and "editing_days_data" not in st.session_state:
            plan_data = get_plan(editing_id)
            if plan_data:
                st.session_state["editing_days_data"] = plan_data.get("days_data", {})
                st.session_state["editing_plan_type"] = plan_data.get("plan_type", "single")

        st.markdown("---")
        title = "✨ 新建计划" if is_new else "✏️ 编辑计划"
        st.markdown(f'<p style="color:#00d9f5;font-weight:700;font-size:18px;">{title}</p>', unsafe_allow_html=True)

        plan_data = get_plan(editing_id) if not is_new else {}

        ec1, ec2 = st.columns([2, 1])
        with ec1:
            e_name = st.text_input("计划名称", value=plan_data.get("plan_name", ""), key="ep_name")
        with ec2:
            plan_type_choice = st.radio("计划类型",
                ["single", "weekly"],
                format_func=lambda x: "📋 单日计划" if x == "single" else "📅 一周计划",
                index=0 if st.session_state.get("editing_plan_type","single") == "single" else 1,
                horizontal=True, key="ep_type")
            # 切换类型时重置 days_data
            if plan_type_choice != st.session_state.get("editing_plan_type"):
                st.session_state["editing_plan_type"] = plan_type_choice
                if plan_type_choice == "single":
                    st.session_state["editing_days_data"] = {
                        "single": {"muscle_group":"胸","is_rest":False,"exercises":[]}
                    }
                else:
                    st.session_state["editing_days_data"] = {
                        str(w): {"muscle_group":"未指定","is_rest":True,"exercises":[]}
                        for w in range(7)
                    }
                st.rerun()

        e_desc = st.text_area("计划描述（可选）",
            value=(plan_data.get("description") or "")[:300], height=60, key="ep_desc")

        days_data = st.session_state.get("editing_days_data", {})

        if plan_type_choice == "single":
            # 单日编辑
            day = days_data.get("single", {"muscle_group":"胸","is_rest":False,"exercises":[]})

            sc1, sc2 = st.columns([2, 1])
            with sc1:
                muscle_opts = ["胸","背","腿","肩","臂","核心","胸+三头","背+二头","肩+腹","全身","其他"]
                cur_muscle = day.get("muscle_group", "胸")
                if cur_muscle not in muscle_opts:
                    muscle_opts.insert(0, cur_muscle)
                day["muscle_group"] = st.selectbox("训练部位", muscle_opts,
                    index=muscle_opts.index(cur_muscle), key="sg_muscle")
            with sc2:
                day["is_rest"] = st.checkbox("设为休息日", value=day.get("is_rest", False), key="sg_rest")

            if not day["is_rest"]:
                _render_exercises_editor(day, "single_day")
            days_data["single"] = day
        else:
            # 周计划编辑
            st.markdown('<p style="color:#c8d8e8;font-weight:600;margin-top:8px;">逐日设置：</p>', unsafe_allow_html=True)

            for w in range(7):
                day = days_data.get(str(w), {"muscle_group":"未指定","is_rest":True,"exercises":[]})
                weekday = WEEKDAY_NAMES[w]
                exp_label = f"{weekday}：{'休息' if day.get('is_rest') else day.get('muscle_group','训练')}"
                with st.expander(exp_label, expanded=False):
                    dc1, dc2 = st.columns([2, 1])
                    with dc1:
                        muscle_opts = ["胸","背","腿","肩","臂","核心","胸+三头","背+二头","肩+腹","全身","其他","未指定"]
                        cur_muscle = day.get("muscle_group", "未指定")
                        if cur_muscle not in muscle_opts:
                            muscle_opts.insert(0, cur_muscle)
                        day["muscle_group"] = st.selectbox("训练部位",
                            muscle_opts, index=muscle_opts.index(cur_muscle),
                            key=f"wg_muscle_{w}")
                    with dc2:
                        day["is_rest"] = st.checkbox("休息日", value=day.get("is_rest", False),
                            key=f"wg_rest_{w}")

                    if not day["is_rest"]:
                        _render_exercises_editor(day, f"w{w}")

                days_data[str(w)] = day

        st.markdown("<br>", unsafe_allow_html=True)
        bs1, bs2 = st.columns(2)
        with bs1:
            if st.button("💾 保存", use_container_width=True, type="primary", key="save_plan_btn"):
                if not e_name.strip():
                    st.error("请填写计划名称")
                else:
                    if is_new:
                        save_plan(e_name, e_desc, plan_type_choice, days_data, source="手动")
                        st.success("✅ 计划已创建")
                    else:
                        update_plan(editing_id, e_name, e_desc, plan_type_choice, days_data)
                        st.success("✅ 计划已更新")
                    st.session_state.pop("editing_plan_id", None)
                    st.session_state.pop("editing_days_data", None)
                    st.session_state.pop("editing_plan_type", None)
                    st.rerun()
        with bs2:
            if st.button("取消", use_container_width=True, key="cancel_plan_btn"):
                st.session_state.pop("editing_plan_id", None)
                st.session_state.pop("editing_days_data", None)
                st.session_state.pop("editing_plan_type", None)
                st.rerun()

    # 计划列表
    st.markdown("---")
    if not plans:
        st.info("还没有计划模板。从「AI训练计划」生成保存，或点右上角「手动新建」")
    else:
        for p in plans:
            pcc1, pcc2 = st.columns([4, 1])
            with pcc1:
                src_tag = "🤖 AI" if p.get("source") == "AI" else "✏️ 手动"
                days_data = p.get("days_data", {})

                if p.get("plan_type") == "weekly":
                    train_count = sum(1 for d in days_data.values() if not d.get("is_rest"))
                    rest_count = sum(1 for d in days_data.values() if d.get("is_rest"))
                    type_desc = f"📅 一周计划 · {train_count}训练 + {rest_count}休息"
                else:
                    sd = days_data.get("single", {})
                    type_desc = f"📋 单日计划 · {sd.get('muscle_group','未指定')}"

                st.markdown(f"""
                <div class="plan-card">
                    <div class="plan-name">{p['plan_name']}</div>
                    <div class="plan-meta">{src_tag} · {type_desc} · 创建于 {(p.get('created_at') or '')[:10]}</div>
                </div>
                """, unsafe_allow_html=True)
            with pcc2:
                if st.button("✏️ 编辑", key=f"edit_p_{p['id']}", use_container_width=True):
                    st.session_state["editing_plan_id"] = p['id']
                    st.session_state["editing_days_data"] = p.get("days_data", {})
                    st.session_state["editing_plan_type"] = p.get("plan_type", "single")
                    st.rerun()
                if st.button("🗑 删除", key=f"del_p_{p['id']}", use_container_width=True):
                    delete_plan(p['id'])
                    st.rerun()


# =================================================================
# Tab3: 训练日历
# =================================================================
with tabs[2]:
    plans = list_plans()
    if not plans:
        st.info("请先创建至少一个计划模板，再来日历安排训练")
    else:
        # 视图选择 - 用 session_state 持久化（避免 Tab 切换重置）
        if "cal_view_mode" not in st.session_state:
            st.session_state.cal_view_mode = "周列表视图"
        _view_options = ["月历视图", "周列表视图"]
        _cur_view_idx = _view_options.index(st.session_state.cal_view_mode) if st.session_state.cal_view_mode in _view_options else 1
        view_mode = st.radio("视图", _view_options, index=_cur_view_idx, horizontal=True, key="cal_view")
        st.session_state.cal_view_mode = view_mode

        # ===== 顶部工具栏：默认时间设置 + 一键安排 =====
        weekly_plans = [p for p in plans if p.get("plan_type") == "weekly"]

        with st.container():
            tc1, tc2, tc3 = st.columns([2, 2, 2])
            with tc1:
                # 用下拉框代替time_input，避免Streamlit组件DOM冲突
                cur_default_time = get_setting("default_workout_time", "18:00")
                # 生成所有半小时时间选项
                time_options = []
                for h in range(5, 23):
                    for m in [0, 30]:
                        time_options.append(f"{h:02d}:{m:02d}")
                try:
                    cur_idx = time_options.index(cur_default_time)
                except ValueError:
                    cur_idx = time_options.index("18:00")
                new_default_time = st.selectbox(
                    "⏰ 默认训练时间",
                    time_options, index=cur_idx, key="default_time_select")
                if new_default_time != cur_default_time:
                    set_setting("default_workout_time", new_default_time)
                    st.toast("默认时间已保存", icon="✅")
            with tc2:
                st.write("")
                st.write("")
                st.markdown(f'<p style="color:#8ca0b8;font-size:13px;padding-top:2px;">一键安排时使用 <b style="color:#00d9f5;">{new_default_time}</b> 作为训练时间</p>', unsafe_allow_html=True)
            with tc3:
                st.write("")
                st.write("")
                if weekly_plans:
                    btn_label = "📅 一键安排此月" if view_mode == "月历视图" else "📅 一键安排本周"
                    if st.button(btn_label, use_container_width=True, type="primary", key="batch_schedule_btn"):
                        st.session_state["show_batch_schedule"] = view_mode
                        st.rerun()
                else:
                    st.button("📅 一键安排（需先创建一周计划）", use_container_width=True, disabled=True, key="batch_disabled")

        # ===== 一键安排弹窗 =====
        if st.session_state.get("show_batch_schedule"):
            mode = st.session_state["show_batch_schedule"]
            st.markdown("---")
            st.markdown(f'<p style="color:#00d9f5;font-weight:700;font-size:18px;">📅 一键安排（{mode}）</p>', unsafe_allow_html=True)

            bs1, bs2 = st.columns([2, 1])
            with bs1:
                wp_opts = {f"📅 {p['plan_name']}": p for p in weekly_plans}
                sel_label = st.selectbox("选择一周计划", list(wp_opts.keys()), key="batch_plan_sel")
                sel_plan = wp_opts[sel_label]
            with bs2:
                default_time_str = get_setting("default_workout_time", "18:00")
                st.markdown(f'<p style="color:#c8d8e8;font-size:13px;margin-top:8px;">每天 <b style="color:#00d9f5;">{default_time_str}</b> 开练（可在上方修改）</p>', unsafe_allow_html=True)

            if mode == "月历视图":
                bcols = st.columns(2)
                with bcols[0]:
                    today = date.today()
                    batch_start_date = st.date_input(
                        "起始日期（建议选周一）",
                        value=today,
                        key="batch_start_date_m")
                with bcols[1]:
                    weeks_to_repeat = st.selectbox("重复几周",
                        [1, 2, 4, 8],
                        format_func=lambda x: f"{x} 周",
                        index=3,  # 默认8周（约一个月）
                        key="batch_weeks_m")
            else:
                # 周列表
                bcols = st.columns(2)
                with bcols[0]:
                    today = date.today()
                    monday_of_this_week = today - timedelta(days=today.weekday())
                    batch_start_date = st.date_input(
                        "起始日期（建议选周一）",
                        value=monday_of_this_week,
                        key="batch_start_date_w")
                with bcols[1]:
                    weeks_to_repeat = 1

            # 预览
            preview_start = batch_start_date
            preview_end = batch_start_date + timedelta(days=weeks_to_repeat * 7 - 1)
            sel_days = sel_plan["days_data"]
            train_count_per_week = sum(1 for d in sel_days.values() if not d.get("is_rest"))
            rest_count_per_week = sum(1 for d in sel_days.values() if d.get("is_rest"))
            total_train = train_count_per_week * weeks_to_repeat
            total_rest = rest_count_per_week * weeks_to_repeat

            st.markdown(f"""
            <div style="background:#162032;border-left:3px solid #00d9f5;padding:12px 16px;border-radius:6px;color:#c8d8e8;font-size:13px;line-height:1.8;margin:8px 0;">
                <b style="color:#00d9f5;">将安排：</b><br>
                · 日期范围：<b>{preview_start.strftime('%Y-%m-%d')}</b> ~ <b>{preview_end.strftime('%Y-%m-%d')}</b>（{weeks_to_repeat} 周）<br>
                · 共 <b style="color:#00f5a0;">{total_train}</b> 个训练日 + <b style="color:#8ca0b8;">{total_rest}</b> 个休息日<br>
                · 时间：每天 <b>{default_time_str}</b>
            </div>
            """, unsafe_allow_html=True)

            # 检查冲突
            existing_in_range = get_schedules_in_range(preview_start.isoformat(), preview_end.isoformat())
            if existing_in_range:
                st.markdown(f"""
                <div class="warning-card">
                    ⚠ 该日期范围内已有 <b>{len(existing_in_range)}</b> 个训练安排，一键安排将<b>覆盖</b>它们。
                </div>
                """, unsafe_allow_html=True)

            bsubmit1, bsubmit2 = st.columns(2)
            with bsubmit1:
                if st.button("✅ 确认一键安排", use_container_width=True, type="primary", key="batch_confirm"):
                    sch_time_str = get_setting("default_workout_time", "18:00")

                    # 检查是否需要避开经期（仅女性用户）
                    _is_female_b = profile and profile.get("gender") == "女"
                    if _is_female_b:
                        from database import get_menstrual_cycle, predict_period_dates
                        cycle_data = get_menstrual_cycle()
                        avoid_period = bool(cycle_data and cycle_data.get("auto_avoid"))
                        period_dates = predict_period_dates(weeks_ahead=12) if avoid_period else set()
                    else:
                        avoid_period = False
                        period_dates = set()

                    # 先删除冲突的旧安排
                    for old in existing_in_range:
                        delete_schedule(old["id"])
                    # 批量添加
                    added = 0
                    period_replaced = 0
                    for week_offset in range(weeks_to_repeat):
                        for wday in range(7):
                            d = batch_start_date + timedelta(days=week_offset * 7 + wday)
                            target_widx = d.weekday()
                            target_day = sel_days.get(str(target_widx), {})

                            # 如果开启了"经期避开"且这天在预测经期内 → 强制改成"经期休息"
                            if avoid_period and d in period_dates and not target_day.get("is_rest"):
                                # 注意：add_schedule 会根据 plan 的 days_data 决定是不是休息
                                # 为了让经期那天显示成"休息"，我们用一个"特殊"的策略：
                                # 在 schedule 表里加一个标记，让显示层识别为休息
                                # 简单做法：调用 add_schedule，但 weekday_index 传 -1（表示经期休息）
                                # 这里直接用 plan_id 但 weekday_index=-1 我们的 day_info 逻辑要支持
                                add_schedule(
                                    plan_id=sel_plan["id"],
                                    schedule_date=d.isoformat(),
                                    schedule_time=sch_time_str,
                                    weekday_index=target_widx,
                                    notes="period_rest"  # 标记为经期休息
                                )
                                period_replaced += 1
                            else:
                                add_schedule(
                                    plan_id=sel_plan["id"],
                                    schedule_date=d.isoformat(),
                                    schedule_time=sch_time_str,
                                    weekday_index=target_widx
                                )
                            added += 1
                    st.session_state.pop("show_batch_schedule", None)
                    msg = f"✅ 已一键安排 {added} 天的训练计划"
                    if period_replaced:
                        msg += f"，其中 {period_replaced} 天因预测经期自动改为休息"
                    st.success(msg)
                    st.balloons()
                    st.rerun()
            with bsubmit2:
                if st.button("取消", use_container_width=True, key="batch_cancel"):
                    st.session_state.pop("show_batch_schedule", None)
                    st.rerun()
            st.markdown("---")

        if "cal_year" not in st.session_state:
            st.session_state.cal_year = date.today().year
            st.session_state.cal_month = date.today().month
        if "cal_week_start" not in st.session_state:
            today = date.today()
            st.session_state.cal_week_start = today - timedelta(days=today.weekday())

        nav1, nav2, nav3, nav4 = st.columns([1, 2, 1, 1])
        with nav1:
            label = "◀ 上月" if view_mode == "月历视图" else "◀ 上周"
            if st.button(label, use_container_width=True, key="cal_prev"):
                if view_mode == "月历视图":
                    if st.session_state.cal_month == 1:
                        st.session_state.cal_month = 12
                        st.session_state.cal_year -= 1
                    else:
                        st.session_state.cal_month -= 1
                else:
                    st.session_state.cal_week_start -= timedelta(days=7)
                st.rerun()
        with nav2:
            if view_mode == "月历视图":
                st.markdown(f'<p style="text-align:center;font-size:20px;color:#00d9f5;font-weight:700;font-family:Rajdhani,sans-serif;">{st.session_state.cal_year} 年 {st.session_state.cal_month} 月</p>', unsafe_allow_html=True)
            else:
                ws = st.session_state.cal_week_start
                we = ws + timedelta(days=6)
                st.markdown(f'<p style="text-align:center;font-size:18px;color:#00d9f5;font-weight:700;">{ws.strftime("%m/%d")} - {we.strftime("%m/%d")}</p>', unsafe_allow_html=True)
        with nav3:
            label = "下月 ▶" if view_mode == "月历视图" else "下周 ▶"
            if st.button(label, use_container_width=True, key="cal_next"):
                if view_mode == "月历视图":
                    if st.session_state.cal_month == 12:
                        st.session_state.cal_month = 1
                        st.session_state.cal_year += 1
                    else:
                        st.session_state.cal_month += 1
                else:
                    st.session_state.cal_week_start += timedelta(days=7)
                st.rerun()
        with nav4:
            if st.button("📅 今天", use_container_width=True, key="cal_today"):
                today = date.today()
                st.session_state.cal_year = today.year
                st.session_state.cal_month = today.month
                st.session_state.cal_week_start = today - timedelta(days=today.weekday())
                st.rerun()

        st.markdown("---")

        if view_mode == "月历视图":
            cal = calendar.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)
            month_start = date(st.session_state.cal_year, st.session_state.cal_month, 1)
            last_day = calendar.monthrange(st.session_state.cal_year, st.session_state.cal_month)[1]
            month_end = date(st.session_state.cal_year, st.session_state.cal_month, last_day)
            all_schedules = get_schedules_in_range(month_start.isoformat(), month_end.isoformat())

            sch_by_date = {}
            for s in all_schedules:
                sch_by_date.setdefault(s["schedule_date"], []).append(s)

            today_iso = date.today().isoformat()

            # ===== 纯HTML月历（避免Streamlit按钮DOM冲突）=====
            cal_html = """
            <style>
            .month-cal{width:100%;border-collapse:separate;border-spacing:6px;margin-top:8px;}
            .month-cal th{color:#8ca0b8;font-size:13px;font-weight:600;padding:8px;text-align:center;}
            .month-cal td{vertical-align:top;background:#162032;border:1px solid #2a3a55;
                border-radius:10px;padding:8px;width:14.28%;height:88px;position:relative;}
            .month-cal td.empty{background:transparent;border:none;}
            .month-cal td.today{border-color:#00f5a0 !important;background:rgba(0,245,160,0.04) !important;}
            .month-cal .day-num{font-family:'Rajdhani',sans-serif;font-size:16px;color:#e8eaf0;font-weight:600;margin-bottom:4px;}
            .month-cal td.today .day-num{color:#00f5a0;}
            .month-cal .ev{font-size:11px;padding:2px 6px;border-radius:6px;margin-top:2px;
                background:rgba(0,217,245,0.12);color:#00d9f5;border-left:2px solid #00d9f5;
                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
            .month-cal .ev-rest{background:rgba(140,160,184,0.1);color:#8ca0b8;border-left-color:#8ca0b8;}
            .month-cal .ev-period{background:rgba(255,121,180,0.15);color:#ff79b4;border-left-color:#ff79b4;}
            .month-cal .ev-done{background:rgba(0,245,160,0.12);color:#00f5a0;border-left-color:#00f5a0;}
            .month-cal .ev-skip{background:rgba(255,87,87,0.1);color:#ff8c8c;border-left-color:#ff5757;opacity:0.7;}
            .month-cal .ev-more{font-size:10px;color:#8ca0b8;margin-top:2px;}
            </style>
            <table class="month-cal">
            <thead><tr>
                <th>星期一</th><th>星期二</th><th>星期三</th><th>星期四</th><th>星期五</th><th>星期六</th><th>星期日</th>
            </tr></thead>
            <tbody>
            """

            for week in cal:
                cal_html += "<tr>"
                for day in week:
                    if day == 0:
                        cal_html += '<td class="empty">&nbsp;</td>'
                    else:
                        d_iso = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                        is_today = d_iso == today_iso
                        events = sch_by_date.get(d_iso, [])

                        td_class = "today" if is_today else ""
                        events_html = ""
                        for e in events[:2]:
                            di = e.get("day_info", {})
                            status = e.get("status", "pending")
                            if di.get("is_period"):
                                events_html += f'<div class="ev ev-period">🌸 {e["schedule_time"]} 经期</div>'
                            elif di.get("is_rest"):
                                events_html += f'<div class="ev ev-rest">💤 {e["schedule_time"]} 休息</div>'
                            elif status == "completed":
                                muscle = di.get("muscle_group", "训练")[:4]
                                events_html += f'<div class="ev ev-done">✅ {e["schedule_time"]} {muscle}</div>'
                            elif status == "skipped":
                                muscle = di.get("muscle_group", "训练")[:4]
                                events_html += f'<div class="ev ev-skip">❌ {e["schedule_time"]} {muscle}</div>'
                            else:
                                muscle = di.get("muscle_group", "训练")[:4]
                                events_html += f'<div class="ev">⏰ {e["schedule_time"]} {muscle}</div>'
                        if len(events) > 2:
                            events_html += f'<div class="ev-more">+{len(events)-2} 更多</div>'

                        cal_html += f'<td class="{td_class}"><div class="day-num">{day}</div>{events_html}</td>'
                cal_html += "</tr>"
            cal_html += "</tbody></table>"

            st.markdown(cal_html, unsafe_allow_html=True)

            # ===== 月历下方：快速安排表单 =====
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p style="color:#00d9f5;font-weight:700;font-size:16px;">📝 快速安排单日训练</p>', unsafe_allow_html=True)
            st.caption("选择具体日期、计划和时间，点击「安排」即可。批量安排请用顶部「📅 一键安排此月」按钮。")

            qs1, qs2, qs3 = st.columns([1.2, 2, 1])
            with qs1:
                quick_date = st.date_input(
                    "选择日期",
                    value=date.today(),
                    min_value=month_start,
                    max_value=month_end,
                    key="quick_sch_date")
            with qs2:
                _plan_opts = {f"{'📅' if p.get('plan_type')=='weekly' else '📋'} {p['plan_name']}": p for p in plans}
                quick_plan_label = st.selectbox("选择计划", list(_plan_opts.keys()), key="quick_sch_plan")
                quick_plan = _plan_opts[quick_plan_label]
            with qs3:
                _time_opts = [f"{h:02d}:{m:02d}" for h in range(5, 23) for m in [0, 30]]
                _default_t = get_setting("default_workout_time", "18:00")
                try:
                    _t_idx = _time_opts.index(_default_t)
                except ValueError:
                    _t_idx = _time_opts.index("18:00")
                quick_time = st.selectbox("时间", _time_opts, index=_t_idx, key="quick_sch_time")

            # 预览
            qd_iso = quick_date.isoformat()
            existing = sch_by_date.get(qd_iso, [])
            if existing:
                st.caption(f"⚠ {qd_iso} 当天已有 {len(existing)} 个安排，新增的不会覆盖（除非时间相同）")

            # 经期警告（仅女性用户）
            _is_female = profile and profile.get("gender") == "女"
            if _is_female:
                from database import is_near_period as _is_near_p
                try:
                    _period_check = _is_near_p(quick_date)
                    if _period_check == "in_period":
                        st.warning(f"🌸 {qd_iso} 在预测经期内。继续安排训练？建议改为休息或低强度。")
                    elif _period_check and _period_check.startswith("pre_"):
                        _d = _period_check.split("_")[1]
                        st.info(f"🌸 {qd_iso} 距离预测经期还有 {_d} 天")
                except: pass

            if st.button("📅 安排此次训练", use_container_width=True, type="primary", key="quick_sch_submit"):
                # 计算 weekday_index
                _wd = quick_date.weekday()
                # 检查是否经期 → 自动改为经期休息（仅女性）
                _notes = ""
                if _is_female:
                    try:
                        from database import get_menstrual_cycle, is_near_period as _is_near_p2
                        _cycle = get_menstrual_cycle()
                        _avoid = bool(_cycle and _cycle.get("auto_avoid"))
                        if _avoid and _is_near_p2(quick_date) == "in_period":
                            _notes = "period_rest"
                    except: pass
                add_schedule(
                    plan_id=quick_plan["id"],
                    schedule_date=qd_iso,
                    schedule_time=quick_time,
                    weekday_index=_wd,
                    notes=_notes
                )
                if _notes == "period_rest":
                    st.success(f"✅ 已在 {qd_iso} {quick_time} 安排「{quick_plan['plan_name']}」（经期休息）")
                else:
                    st.success(f"✅ 已在 {qd_iso} {quick_time} 安排「{quick_plan['plan_name']}」")
                st.rerun()

        else:
            # 周列表
            week_start = st.session_state.cal_week_start
            week_end = week_start + timedelta(days=6)
            week_schedules = get_schedules_in_range(week_start.isoformat(), week_end.isoformat())
            sch_by_date = {}
            for s in week_schedules:
                sch_by_date.setdefault(s["schedule_date"], []).append(s)

            for i in range(7):
                d = week_start + timedelta(days=i)
                weekday = WEEKDAY_NAMES[i]
                is_today = d == date.today()
                day_label_color = "#00d9f5" if is_today else "#c8d8e8"

                dh1, dh2 = st.columns([4, 1])
                with dh1:
                    st.markdown(f'<p style="color:{day_label_color};font-weight:700;font-size:16px;margin:8px 0;">{weekday} · {d.strftime("%m/%d")}{" · 今天" if is_today else ""}</p>', unsafe_allow_html=True)
                with dh2:
                    if st.button("➕ 安排", key=f"week_add_{d.isoformat()}", use_container_width=True):
                        st.session_state["scheduling_date"] = d.isoformat()
                        st.rerun()

                day_sch = sch_by_date.get(d.isoformat(), [])
                if not day_sch:
                    st.markdown('<p style="color:#4a6080;font-size:13px;padding-left:8px;">未安排</p>', unsafe_allow_html=True)
                else:
                    for s in day_sch:
                        di = s.get("day_info", {})
                        is_rest = di.get("is_rest", False)
                        is_period = di.get("is_period", False)

                        # 经期休息：粉色样式
                        if is_period:
                            scols = st.columns([4, 1])
                            with scols[0]:
                                st.markdown(
                                    f'<div style="background:rgba(255,121,180,0.08);border:1px solid rgba(255,121,180,0.3);border-radius:8px;padding:10px 14px;margin:6px 0;color:#ff79b4;font-size:14px;">'
                                    f'<span style="color:#ff79b4;">{s["schedule_time"]}</span> · 🌸 经期休息日 · 注意保暖与营养'
                                    f'</div>',
                                    unsafe_allow_html=True)
                            with scols[1]:
                                if st.button("删除", key=f"del_sch_{s['id']}", use_container_width=True):
                                    delete_schedule(s['id'])
                                    st.rerun()
                        # 普通休息日
                        elif is_rest:
                            scols = st.columns([4, 1])
                            with scols[0]:
                                st.markdown(
                                    f'<div style="background:rgba(140,160,184,0.08);border:1px solid rgba(140,160,184,0.2);border-radius:8px;padding:10px 14px;margin:6px 0;color:#8ca0b8;font-size:14px;">'
                                    f'<span style="color:#7898b8;">{s["schedule_time"]}</span> · {s.get("plan_name","")} · 💤 休息日'
                                    f'</div>',
                                    unsafe_allow_html=True)
                            with scols[1]:
                                if st.button("删除", key=f"del_sch_{s['id']}", use_container_width=True):
                                    delete_schedule(s['id'])
                                    st.rerun()
                        else:
                            # 训练日：根据 status 区分显示
                            status = s.get("status", "pending")
                            status_tag = {"pending":"⏰ 待训","completed":"✅ 完成","skipped":"❌ 跳过"}.get(status, "⏰")
                            muscle = di.get('muscle_group','训练')

                            # 已完成 / 已跳过 → 不显示开始按钮，只显示删除
                            if status in ("completed", "skipped"):
                                _opacity = "0.6"
                                scols = st.columns([4, 1])
                                with scols[0]:
                                    st.markdown(
                                        f'<div class="exercise-row" style="opacity:{_opacity};"><b style="color:#00d9f5;">{s["schedule_time"]}</b> · {s.get("plan_name","")} · 💪 {muscle} '
                                        f'<span style="float:right;color:#8ca0b8;font-size:12px;">{status_tag}</span></div>',
                                        unsafe_allow_html=True)
                                with scols[1]:
                                    if st.button("删除", key=f"del_sch_{s['id']}", use_container_width=True):
                                        delete_schedule(s['id'])
                                        st.rerun()
                            else:
                                # pending → 显示开始 + 删除
                                scols = st.columns([3, 1, 1])
                                with scols[0]:
                                    st.markdown(
                                        f'<div class="exercise-row"><b style="color:#00d9f5;">{s["schedule_time"]}</b> · {s.get("plan_name","")} · 💪 {muscle} '
                                        f'<span style="float:right;color:#8ca0b8;font-size:12px;">{status_tag}</span></div>',
                                        unsafe_allow_html=True)
                                with scols[1]:
                                    if st.button("开始", key=f"start_sch_{s['id']}", use_container_width=True, type="primary"):
                                        st.session_state["jump_schedule_id"] = s['id']
                                        st.rerun()
                                with scols[2]:
                                    if st.button("删除", key=f"del_sch_{s['id']}", use_container_width=True):
                                        delete_schedule(s['id'])
                                        st.rerun()
                st.markdown("<hr>", unsafe_allow_html=True)

        # 安排弹窗
        if st.session_state.get("scheduling_date"):
            sch_date = st.session_state["scheduling_date"]
            st.markdown("---")
            d_obj = datetime.strptime(sch_date, "%Y-%m-%d").date()
            wkn = WEEKDAY_NAMES[d_obj.weekday()]
            st.markdown(f'<p style="color:#00d9f5;font-weight:700;font-size:18px;">📅 安排训练 · {sch_date} ({wkn})</p>', unsafe_allow_html=True)

            # 显示当天已有安排
            existing = get_schedules_by_date(sch_date)
            if existing:
                st.markdown('<p style="color:#ffaa3c;font-size:13px;">⚠ 当天已有安排（保存后会被覆盖）：</p>', unsafe_allow_html=True)
                for e in existing:
                    di = e.get("day_info", {})
                    label = "休息" if di.get("is_rest") else di.get("muscle_group", "训练")
                    st.markdown(f'<div style="font-size:12px;color:#8ca0b8;margin-left:12px;">· {e["schedule_time"]} - {e.get("plan_name","")} ({label})</div>', unsafe_allow_html=True)

            sc1, sc2 = st.columns([2, 1])
            with sc1:
                plan_opts = {}
                for p in plans:
                    if p.get("plan_type") == "weekly":
                        # 取这一天对应的部位
                        day = p["days_data"].get(str(d_obj.weekday()), {})
                        if day.get("is_rest"):
                            label = f"📅 {p['plan_name']} (周计划 · {wkn}=休息)"
                        else:
                            label = f"📅 {p['plan_name']} (周计划 · {wkn}={day.get('muscle_group','训练')})"
                    else:
                        sd = p["days_data"].get("single", {})
                        label = f"📋 {p['plan_name']} (单日 · {sd.get('muscle_group','训练')})"
                    plan_opts[label] = p

                sch_plan_label = st.selectbox("选择计划", list(plan_opts.keys()), key="sch_plan_v2")
            with sc2:
                # 用selectbox避免time_input冲突
                _time_opts = [f"{h:02d}:{m:02d}" for h in range(5, 23) for m in [0, 30]]
                _default_t = get_setting("default_workout_time", "18:00")
                try:
                    _t_idx = _time_opts.index(_default_t)
                except ValueError:
                    _t_idx = _time_opts.index("18:00")
                sch_time_str = st.selectbox("时间", _time_opts, index=_t_idx, key="sch_time_v2")

            selected_plan = plan_opts.get(sch_plan_label)

            # 提前检查相邻同部位冲突
            if selected_plan:
                if selected_plan["plan_type"] == "weekly":
                    target_day = selected_plan["days_data"].get(str(d_obj.weekday()), {})
                else:
                    target_day = selected_plan["days_data"].get("single", {})
                target_muscle = target_day.get("muscle_group", "")
                is_rest = target_day.get("is_rest", False)

                if not is_rest:
                    conflicts = check_adjacent_muscle(sch_date, target_muscle)
                    if conflicts:
                        for c in conflicts:
                            d_str = "前一天" if c["date"] < sch_date else "第二天"
                            st.markdown(f"""
                            <div class="warning-card">
                                ⚠ 注意：{d_str}（{c["date"]}）已安排了 <b>{c["muscle"]}</b> 训练，
                                与今天的 <b>{target_muscle}</b> 部位有重叠。<br>
                                同一肌群通常需要 48 小时恢复，建议改到其他日期，或将其中一天改为休息/其他部位。
                            </div>
                            """, unsafe_allow_html=True)

            add_col1, add_col2 = st.columns(2)
            with add_col1:
                if st.button("✅ 确认安排", use_container_width=True, type="primary", key="confirm_sch"):
                    if selected_plan:
                        add_schedule(
                            plan_id=selected_plan["id"],
                            schedule_date=sch_date,
                            schedule_time=sch_time_str,
                            weekday_index=d_obj.weekday()
                        )
                        st.session_state.pop("scheduling_date", None)
                        st.success("已安排")
                        st.rerun()
            with add_col2:
                if st.button("取消", use_container_width=True, key="cancel_sch"):
                    st.session_state.pop("scheduling_date", None)
                    st.rerun()


# =================================================================
# Tab4: 今日训练
# =================================================================
with tabs[3]:
    today_session = get_today_session()

    # ========== 经期提示（女性用户 & 有训练 session 或即将开始）==========
    period_prompt_shown = False
    if profile and profile.get("gender") == "女":
        from database import is_near_period, add_menstrual_log, update_menstrual_log_end, get_recent_menstrual_logs
        today_dt = date.today()
        period_status = is_near_period(today_dt)
        # 仅在有当前 session 或有即将跳转的训练时提示
        pending_jump = st.session_state.get("jump_schedule_id")
        # 检查今日是否有任何待训训练日程
        from database import get_schedules_by_date
        _today_schs = get_schedules_by_date(today_dt.isoformat())
        _has_pending_today = any(
            s.get("status") == "pending" and not s.get("day_info", {}).get("is_rest")
            for s in _today_schs
        )

        if period_status and (today_session or pending_jump or _has_pending_today) \
                and not st.session_state.get(f"period_dismissed_today4_{today_dt.isoformat()}"):
            period_prompt_shown = True
            if period_status == "in_period":
                st.warning(
                    "🌸 **今天处于预测经期内**\n\n"
                    "建议：根据身体状态决定是否训练。如经期反应较强烈（痛经、头晕、量大），"
                    "建议休息或只做轻度瑜伽/拉伸。如状态良好，可降低训练强度（重量减少 30%）继续。"
                )
                ppc1, ppc2 = st.columns(2)
                with ppc1:
                    if st.button("✅ 我决定休息（今天）", use_container_width=True, key="tab4_period_rest"):
                        # 标记所有今天待训训练为跳过
                        for s in _today_schs:
                            if s.get("status") == "pending":
                                update_schedule_status(s['id'], 'skipped')
                                mark_schedule_notified(s['id'])
                        st.session_state[f"period_dismissed_today4_{today_dt.isoformat()}"] = True
                        st.session_state.pop("jump_schedule_id", None)
                        st.success("好好休息～")
                        st.rerun()
                with ppc2:
                    if st.button("💪 状态良好，继续训练", use_container_width=True, key="tab4_period_train"):
                        st.session_state[f"period_dismissed_today4_{today_dt.isoformat()}"] = True
                        st.rerun()
            elif period_status.startswith("pre_"):
                days = period_status.split("_")[1]
                st.info(
                    f"🌸 **预测经期将在 {days} 天内开始**\n\n"
                    f"如果经期已提前到来，可以点击下方按钮记录并把今天改为休息。"
                )
                ppc1, ppc2 = st.columns(2)
                with ppc1:
                    if st.button("🌸 经期已开始（今天）", use_container_width=True, key="tab4_period_started"):
                        add_menstrual_log(start_date=today_dt.isoformat(), notes="提前到来")
                        for s in _today_schs:
                            if s.get("status") == "pending":
                                update_schedule_status(s['id'], 'skipped')
                                mark_schedule_notified(s['id'])
                        st.session_state[f"period_dismissed_today4_{today_dt.isoformat()}"] = True
                        st.session_state.pop("jump_schedule_id", None)
                        st.success("已记录，今天休息～")
                        st.rerun()
                with ppc2:
                    if st.button("继续训练", use_container_width=True, key="tab4_period_pre_train"):
                        st.session_state[f"period_dismissed_today4_{today_dt.isoformat()}"] = True
                        st.rerun()
            elif period_status.startswith("post_"):
                days = period_status.split("_")[1]
                st.info(
                    f"🌸 **预测经期已结束 {days} 天**\n\n"
                    f"如果经期还没结束，可以记录。如已结束，建议本周从轻量训练开始。"
                )
                ppc1, ppc2 = st.columns(2)
                with ppc1:
                    if st.button("🌸 经期还在进行", use_container_width=True, key="tab4_period_post_ongoing"):
                        for s in _today_schs:
                            if s.get("status") == "pending":
                                update_schedule_status(s['id'], 'skipped')
                                mark_schedule_notified(s['id'])
                        st.session_state[f"period_dismissed_today4_{today_dt.isoformat()}"] = True
                        st.session_state.pop("jump_schedule_id", None)
                        st.success("已记录，休息～")
                        st.rerun()
                with ppc2:
                    if st.button("已结束，继续训练", use_container_width=True, key="tab4_period_post_train"):
                        logs = get_recent_menstrual_logs(limit=1)
                        if logs and not logs[0].get("end_date"):
                            try:
                                ended_at = today_dt - timedelta(days=int(days))
                                update_menstrual_log_end(logs[0]["id"], ended_at.isoformat())
                            except: pass
                        st.session_state[f"period_dismissed_today4_{today_dt.isoformat()}"] = True
                        st.rerun()

    # 处理「开始」按钮跳转（仅在经期提示未阻挡时）
    if not period_prompt_shown:
        jump_sch_id = st.session_state.pop("jump_schedule_id", None)
    else:
        jump_sch_id = None  # 经期提示期间不开始训练
    if jump_sch_id and not today_session:
        from database import get_conn
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT * FROM schedule WHERE id=?", (jump_sch_id,))
        row = c.fetchone()
        cols = [d[0] for d in c.description]; conn.close()

        if row:
            sch = dict(zip(cols, row))
            plan = get_plan(sch["plan_id"])
            if plan:
                if plan["plan_type"] == "weekly":
                    target_day = plan["days_data"].get(str(sch.get("weekday_index") or 0), {})
                else:
                    target_day = plan["days_data"].get("single", {})

                if not target_day.get("is_rest") and target_day.get("exercises"):
                    exercises_with_logs = []
                    for ex in target_day["exercises"]:
                        exercises_with_logs.append({
                            "name": ex.get("name", ""),
                            "target_sets": ex.get("sets", 3),
                            "target_reps": ex.get("reps", "10"),
                            "target_weight": ex.get("weight", ""),
                            "set_logs": [
                                {"done": False, "actual_reps": 0, "actual_weight": 0}
                                for _ in range(int(ex.get("sets", 3) or 3))
                            ]
                        })
                    start_session(
                        plan_id=plan["id"],
                        plan_name=plan["plan_name"],
                        target_muscle=target_day.get("muscle_group", ""),
                        exercises=exercises_with_logs
                    )
                    st.session_state["session_start_time"] = datetime.now().isoformat()
                    update_schedule_status(jump_sch_id, 'completed')
                    st.rerun()

    if today_session:
        # 顶部信息卡片 - 完全独立的st.info组件，不嵌HTML
        st.info(f"🎯 **正在进行：{today_session['plan_name']}** · 部位：{today_session.get('target_muscle','训练')} · 开始于 {today_session['created_at'][:16]}")
        exercises_data = today_session.get("exercises_data", [])

        # 用 form 包裹避免每个组件改动都触发 rerun
        with st.form(key=f"workout_form_{today_session['id']}", clear_on_submit=False):
            for ei, ex in enumerate(exercises_data):
                done_count = sum(1 for s in ex.get("set_logs", []) if s.get("done"))
                total = len(ex.get("set_logs", []))

                # 动作标题用纯markdown（确保闭合）
                st.markdown("---")
                _ex_name = ex.get('name','').replace('**','').replace('*','').strip()
                _tw = str(ex.get('target_weight','') or '').strip()
                _tw_str = f" · {_tw}kg" if _tw and _tw != "0" else ""
                st.markdown(f"### 💪 {_ex_name}")
                st.caption(f"目标：{ex.get('target_sets',0)} 组 × {ex.get('target_reps','')} 次{_tw_str}  ·  已完成 {done_count}/{total}")

                # 每组打卡 - 简化布局
                for si, s in enumerate(ex.get("set_logs", [])):
                    sc = st.columns([0.5, 1, 2, 2, 1.2])
                    with sc[0]:
                        st.checkbox("done",
                            value=s.get("done", False),
                            key=f"sess_done_{ei}_{si}",
                            label_visibility="collapsed")
                    with sc[1]:
                        st.markdown(f"<div style='padding-top:6px;color:#8ca0b8;font-size:13px;'>第 {si+1} 组</div>", unsafe_allow_html=True)
                    with sc[2]:
                        # 重量输入 - 空字符串默认（不再显示0）
                        _w_default = str(s.get("actual_weight", "") or "")
                        if _w_default == "0" or _w_default == "0.0":
                            _w_default = ""
                        st.text_input(
                            f"重量{ei}_{si}",
                            value=_w_default,
                            key=f"sess_w_{ei}_{si}",
                            label_visibility="collapsed",
                            placeholder="重量 (kg)")
                    with sc[3]:
                        _r_default = str(s.get("actual_reps", "") or "")
                        if _r_default == "0":
                            _r_default = ""
                        st.text_input(
                            f"次数{ei}_{si}",
                            value=_r_default,
                            key=f"sess_r_{ei}_{si}",
                            label_visibility="collapsed",
                            placeholder="次数")
                    with sc[4]:
                        # 容量显示 - 只在勾选并有数据时显示
                        try:
                            _w_str = st.session_state.get(f"sess_w_{ei}_{si}", "")
                            _r_str = st.session_state.get(f"sess_r_{ei}_{si}", "")
                            _is_done = st.session_state.get(f"sess_done_{ei}_{si}", False)
                            if _is_done and _w_str and _r_str:
                                _vol = float(_w_str) * int(_r_str)
                                st.markdown(f"<div style='padding-top:6px;color:#00f5a0;font-size:13px;'>✓ {_vol:.0f}kg</div>", unsafe_allow_html=True)
                            else:
                                st.markdown("<div style='padding-top:6px;'>&nbsp;</div>", unsafe_allow_html=True)
                        except:
                            st.markdown("<div style='padding-top:6px;'>&nbsp;</div>", unsafe_allow_html=True)

            st.markdown("---")
            session_notes = st.text_area("训练备注（可选）",
                value=today_session.get("notes") or "",
                placeholder="今天感觉如何？",
                height=70, key="session_notes_form")

            sf1, sf2 = st.columns([1, 1])
            with sf1:
                save_only = st.form_submit_button("💾 保存进度（继续训练）", use_container_width=True)
            with sf2:
                finish_now = st.form_submit_button("🎉 完成本次训练", use_container_width=True, type="primary")

            if save_only or finish_now:
                # 从 form 中收集数据
                for ei, ex in enumerate(exercises_data):
                    for si, s in enumerate(ex.get("set_logs", [])):
                        s["done"] = st.session_state.get(f"sess_done_{ei}_{si}", False)
                        try:
                            _w = st.session_state.get(f"sess_w_{ei}_{si}", "")
                            s["actual_weight"] = float(_w) if _w else 0
                        except: s["actual_weight"] = 0
                        try:
                            _r = st.session_state.get(f"sess_r_{ei}_{si}", "")
                            s["actual_reps"] = int(_r) if _r else 0
                        except: s["actual_reps"] = 0

                update_session(today_session["id"], exercises_data, notes=session_notes)

                if finish_now:
                    start_t = st.session_state.get("session_start_time")
                    duration = 0
                    if start_t:
                        try:
                            dt = datetime.fromisoformat(start_t)
                            duration = int((datetime.now() - dt).total_seconds() / 60)
                        except: pass
                    finish_session(today_session["id"], duration_minutes=duration)
                    st.session_state["last_finished_session"] = today_session["id"]
                    st.session_state["just_finished"] = True
                    st.balloons()
                    st.rerun()
                else:
                    st.success("✅ 进度已保存")
                    st.rerun()

        # 放弃按钮单独放在 form 外
        st.markdown("---")
        ga1, ga2, ga3 = st.columns([1, 2, 1])
        with ga2:
            if st.button("❌ 放弃本次训练（清除所有打卡数据）", use_container_width=True, key="abandon_session"):
                delete_session(today_session["id"])
                st.rerun()
    elif st.session_state.get("just_finished"):
        # 训练刚完成 - 显示成就卡片和跳转
        st.session_state.pop("just_finished", None)
        from database import get_session as _get_sess
        finished_sid = st.session_state.get("last_finished_session")
        finished_s = _get_sess(finished_sid) if finished_sid else None

        if finished_s:
            total_vol = int(finished_s.get("total_volume") or 0)
            duration = finished_s.get("duration_minutes", 0)
            done_count = sum(
                1 for ex in finished_s.get("exercises_data", [])
                for sl in ex.get("set_logs", []) if sl.get("done")
            )

            st.markdown(f"## 🎉 训练完成！")
            st.markdown(f"**{finished_s.get('plan_name','')}** · {finished_s.get('target_muscle','')}")

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("训练容量", f"{total_vol} kg")
            with mc2:
                st.metric("完成组数", f"{done_count}")
            with mc3:
                st.metric("训练时长", f"{duration} 分钟")

            st.markdown("---")
            st.info("👉 点击页面顶部的 **「💚 AI联动建议」** Tab 查看：伤病预警 · 营养补剂建议 · 渐进超负荷建议")

            cf1, cf2 = st.columns([1, 1])
            with cf1:
                if st.button("✕ 关闭这张卡片", use_container_width=True, key="close_finish_card"):
                    st.rerun()
            with cf2:
                if st.button("🔄 重新开始今日训练", use_container_width=True, key="restart_today"):
                    st.rerun()
    else:
        # 智能匹配今天的训练
        today_weekday = date.today().weekday()
        today_iso = date.today().isoformat()
        today_schedules = get_schedules_by_date(today_iso)

        # 找出今天的待训练（不含休息日）
        pending_today = []
        for s in today_schedules:
            di = s.get("day_info", {})
            if s.get("status") == "pending" and not di.get("is_rest"):
                pending_today.append(s)

        if pending_today:
            st.markdown(f'<p style="color:#00d9f5;font-weight:700;font-size:16px;">📅 今天（{WEEKDAY_NAMES[today_weekday]}）的训练安排：</p>', unsafe_allow_html=True)
            for s in pending_today:
                di = s.get("day_info", {})
                sc1, sc2 = st.columns([3, 1])
                with sc1:
                    st.markdown(f'<div class="exercise-row"><b style="color:#00d9f5;">{s["schedule_time"]}</b> · {s.get("plan_name","")} · <span class="muscle-tag">{di.get("muscle_group","训练")}</span></div>', unsafe_allow_html=True)
                with sc2:
                    if st.button("▶ 开始", key=f"today_start_{s['id']}", use_container_width=True, type="primary"):
                        st.session_state["jump_schedule_id"] = s['id']
                        st.rerun()
            st.markdown("---")

        # 检查今天是否为休息日
        rest_today = [s for s in today_schedules if s.get("day_info",{}).get("is_rest")]
        if rest_today and not pending_today:
            st.markdown(f"""
            <div class="success-card" style="text-align:center;">
                💤 今天（{WEEKDAY_NAMES[today_weekday]}）是休息日，好好恢复！
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")

        # 或者从模板库随便选一个开始
        plans = list_plans()
        if not plans:
            st.info("还没有计划模板，请先在「AI训练计划」或「计划模板库」创建")
        else:
            st.markdown('<p style="color:#c8d8e8;font-weight:600;">或临时选一个计划开始（按当前日期智能匹配）：</p>', unsafe_allow_html=True)
            for p in plans:
                # 单日计划：直接用
                # 周计划：取今天对应那天
                if p.get("plan_type") == "weekly":
                    target_day = p["days_data"].get(str(today_weekday), {})
                    if target_day.get("is_rest"):
                        label_extra = f"（今天{WEEKDAY_NAMES[today_weekday]}=休息日）"
                        disabled = True
                    elif not target_day.get("exercises"):
                        label_extra = f"（今天{WEEKDAY_NAMES[today_weekday]}=未安排动作）"
                        disabled = True
                    else:
                        label_extra = f"（今天{WEEKDAY_NAMES[today_weekday]}={target_day.get('muscle_group','')} · {len(target_day['exercises'])} 个动作）"
                        disabled = False
                else:
                    sd = p["days_data"].get("single", {})
                    if sd.get("is_rest"):
                        label_extra = "（休息日）"
                        disabled = True
                    else:
                        label_extra = f"（{sd.get('muscle_group','')} · {len(sd.get('exercises',[]))} 个动作）"
                        disabled = False

                pc1, pc2 = st.columns([4, 1])
                with pc1:
                    type_icon = "📅" if p.get("plan_type") == "weekly" else "📋"
                    st.markdown(f"""
                    <div class="plan-card">
                        <div class="plan-name">{type_icon} {p['plan_name']}</div>
                        <div class="plan-meta">{label_extra}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with pc2:
                    if disabled:
                        st.button("不可用", key=f"begin_d_{p['id']}", use_container_width=True, disabled=True)
                    else:
                        if st.button("开始此计划", key=f"begin_{p['id']}", use_container_width=True, type="primary"):
                            # 直接创建临时安排
                            sid = add_schedule(
                                plan_id=p["id"],
                                schedule_date=today_iso,
                                schedule_time=datetime.now().strftime("%H:%M"),
                                weekday_index=today_weekday
                            )
                            st.session_state["jump_schedule_id"] = sid
                            st.rerun()


# =================================================================
# Tab5: AI联动建议
# =================================================================
with tabs[4]:
    last_sid = st.session_state.get("last_finished_session")
    sessions = list_sessions(limit=10)
    target_session = get_session(last_sid) if last_sid else (sessions[0] if sessions else None)

    if not target_session:
        st.info("还没有完成的训练。完成一次训练后会自动在这里显示个性化建议")
    else:
        st.markdown(f'<p style="color:#00d9f5;font-weight:700;font-size:18px;">📊 基于「{target_session["plan_name"]}」的个性化建议</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#8ca0b8;font-size:13px;">训练日期：{target_session["session_date"]} · 总容量：{int(target_session.get("total_volume") or 0)} kg · 时长：{target_session.get("duration_minutes",0)} 分钟</p>', unsafe_allow_html=True)
        st.markdown("---")

        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">🩺 伤病预警</p>', unsafe_allow_html=True)
        injury_warnings = check_injury_risk(
            profile,
            target_session.get("exercises_data", []),
            session_notes=target_session.get("notes") or ""
        )
        if injury_warnings:
            for w in injury_warnings:
                # 把消息里的换行转成 <br>
                _w_html = w.replace("\n", "<br>")
                st.markdown(f'<div class="alert-card">{_w_html}</div><br>', unsafe_allow_html=True)
            st.markdown('<p style="color:#ffaa3c;font-size:13px;">💡 建议：前往左侧「🩺 伤病筛查」详细描述症状获取专业评估</p>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-card">✅ 暂无伤病预警。如有任何不适，请前往「伤病筛查」咨询AI。</div>', unsafe_allow_html=True)

        # ===== 辅助工具推荐（基于训练备注） =====
        try:
            from equipment_data import recommend_equipment_from_notes, EQUIPMENT_CATEGORIES
            equip_recs = recommend_equipment_from_notes(target_session.get("notes") or "")
            if equip_recs:
                st.markdown("---")
                st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">🛡️ 辅助工具推荐</p>', unsafe_allow_html=True)
                for r in equip_recs:
                    cat_info = EQUIPMENT_CATEGORIES.get(r["category"], {})
                    icon = cat_info.get("icon", "🔧")
                    priority_color = "#ff5757" if r["priority"] == "high" else "#ffaa3c"
                    priority_text = "强烈建议" if r["priority"] == "high" else "可考虑"
                    st.markdown(f'''
                    <div style="background:rgba(255,170,60,0.06);border-left:3px solid {priority_color};
                        border-radius:8px;padding:12px 16px;margin:8px 0;">
                        <div style="color:{priority_color};font-weight:700;font-size:14px;">
                            {icon} {r['category']} · {priority_text}
                        </div>
                        <div style="color:#c8d8e8;font-size:13px;margin-top:6px;line-height:1.7;">
                            {r['reason']}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                st.markdown('<p style="color:#8ca0b8;font-size:13px;">→ 前往左侧菜单「🛡️ 辅助工具」查看具体品牌产品和评分</p>', unsafe_allow_html=True)
        except Exception:
            pass

        st.markdown("---")
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">💊 营养与补剂建议</p>', unsafe_allow_html=True)
        advice = get_nutrition_advice(target_session.get("target_muscle",""), target_session.get("exercises_data",[]))
        for tip in advice.get("post_workout", []):
            st.markdown(f'<p style="color:#c8d8e8;font-size:14px;">· {tip}</p>', unsafe_allow_html=True)
        st.markdown('<p style="color:#c8d8e8;font-weight:600;margin-top:12px;">推荐补剂：</p>', unsafe_allow_html=True)
        for supp in advice.get("supplements", []):
            priority_tag = "🔴 核心" if supp["priority"] == "core" else "🟡 可选"
            st.markdown(f'<div class="exercise-row"><b style="color:#00f5a0;">{priority_tag} {supp["category"]}</b><br><span style="color:#c8d8e8;font-size:13px;">{supp["reason"]}</span></div>', unsafe_allow_html=True)
        st.markdown('<br><p style="color:#8ca0b8;font-size:13px;">→ 想查看具体品牌产品？前往左侧菜单「补剂推荐」</p>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">📈 渐进超负荷建议</p>', unsafe_allow_html=True)
        po_tips = []
        for ex in target_session.get("exercises_data", []):
            tip = progressive_overload_tip(sessions, ex.get("name", ""))
            if tip: po_tips.append(tip)
        if po_tips:
            for t in po_tips:
                st.markdown(f'<div class="exercise-row">{t}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#8ca0b8;font-size:13px;">需要连续训练同一动作3次以上才能给出渐进建议</p>', unsafe_allow_html=True)


# =================================================================
# Tab6: 进步曲线
# =================================================================
with tabs[5]:
    sessions = list_sessions(limit=60)
    if not sessions:
        st.info("还没有训练记录。完成至少一次训练后会显示进步曲线")
    else:
        total_sessions = len(sessions)
        total_volume = sum(s.get("total_volume") or 0 for s in sessions)
        total_minutes = sum(s.get("duration_minutes") or 0 for s in sessions)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f'<div class="plan-card" style="text-align:center;"><div style="font-size:11px;color:#8ca0b8;letter-spacing:2px;">总训练次数</div><div style="font-size:42px;color:#00d9f5;font-weight:700;font-family:Rajdhani,sans-serif;">{total_sessions}</div></div>', unsafe_allow_html=True)
        with sc2:
            st.markdown(f'<div class="plan-card" style="text-align:center;"><div style="font-size:11px;color:#8ca0b8;letter-spacing:2px;">累计训练容量</div><div style="font-size:42px;color:#00f5a0;font-weight:700;font-family:Rajdhani,sans-serif;">{int(total_volume)}<span style="font-size:18px;">kg</span></div></div>', unsafe_allow_html=True)
        with sc3:
            st.markdown(f'<div class="plan-card" style="text-align:center;"><div style="font-size:11px;color:#8ca0b8;letter-spacing:2px;">累计训练时长</div><div style="font-size:42px;color:#7b61ff;font-weight:700;font-family:Rajdhani,sans-serif;">{int(total_minutes/60)}<span style="font-size:18px;">小时</span></div></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">📈 每次训练总容量</p>', unsafe_allow_html=True)
        try:
            import pandas as pd
            import altair as alt

            df = pd.DataFrame([
                {"日期": s["session_date"], "容量(kg)": int(s.get("total_volume") or 0)}
                for s in reversed(sessions)
            ])
            df["日期"] = pd.to_datetime(df["日期"])

            # 用altair精确控制坐标轴样式
            chart = (
                alt.Chart(df)
                .mark_line(point=alt.OverlayMarkDef(filled=True, size=80, color="#00d9f5"),
                           strokeWidth=3, color="#00d9f5")
                .encode(
                    x=alt.X("日期:T",
                            axis=alt.Axis(
                                format="%m/%d",
                                labelAngle=0,       # 水平显示
                                labelColor="#c8d8e8",
                                titleColor="#8ca0b8",
                                tickColor="#2a3a55",
                                domainColor="#2a3a55"
                            )),
                    y=alt.Y("容量(kg):Q",
                            axis=alt.Axis(
                                labelColor="#c8d8e8",
                                titleColor="#8ca0b8",
                                tickColor="#2a3a55",
                                domainColor="#2a3a55",
                                grid=True, gridColor="#1e2d42"
                            )),
                    tooltip=["日期:T", "容量(kg):Q"]
                )
                .properties(height=320)
                .configure_view(strokeWidth=0)
                .configure(background="transparent")
            )
            st.altair_chart(chart, use_container_width=True)
        except Exception as _e:
            for s in sessions[:10]:
                st.markdown(f'<div class="exercise-row">{s["session_date"]} · {s["plan_name"]} · {int(s.get("total_volume") or 0)} kg</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">🏆 动作PR追踪</p>', unsafe_allow_html=True)
        pr_records = {}
        for s in sessions:
            for ex in s.get("exercises_data", []):
                name = ex.get("name", "")
                if not name: continue
                for sl in ex.get("set_logs", []):
                    if sl.get("done") and sl.get("actual_weight"):
                        w = sl["actual_weight"]
                        r = sl.get("actual_reps", 0) or 0
                        if name not in pr_records or w > pr_records[name]["weight"]:
                            pr_records[name] = {"weight": w, "reps": r, "date": s["session_date"]}
        if pr_records:
            sorted_prs = sorted(pr_records.items(), key=lambda x: x[1]["weight"], reverse=True)
            for name, rec in sorted_prs[:15]:
                st.markdown(f'<div class="exercise-row"><b style="color:#00d9f5;">{name}</b> · 最大 <b style="color:#00f5a0;">{rec["weight"]}kg × {rec["reps"]}次</b> <span style="float:right;color:#8ca0b8;font-size:12px;">{rec["date"]}</span></div>', unsafe_allow_html=True)
        else:
            st.info("还没有打卡记录，完成几次训练后会显示PR")

        st.markdown("---")
        st.markdown('<p style="color:#e8eaf0;font-weight:700;font-size:16px;">📋 训练历史</p>', unsafe_allow_html=True)
        for s in sessions[:20]:
            with st.expander(f"{s['session_date']} · {s['plan_name']} · {int(s.get('total_volume') or 0)}kg · {s.get('duration_minutes',0)}分钟"):
                for ex in s.get("exercises_data", []):
                    done_sets = [sl for sl in ex.get("set_logs", []) if sl.get("done")]
                    if done_sets:
                        sets_str = " | ".join([f"{sl.get('actual_weight',0)}kg×{sl.get('actual_reps',0)}" for sl in done_sets])
                        st.markdown(f'<div class="exercise-row"><b>{ex["name"]}</b> · {sets_str}</div>', unsafe_allow_html=True)
                if s.get("notes"):
                    st.markdown(f'<p style="color:#8ca0b8;font-size:13px;margin-top:8px;">备注：{s["notes"]}</p>', unsafe_allow_html=True)
