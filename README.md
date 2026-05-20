🏋️ FitAI Pro
面向中国健身用户的本地 AI 一体化训练 · 营养 · 装备助手
An AI-Powered Fitness Assistant for Chinese Users
[!\[Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[!\[Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[!\[Ollama](https://img.shields.io/badge/Ollama-llama3-000000.svg)](https://ollama.com/)
[!\[License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
📖 项目简介
FitAI Pro 是一款基于本地大模型（Ollama + llama3）的一体化健身助手，专为中国市场设计。
不同于市面上大众化的健身 App，FitAI Pro 专注于主流产品忽略的细分人群——女性新手、有伤病史的用户、追求科学化训练的进阶玩家。
💡 为什么做这个？
现有健身 App 的 AI 教练能力普遍有限：
❌ 对女性新手不够友好（动辄推荐高难度动作）
❌ 忽视经期、伤病等特殊身体状态
❌ 补剂和装备信息混乱，缺乏真实用户评测
❌ 不会基于用户的体测数据（体脂率、围度）做个性化推荐
FitAI Pro 通过Prompt 工程 + 结构化领域知识库解决这些问题。
✨ 核心功能
五大模块概览
|模块|主要功能|
|-|-|
|👤 用户档案|基础档案 + 进阶档案（体脂率、肌肉量、16 项围度数据）|
|💊 补剂中心|25 个品类 · 20+ 主流品牌 · 49 个产品 · 五维社区评分|
|🩺 伤病筛查|AI 康复师对话 + 训练备注关键词预警（14 部位 × 6 类不适）|
|🏋️ 力量训练|AI 计划生成 / 训练日历 / 今日打卡 / AI 联动建议 / 进步曲线|
|🛡️ 辅助工具|8 大品类 · 30+ 品牌 · 五维评分 + 多条评测日记|
|🌸 经期管理|4 位 PIN 隐私保护 · 周期预测 · 训练自动避开|
特色亮点
🤖 AI 多角色 Prompt 编排
训练师 · 营养师 · 康复师 · 装备顾问 · 默认顾问，5 个角色独立 Prompt，用户体测数据动态注入。
📈 训练计划智能解析
将 AI 自然语言输出自动解析为结构化训练数据（部位、动作、组数、次数），支持单日 / 周计划自动识别。
🌸 经期智能避训
基于历史数据预测下次经期，训练计划自动避开经期前后 3 天；4 位 PIN 密码保护隐私数据。
🏆 虎扑风评分社区
补剂和辅助工具均采用列表概览 + 详情页双层结构，支持五维评分、多条评测日记、服用周期追踪。
🎬 项目截图
首页 - 训练总览
!\[首页](screenshots/01-home.png)
用户档案 - 基础信息 + 进阶体测
!\[用户档案](screenshots/02-profile.png)
补剂中心 - 虎扑风评分社区
!\[补剂](screenshots/03-supplements.png)
伤病筛查 - AI 康复师对话
!\[伤病筛查](screenshots/04-injury.png)
力量训练 - AI 计划生成
!\[力量训练](screenshots/05-training.png)
辅助工具 - 八大品类
!\[辅助工具](screenshots/06-equipment.png)
经期管理 - 隐私保护 + 智能避训
!\[经期管理](screenshots/07-menstrual.png)
🚀 快速开始
环境要求
* Python 3.10+
* [Ollama](https://ollama.com/) 已安装并下载 llama3 模型
* Windows / macOS / Linux
安装步骤
1. 克隆项目
git clone https://github.com/sneakesu-create/fitai-pro.git
cd fitai-pro
2. 安装依赖
pip install -r requirements.txt
3. 启动 Ollama 服务并下载模型
ollama serve
ollama pull llama3
4. 初始化数据库（首次运行）
python seed\_brands.py
5. 启动应用
streamlit run app.py
浏览器打开 `http://localhost:8501` 即可使用。
🏗️ 技术架构
技术栈
|层|技术|用途|
|-|-|-|
|前端|Streamlit + 自研 hupu\_ui 组件库|多页面交互、虎扑风评分卡片、深色主题|
|AI|Ollama (本地部署) + llama3:8b|五角色 Prompt 编排|
|后端|Python 3.10 + 标准库|业务逻辑、Prompt 编排、数据解析|
|数据|SQLite|12+ 张表、ON CONFLICT 数据演进|
|可视化|Altair + 自研 SVG/HTML|进步曲线、月历、围度对比|
项目结构
fitai-pro/
├── app.py                  # 主入口（首页 + 5 个模块入口）
├── ai\_engine.py            # Ollama AI 引擎 + 多角色 Prompt
├── database.py             # SQLite 数据层（12+ 张表）
├── training\_helpers.py     # 训练计划 NLP 解析 + 伤病预警
├── supplement\_data.py      # 补剂分类配置（25 品类）
├── equipment\_data.py       # 辅助工具数据（30+ 产品）
├── seed\_brands.py          # 品牌产品种子数据
├── hupu\_ui.py              # 虎扑风 UI 组件库
├── pages/
│   ├── 1\_用户档案.py
│   ├── 2\_补剂推荐.py
│   ├── 3\_伤病筛查.py
│   ├── 4\_力量训练.py
│   └── 5\_辅助工具.py
├── screenshots/            # 项目截图
└── requirements.txt
💡 核心算法亮点
1\. 训练计划智能解析器
问题：AI 返回的是自然语言，需要解析为结构化训练数据。
解决：
关键词加权评分识别天数、部位、动作、组数次数
用户提问 + AI 回复前 800 字加权识别部位
用户问"一天臀腿训练"被误判为全身计划的 bug 已修复
2\. 部位识别加权算法
python
top 2 ≥ 1 且 ≥ top 1 × 25% 时判为组合训练
if scores\[top2] >= 1 and scores\[top2] >= scores\[top1] \* 0.25:
    muscle\_group = f"{top1}+{top2}"  # 如 "胸+三头"
3\. AI Prompt 工程
多层注入：基础角色 → 用户档案 → 进阶体测数据 → 特殊规则
python
女性新手 6 大禁推动作
FEMALE\_BEGINNER\_FORBIDDEN = \[
    "标准引体向上", "双杠臂屈伸",
    "负重保加利亚分腿蹲", "奥林匹克举",
    # ...
]
强制开场白：让 AI 必须说"根据你的进阶档案我为你设计了..."，让用户感知到个性化。
4\. Streamlit Widget 重建机制
问题：Streamlit 硬规则——widget 一旦用 key 实例化，value 参数会被忽略，session\_state 也不能修改。
解决：generation 编号机制
python
每次按"全部勾选 / 全部取消"按钮，generation +1
\_ck\_key = f"keep\_{msg\_hash}\_g{generation}\_{i}"
Streamlit 把它当全新 widget 创建
st.checkbox(value=default\_checked, key=\_ck\_key)
📊 项目数据
代码量：约 9,700 行 Python
数据表：12+ 张
AI Prompt 角色**：5 个
补剂产品：49 个 / 20+ 品牌 / 25 品类
辅助工具：30+ 产品 / 8 大品类
开发周期：8 个月（断续）/ 3 个月集中开发
🛣️ Roadmap
✅ 已完成
5 大功能模块
AI 多角色 Prompt 编排
经期管理 + 隐私保护
虎扑风评分社区
训练计划 NLP 解析
进阶体测档案 + AI 个性化
🔄 进行中
邀请真实用户试用（目标 5-10 人）
收集反馈持续迭代
📋 计划中
移动端重做（Webview / Flutter）
AI 输出自动化评估管线（LLM-as-Judge）
训练动作示范视频集成
多用户登录系统
👤 作者
粟展 ([@sneakesu-create](https://github.com/sneakesu-create))
湘潭理工学院 数据科学与大数据技术在读 · 关注 AI 应用、健身科学化、女性健康
🙏 致谢
[Ollama](https://ollama.com/) — 本地大模型运行环境
[Streamlit](https://streamlit.io/) — 单人快速做出全栈应用的利器
感谢指导老师对项目的支持
📄 License
XIT License © 2026 谢沐雨
⭐如果这个项目对你有启发，欢迎 Star！

