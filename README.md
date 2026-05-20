# 🏋️ FitAI Pro

**面向中国健身用户的本地 AI 一体化训练 · 营养 · 装备助手**

*A Local AI-Powered Fitness Assistant for Chinese Users*

[!\[Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[!\[Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[!\[Ollama](https://img.shields.io/badge/Ollama-llama3-orange.svg)](https://ollama.com/)
[!\[License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
\[!\[Code Size](https://img.shields.io/badge/Python-9.4k%20lines-brightgreen.svg)]()

[功能演示](#-功能演示) · [快速开始](#-快速开始) · [技术架构](#-技术架构) · [核心算法](#-核心算法亮点) · [English](#-english)

!\[FitAI Pro 主页](docs/screenshots/01-home.png)

## 📖 项目简介

**FitAI Pro** 是一款基于本地大模型 (Ollama + llama3) 的 AI 健身助手，针对中国市场设计，特别关注**主流健身 App 忽略的人群**——女性新手、有伤病史用户、追求科学化训练的进阶玩家。

### 💡 为什么做这个？

市面健身 App 的 AI 教练能力有限：

* ❌ 对女性新手不友好（动辄推荐高难度动作）
* ❌ 忽视经期、伤病等特殊状态
* ❌ 补剂和装备信息混乱，缺真实用户评测
* ❌ 不会基于体测数据（体脂、围度）做个性化

FitAI Pro 用 **Prompt 工程 + 结构化领域知识库** 解决这些问题。

## ✨ 功能演示

### 📊 五大核心模块

|模块|功能亮点|
|-|-|
|👤 **用户档案**|基础档案 + 进阶档案（体脂 / 肌肉量 / 16 项围度）|
|💊 **补剂中心**|25 品类 · 20+ 主流品牌 · 49 个产品 · 五维社区评分|
|🩺 **伤病筛查**|AI 康复师 + 训练备注关键词预警（14 部位 × 6 类不适）|
|🏋️ **力量训练**|AI 计划生成 / 训练日历 / 今日打卡 / AI 联动建议 / 进步曲线|
|🛡️ **辅助工具**|8 大品类 · 30+ 品牌 · 五维评分 + 多条评测日记|
|🌸 **经期管理**|4 位 PIN 隐私保护 · 周期预测 · 训练自动避开|



#### 👤 用户档案

基础档案 + 进阶档案，AI 必须基于体测数据给出个性化方案。

!\[用户档案](docs/screenshots/02-profile.png)

#### 💊 补剂中心

20+ 主流品牌 · 49 个产品，列表概览 + 详情页双层结构，支持五维社区评分。

!\[补剂中心 - 品牌库](docs/screenshots/03-supplements.png)

#### 🩺 伤病筛查

14 部位 × 6 类不适关键词预警，AI 康复师对话评估，**不替代医生诊断**。

!\[伤病筛查](docs/screenshots/04-injury.png)

#### 🏋️ 力量训练

AI 训练计划生成 + 模板库 + 日历 + 今日打卡 + 联动建议 + 进步曲线，一站式力量训练管理。

!\[力量训练](docs/screenshots/05-training.png)

#### 🛡️ 辅助工具

8 大品类（腰带 / 护腕 / 护膝 / 护肘 / 助力带 / 筋膜枪 / 拉力带 / 推举垫），五维评分 + 评测日记。

!\[辅助工具](docs/screenshots/06-equipment.png)

#### 🌸 经期管理

4 位 PIN 隐私保护 · 自动锁回 · 周期预测 · 训练计划自动避开经期 ± 3 天。

!\[经期管理](docs/screenshots/07-menstrual.png)

### 🎯 特色功能

**🤖 AI 多角色 Prompt 编排**

* 训练师 · 营养师 · 康复师 · 装备顾问 · 默认顾问
* 用户体测数据动态注入，AI 必须开场白说明使用了个人数据

**📈 训练计划智能解析**

* 自然语言 → 结构化数据（部位 / 动作 / 组数 / 次数）
* 单日 / 周计划自动识别，关键词加权评分判断目标部位

**🌸 经期智能避训**

* 4 位 PIN 隐私保护，可设置自动锁回
* 基于历史数据预测周期，训练计划自动避开经期 ± 3 天

**🏆 虎扑风评分社区**

* 五维评分 + 多条评测日记 + 服用周期追踪
* 列表概览 + 详情页双层结构，支持品牌库点击进入

## 🚀 快速开始

### 环境要求

* Python 3.10+
* [Ollama](https://ollama.com/) 已安装并下载 llama3 模型
* Windows / macOS / Linux

安装步骤

1. 克隆项目
git clone https://github.com/<你的用户名>/fitai-pro.git
cd fitai-pro

# 2\. 安装依赖

pip install -r requirements.txt

# 3\. 启动 Ollama 服务

ollama serve
ollama pull llama3

# 4\. 初始化数据库（首次运行）

python seed\_brands.py

# 5\. 启动应用

streamlit run app.py

浏览器打开 `http://localhost:8501` 即可使用。

🏗️ 技术架构
┌─────────────────────────────────────────────────────┐
│              Streamlit Multi-Page UI                                                                        │
│  主页 · 用户档案 · 补剂 · 伤病 · 训练 · 辅助工具                                                       │
└─────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────┐
│             业务层 (Python Modules)                                                                       │
│   ai\_engine · training\_helpers · equipment\_data ·                                                │
│   supplement\_data · hupu\_ui                                                                             │
└─────────────────────────────────────────────────────┘
↓                                                                      ↓
┌─────────────────────────┐  ┌──────────────────────┐
│  Ollama (本地大模型)                          │  │  SQLite (单文件库)                      │
│  llama3:8b                                         │  │  12+ 张表                                  │
│  多角色 Prompt                                  │  │  ON CONFLICT 演进                   │
└─────────────────────────┘  └──────────────────────┘

### 技术栈

|层|技术|用途|
|-|-|-|
|前端|Streamlit + 自研 hupu\_ui 组件库|多页面交互 / 虎扑风评分卡片 / 深色主题|
|AI|Ollama + llama3:8b|本地大模型，五角色 Prompt 编排|
|后端|Python 3.10|业务逻辑 / Prompt 编排 / 数据解析|
|数据|SQLite|12+ 张表 / ON CONFLICT 数据演进|
|可视化|Altair + 自研 SVG/HTML|进步曲线 / 月历 / 围度对比|



💡 核心算法亮点

1️⃣训练计划智能解析器

**问题**：AI 返回的是自然语言，需要解析出结构化训练数据。

**解决**：

* 关键词加权评分识别天数、部位、动作、组数次数
* 用户提问 + AI 回复前 800 字加权部位识别
* 实际 bug 修复：用户问"一天臀腿训练"被识别为全身计划

  * 加入 `\\\\\\\_force\\\\\\\_single` 关键词检测（"一天"/"单日"）
  * 天标题数量阈值（≥2 才算周计划）

2️⃣ 部位识别加权算法

python

top 2 ≥ 1 且 ≥ top 1 × 25% 时判为组合训练

if scores\\\[top2] >= 1 and scores\\\[top2] >= scores\\\[top1] \\\* 0.25:
muscle\\\_group = f"{top1}+{top2}"  # 如 "胸+三头"
3️⃣ AI Prompt
多层注入：基础角色 → 用户档案 → 进阶体测数据 → 特殊规则
python

女性新手 6 大禁推动作清单

FEMALE\\\_BEGINNER\\\_FORBIDDEN = \\\[
"标准引体向上", "双杠臂屈伸",
"负重保加利亚分腿蹲", "奥林匹克举",
# ...
]
强制开场白：让 AI 必须说"根据你的进阶档案我为你设计了..."，让用户感知个性化。
4️⃣ Streamlit Widget
问题：Streamlit 硬规则——widget 一旦用 key 实例化，value 参数会被忽略，session\\\_state 也不能改。
解决：generation 编号机制
python

每次按"全部勾选/取消"按钮，generation +1

\\\_ck\\\_key = f"keep\\\_{msg\\\_hash}\\\_g{generation}\\\_{i}"

Streamlit 看到全新 key，把 widget 当全新创建

st.checkbox(value=default\\\_checked, key=\\\_ck\\\_key)
📊 项目数据
代码量：\\\~9,400 行 Python + \\\~2,000 行 CSS/HTML
数据表：12+ 张
AI Prompt 角色：5 个
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
🔄 进行中
邀请真实用户试用（目标 5-10 人）
收集反馈迭代

📋 计划中
移动端重做（Webview / Flutter）
AI 输出自动化评估管线（LLM-as-Judge）
训练动作示范视频集成
多用户登录系统
📁 项目结构
AI\\\_Fitness/
├── app.py                    # 主入口（首页 + 5 个模块入口）
├── ai\\\_engine.py              # Ollama AI 引擎 + 多角色 Prompt
├── database.py               # SQLite 数据层（12+ 张表）
├── training\\\_helpers.py       # 训练计划 NLP 解析 + 伤病预警
├── supplement\\\_data.py        # 补剂分类配置（25 品类）
├── equipment\\\_data.py         # 辅助工具数据（30+ 产品）
├── seed\\\_brands.py            # 品牌产品种子数据
├── hupu\\\_ui.py                # 虎扑风 UI 组件库
├── pages/
│   ├── 1\\\_用户档案.py          # 基础 + 进阶档案 + 经期管理
│   ├── 2\\\_补剂推荐.py          # 6 Tab 补剂中心
│   ├── 3\\\_伤病筛查.py          # AI 康复师对话
│   ├── 4\\\_力量训练.py          # 6 Tab 训练核心模块
│   └── 5\\\_辅助工具.py          # 5 Tab 辅助工具
├── docs/
│   └── screenshots/          # 项目截图
└── requirements.txt
🤝 贡献
这是一个个人学习项目，目前不接受外部贡献。如果你发现问题或有建议，欢迎在 Issues 区讨论。
📄 License
MIT License — 详见 \[LICENSE](LICENSE) 文件
👤 作者
粟展(\[@sneakesu](https://github.com))
湘潭理工学院数据科学与大数据技术专业在读，关注 AI 应用、健身科学化、女性健康。
📧 Email: sneakesu@gmail.com
🎓 湘潭理工学院 / 数据科学与大数据技术
🏋️ 个人健身爱好者，跆拳道运动员
🙏 致谢
感谢 \[Ollama](https://ollama.com/) 提供本地大模型运行环境
感谢 \[Streamlit](https://streamlit.io/) 让单人快速做出全栈应用成为可能
感谢指导老师对项目的支持

⭐ 如果这个项目对你有启发，欢迎 Star！
🌍 English
📖 About
FitAI Pro is an AI-powered fitness assistant built on top of a locally-deployed LLM (Ollama + llama3), specifically designed for the Chinese market. It focuses on \*\*user groups underserved by mainstream fitness apps— female beginners, people with injury history, and advanced users seeking science-based training.
✨ Highlights
🤖5 AI Roles: Trainer · Nutritionist · Rehab Specialist · Equipment Advisor · Default Advisor
📊 Advanced Profile\*\*: Body fat %, muscle mass, 16 circumference measurements — auto-injected into AI prompts
🌸Menstrual Cycle Management\*\* (female users): PIN-protected, training auto-avoids cycle ± 3 days
🏆 Hupu-Style Rating Community\*\*: 5-dimension scoring + multi-entry review journals + supplement cycle tracking
🧠 Custom NLP Parser: Translates AI free-text plans into structured training data
💪 Injury Warning System: Keyword analysis of 14 body parts × 6 discomfort types
🏗️ Tech Stack
Frontend: Streamlit + custom CSS component library
AI: Ollama (local llama3:8b) with multi-role prompt orchestration
Backend: Python 3.10 (standard library only)
Data: SQLite (12+ tables with `ON CONFLICT` schema evolution)
Viz: Altair + custom SVG/HTML
📊 Stats
\\\~9,400 lines of Python
12+ SQLite tables
5 AI prompt roles
49 supplement products across 25 categories
30+ equipment products across 8 categories
🚀 Quick Start
git clone https://github.com/<your-username>/fitai-pro.git
cd fitai-pro
pip install -r requirements.txt
ollama serve \\\&\\\& ollama pull llama3
python seed\\\_brands.py
streamlit run app.py

Open `http://localhost:8501` in your browser.

📄 License

MIT

