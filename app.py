import streamlit as st
from datetime import datetime, date, timedelta
from database import (
    load_profile, init_db, list_plans, get_plan,
    get_schedules_by_date, list_sessions, get_today_session
)
from ai_engine import check_ollama_status

st.set_page_config(page_title="FitAI Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');
html,body,[class*="css"]{font-family:'Noto Sans SC',sans-serif;}

/* 顶部欢迎栏 */
.welcome-bar{
    background:linear-gradient(135deg,rgba(0,217,245,0.08),rgba(123,97,255,0.08));
    border:1px solid rgba(0,217,245,0.2);
    border-radius:16px;padding:20px 28px;margin-bottom:20px;
    display:flex;justify-content:space-between;align-items:center;
}
.welcome-text{flex:1;}
.welcome-greeting{font-size:13px;color:#8ca0b8;letter-spacing:2px;}
.welcome-name{font-family:'Rajdhani',sans-serif;font-size:32px;color:#00d9f5;font-weight:700;margin-top:4px;}
.welcome-subtitle{font-size:13px;color:#c8d8e8;margin-top:4px;}
.welcome-stats{display:flex;gap:32px;}
.welcome-stat{text-align:center;}
.welcome-stat-num{font-family:'Rajdhani',sans-serif;font-size:32px;color:#00f5a0;font-weight:700;}
.welcome-stat-label{font-size:11px;color:#8ca0b8;letter-spacing:2px;margin-top:2px;}

/* 状态栏 */
.status-bar{display:flex;align-items:center;gap:8px;font-size:13px;color:#8ca0b8;}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;}
.dot-on{background:#00f5a0;box-shadow:0 0 6px #00f5a0;}
.dot-off{background:#ff5757;}

/* 今日训练大卡片 */
.today-card{background:linear-gradient(135deg,#1a2235,#162032);
    border:1px solid #2a3a55;border-radius:18px;padding:28px;margin-bottom:20px;}
.today-card-rest{background:linear-gradient(135deg,rgba(140,160,184,0.08),rgba(140,160,184,0.04));
    border-color:rgba(140,160,184,0.25);}
.today-label{font-size:12px;letter-spacing:3px;color:#8ca0b8;text-transform:uppercase;}
.today-title{font-family:'Rajdhani',sans-serif;font-size:36px;font-weight:700;
    background:linear-gradient(90deg,#00d9f5,#7b61ff);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    margin:8px 0;}
.today-muscle-tag{display:inline-block;padding:4px 14px;border-radius:14px;
    background:rgba(0,245,160,0.12);color:#00f5a0;border:1px solid rgba(0,245,160,0.3);
    font-size:13px;font-weight:600;margin-right:8px;}
.today-rest-tag{display:inline-block;padding:4px 14px;border-radius:14px;
    background:rgba(140,160,184,0.15);color:#8ca0b8;border:1px solid rgba(140,160,184,0.3);
    font-size:13px;font-weight:600;}
.today-detail{font-size:14px;color:#c8d8e8;margin-top:12px;line-height:1.8;}

/* 快捷模块卡片 */
.section-title{font-size:14px;letter-spacing:3px;color:#8ca0b8;
    text-transform:uppercase;margin:24px 0 12px;}

/* 社区占位卡片 */
.community-card{background:#1a2235;border:1px solid #2a3a55;border-radius:14px;
    padding:18px 22px;margin-bottom:12px;}
.community-user{display:flex;align-items:center;gap:12px;margin-bottom:10px;}
.community-avatar{width:42px;height:42px;border-radius:50%;
    background:linear-gradient(135deg,#00d9f5,#7b61ff);
    display:flex;align-items:center;justify-content:center;
    font-size:18px;font-weight:700;color:#0e1525;}
.community-user-info{flex:1;}
.community-username{font-weight:700;color:#e8eaf0;font-size:14px;}
.community-time{font-size:12px;color:#8ca0b8;}
.community-content{color:#c8d8e8;font-size:14px;line-height:1.7;margin:8px 0;}
.community-tags{margin-top:8px;}
.community-tag{display:inline-block;padding:2px 10px;border-radius:10px;
    background:rgba(0,217,245,0.1);color:#00d9f5;font-size:11px;
    border:1px solid rgba(0,217,245,0.25);margin-right:6px;}
.community-actions{display:flex;gap:24px;margin-top:12px;color:#8ca0b8;font-size:12px;}
.coming-soon{background:linear-gradient(135deg,rgba(255,170,87,0.08),rgba(255,170,87,0.04));
    border:1px dashed rgba(255,170,87,0.35);border-radius:14px;padding:16px 22px;
    color:#ffcc80;font-size:13px;text-align:center;margin-bottom:16px;}

/* 模块按钮覆盖 */
div[data-testid="column"] .stButton>button{
    background:#1a2235;
    border:1px solid #2a3a55;
    border-radius:14px;
    padding:18px 16px;
    width:100%;
    min-height:110px;
    transition:all 0.2s;
}
div[data-testid="column"] .stButton>button:hover{
    border-color:#00d9f5 !important;
    background:rgba(0,217,245,0.05) !important;
    transform:translateY(-2px);
}
div[data-testid="column"] .stButton>button p{
    color:#e8eaf0 !important;
    font-family:'Noto Sans SC',sans-serif;
    white-space:pre-line;
    text-align:center;
    line-height:1.7;
}
hr{border-color:#2a3a55;}
</style>
""", unsafe_allow_html=True)

init_db()
ollama_ok = check_ollama_status()
profile = load_profile()

WEEKDAY_NAMES = ["周一","周二","周三","周四","周五","周六","周日"]

# ===== 顶部状态栏 =====
s1, s2 = st.columns([2, 1])
with s1:
    dot = "dot dot-on" if ollama_ok else "dot dot-off"
    label = "AI 服务运行中" if ollama_ok else "AI 服务未启动"
    st.markdown(f'<div class="status-bar"><span class="{dot}"></span>{label}</div>', unsafe_allow_html=True)
with s2:
    today_str = date.today().strftime("%Y-%m-%d")
    weekday_name = WEEKDAY_NAMES[date.today().weekday()]
    st.markdown(f'<div class="status-bar" style="justify-content:flex-end;">📅 {today_str} · {weekday_name}</div>', unsafe_allow_html=True)

# ===== 欢迎栏（带统计数据） =====
if profile:
    sessions = list_sessions(limit=100)
    total_sessions = len(sessions)
    total_volume = sum(s.get("total_volume") or 0 for s in sessions)

    # 本周完成的训练
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_sessions = [s for s in sessions if s.get("session_date","") >= week_start.isoformat()]
    week_count = len(week_sessions)

    # 时段问候
    hour = datetime.now().hour
    if hour < 6:
        greeting = "凌晨好"
    elif hour < 12:
        greeting = "早上好"
    elif hour < 14:
        greeting = "中午好"
    elif hour < 18:
        greeting = "下午好"
    elif hour < 22:
        greeting = "晚上好"
    else:
        greeting = "夜深了"

    st.markdown(f"""
    <div class="welcome-bar">
        <div class="welcome-text">
            <div class="welcome-greeting">{greeting}</div>
            <div class="welcome-name">{profile['name']}</div>
            <div class="welcome-subtitle">目标：{profile.get('goal','增肌')} · 健身水平：{profile.get('fitness_level','新手')}</div>
        </div>
        <div class="welcome-stats">
            <div class="welcome-stat">
                <div class="welcome-stat-num">{week_count}</div>
                <div class="welcome-stat-label">本周训练</div>
            </div>
            <div class="welcome-stat">
                <div class="welcome-stat-num">{total_sessions}</div>
                <div class="welcome-stat-label">累计次数</div>
            </div>
            <div class="welcome-stat">
                <div class="welcome-stat-num">{int(total_volume/1000)}<span style="font-size:14px;">t</span></div>
                <div class="welcome-stat-label">累计容量</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="welcome-bar">
        <div class="welcome-text">
            <div class="welcome-greeting">欢迎</div>
            <div class="welcome-name">FitAI Pro</div>
            <div class="welcome-subtitle">运动营养 · 补剂推荐 · 伤病筛查 · 力量训练</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("👆 请先点击下方「用户档案」填写个人信息，AI 才能给出个性化建议。")

if not ollama_ok:
    st.warning("**⚠️ AI 服务未启动**\n\n1. 访问 ollama.com 下载安装 Ollama\n2. 终端运行：`ollama pull llama3`（首次约4GB）\n3. 终端运行：`ollama serve`\n4. 刷新页面")


# ===== 经期关怀卡片（仅女性用户）=====
if profile and profile.get("gender") == "女":
    try:
        from database import is_near_period
        _period_status = is_near_period(date.today())

        if _period_status == "in_period":
            st.markdown("""
            <div style="background:linear-gradient(135deg,rgba(255,121,180,0.12),rgba(255,121,180,0.04));
                border:1px solid rgba(255,121,180,0.3);border-radius:14px;padding:16px 22px;margin:12px 0;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:22px;">🌸</span>
                    <span style="color:#ff79b4;font-weight:700;font-size:16px;">温柔关怀</span>
                </div>
                <div style="color:#c8d8e8;font-size:14px;margin-top:8px;line-height:1.8;">
                    今天身体可能比较辛苦，多喝温水，少喝冷饮 💕<br>
                    可以选择休息或做一些轻度瑜伽、拉伸。无论选什么都好，照顾自己最重要。
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif _period_status and _period_status.startswith("pre_"):
            _d = _period_status.split("_")[1]
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(255,170,60,0.10),rgba(255,170,60,0.03));
                border:1px solid rgba(255,170,60,0.3);border-radius:14px;padding:14px 22px;margin:12px 0;">
                <div style="color:#ffaa3c;font-size:13px;">
                    💗 预计 <b>{_d} 天后</b> 经期来潮 · 这几天可以适当降低训练强度，多注意保暖
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif _period_status and _period_status.startswith("post_"):
            _d = _period_status.split("_")[1]
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(0,217,245,0.08),rgba(0,217,245,0.03));
                border:1px solid rgba(0,217,245,0.25);border-radius:14px;padding:14px 22px;margin:12px 0;">
                <div style="color:#00d9f5;font-size:13px;">
                    🌿 经期已结束 <b>{_d} 天</b> · 身体逐渐恢复中，建议从轻量训练开始，循序渐进
                </div>
            </div>
            """, unsafe_allow_html=True)
    except: pass


# ===== 今日训练大卡片 =====
if profile:
    today_iso = date.today().isoformat()
    today_schedules = get_schedules_by_date(today_iso)
    today_weekday = date.today().weekday()
    in_progress_session = get_today_session()

    # 找今天的训练 - 优先 in_progress > pending训练日 > 休息日
    if in_progress_session:
        # 训练进行中
        st.markdown('<p class="section-title">🎯 训练进行中</p>', unsafe_allow_html=True)
        ex_count = len(in_progress_session.get("exercises_data", []))
        done_sets = sum(
            1 for ex in in_progress_session.get("exercises_data", [])
            for sl in ex.get("set_logs", []) if sl.get("done")
        )
        total_sets = sum(len(ex.get("set_logs", [])) for ex in in_progress_session.get("exercises_data", []))
        progress = int(done_sets/total_sets*100) if total_sets else 0

        st.markdown(f"""
        <div class="today-card">
            <div class="today-label">⏳ 进行中</div>
            <div class="today-title">{in_progress_session['plan_name']}</div>
            <span class="today-muscle-tag">{in_progress_session.get('target_muscle','训练')}</span>
            <div class="today-detail">
                进度：{done_sets} / {total_sets} 组（{progress}%）· {ex_count} 个动作
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("➜ 继续训练", use_container_width=True, type="primary", key="home_continue"):
            st.switch_page("pages/4_力量训练.py")

    elif today_schedules:
        # 今天有日程
        pending = [s for s in today_schedules if s.get("status") == "pending"]
        if pending:
            sch = pending[0]
            di = sch.get("day_info", {})
            is_rest = di.get("is_rest", False)

            if is_rest:
                st.markdown('<p class="section-title">📅 今日</p>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="today-card today-card-rest">
                    <div class="today-label">💤 休息日</div>
                    <div class="today-title" style="background:linear-gradient(90deg,#8ca0b8,#5a7090);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">好好休息</div>
                    <span class="today-rest-tag">恢复中</span>
                    <div class="today-detail">
                        今天是计划安排的休息日，肌肉需要 48 小时恢复时间。
                        建议：充足睡眠、补充蛋白质、轻度拉伸放松。
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<p class="section-title">🎯 今日训练</p>', unsafe_allow_html=True)
                ex_count = len(di.get("exercises", []))
                muscle = di.get('muscle_group','训练')
                st.markdown(f"""
                <div class="today-card">
                    <div class="today-label">📅 {WEEKDAY_NAMES[today_weekday]} · {sch['schedule_time']}</div>
                    <div class="today-title">{sch.get('plan_name','训练')}</div>
                    <span class="today-muscle-tag">{muscle}</span>
                    <div class="today-detail">
                        本次将完成 <b style="color:#00f5a0;">{ex_count}</b> 个动作。<br>
                        预计训练时长 45-60 分钟。
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("➜ 开始训练", use_container_width=True, type="primary", key="home_start"):
                    st.session_state["jump_schedule_id"] = sch["id"]
                    st.switch_page("pages/4_力量训练.py")
    else:
        # 今天没安排
        st.markdown('<p class="section-title">📅 今日</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="today-card">
            <div class="today-label">😴 今日未安排</div>
            <div class="today-title">还没安排训练</div>
            <div class="today-detail">
                前往「力量训练」让 AI 生成计划，并在日历中一键安排到本周。
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("➜ 去安排训练", use_container_width=True, key="home_arrange"):
            st.switch_page("pages/4_力量训练.py")


# ===== 快捷模块入口 =====
st.markdown('<p class="section-title">⚡ 功能模块</p>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    if st.button("👤\n\n**用户档案**\n\n身高体重 · 健身目标", key="btn_profile", use_container_width=True):
        st.switch_page("pages/1_用户档案.py")
with c2:
    if st.button("💊\n\n**补剂推荐**\n\n个性化补剂 · AI营养师", key="btn_supp", use_container_width=True):
        st.switch_page("pages/2_补剂推荐.py")
with c3:
    if st.button("🩺\n\n**伤病筛查**\n\nAI康复师 · 风险评估", key="btn_injury", use_container_width=True):
        st.switch_page("pages/3_伤病筛查.py")
with c4:
    if st.button("🏋️\n\n**力量训练**\n\nAI计划 · 训练日历 · 打卡", key="btn_train", use_container_width=True):
        st.switch_page("pages/4_力量训练.py")
with c5:
    if st.button("🛡️\n\n**辅助工具**\n\n护具 · 助力带 · 恢复", key="btn_equip", use_container_width=True):
        st.switch_page("pages/5_辅助工具.py")


# ===== 社区动态（占位） =====
st.markdown('<p class="section-title">🌟 健身圈动态</p>', unsafe_allow_html=True)
st.markdown("""
<div class="coming-soon">
    🚧 社区功能开发中 · 即将上线 - 训练分享、饮食日记、补剂测评、伤病恢复经验，纯粹的健身自律平台
</div>
""", unsafe_allow_html=True)

# 模拟社区动态（占位数据）
demo_posts = [
    {
        "avatar": "粟",
        "username": "粟展",
        "time": "2 分钟前",
        "content": "今天完成了胸+三头训练，史密斯架卧推突破 50kg 了！💪 训练 45 分钟，状态在线。",
        "tags": ["#训练日常", "#胸肌"],
        "likes": 18, "comments": 3, "shares": 1
    },
    {
        "avatar": "L",
        "username": "Lina_健身",
        "time": "1 小时前",
        "content": "分享一下我的经期训练心得：经期前 3 天可以保持轻强度的瑜伽，经期 1-3 天完全休息，后期再恢复力量训练。听身体的话很重要🌷",
        "tags": ["#女性健身", "#经期管理"],
        "likes": 86, "comments": 24, "shares": 12
    },
    {
        "avatar": "T",
        "username": "Tom_健身",
        "time": "3 小时前",
        "content": "测评了 ON 金标乳清和 Dymatize ISO100，详细对比口感、溶解度、性价比。我个人觉得 ISO100 更适合饭后补充，金标早晨喝更好...",
        "tags": ["#补剂测评", "#蛋白粉"],
        "likes": 142, "comments": 38, "shares": 25
    },
    {
        "avatar": "K",
        "username": "康复教练Kai",
        "time": "5 小时前",
        "content": "肩部不适怎么办？我整理了一份「肩袖肌群激活+预防」的简单方案，适合所有训练前热身使用，每个动作 30 秒，全程不到 5 分钟。",
        "tags": ["#伤病恢复", "#肩部"],
        "likes": 67, "comments": 9, "shares": 18
    },
]
for post in demo_posts:
    st.markdown(f"""
    <div class="community-card">
        <div class="community-user">
            <div class="community-avatar">{post['avatar']}</div>
            <div class="community-user-info">
                <div class="community-username">{post['username']}</div>
                <div class="community-time">{post['time']}</div>
            </div>
        </div>
        <div class="community-content">{post['content']}</div>
        <div class="community-tags">
            {''.join([f'<span class="community-tag">{t}</span>' for t in post['tags']])}
        </div>
        <div class="community-actions">
            <span>❤️ {post['likes']}</span>
            <span>💬 {post['comments']}</span>
            <span>🔄 {post['shares']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p style="text-align:center;font-size:13px;color:#4a6080;">⚠️ 本系统内容仅供参考，不构成医疗建议 · 所有数据储存于本地，不上传服务器</p>', unsafe_allow_html=True)
