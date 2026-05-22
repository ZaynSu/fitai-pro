"""
完整数据库层 - 支持按周几分组的训练计划
"""
import sqlite3
import json
from datetime import datetime, date, timedelta

DB_PATH = "fitness_data.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, age INTEGER, gender TEXT,
        height REAL, weight REAL, goal TEXT,
        fitness_level TEXT, health_conditions TEXT,
        dietary_restrictions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # 进阶档案（体测数据 - 体脂率/肌肉量/围度等）
    c.execute("""CREATE TABLE IF NOT EXISTS advanced_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1 UNIQUE,
        body_fat_pct REAL,
        muscle_mass REAL,
        fat_free_mass REAL,
        visceral_fat INTEGER,
        bone_mass REAL,
        bmr INTEGER,
        body_water_pct REAL,
        chest_cm REAL,
        waist_cm REAL,
        hip_cm REAL,
        left_thigh_cm REAL,
        right_thigh_cm REAL,
        left_arm_cm REAL,
        right_arm_cm REAL,
        left_calf_cm REAL,
        right_calf_cm REAL,
        measured_at TEXT,
        notes TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, module TEXT, role TEXT, content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS supp_brand (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_cn TEXT NOT NULL, name_en TEXT, country TEXT, tier TEXT,
        description TEXT, logo_emoji TEXT, verified INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS supp_product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER NOT NULL, series_name TEXT NOT NULL,
        category TEXT NOT NULL, subcategory TEXT, description TEXT,
        key_features TEXT, certifications TEXT,
        ref_price_min REAL, ref_price_max REAL, currency TEXT DEFAULT 'CNY',
        sizes TEXT, flavors TEXT,
        science_rating INTEGER DEFAULT 3, target_users TEXT,
        usage_timing TEXT, dosage TEXT, cautions TEXT,
        verified INTEGER DEFAULT 1, submitted_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS supp_rating (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL, user_name TEXT, flavor TEXT,
        dim1_score INTEGER, dim2_score INTEGER, dim3_score INTEGER,
        dim4_score INTEGER, dim5_score INTEGER,
        overall REAL, review TEXT, likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # ===== 训练计划（新结构：支持单日/多日）=====
    # plan_type: 'single' = 单日计划，'weekly' = 一周计划
    # days_data: 单日时只有1个key='single'，一周时key为0-6（周一到周日）
    # 每个day包含: {muscle_group, is_rest, exercises}
    c.execute("""CREATE TABLE IF NOT EXISTS workout_plan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        plan_name TEXT NOT NULL,
        description TEXT,
        plan_type TEXT DEFAULT 'single',
        days_data TEXT NOT NULL,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # ===== 日历调度 =====
    # 单日计划：直接用plan_id
    # 周计划：plan_id + weekday_index（0=周一, 6=周日）
    c.execute("""CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        plan_id INTEGER NOT NULL,
        weekday_index INTEGER,
        schedule_date DATE NOT NULL,
        schedule_time TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        notify_status TEXT DEFAULT 'none',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # ===== 训练会话 =====
    c.execute("""CREATE TABLE IF NOT EXISTS workout_session (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        plan_id INTEGER, plan_name TEXT,
        session_date DATE NOT NULL,
        target_muscle TEXT,
        exercises_data TEXT NOT NULL,
        total_volume REAL DEFAULT 0,
        duration_minutes INTEGER,
        notes TEXT,
        status TEXT DEFAULT 'in_progress',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS workout_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, exercise TEXT, reps INTEGER,
        duration_seconds INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # 用户偏好设置
    c.execute("""CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        setting_key TEXT NOT NULL,
        setting_value TEXT,
        UNIQUE(user_id, setting_key))""")

    # 经期管理表
    c.execute("""CREATE TABLE IF NOT EXISTS menstrual_cycle (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1 UNIQUE,
        last_start_date TEXT,
        cycle_length INTEGER DEFAULT 28,
        period_length INTEGER DEFAULT 5,
        auto_avoid INTEGER DEFAULT 1,
        privacy_pin TEXT,
        notes TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # 经期日记/历史（每次经期开始/结束的实际记录）
    c.execute("""CREATE TABLE IF NOT EXISTS menstrual_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        start_date TEXT NOT NULL,
        end_date TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # 辅助工具评分
    c.execute("""CREATE TABLE IF NOT EXISTS equipment_rating (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        category TEXT NOT NULL,
        brand TEXT NOT NULL,
        product_name TEXT NOT NULL,
        protection INTEGER DEFAULT 0,
        comfort INTEGER DEFAULT 0,
        value INTEGER DEFAULT 0,
        durability INTEGER DEFAULT 0,
        appearance INTEGER DEFAULT 0,
        review TEXT,
        is_owned INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, category, product_name))""")

    # 辅助工具评测日记（一个产品可以有多条日记）
    c.execute("""CREATE TABLE IF NOT EXISTS equipment_journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        content TEXT NOT NULL,
        stars INTEGER DEFAULT 5,
        usage_days INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # 补剂评分
    c.execute("""CREATE TABLE IF NOT EXISTS supplement_rating (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        category TEXT NOT NULL,
        brand TEXT NOT NULL,
        product_name TEXT NOT NULL,
        effectiveness INTEGER DEFAULT 0,
        taste INTEGER DEFAULT 0,
        value INTEGER DEFAULT 0,
        solubility INTEGER DEFAULT 0,
        side_effects INTEGER DEFAULT 0,
        review TEXT,
        is_owned INTEGER DEFAULT 0,
        purchase_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, category, product_name))""")

    # 补剂周期日记（含使用天数）
    c.execute("""CREATE TABLE IF NOT EXISTS supplement_journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        content TEXT NOT NULL,
        stars INTEGER DEFAULT 5,
        usage_days INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # 多条评测日记 (产品评论)
    # product_type: 'equipment' / 'supplement'
    c.execute("""CREATE TABLE IF NOT EXISTS product_review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        product_type TEXT NOT NULL,
        category TEXT NOT NULL,
        product_name TEXT NOT NULL,
        brand TEXT,
        review_stars INTEGER DEFAULT 0,
        review_text TEXT NOT NULL,
        usage_day INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    # 补剂服用周期
    c.execute("""CREATE TABLE IF NOT EXISTS supplement_cycle (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        product_name TEXT NOT NULL,
        brand TEXT,
        category TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT,
        dosage TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    conn.commit()
    conn.close()


# ===== 用户偏好设置 =====
def get_setting(key, default=None, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT setting_value FROM user_settings WHERE user_id=? AND setting_key=?",
              (user_id, key))
    row = c.fetchone(); conn.close()
    return row[0] if row else default

def set_setting(key, value, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO user_settings (user_id, setting_key, setting_value)
                 VALUES (?,?,?)
                 ON CONFLICT(user_id, setting_key)
                 DO UPDATE SET setting_value=excluded.setting_value""",
              (user_id, key, str(value)))
    conn.commit(); conn.close()


# ===== 经期管理 =====
def get_menstrual_cycle(user_id=1):
    """获取经期设置"""
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM menstrual_cycle WHERE user_id=?", (user_id,))
    row = c.fetchone()
    cols = [d[0] for d in c.description] if row else []
    conn.close()
    return dict(zip(cols, row)) if row else None

def save_menstrual_cycle(last_start_date, cycle_length=28, period_length=5,
                          auto_avoid=1, privacy_pin=None, notes="", user_id=1):
    """保存经期设置"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO menstrual_cycle
                 (user_id, last_start_date, cycle_length, period_length,
                  auto_avoid, privacy_pin, notes, updated_at)
                 VALUES (?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
                 ON CONFLICT(user_id) DO UPDATE SET
                 last_start_date=excluded.last_start_date,
                 cycle_length=excluded.cycle_length,
                 period_length=excluded.period_length,
                 auto_avoid=excluded.auto_avoid,
                 privacy_pin=COALESCE(excluded.privacy_pin, menstrual_cycle.privacy_pin),
                 notes=excluded.notes,
                 updated_at=CURRENT_TIMESTAMP""",
              (user_id, last_start_date, cycle_length, period_length,
               auto_avoid, privacy_pin, notes))
    conn.commit(); conn.close()

def delete_menstrual_cycle(user_id=1):
    """删除经期设置（用户撤回隐私）"""
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM menstrual_cycle WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM menstrual_log WHERE user_id=?", (user_id,))
    conn.commit(); conn.close()

def add_menstrual_log(start_date, end_date=None, notes="", user_id=1):
    """记录一次实际经期"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO menstrual_log (user_id, start_date, end_date, notes)
                 VALUES (?,?,?,?)""", (user_id, start_date, end_date, notes))
    log_id = c.lastrowid
    # 同步更新 last_start_date
    c.execute("""UPDATE menstrual_cycle SET last_start_date=?, updated_at=CURRENT_TIMESTAMP
                 WHERE user_id=?""", (start_date, user_id))
    conn.commit(); conn.close()
    return log_id

def update_menstrual_log_end(log_id, end_date):
    """补充经期结束日期"""
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE menstrual_log SET end_date=? WHERE id=?", (end_date, log_id))
    conn.commit(); conn.close()

def get_recent_menstrual_logs(user_id=1, limit=12):
    """获取最近的经期记录"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM menstrual_log WHERE user_id=?
                 ORDER BY start_date DESC LIMIT ?""", (user_id, limit))
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]


# ===== 辅助工具评分 =====
def save_equipment_rating(category, brand, product_name, ratings: dict,
                           review="", is_owned=False, user_id=1):
    """保存或更新工具评分"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO equipment_rating
                 (user_id, category, brand, product_name,
                  protection, comfort, value, durability, appearance,
                  review, is_owned)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)
                 ON CONFLICT(user_id, category, product_name) DO UPDATE SET
                 brand=excluded.brand,
                 protection=excluded.protection,
                 comfort=excluded.comfort,
                 value=excluded.value,
                 durability=excluded.durability,
                 appearance=excluded.appearance,
                 review=excluded.review,
                 is_owned=excluded.is_owned,
                 created_at=CURRENT_TIMESTAMP""",
              (user_id, category, brand, product_name,
               int(ratings.get("protection", 0)),
               int(ratings.get("comfort", 0)),
               int(ratings.get("value", 0)),
               int(ratings.get("durability", 0)),
               int(ratings.get("appearance", 0)),
               review, int(bool(is_owned))))
    conn.commit(); conn.close()


def get_equipment_rating(product_name, category, user_id=1):
    """获取单个产品的评分"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM equipment_rating
                 WHERE user_id=? AND category=? AND product_name=?""",
              (user_id, category, product_name))
    row = c.fetchone()
    cols = [d[0] for d in c.description] if row else []
    conn.close()
    return dict(zip(cols, row)) if row else None


def get_all_equipment_ratings(user_id=1):
    """获取所有工具评分（按分类分组）"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM equipment_rating WHERE user_id=?
                 ORDER BY created_at DESC""", (user_id,))
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]


def get_owned_equipment(user_id=1):
    """获取用户标记为"已拥有"的工具"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM equipment_rating
                 WHERE user_id=? AND is_owned=1
                 ORDER BY created_at DESC""", (user_id,))
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]


# ===== 辅助工具评测日记 =====
def add_equipment_journal(product_name, category, content, stars=5, usage_days=0, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO equipment_journal
                 (user_id, product_name, category, content, stars, usage_days)
                 VALUES (?,?,?,?,?,?)""",
              (user_id, product_name, category, content, int(stars), int(usage_days)))
    conn.commit(); conn.close()

def get_equipment_journals(product_name, category, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM equipment_journal
                 WHERE user_id=? AND product_name=? AND category=?
                 ORDER BY created_at DESC""",
              (user_id, product_name, category))
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

def delete_equipment_journal(journal_id, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM equipment_journal WHERE id=? AND user_id=?", (journal_id, user_id))
    conn.commit(); conn.close()


# ===== 补剂评分 =====
def save_supplement_rating(category, brand, product_name, ratings: dict,
                            review="", is_owned=False, purchase_date=None, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO supplement_rating
                 (user_id, category, brand, product_name,
                  effectiveness, taste, value, solubility, side_effects,
                  review, is_owned, purchase_date)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                 ON CONFLICT(user_id, category, product_name) DO UPDATE SET
                 brand=excluded.brand,
                 effectiveness=excluded.effectiveness,
                 taste=excluded.taste,
                 value=excluded.value,
                 solubility=excluded.solubility,
                 side_effects=excluded.side_effects,
                 review=excluded.review,
                 is_owned=excluded.is_owned,
                 purchase_date=COALESCE(excluded.purchase_date, supplement_rating.purchase_date),
                 created_at=CURRENT_TIMESTAMP""",
              (user_id, category, brand, product_name,
               int(ratings.get("effectiveness", 0)),
               int(ratings.get("taste", 0)),
               int(ratings.get("value", 0)),
               int(ratings.get("solubility", 0)),
               int(ratings.get("side_effects", 0)),
               review, int(bool(is_owned)), purchase_date))
    conn.commit(); conn.close()

def get_supplement_rating(product_name, category, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM supplement_rating
                 WHERE user_id=? AND category=? AND product_name=?""",
              (user_id, category, product_name))
    row = c.fetchone()
    cols = [d[0] for d in c.description] if row else []
    conn.close()
    return dict(zip(cols, row)) if row else None

def get_all_supplement_ratings(user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM supplement_rating WHERE user_id=?
                 ORDER BY created_at DESC""", (user_id,))
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]


# ===== 补剂周期日记 =====
def add_supplement_journal(product_name, category, content, stars=5, usage_days=0, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO supplement_journal
                 (user_id, product_name, category, content, stars, usage_days)
                 VALUES (?,?,?,?,?,?)""",
              (user_id, product_name, category, content, int(stars), int(usage_days)))
    conn.commit(); conn.close()

def get_supplement_journals(product_name, category, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM supplement_journal
                 WHERE user_id=? AND product_name=? AND category=?
                 ORDER BY created_at DESC""",
              (user_id, product_name, category))
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

def delete_supplement_journal(journal_id, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM supplement_journal WHERE id=? AND user_id=?", (journal_id, user_id))
    conn.commit(); conn.close()


# ===== 评测日记（多条评论） =====
def add_product_review(product_type, category, product_name, brand,
                        review_text, review_stars=0, usage_day=None, user_id=1):
    """添加一条评测"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO product_review
                 (user_id, product_type, category, product_name, brand,
                  review_stars, review_text, usage_day)
                 VALUES (?,?,?,?,?,?,?,?)""",
              (user_id, product_type, category, product_name, brand,
               int(review_stars), review_text, usage_day))
    rid = c.lastrowid
    conn.commit(); conn.close()
    return rid

def get_product_reviews(product_type, product_name, category, user_id=1):
    """获取某产品的所有评测（按时间倒序）"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM product_review
                 WHERE user_id=? AND product_type=? AND product_name=? AND category=?
                 ORDER BY created_at DESC""",
              (user_id, product_type, product_name, category))
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

def delete_product_review(review_id, user_id=1):
    """删除一条评测"""
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM product_review WHERE id=? AND user_id=?", (review_id, user_id))
    conn.commit(); conn.close()

def get_review_count_by_product(product_type, product_name, category, user_id=1):
    """获取某产品的评测数量"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT COUNT(*) FROM product_review
                 WHERE user_id=? AND product_type=? AND product_name=? AND category=?""",
              (user_id, product_type, product_name, category))
    cnt = c.fetchone()[0]
    conn.close()
    return cnt


# ===== 补剂服用周期 =====
def add_supplement_cycle(product_name, brand, category, start_date,
                          dosage="", notes="", user_id=1):
    """开始一个新的服用周期"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO supplement_cycle
                 (user_id, product_name, brand, category, start_date, dosage, notes)
                 VALUES (?,?,?,?,?,?,?)""",
              (user_id, product_name, brand, category, start_date, dosage, notes))
    cid = c.lastrowid
    conn.commit(); conn.close()
    return cid

def end_supplement_cycle(cycle_id, end_date, notes_append="", user_id=1):
    """结束一个服用周期"""
    conn = get_conn(); c = conn.cursor()
    if notes_append:
        c.execute("""UPDATE supplement_cycle
                     SET end_date=?, notes=COALESCE(notes,'') || ? WHERE id=? AND user_id=?""",
                  (end_date, "\n" + notes_append, cycle_id, user_id))
    else:
        c.execute("UPDATE supplement_cycle SET end_date=? WHERE id=? AND user_id=?",
                  (end_date, cycle_id, user_id))
    conn.commit(); conn.close()

def get_supplement_cycles(product_name, category, user_id=1):
    """获取某补剂的所有服用周期"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM supplement_cycle
                 WHERE user_id=? AND product_name=? AND category=?
                 ORDER BY start_date DESC""",
              (user_id, product_name, category))
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

def get_active_supplement_cycle(product_name, category, user_id=1):
    """获取某补剂的当前进行中周期（end_date为空）"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM supplement_cycle
                 WHERE user_id=? AND product_name=? AND category=? AND end_date IS NULL
                 ORDER BY start_date DESC LIMIT 1""",
              (user_id, product_name, category))
    row = c.fetchone()
    cols = [d[0] for d in c.description] if row else []
    conn.close()
    return dict(zip(cols, row)) if row else None


def predict_period_dates(user_id=1, weeks_ahead=8):
    """
    预测接下来 N 周内的所有经期日期
    返回 set[date]
    """
    from datetime import date as _date, timedelta as _td

    cycle = get_menstrual_cycle(user_id)
    if not cycle or not cycle.get("last_start_date"):
        return set()

    try:
        last = datetime.strptime(cycle["last_start_date"], "%Y-%m-%d").date()
    except:
        return set()

    cycle_len = cycle.get("cycle_length") or 28
    period_len = cycle.get("period_length") or 5

    today = _date.today()
    horizon_end = today + _td(weeks=weeks_ahead)
    # 也回溯一段时间（为了显示日历上已过经期）
    horizon_start = today - _td(weeks=4)

    period_dates = set()
    current = last
    # 往前回溯到 horizon_start 之前
    while current > horizon_start:
        current -= _td(days=cycle_len)
    # 从这里开始往后推
    while current <= horizon_end:
        for i in range(period_len):
            d = current + _td(days=i)
            if horizon_start <= d <= horizon_end:
                period_dates.add(d)
        current += _td(days=cycle_len)
    return period_dates


def is_near_period(target_date, user_id=1, buffer_days=3):
    """
    判断某日是否在经期前后 buffer_days 天内
    返回:
      - 'in_period': 当天在经期内
      - 'pre_X': 经期前第 X 天（X=1,2,3）
      - 'post_X': 经期结束后第 X 天（X=1,2,3）
      - None: 都不是
    """
    from datetime import date as _date, timedelta as _td

    cycle = get_menstrual_cycle(user_id)
    if not cycle or not cycle.get("last_start_date"):
        return None

    period_dates = predict_period_dates(user_id, weeks_ahead=8)
    if not period_dates:
        return None

    if target_date in period_dates:
        return "in_period"

    # 找最近的经期窗口
    sorted_dates = sorted(period_dates)
    # 找经期段（连续的日期）
    period_ranges = []
    cur_start = sorted_dates[0]
    cur_end = sorted_dates[0]
    for d in sorted_dates[1:]:
        if (d - cur_end).days == 1:
            cur_end = d
        else:
            period_ranges.append((cur_start, cur_end))
            cur_start = cur_end = d
    period_ranges.append((cur_start, cur_end))

    for pr_start, pr_end in period_ranges:
        # 经期前 N 天
        for i in range(1, buffer_days + 1):
            if target_date == pr_start - _td(days=i):
                return f"pre_{i}"
        # 经期后 N 天
        for i in range(1, buffer_days + 1):
            if target_date == pr_end + _td(days=i):
                return f"post_{i}"
    return None


# ===== 用户档案 =====
def save_profile(data):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM user_profile")
    c.execute("""INSERT INTO user_profile
        (name,age,gender,height,weight,goal,fitness_level,health_conditions,dietary_restrictions)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (data.get("name"),data.get("age"),data.get("gender"),data.get("height"),
         data.get("weight"),data.get("goal"),data.get("fitness_level"),
         data.get("health_conditions"),data.get("dietary_restrictions")))
    conn.commit(); conn.close()

def load_profile():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1")
    row = c.fetchone(); conn.close()
    if row:
        keys = ["id","name","age","gender","height","weight","goal",
                "fitness_level","health_conditions","dietary_restrictions","created_at"]
        return dict(zip(keys, row))
    return None


# ===== 进阶档案 =====
def save_advanced_profile(data, user_id=1):
    """
    data: dict 含字段:
    body_fat_pct, muscle_mass, fat_free_mass, visceral_fat, bone_mass, bmr,
    body_water_pct, chest_cm, waist_cm, hip_cm, left_thigh_cm, right_thigh_cm,
    left_arm_cm, right_arm_cm, left_calf_cm, right_calf_cm, measured_at, notes
    """
    conn = get_conn(); c = conn.cursor()
    # None 数值统一存 NULL
    def _n(v):
        if v is None or v == "":
            return None
        try:
            return float(v) if not isinstance(v, int) else v
        except:
            return None

    c.execute("""INSERT INTO advanced_profile
        (user_id, body_fat_pct, muscle_mass, fat_free_mass, visceral_fat, bone_mass,
         bmr, body_water_pct, chest_cm, waist_cm, hip_cm,
         left_thigh_cm, right_thigh_cm, left_arm_cm, right_arm_cm,
         left_calf_cm, right_calf_cm, measured_at, notes, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            body_fat_pct=excluded.body_fat_pct,
            muscle_mass=excluded.muscle_mass,
            fat_free_mass=excluded.fat_free_mass,
            visceral_fat=excluded.visceral_fat,
            bone_mass=excluded.bone_mass,
            bmr=excluded.bmr,
            body_water_pct=excluded.body_water_pct,
            chest_cm=excluded.chest_cm,
            waist_cm=excluded.waist_cm,
            hip_cm=excluded.hip_cm,
            left_thigh_cm=excluded.left_thigh_cm,
            right_thigh_cm=excluded.right_thigh_cm,
            left_arm_cm=excluded.left_arm_cm,
            right_arm_cm=excluded.right_arm_cm,
            left_calf_cm=excluded.left_calf_cm,
            right_calf_cm=excluded.right_calf_cm,
            measured_at=excluded.measured_at,
            notes=excluded.notes,
            updated_at=CURRENT_TIMESTAMP""",
        (user_id,
         _n(data.get("body_fat_pct")),
         _n(data.get("muscle_mass")),
         _n(data.get("fat_free_mass")),
         data.get("visceral_fat") if data.get("visceral_fat") not in (None,"") else None,
         _n(data.get("bone_mass")),
         data.get("bmr") if data.get("bmr") not in (None,"") else None,
         _n(data.get("body_water_pct")),
         _n(data.get("chest_cm")),
         _n(data.get("waist_cm")),
         _n(data.get("hip_cm")),
         _n(data.get("left_thigh_cm")),
         _n(data.get("right_thigh_cm")),
         _n(data.get("left_arm_cm")),
         _n(data.get("right_arm_cm")),
         _n(data.get("left_calf_cm")),
         _n(data.get("right_calf_cm")),
         data.get("measured_at"),
         data.get("notes","")))
    conn.commit(); conn.close()

def load_advanced_profile(user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM advanced_profile WHERE user_id=?", (user_id,))
    row = c.fetchone()
    cols = [d[0] for d in c.description] if row else []
    conn.close()
    return dict(zip(cols, row)) if row else None

def clear_advanced_profile(user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM advanced_profile WHERE user_id=?", (user_id,))
    conn.commit(); conn.close()


# ===== AI对话 =====
def save_chat(module, role, content, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_id,module,role,content) VALUES (?,?,?,?)",
              (user_id,module,role,content))
    conn.commit(); conn.close()

def load_chat(module, user_id=1, limit=20):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT role,content FROM chat_history
                 WHERE user_id=? AND module=? ORDER BY id DESC LIMIT ?""",
              (user_id,module,limit))
    rows = c.fetchall(); conn.close()
    return [{"role":r[0],"content":r[1]} for r in reversed(rows)]

def clear_chat(module, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE user_id=? AND module=?", (user_id,module))
    conn.commit(); conn.close()


# ===== 兼容旧训练日志 =====
def save_workout(exercise, reps, duration, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO workout_log (user_id,exercise,reps,duration_seconds) VALUES (?,?,?,?)",
              (user_id,exercise,reps,duration))
    conn.commit(); conn.close()

def load_workout_history(user_id=1, limit=10):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT exercise,reps,duration_seconds,created_at FROM workout_log
                 WHERE user_id=? ORDER BY id DESC LIMIT ?""", (user_id,limit))
    rows = c.fetchall(); conn.close()
    return rows


# ===== 补剂品牌产品（保持原有）=====
def get_all_brands():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM supp_brand ORDER BY tier, name_cn")
    rows = c.fetchall(); conn.close()
    keys = ["id","name_cn","name_en","country","tier","description","logo_emoji","verified","created_at"]
    return [dict(zip(keys, r)) for r in rows]

def get_brand(brand_id):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM supp_brand WHERE id=?", (brand_id,))
    row = c.fetchone(); conn.close()
    if not row: return None
    keys = ["id","name_cn","name_en","country","tier","description","logo_emoji","verified","created_at"]
    return dict(zip(keys, row))

def add_brand(data):
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO supp_brand (name_cn,name_en,country,tier,description,logo_emoji,verified)
                 VALUES (?,?,?,?,?,?,?)""",
              (data.get("name_cn"),data.get("name_en"),data.get("country"),
               data.get("tier"),data.get("description"),data.get("logo_emoji","🏷"),
               data.get("verified",1)))
    bid = c.lastrowid; conn.commit(); conn.close()
    return bid

def get_products_by_category(category=None, brand_id=None, only_verified=True):
    conn = get_conn(); c = conn.cursor()
    sql = """SELECT p.*, b.name_cn as brand_name, b.logo_emoji as brand_emoji
             FROM supp_product p JOIN supp_brand b ON p.brand_id=b.id WHERE 1=1"""
    params = []
    if category: sql += " AND p.category=?"; params.append(category)
    if brand_id: sql += " AND p.brand_id=?"; params.append(brand_id)
    if only_verified: sql += " AND p.verified=1"
    sql += " ORDER BY p.science_rating DESC, b.name_cn"
    c.execute(sql, params)
    rows = c.fetchall(); cols = [d[0] for d in c.description]; conn.close()
    result = []
    for r in rows:
        d = dict(zip(cols, r))
        for f in ["sizes","flavors","key_features","certifications","target_users"]:
            if d.get(f):
                try: d[f] = json.loads(d[f])
                except: d[f] = []
        result.append(d)
    return result

def get_product(product_id):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT p.*, b.name_cn as brand_name, b.logo_emoji as brand_emoji
                 FROM supp_product p JOIN supp_brand b ON p.brand_id=b.id WHERE p.id=?""",
              (product_id,))
    row = c.fetchone()
    if not row: conn.close(); return None
    cols = [d[0] for d in c.description]; conn.close()
    d = dict(zip(cols, row))
    for f in ["sizes","flavors","key_features","certifications","target_users"]:
        if d.get(f):
            try: d[f] = json.loads(d[f])
            except: d[f] = []
    return d

def add_product(data):
    conn = get_conn(); c = conn.cursor()
    def to_json(v):
        if isinstance(v,(list,dict)): return json.dumps(v, ensure_ascii=False)
        return v
    c.execute("""INSERT INTO supp_product
        (brand_id,series_name,category,subcategory,description,key_features,
         certifications,ref_price_min,ref_price_max,sizes,flavors,science_rating,
         target_users,usage_timing,dosage,cautions,verified,submitted_by)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (data.get("brand_id"),data.get("series_name"),data.get("category"),
         data.get("subcategory"),data.get("description"),
         to_json(data.get("key_features")),to_json(data.get("certifications")),
         data.get("ref_price_min"),data.get("ref_price_max"),
         to_json(data.get("sizes")),to_json(data.get("flavors")),
         data.get("science_rating",3),to_json(data.get("target_users")),
         data.get("usage_timing"),data.get("dosage"),data.get("cautions"),
         data.get("verified",0),data.get("submitted_by")))
    pid = c.lastrowid; conn.commit(); conn.close()
    return pid

def get_all_categories():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM supp_product WHERE verified=1 ORDER BY category")
    rows = c.fetchall(); conn.close()
    return [r[0] for r in rows]

def get_pending_products():
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT p.*, b.name_cn as brand_name FROM supp_product p
                 JOIN supp_brand b ON p.brand_id=b.id
                 WHERE p.verified=0 ORDER BY p.created_at DESC""")
    rows = c.fetchall(); cols = [d[0] for d in c.description]; conn.close()
    return [dict(zip(cols, r)) for r in rows]

def verify_product(pid):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE supp_product SET verified=1 WHERE id=?", (pid,))
    conn.commit(); conn.close()


# ===== 评分 =====
def add_rating(data):
    conn = get_conn(); c = conn.cursor()
    scores = [data.get(f"dim{i}_score",0) for i in range(1,6)]
    valid = [s for s in scores if s and s>0]
    overall = sum(valid)/len(valid) if valid else 0
    c.execute("""INSERT INTO supp_rating
        (product_id,user_name,flavor,dim1_score,dim2_score,dim3_score,
         dim4_score,dim5_score,overall,review)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (data["product_id"],data.get("user_name","匿名用户"),data.get("flavor",""),
         scores[0],scores[1],scores[2],scores[3],scores[4],overall,
         data.get("review","")))
    conn.commit(); conn.close()

def get_product_ratings(pid, limit=50):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM supp_rating WHERE product_id=?
                 ORDER BY likes DESC, created_at DESC LIMIT ?""", (pid,limit))
    rows = c.fetchall(); cols = [d[0] for d in c.description]; conn.close()
    return [dict(zip(cols, r)) for r in rows]

def get_product_score_summary(pid):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT AVG(dim1_score),AVG(dim2_score),AVG(dim3_score),
                        AVG(dim4_score),AVG(dim5_score),AVG(overall),COUNT(*)
                 FROM supp_rating WHERE product_id=?""", (pid,))
    row = c.fetchone(); conn.close()
    if not row or row[6]==0: return None
    return {"dim1":round(row[0] or 0,1),"dim2":round(row[1] or 0,1),
            "dim3":round(row[2] or 0,1),"dim4":round(row[3] or 0,1),
            "dim5":round(row[4] or 0,1),"overall":round(row[5] or 0,1),"count":row[6]}

def like_rating(rid):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE supp_rating SET likes=likes+1 WHERE id=?", (rid,))
    conn.commit(); conn.close()


# ===== 训练计划（新结构）=====
def save_plan(plan_name, description, plan_type, days_data, source="AI", user_id=1):
    """
    plan_type: 'single' 或 'weekly'
    days_data: dict
      single: {"single": {"muscle_group": "胸+三头", "is_rest": False, "exercises": [...]}}
      weekly: {0: {...}, 1: {...}, ..., 6: {...}}  键为周一到周日索引
    """
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO workout_plan
                 (user_id,plan_name,description,plan_type,days_data,source)
                 VALUES (?,?,?,?,?,?)""",
              (user_id, plan_name, description, plan_type,
               json.dumps(days_data, ensure_ascii=False), source))
    pid = c.lastrowid; conn.commit(); conn.close()
    return pid

def list_plans(user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM workout_plan WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall(); cols = [d[0] for d in c.description]; conn.close()
    plans = []
    for r in rows:
        d = dict(zip(cols, r))
        try:
            d["days_data"] = json.loads(d["days_data"])
        except:
            d["days_data"] = {}
        plans.append(d)
    return plans

def get_plan(plan_id):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM workout_plan WHERE id=?", (plan_id,))
    row = c.fetchone()
    if not row: conn.close(); return None
    cols = [d[0] for d in c.description]; conn.close()
    d = dict(zip(cols, row))
    try:
        d["days_data"] = json.loads(d["days_data"])
    except:
        d["days_data"] = {}
    return d

def update_plan(plan_id, plan_name, description, plan_type, days_data):
    conn = get_conn(); c = conn.cursor()
    c.execute("""UPDATE workout_plan SET plan_name=?,description=?,plan_type=?,days_data=?
                 WHERE id=?""",
              (plan_name, description, plan_type,
               json.dumps(days_data, ensure_ascii=False), plan_id))
    conn.commit(); conn.close()

def delete_plan(plan_id):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM workout_plan WHERE id=?", (plan_id,))
    c.execute("DELETE FROM schedule WHERE plan_id=?", (plan_id,))
    conn.commit(); conn.close()


# ===== 日历调度 =====
def add_schedule(plan_id, schedule_date, schedule_time, weekday_index=None, notes="", user_id=1):
    """
    weekday_index: 仅 weekly 计划用，指定使用计划中的哪一天
                   None = 自动根据 schedule_date 推断
    """
    if weekday_index is None:
        # 根据日期自动推断
        d = datetime.strptime(schedule_date, "%Y-%m-%d").date() if isinstance(schedule_date, str) else schedule_date
        weekday_index = d.weekday()  # 0=周一

    conn = get_conn(); c = conn.cursor()
    # 先删除当天同时段的旧安排（实现"覆盖"）
    c.execute("""DELETE FROM schedule WHERE user_id=? AND schedule_date=? AND schedule_time=?""",
              (user_id, schedule_date, schedule_time))
    # 如果是今天的安排发生覆盖 → 同时清掉所有 in_progress session
    today_iso = date.today().isoformat()
    if str(schedule_date) == today_iso:
        c.execute("""DELETE FROM workout_session
                     WHERE user_id=? AND session_date=? AND status='in_progress'""",
                  (user_id, today_iso))
    c.execute("""INSERT INTO schedule (user_id,plan_id,weekday_index,schedule_date,schedule_time,notes)
                 VALUES (?,?,?,?,?,?)""",
              (user_id, plan_id, weekday_index, schedule_date, schedule_time, notes))
    sid = c.lastrowid; conn.commit(); conn.close()
    return sid

def get_schedules_by_date(target_date, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT s.*, p.plan_name, p.plan_type, p.days_data
                 FROM schedule s LEFT JOIN workout_plan p ON s.plan_id=p.id
                 WHERE s.user_id=? AND s.schedule_date=?
                 ORDER BY s.schedule_time""",
              (user_id, target_date))
    rows = c.fetchall(); cols = [d[0] for d in c.description]; conn.close()
    result = []
    for r in rows:
        d = dict(zip(cols, r))
        if d.get("days_data"):
            try: d["days_data"] = json.loads(d["days_data"])
            except: d["days_data"] = {}
        # 解析当天对应的训练部位
        d["day_info"] = _resolve_day_info(d)
        result.append(d)
    return result

def get_schedules_in_range(start_date, end_date, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT s.*, p.plan_name, p.plan_type, p.days_data
                 FROM schedule s LEFT JOIN workout_plan p ON s.plan_id=p.id
                 WHERE s.user_id=? AND s.schedule_date BETWEEN ? AND ?
                 ORDER BY s.schedule_date, s.schedule_time""",
              (user_id, start_date, end_date))
    rows = c.fetchall(); cols = [d[0] for d in c.description]; conn.close()
    result = []
    for r in rows:
        d = dict(zip(cols, r))
        if d.get("days_data"):
            try: d["days_data"] = json.loads(d["days_data"])
            except: d["days_data"] = {}
        d["day_info"] = _resolve_day_info(d)
        result.append(d)
    return result


def _resolve_day_info(schedule_dict):
    """从 schedule + plan.days_data 解析出这一天的训练信息"""
    days_data = schedule_dict.get("days_data") or {}
    plan_type = schedule_dict.get("plan_type", "single")

    # 检查是否标记为经期休息（仅当当前用户性别为女时才显示）
    notes = (schedule_dict.get("notes") or "").lower()
    if notes == "period_rest":
        # 检查当前用户性别 - 如果改成男了，period_rest 标记忽略
        try:
            _conn_g = get_conn(); _c_g = _conn_g.cursor()
            _c_g.execute("SELECT gender FROM user_profile ORDER BY id DESC LIMIT 1")
            _row_g = _c_g.fetchone()
            _conn_g.close()
            _current_gender = _row_g[0] if _row_g else None
        except Exception:
            _current_gender = None

        if _current_gender == "女":
            return {
                "muscle_group": "经期休息",
                "is_rest": True,
                "is_period": True,
                "exercises": [],
            }
        # 非女性：忽略 period_rest 标记，按正常训练日处理

    if plan_type == "single":
        day = days_data.get("single", {})
    else:
        widx = schedule_dict.get("weekday_index", 0)
        day = days_data.get(str(widx), {}) or days_data.get(widx, {})

    return {
        "muscle_group": day.get("muscle_group", "未指定"),
        "is_rest": day.get("is_rest", False),
        "is_period": False,
        "exercises": day.get("exercises", []),
    }


def update_schedule_status(schedule_id, status):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE schedule SET status=? WHERE id=?", (status, schedule_id))
    conn.commit(); conn.close()

def update_schedule_time(schedule_id, new_time):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE schedule SET schedule_time=?,notify_status='none' WHERE id=?",
              (new_time, schedule_id))
    conn.commit(); conn.close()

def mark_schedule_notified(schedule_id):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE schedule SET notify_status='notified' WHERE id=?", (schedule_id,))
    conn.commit(); conn.close()

def delete_schedule(schedule_id):
    conn = get_conn(); c = conn.cursor()
    # 先查这个日程是当天的就把对应的 in_progress session 也清掉
    c.execute("SELECT user_id, plan_id, schedule_date FROM schedule WHERE id=?", (schedule_id,))
    row = c.fetchone()
    if row:
        user_id, plan_id, sch_date = row
        today_iso = date.today().isoformat()
        if sch_date == today_iso:
            # 清除当天所有 in_progress session（避免开始训练时调出旧计划）
            c.execute("""DELETE FROM workout_session
                         WHERE user_id=? AND session_date=? AND status='in_progress'""",
                      (user_id, today_iso))
    c.execute("DELETE FROM schedule WHERE id=?", (schedule_id,))
    conn.commit(); conn.close()

def get_due_schedules(user_id=1):
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M")
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT s.*, p.plan_name, p.plan_type, p.days_data
                 FROM schedule s LEFT JOIN workout_plan p ON s.plan_id=p.id
                 WHERE s.user_id=? AND s.schedule_date=? AND s.schedule_time<=?
                 AND s.status='pending' AND s.notify_status='none'""",
              (user_id, today, now))
    rows = c.fetchall(); cols = [d[0] for d in c.description]; conn.close()
    result = []
    for r in rows:
        d = dict(zip(cols, r))
        if d.get("days_data"):
            try: d["days_data"] = json.loads(d["days_data"])
            except: d["days_data"] = {}
        d["day_info"] = _resolve_day_info(d)
        result.append(d)
    return result


# ===== 训练会话 =====
def start_session(plan_id, plan_name, target_muscle, exercises, user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO workout_session
        (user_id,plan_id,plan_name,session_date,target_muscle,exercises_data,status)
        VALUES (?,?,?,?,?,?,?)""",
        (user_id, plan_id, plan_name, date.today().isoformat(),
         target_muscle, json.dumps(exercises, ensure_ascii=False), "in_progress"))
    sid = c.lastrowid; conn.commit(); conn.close()
    return sid

def update_session(session_id, exercises, notes=""):
    conn = get_conn(); c = conn.cursor()
    total_vol = 0
    for ex in exercises:
        for s in ex.get("set_logs", []):
            if s.get("done"):
                w = s.get("actual_weight", 0) or 0
                r = s.get("actual_reps", 0) or 0
                total_vol += w * r
    c.execute("""UPDATE workout_session SET exercises_data=?,total_volume=?,notes=?
                 WHERE id=?""",
              (json.dumps(exercises, ensure_ascii=False), total_vol, notes, session_id))
    conn.commit(); conn.close()

def finish_session(session_id, duration_minutes=0):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE workout_session SET status='finished',duration_minutes=? WHERE id=?",
              (duration_minutes, session_id))
    conn.commit(); conn.close()

def get_session(session_id):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM workout_session WHERE id=?", (session_id,))
    row = c.fetchone()
    if not row: conn.close(); return None
    cols = [d[0] for d in c.description]; conn.close()
    d = dict(zip(cols, row))
    try: d["exercises_data"] = json.loads(d["exercises_data"])
    except: d["exercises_data"] = []
    return d

def get_today_session(user_id=1):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM workout_session
                 WHERE user_id=? AND session_date=? AND status='in_progress'
                 ORDER BY id DESC LIMIT 1""",
              (user_id, date.today().isoformat()))
    row = c.fetchone()
    if not row: conn.close(); return None
    cols = [d[0] for d in c.description]; conn.close()
    d = dict(zip(cols, row))
    try: d["exercises_data"] = json.loads(d["exercises_data"])
    except: d["exercises_data"] = []
    return d

def list_sessions(user_id=1, limit=30):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM workout_session
                 WHERE user_id=? AND status='finished'
                 ORDER BY session_date DESC, id DESC LIMIT ?""", (user_id, limit))
    rows = c.fetchall(); cols = [d[0] for d in c.description]; conn.close()
    sessions = []
    for r in rows:
        d = dict(zip(cols, r))
        try: d["exercises_data"] = json.loads(d["exercises_data"])
        except: d["exercises_data"] = []
        sessions.append(d)
    return sessions

def delete_session(session_id):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM workout_session WHERE id=?", (session_id,))
    conn.commit(); conn.close()


# ===== 工具：检查相邻日期是否同部位 =====
def check_adjacent_muscle(schedule_date, muscle_group, user_id=1):
    """
    检查前一天和后一天是否安排了相同部位
    返回: list[dict] 冲突的安排
    """
    if not muscle_group or muscle_group in ("休息", "未指定", ""):
        return []
    d = datetime.strptime(schedule_date, "%Y-%m-%d").date() if isinstance(schedule_date, str) else schedule_date
    prev_day = (d - timedelta(days=1)).isoformat()
    next_day = (d + timedelta(days=1)).isoformat()
    conflicts = []
    for chk_date in [prev_day, next_day]:
        same_day_sch = get_schedules_by_date(chk_date, user_id)
        for s in same_day_sch:
            di = s.get("day_info", {})
            if di.get("is_rest"): continue
            other_muscle = di.get("muscle_group", "")
            if _muscle_overlap(muscle_group, other_muscle):
                conflicts.append({
                    "date": chk_date,
                    "muscle": other_muscle,
                    "plan_name": s.get("plan_name", "")
                })
    return conflicts


def _muscle_overlap(m1, m2):
    """判断两个部位是否有重叠"""
    if not m1 or not m2: return False
    # 标准化分词
    parts1 = set()
    parts2 = set()
    for kw in ["胸", "背", "腿", "肩", "臂", "二头", "三头", "腹", "核心", "臀", "全身"]:
        if kw in m1: parts1.add(kw)
        if kw in m2: parts2.add(kw)
    return bool(parts1 & parts2)


init_db()
