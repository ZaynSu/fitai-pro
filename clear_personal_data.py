"""
🧹 数据清理脚本
==================
在上传 GitHub 前运行，清除所有个人测试数据。

清理范围：
- 用户档案（姓名、年龄、身高体重等）
- 进阶档案（体脂、围度等）
- 经期数据（含密码 PIN）
- AI 对话历史
- 训练计划、训练日程、训练记录
- 补剂评分、辅助工具评分
- 评测日记
- 服用周期
- 用户设置

保留的内容（这些是项目本身的种子数据，没有隐私）：
- 补剂品牌库 (supp_brand)
- 补剂产品库 (supp_product)
- 工具品类配置（在代码里，不在数据库）

使用方法：
    python clear_personal_data.py
"""

import sqlite3
import os
import sys

DB_PATH = "fitness_data.db"

# 含个人数据的表清单
PERSONAL_TABLES = [
    "user_profile",          # 基础档案（姓名、年龄等）
    "advanced_profile",      # 进阶档案（体测数据）
    "menstrual_cycle",       # 经期设置（含 PIN 密码）
    "menstrual_log",         # 经期记录
    "chat_history",          # AI 对话历史
    "plans",                 # 训练计划模板
    "schedule",              # 训练日程
    "workout_session",       # 训练打卡记录
    "supp_rating",           # 补剂评分
    "equipment_rating",      # 辅助工具评分
    "product_review",        # 评测日记
    "supplement_cycle",      # 服用周期
    "user_settings",         # 用户设置
]


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ 找不到数据库文件：{DB_PATH}")
        print("   请在 AI_Fitness 项目根目录下运行此脚本")
        sys.exit(1)

    print("🧹 FitAI Pro 个人数据清理工具")
    print("=" * 50)
    print()
    print("将清理以下表的所有数据：")
    for t in PERSONAL_TABLES:
        print(f"  - {t}")
    print()
    print("保留以下表（项目种子数据）：")
    print("  - supp_brand    (补剂品牌库)")
    print("  - supp_product  (补剂产品库)")
    print()

    # 二次确认
    confirm = input("⚠️  这个操作不可撤销！确认清理吗？请输入 YES 确认：").strip()
    if confirm != "YES":
        print("❌ 已取消，未执行任何操作")
        sys.exit(0)

    # 备份
    backup_choice = input("📦 是否先备份数据库？(y/n，强烈建议 y)：").strip().lower()
    if backup_choice in ("y", "yes", ""):
        from datetime import datetime
        backup_path = f"fitness_data.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy(DB_PATH, backup_path)
        print(f"✅ 已备份到：{backup_path}")
        print()

    # 执行清理
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    cleared = []
    skipped = []

    for table in PERSONAL_TABLES:
        try:
            # 先看有多少行
            c.execute(f"SELECT COUNT(*) FROM {table}")
            count = c.fetchone()[0]

            # 清空
            c.execute(f"DELETE FROM {table}")
            # 重置自增 ID（如果表有自增）
            try:
                c.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            except sqlite3.OperationalError:
                # sqlite_sequence 可能不存在
                pass

            cleared.append((table, count))
            print(f"✅ {table:25s} 清理了 {count} 条记录")
        except sqlite3.OperationalError as e:
            skipped.append((table, str(e)))
            print(f"⏭️  {table:25s} 跳过（{e}）")

    conn.commit()

    # 验证保留的种子数据
    print()
    print("📊 保留的种子数据：")
    for table in ("supp_brand", "supp_product"):
        try:
            c.execute(f"SELECT COUNT(*) FROM {table}")
            n = c.fetchone()[0]
            print(f"  {table:25s} {n} 条")
        except:
            pass

    conn.close()

    print()
    print("=" * 50)
    print(f"✅ 清理完成！共清理 {len(cleared)} 张表")
    if skipped:
        print(f"⏭️  跳过 {len(skipped)} 张表（可能未创建）")
    print()
    print("下一步：")
    print("  1. 启动 streamlit run app.py 验证数据已清空")
    print("  2. 用一个测试身份重新填写一次（如 名字: 测试用户）")
    print("  3. 决定要不要把数据库文件也上传到 GitHub")
    print()
    print("⚠️  关于 fitness_data.db：")
    print("   - 推荐：加入 .gitignore，不上传数据库文件")
    print("     这样每个克隆者首次运行时会自动初始化空库")
    print("   - 如果一定要上传：现在的数据库已清空，可以上传")


if __name__ == "__main__":
    main()
