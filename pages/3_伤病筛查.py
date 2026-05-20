import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import load_profile, save_chat, load_chat, clear_chat
from ai_engine import chat_with_ollama, check_ollama_status

st.set_page_config(page_title="伤病筛查", page_icon="🩺", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@700&family=Noto+Sans+SC:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans SC', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e); color: #e0e0e0; }
[data-testid="stSidebar"] { background: rgba(255,255,255,0.04); border-right: 1px solid rgba(255,255,255,0.08); }
.page-title { font-family:'Rajdhani',sans-serif; font-size:38px; font-weight:700;
    background:linear-gradient(90deg,#ff7070,#ffaa57); -webkit-background-clip:text;
    -webkit-text-fill-color:transparent; margin-bottom:4px; }
.chat-user { background:rgba(255,112,112,0.08); border:1px solid rgba(255,112,112,0.15);
    border-radius:12px; padding:12px 16px; margin:8px 0; font-size:14px; }
.chat-ai { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
    border-radius:12px; padding:14px 18px; margin:8px 0; font-size:14px; line-height:1.9; }
.stButton>button {
    background: linear-gradient(90deg, #ff7070, #ffaa57);
    color: #1a0a0a; font-weight:700; border:none;
    border-radius:8px; font-family:'Rajdhani',sans-serif; font-size:15px;
}
.stSelectbox>div>div, .stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important; color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🩺 伤病筛查</div>', unsafe_allow_html=True)
st.markdown('<p style="color:rgba(255,255,255,0.4);font-size:14px;">描述症状 → 点击 AI 评估 → 查看结果（不替代医生诊断）</p>', unsafe_allow_html=True)

profile = load_profile()
ollama_ok = check_ollama_status()
MODULE = "injury"

if "injury_messages" not in st.session_state:
    st.session_state.injury_messages = load_chat(MODULE)

if not ollama_ok:
    st.error("❌ AI 服务未启动。请打开新的终端窗口运行 `ollama serve`，然后刷新页面。")

tab_form, tab_chat = st.tabs(["📋 填写症状（点这里开始）", "💬 对话记录"])

with tab_form:
    st.markdown("#### 填写症状信息")
    c1, c2 = st.columns(2)
    with c1:
        area = st.selectbox("受伤/疼痛部位", [
            "膝关节", "肩关节", "腰部/脊柱", "肘关节",
            "踝关节", "髋关节", "颈部", "其他部位"
        ])
        pain_type = st.selectbox("疼痛性质", [
            "刺痛（急性、尖锐）", "酸痛（肌肉疲劳感）",
            "胀痛（持续性肿胀感）", "灼烧感（神经相关）",
            "钝痛（慢性不适）", "运动时痛、休息不痛", "休息时也痛"
        ])
        pain_level = st.slider("疼痛程度（1轻微～10剧烈）", 1, 10, 4)
    with c2:
        duration = st.selectbox("持续时间", [
            "刚刚发生（<24小时）", "几天（1-7天）",
            "几周（1-4周）", "超过1个月", "超过3个月（慢性）"
        ])
        trigger = st.selectbox("触发原因", [
            "训练中突然受伤", "训练后逐渐出现",
            "长期积累，无明显诱因", "日常生活动作引起", "旧伤复发"
        ])
        extra = st.text_area("补充说明（可选）",
            placeholder="有无肿胀？有无弹响？之前是否有过类似情况？",
            height=108)

    st.markdown("---")
    if st.button("🔍 开始 AI 评估", use_container_width=True, type="primary"):
        if not ollama_ok:
            st.error("❌ AI 服务未启动，请先运行 `ollama serve`")
        else:
            question = f"""请帮我评估以下运动伤病症状：
- 部位：{area}
- 疼痛性质：{pain_type}
- 疼痛程度：{pain_level}/10
- 持续时间：{duration}
- 触发原因：{trigger}
- 补充信息：{extra if extra.strip() else '无'}

请分5点回答：1)可能原因 2)风险等级 3)应急处理 4)是否需要就医 5)康复训练建议"""

            st.session_state.injury_messages.append({"role": "user", "content": question})
            save_chat(MODULE, "user", question)

            with st.spinner("AI 康复师评估中，请稍候（约20-60秒）..."):
                reply = chat_with_ollama(
                    st.session_state.injury_messages, MODULE, profile)

            st.session_state.injury_messages.append({"role": "assistant", "content": reply})
            save_chat(MODULE, "assistant", reply)

            st.markdown("---")
            st.markdown("#### ✅ AI 评估结果")
            st.markdown(f'<div class="chat-ai">🤖 {reply}</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:12px;color:rgba(255,255,255,0.25);line-height:2.2;margin-top:24px;">
    ⚠️ 以下情况请立即就医：剧烈疼痛无法活动 · 明显肿胀变形 · 关节不稳定 · 麻木失去知觉 · 持续疼痛超过2周
    </div>
    """, unsafe_allow_html=True)

with tab_chat:
    st.markdown("#### 快速提问")
    qcols = st.columns(4)
    quick_qs = ["膝盖深蹲时疼痛怎么办？", "RICE原则是什么？", "肩袖损伤如何康复？", "腰痛能继续训练吗？"]
    for i, q in enumerate(quick_qs):
        with qcols[i]:
            if st.button(q, key=f"qq_{i}", use_container_width=True):
                if not ollama_ok:
                    st.error("AI 服务未启动")
                else:
                    st.session_state.injury_messages.append({"role": "user", "content": q})
                    save_chat(MODULE, "user", q)
                    with st.spinner("思考中..."):
                        reply = chat_with_ollama(st.session_state.injury_messages, MODULE, profile)
                    st.session_state.injury_messages.append({"role": "assistant", "content": reply})
                    save_chat(MODULE, "assistant", reply)
                    st.rerun()

    st.markdown("---")
    if st.session_state.injury_messages:
        for msg in st.session_state.injury_messages:
            if msg["role"] == "user":
                content = msg["content"]
                if "请帮我评估以下运动伤病症状" in content:
                    content = "📋 已提交症状评估表单"
                st.markdown(f'<div class="chat-user">🙋 {content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:rgba(255,255,255,0.25);text-align:center;padding:40px;">暂无对话记录，请先在「填写症状」Tab 进行评估</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 继续提问")
    user_input = st.text_input("输入问题...", placeholder="例如：有什么拉伸动作可以缓解？", key="inj_free_input")
    bcol1, bcol2 = st.columns([4, 1])
    with bcol1:
        if st.button("发送", key="inj_send", use_container_width=True):
            if not ollama_ok:
                st.error("AI 服务未启动")
            elif user_input.strip():
                st.session_state.injury_messages.append({"role": "user", "content": user_input})
                save_chat(MODULE, "user", user_input)
                with st.spinner("思考中..."):
                    reply = chat_with_ollama(st.session_state.injury_messages, MODULE, profile)
                st.session_state.injury_messages.append({"role": "assistant", "content": reply})
                save_chat(MODULE, "assistant", reply)
                st.rerun()
    with bcol2:
        if st.button("🗑 清空", key="inj_clear", use_container_width=True):
            clear_chat(MODULE)
            st.session_state.injury_messages = []
            st.rerun()