"""
虎扑风格的评分/详情页 UI 组件
所有 HTML 拼接都用 .format() 或预拼接好的字符串，避免 f-string 嵌套引号 bug
"""

HUPU_STYLE = """
<style>
.hp-list-card{background:#1a2235;border:1px solid #2a3a55;border-radius:14px;
    padding:18px 22px;margin:10px 0;transition:all 0.2s;cursor:pointer;
    display:flex;align-items:center;gap:18px;}
.hp-list-card:hover{border-color:#00d9f5;transform:translateY(-2px);
    box-shadow:0 4px 16px rgba(0,217,245,0.1);}
.hp-list-avatar{width:64px;height:64px;background:linear-gradient(135deg,#1e2a44,#2a3a55);
    border-radius:12px;display:flex;align-items:center;justify-content:center;
    font-size:36px;flex-shrink:0;}
.hp-list-mid{flex:1;min-width:0;}
.hp-list-brand{color:#00d9f5;font-size:15px;font-weight:700;}
.hp-list-product{color:#e8eaf0;font-size:14px;margin-top:2px;}
.hp-list-comment{color:#8ca0b8;font-size:12px;margin-top:6px;
    background:rgba(140,160,184,0.08);padding:4px 10px;border-radius:6px;
    display:inline-block;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.hp-list-right{flex-shrink:0;text-align:right;}
.hp-list-score{font-family:'Rajdhani',sans-serif;font-size:28px;font-weight:700;
    background:linear-gradient(90deg,#00f5a0,#00d9f5);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hp-list-stars{color:#00d9f5;font-size:12px;letter-spacing:1px;}
.hp-list-noscore{font-family:'Rajdhani',sans-serif;font-size:18px;color:#4a6080;}
.hp-list-rated{color:#8ca0b8;font-size:11px;margin-top:2px;}
.hp-tier-h{display:inline-block;padding:1px 8px;border-radius:8px;font-size:10px;
    margin-left:6px;background:rgba(255,170,60,0.15);color:#ffaa3c;
    border:1px solid rgba(255,170,60,0.3);}
.hp-tier-m{display:inline-block;padding:1px 8px;border-radius:8px;font-size:10px;
    margin-left:6px;background:rgba(0,217,245,0.12);color:#00d9f5;
    border:1px solid rgba(0,217,245,0.25);}
.hp-tier-l{display:inline-block;padding:1px 8px;border-radius:8px;font-size:10px;
    margin-left:6px;background:rgba(0,245,160,0.12);color:#00f5a0;
    border:1px solid rgba(0,245,160,0.25);}
.hp-owned{display:inline-block;padding:1px 8px;border-radius:8px;font-size:10px;
    margin-left:6px;background:rgba(0,245,160,0.15);color:#00f5a0;
    border:1px solid rgba(0,245,160,0.3);}

/* 详情页 */
.hp-detail-top{background:linear-gradient(135deg,#1a2235,#162032);
    border:1px solid #2a3a55;border-radius:16px;padding:24px;margin-bottom:16px;}
.hp-detail-header{display:flex;gap:18px;align-items:center;}
.hp-detail-avatar{width:88px;height:88px;background:linear-gradient(135deg,#1e2a44,#2a3a55);
    border-radius:14px;display:flex;align-items:center;justify-content:center;
    font-size:48px;flex-shrink:0;}
.hp-detail-brand{color:#00d9f5;font-size:20px;font-weight:700;}
.hp-detail-product{color:#e8eaf0;font-size:16px;margin-top:4px;}
.hp-detail-meta{color:#8ca0b8;font-size:12px;margin-top:6px;}
.hp-score-panel{display:flex;gap:24px;margin-top:20px;
    padding:18px;background:#0e1525;border-radius:12px;}
.hp-score-big{flex-shrink:0;text-align:center;min-width:140px;}
.hp-score-num{font-family:'Rajdhani',sans-serif;font-size:56px;font-weight:700;
    background:linear-gradient(90deg,#00f5a0,#00d9f5);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1;}
.hp-score-label{color:#8ca0b8;font-size:12px;margin-top:6px;}
.hp-bars{flex:1;display:flex;flex-direction:column;gap:8px;}
.hp-bar-row{display:flex;align-items:center;gap:10px;font-size:12px;}
.hp-bar-name{color:#c8d8e8;width:64px;flex-shrink:0;}
.hp-bar-track{flex:1;height:8px;background:rgba(140,160,184,0.15);border-radius:4px;
    overflow:hidden;}
.hp-bar-fill{height:100%;background:linear-gradient(90deg,#00f5a0,#00d9f5);
    border-radius:4px;}
.hp-bar-val{color:#00d9f5;width:32px;text-align:right;font-weight:600;
    font-family:'Rajdhani',sans-serif;}

/* 评论/日记卡片 */
.hp-journal{background:#1a2235;border:1px solid #2a3a55;border-radius:12px;
    padding:16px 20px;margin:10px 0;}
.hp-journal-head{display:flex;justify-content:space-between;align-items:center;
    margin-bottom:8px;}
.hp-journal-stars{color:#ffaa3c;font-size:14px;letter-spacing:2px;}
.hp-journal-time{color:#8ca0b8;font-size:11px;}
.hp-journal-days{color:#00d9f5;font-size:11px;
    background:rgba(0,217,245,0.1);padding:2px 8px;border-radius:10px;margin-left:6px;}
.hp-journal-body{color:#e8eaf0;font-size:14px;line-height:1.7;
    background:rgba(140,160,184,0.04);padding:10px 14px;border-radius:8px;
    border-left:3px solid #00d9f5;}
.hp-empty{text-align:center;color:#4a6080;padding:32px 16px;font-size:13px;}

/* 分类筛选小标签 */
.hp-pill{display:inline-block;padding:5px 14px;border-radius:14px;
    background:#1a2235;border:1px solid #2a3a55;color:#c8d8e8;font-size:12px;
    margin:4px 4px 4px 0;}
.hp-pill-active{background:linear-gradient(90deg,#00f5a0,#00d9f5);color:#0e1525;
    border-color:transparent;font-weight:600;}
</style>
"""


def stars_html(score, max_score=5):
    """生成星级 HTML 字符串"""
    if score is None or score == 0:
        return '<span style="color:#4a6080;">尚未评分</span>'
    full = int(score)
    half = 1 if (score - full) >= 0.5 else 0
    empty = max_score - full - half
    return '★' * full + ('⯨' if half else '') + '☆' * empty


def render_list_card(
    avatar, brand, product_name, category, tier,
    rating_score=None, journal_count=0, latest_comment=None,
    is_owned=False, price_range=None
):
    """
    生成单个产品列表卡（虎扑风列表项）
    rating_score: 综合评分（0-5 或 None）
    """
    tier_class_map = {"高端": "hp-tier-h", "中高端": "hp-tier-h",
                       "中端": "hp-tier-m", "性价比": "hp-tier-l"}
    tier_class = tier_class_map.get(tier, "hp-tier-m")
    tier_badge = '<span class="' + tier_class + '">' + str(tier) + '</span>'
    owned_badge = '<span class="hp-owned">✓ 已拥有</span>' if is_owned else ''

    if rating_score is None or rating_score == 0:
        right_html = (
            '<div class="hp-list-noscore">未评分</div>'
            '<div class="hp-list-rated">点击进入评分</div>'
        )
    else:
        score_str = '{:.1f}'.format(rating_score)
        full_stars = int(round(rating_score))
        stars_str = '★' * full_stars + '☆' * (5 - full_stars)
        right_html = (
            '<div class="hp-list-score">' + score_str + '</div>'
            '<div class="hp-list-stars">' + stars_str + '</div>'
            '<div class="hp-list-rated">' + str(journal_count) + ' 条评测</div>'
        )

    comment_html = ''
    if latest_comment:
        cm = latest_comment.strip()
        if len(cm) > 40:
            cm = cm[:38] + '...'
        comment_html = '<div class="hp-list-comment">💬 ' + cm + '</div>'

    price_html = ''
    if price_range:
        price_html = ' · ' + price_range

    html = (
        '<div class="hp-list-card">'
        '<div class="hp-list-avatar">' + str(avatar) + '</div>'
        '<div class="hp-list-mid">'
        '<div class="hp-list-brand">' + str(brand) + tier_badge + owned_badge + '</div>'
        '<div class="hp-list-product">' + str(product_name) + '</div>'
        '<div class="hp-list-meta" style="color:#8ca0b8;font-size:11px;margin-top:4px;">'
        + str(category) + price_html + '</div>'
        + comment_html +
        '</div>'
        '<div class="hp-list-right">' + right_html + '</div>'
        '</div>'
    )
    return html


def render_detail_top(
    avatar, brand, product_name, category, tier, country,
    price_range, description,
    ratings_dict, dimension_labels
):
    """
    渲染详情页顶部（评分柱状图 + 综合分）
    ratings_dict: {key: score}
    dimension_labels: [{key, label, icon}]
    """
    # 综合分
    if ratings_dict and any(ratings_dict.values()):
        scores = [ratings_dict.get(d["key"], 0) for d in dimension_labels if ratings_dict.get(d["key"], 0) > 0]
        avg = sum(scores) / len(scores) if scores else 0
    else:
        avg = 0

    if avg > 0:
        big_score_html = (
            '<div class="hp-score-num">' + '{:.1f}'.format(avg) + '</div>'
            '<div class="hp-score-label">综合评分 · ' + str(len(scores)) + ' 项</div>'
        )
    else:
        big_score_html = (
            '<div class="hp-score-num" style="background:none;-webkit-text-fill-color:#4a6080;">--</div>'
            '<div class="hp-score-label">尚未评分</div>'
        )

    # 各维度柱状图
    bars_html = ''
    for d in dimension_labels:
        score = ratings_dict.get(d["key"], 0) if ratings_dict else 0
        pct = (score / 5.0 * 100) if score else 0
        bars_html += (
            '<div class="hp-bar-row">'
            '<span class="hp-bar-name">' + d.get("icon", "") + ' ' + d["label"] + '</span>'
            '<div class="hp-bar-track"><div class="hp-bar-fill" style="width:' + str(pct) + '%;"></div></div>'
            '<span class="hp-bar-val">' + ('{:.0f}'.format(score) if score else '-') + '</span>'
            '</div>'
        )

    tier_class_map = {"高端": "hp-tier-h", "中高端": "hp-tier-h",
                       "中端": "hp-tier-m", "性价比": "hp-tier-l"}
    tier_class = tier_class_map.get(tier, "hp-tier-m")
    tier_badge = '<span class="' + tier_class + '">' + str(tier) + '</span>'

    html = (
        '<div class="hp-detail-top">'
        '<div class="hp-detail-header">'
        '<div class="hp-detail-avatar">' + str(avatar) + '</div>'
        '<div style="flex:1;">'
        '<div class="hp-detail-brand">' + str(brand) + ' ' + tier_badge + '</div>'
        '<div class="hp-detail-product">' + str(product_name) + '</div>'
        '<div class="hp-detail-meta">' + str(country) + ' · ' + str(category) + ' · ' + str(price_range) + '</div>'
        '</div>'
        '</div>'
        '<div class="hp-score-panel">'
        '<div class="hp-score-big">' + big_score_html + '</div>'
        '<div class="hp-bars">' + bars_html + '</div>'
        '</div>'
        '</div>'
    )
    return html


def render_journal_card(journal):
    """单条评测日记卡片"""
    stars = int(journal.get("stars", 5))
    stars_str = '★' * stars + '☆' * (5 - stars)
    days = journal.get("usage_days", 0)
    days_html = ''
    if days and days > 0:
        days_html = '<span class="hp-journal-days">📅 使用 ' + str(days) + ' 天</span>'

    created = journal.get("created_at", "")
    if created:
        created = created.split(".")[0]  # 去掉毫秒

    content = journal.get("content", "")

    return (
        '<div class="hp-journal">'
        '<div class="hp-journal-head">'
        '<div><span class="hp-journal-stars">' + stars_str + '</span>' + days_html + '</div>'
        '<div class="hp-journal-time">' + str(created) + '</div>'
        '</div>'
        '<div class="hp-journal-body">' + str(content) + '</div>'
        '</div>'
    )
