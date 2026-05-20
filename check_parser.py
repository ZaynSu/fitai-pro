"""
诊断脚本：检查 training_helpers.py 是否是新版本，能否正确解析
直接双击运行，或在终端：python check_parser.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("FitAI Pro 解析器诊断工具")
print("=" * 60)

# 检查文件是否存在
helper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "training_helpers.py")
print(f"\n[1] 文件路径: {helper_path}")
print(f"    文件存在: {os.path.exists(helper_path)}")

if os.path.exists(helper_path):
    mtime = os.path.getmtime(helper_path)
    import datetime
    print(f"    最后修改时间: {datetime.datetime.fromtimestamp(mtime)}")

# 检查关键词
print("\n[2] 检查文件内容是否包含新关键词...")
with open(helper_path, "r", encoding="utf-8") as f:
    content = f.read()

checks = {
    "侧抬关键词": "侧抬",
    "前提关键词": "前提",
    "秒单位支持": "秒|分钟|分",
    "reps_display变量": "reps_display",
    "胸推关键词": "推胸",
}
for label, kw in checks.items():
    status = "✅" if kw in content else "❌"
    print(f"    {status} {label}: {'已包含' if kw in content else '缺失！'}")

# 测试解析
print("\n[3] 测试解析能力...")
try:
    from training_helpers import parse_ai_plan
    
    test_text = """1. 史密斯机胸推：3组×10-12次
2. 上斜哑铃推举：4组×12-15次
3. 三头肌伸展带绳索：3组×10-12次
1. 拉下拉：3组×10-12次
2. 坐姿划船机：4组×12-15次
1. 腿推机：3组×10-12次
3. 哑铃侧举：3组×10-12次
3. 平板支撑：3组×30-60秒
"""
    
    result = parse_ai_plan(test_text)
    print(f"    识别出 {len(result)} 个动作:")
    for r in result:
        print(f"      ✓ {r['name']} | {r['sets']}组 × {r['reps']}")
    
    if len(result) >= 6:
        print("\n✅ 解析器工作正常！")
        print("   如果Streamlit里仍然识别不到，说明Streamlit没加载新模块")
        print("   解决：完全关闭命令行窗口，重新打开cmd，再次 streamlit run app.py")
    else:
        print(f"\n⚠️  解析数量异常（应该 >= 6 个）")
        
except Exception as e:
    print(f"    ❌ 导入或解析出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
input("按 Enter 退出...")
