"""
肌肉骨骼运动追踪与可视化
- draw_muscle_skeleton: 在原始画面上叠加（用于摄像头视角）
- render_anatomy_view: 单独绘制一张解剖示意图（用于右侧轨迹画面）
- analyze_form: 发力分析
"""
import cv2
import numpy as np
from collections import deque
import mediapipe as mp

mp_pose = mp.solutions.pose
PL = mp_pose.PoseLandmark

# ============ 肌肉-关键点映射 ============
MUSCLE_GROUPS = {
    "胸大肌": [(PL.LEFT_SHOULDER, PL.RIGHT_SHOULDER)],
    "三角肌": [(PL.LEFT_SHOULDER, PL.LEFT_ELBOW), (PL.RIGHT_SHOULDER, PL.RIGHT_ELBOW)],
    "肱二头肌": [(PL.LEFT_SHOULDER, PL.LEFT_ELBOW), (PL.RIGHT_SHOULDER, PL.RIGHT_ELBOW)],
    "肱三头肌": [(PL.LEFT_ELBOW, PL.LEFT_WRIST), (PL.RIGHT_ELBOW, PL.RIGHT_WRIST)],
    "前臂": [(PL.LEFT_ELBOW, PL.LEFT_WRIST), (PL.RIGHT_ELBOW, PL.RIGHT_WRIST)],
    "背阔肌": [(PL.LEFT_SHOULDER, PL.LEFT_HIP), (PL.RIGHT_SHOULDER, PL.RIGHT_HIP)],
    "核心": [(PL.LEFT_SHOULDER, PL.RIGHT_HIP), (PL.RIGHT_SHOULDER, PL.LEFT_HIP)],
    "股四头肌": [(PL.LEFT_HIP, PL.LEFT_KNEE), (PL.RIGHT_HIP, PL.RIGHT_KNEE)],
    "腘绳肌": [(PL.LEFT_HIP, PL.LEFT_KNEE), (PL.RIGHT_HIP, PL.RIGHT_KNEE)],
    "臀大肌": [(PL.LEFT_HIP, PL.LEFT_KNEE), (PL.RIGHT_HIP, PL.RIGHT_KNEE)],
    "小腿三头肌": [(PL.LEFT_KNEE, PL.LEFT_ANKLE), (PL.RIGHT_KNEE, PL.RIGHT_ANKLE)],
}

EXERCISE_MUSCLES = {
    "深蹲": {
        "primary": ["股四头肌", "臀大肌"],
        "secondary": ["腘绳肌", "核心", "小腿三头肌"],
        "key_points": "膝盖朝脚尖方向，腰背挺直，重心在脚跟",
    },
    "俯卧撑": {
        "primary": ["胸大肌", "肱三头肌"],
        "secondary": ["三角肌", "核心"],
        "key_points": "肘部约45度展开，身体保持一条直线",
    },
    "哑铃弯举": {
        "primary": ["肱二头肌"],
        "secondary": ["前臂", "三角肌"],
        "key_points": "上臂固定不动，只有前臂转动",
    },
    "硬拉": {
        "primary": ["臀大肌", "腘绳肌", "背阔肌"],
        "secondary": ["核心", "前臂"],
        "key_points": "保持背部挺直，髋部主导发力",
    },
    "卧推": {
        "primary": ["胸大肌", "肱三头肌"],
        "secondary": ["三角肌"],
        "key_points": "肩胛骨后缩下沉，脚踩稳",
    },
    "引体向上": {
        "primary": ["背阔肌", "肱二头肌"],
        "secondary": ["前臂", "核心"],
        "key_points": "肩胛骨先下沉再上拉，胸部贴近横杆",
    },
}

# ============ 几何工具 ============
def calc_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    r = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    ang = np.abs(r*180/np.pi)
    return 360-ang if ang > 180 else ang

def get_pt(lms, enum, w, h):
    lm = lms[enum.value]
    return (int(lm.x * w), int(lm.y * h))

def get_norm(lms, enum):
    lm = lms[enum.value]
    return [lm.x, lm.y]


# ============ 解剖示意图渲染（右侧画面核心）============
def render_anatomy_view(landmarks, exercise: str, width=640, height=540, trail_history=None):
    """
    生成一张纯净的肌肉骨骼解剖图（深色背景），不含摄像头画面
    - 主发力肌群红色高亮
    - 辅助肌群橙黄色
    - 未参与肌群灰色
    - 可选叠加轨迹

    Returns: RGB numpy 数组
    """
    # 深色背景
    canvas = np.full((height, width, 3), 18, dtype=np.uint8)
    canvas[:, :] = (28, 35, 50)  # BGR: 深蓝灰底

    # 装饰网格背景
    for x in range(0, width, 40):
        cv2.line(canvas, (x, 0), (x, height), (38, 45, 65), 1)
    for y in range(0, height, 40):
        cv2.line(canvas, (0, y), (width, y), (38, 45, 65), 1)

    if landmarks is None:
        cv2.putText(canvas, "Waiting for body detection...",
                    (width//2-180, height//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 120, 150), 1, cv2.LINE_AA)
        return canvas

    config = EXERCISE_MUSCLES.get(exercise, EXERCISE_MUSCLES["深蹲"])
    primary = set(config["primary"])
    secondary = set(config["secondary"])

    # ===== 把归一化坐标映射到canvas，居中放大 =====
    # 先计算人体的bounding box，再适应canvas
    key_lms = [PL.LEFT_SHOULDER, PL.RIGHT_SHOULDER, PL.LEFT_HIP, PL.RIGHT_HIP,
               PL.LEFT_KNEE, PL.RIGHT_KNEE, PL.LEFT_ANKLE, PL.RIGHT_ANKLE,
               PL.LEFT_ELBOW, PL.RIGHT_ELBOW, PL.LEFT_WRIST, PL.RIGHT_WRIST,
               PL.NOSE]
    xs = [landmarks[l.value].x for l in key_lms]
    ys = [landmarks[l.value].y for l in key_lms]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # 加 padding
    pad = 0.1
    body_w = max(max_x - min_x, 0.01) * (1 + pad*2)
    body_h = max(max_y - min_y, 0.01) * (1 + pad*2)
    cx_norm = (min_x + max_x) / 2
    cy_norm = (min_y + max_y) / 2

    # 计算缩放比例（保持纵横比，留边距）
    target_w = width * 0.7
    target_h = height * 0.85
    scale = min(target_w / body_w, target_h / body_h)

    def project(enum):
        """归一化坐标 → canvas像素坐标"""
        lm = landmarks[enum.value]
        x = (lm.x - cx_norm) * scale + width / 2
        y = (lm.y - cy_norm) * scale + height / 2
        return (int(x), int(y))

    # ===== 1. 画轨迹（最底层）=====
    if trail_history is not None:
        track_map = {
            "深蹲": [PL.LEFT_KNEE, PL.RIGHT_KNEE],
            "俯卧撑": [PL.LEFT_WRIST, PL.RIGHT_WRIST],
            "哑铃弯举": [PL.LEFT_WRIST, PL.RIGHT_WRIST],
            "硬拉": [PL.LEFT_WRIST, PL.RIGHT_WRIST],
            "卧推": [PL.LEFT_WRIST, PL.RIGHT_WRIST],
            "引体向上": [PL.LEFT_WRIST, PL.RIGHT_WRIST],
        }
        track_pts = track_map.get(exercise, [PL.LEFT_WRIST, PL.RIGHT_WRIST])
        for joint in track_pts:
            trail = trail_history.get(joint.name, [])
            if len(trail) < 2:
                continue
            pts_proj = []
            for nx, ny in trail:
                px = int((nx - cx_norm) * scale + width / 2)
                py = int((ny - cy_norm) * scale + height / 2)
                pts_proj.append((px, py))
            for i in range(1, len(pts_proj)):
                alpha = i / len(pts_proj)
                color = (int(0 * alpha), int(160 * alpha), int(245 * alpha))
                thickness = max(1, int(4 * alpha))
                cv2.line(canvas, pts_proj[i-1], pts_proj[i], color, thickness, cv2.LINE_AA)

    # ===== 2. 灰色骨骼（基底）=====
    BONE_CONNECTIONS = [
        (PL.LEFT_SHOULDER, PL.RIGHT_SHOULDER), (PL.LEFT_HIP, PL.RIGHT_HIP),
        (PL.LEFT_SHOULDER, PL.LEFT_HIP), (PL.RIGHT_SHOULDER, PL.RIGHT_HIP),
        (PL.LEFT_SHOULDER, PL.LEFT_ELBOW), (PL.LEFT_ELBOW, PL.LEFT_WRIST),
        (PL.RIGHT_SHOULDER, PL.RIGHT_ELBOW), (PL.RIGHT_ELBOW, PL.RIGHT_WRIST),
        (PL.LEFT_HIP, PL.LEFT_KNEE), (PL.LEFT_KNEE, PL.LEFT_ANKLE),
        (PL.RIGHT_HIP, PL.RIGHT_KNEE), (PL.RIGHT_KNEE, PL.RIGHT_ANKLE),
        (PL.NOSE, PL.LEFT_SHOULDER), (PL.NOSE, PL.RIGHT_SHOULDER),
    ]
    for a, b in BONE_CONNECTIONS:
        cv2.line(canvas, project(a), project(b), (110, 120, 140), 4, cv2.LINE_AA)

    # ===== 3. 肌肉色块（带半透明效果）=====
    overlay = canvas.copy()

    # 辅助肌群 - 橙黄色（先画，被主肌群覆盖时不影响）
    for muscle in secondary:
        if muscle in MUSCLE_GROUPS and muscle not in primary:
            for a, b in MUSCLE_GROUPS[muscle]:
                cv2.line(overlay, project(a), project(b), (50, 165, 245), 16, cv2.LINE_AA)

    # 主发力肌群 - 红色高亮（粗线）
    for muscle in primary:
        if muscle in MUSCLE_GROUPS:
            for a, b in MUSCLE_GROUPS[muscle]:
                cv2.line(overlay, project(a), project(b), (60, 60, 255), 22, cv2.LINE_AA)

    cv2.addWeighted(overlay, 0.65, canvas, 0.35, 0, canvas)

    # ===== 4. 关节点 =====
    KEY_JOINTS = [PL.LEFT_SHOULDER, PL.RIGHT_SHOULDER, PL.LEFT_ELBOW, PL.RIGHT_ELBOW,
                  PL.LEFT_WRIST, PL.RIGHT_WRIST, PL.LEFT_HIP, PL.RIGHT_HIP,
                  PL.LEFT_KNEE, PL.RIGHT_KNEE, PL.LEFT_ANKLE, PL.RIGHT_ANKLE]
    for j in KEY_JOINTS:
        p = project(j)
        cv2.circle(canvas, p, 8, (0, 245, 160), -1, cv2.LINE_AA)
        cv2.circle(canvas, p, 10, (255, 255, 255), 2, cv2.LINE_AA)

    # 头部
    nose_p = project(PL.NOSE)
    cv2.circle(canvas, nose_p, 22, (110, 120, 140), 3, cv2.LINE_AA)

    return canvas


# ============ 摄像头画面（叠加轻量骨架）============
def draw_skeleton_overlay(image, landmarks):
    """在摄像头画面上画轻量骨架，不含色块，避免遮挡身体"""
    if landmarks is None:
        return image
    h, w = image.shape[:2]

    BONE_CONNECTIONS = [
        (PL.LEFT_SHOULDER, PL.RIGHT_SHOULDER), (PL.LEFT_HIP, PL.RIGHT_HIP),
        (PL.LEFT_SHOULDER, PL.LEFT_HIP), (PL.RIGHT_SHOULDER, PL.RIGHT_HIP),
        (PL.LEFT_SHOULDER, PL.LEFT_ELBOW), (PL.LEFT_ELBOW, PL.LEFT_WRIST),
        (PL.RIGHT_SHOULDER, PL.RIGHT_ELBOW), (PL.RIGHT_ELBOW, PL.RIGHT_WRIST),
        (PL.LEFT_HIP, PL.LEFT_KNEE), (PL.LEFT_KNEE, PL.LEFT_ANKLE),
        (PL.RIGHT_HIP, PL.RIGHT_KNEE), (PL.RIGHT_KNEE, PL.RIGHT_ANKLE),
    ]
    for a, b in BONE_CONNECTIONS:
        pa, pb = get_pt(landmarks, a, w, h), get_pt(landmarks, b, w, h)
        cv2.line(image, pa, pb, (0, 245, 160), 2, cv2.LINE_AA)

    KEY_JOINTS = [PL.LEFT_SHOULDER, PL.RIGHT_SHOULDER, PL.LEFT_ELBOW, PL.RIGHT_ELBOW,
                  PL.LEFT_WRIST, PL.RIGHT_WRIST, PL.LEFT_HIP, PL.RIGHT_HIP,
                  PL.LEFT_KNEE, PL.RIGHT_KNEE, PL.LEFT_ANKLE, PL.RIGHT_ANKLE]
    for j in KEY_JOINTS:
        p = get_pt(landmarks, j, w, h)
        cv2.circle(image, p, 5, (0, 200, 255), -1, cv2.LINE_AA)

    return image


# ============ 动作分析 ============
def analyze_form(lms, exercise: str) -> dict:
    feedback_list = []
    status = "good"

    try:
        if exercise == "深蹲":
            l_knee = get_norm(lms, PL.LEFT_KNEE)
            r_knee = get_norm(lms, PL.RIGHT_KNEE)
            l_ankle = get_norm(lms, PL.LEFT_ANKLE)
            r_ankle = get_norm(lms, PL.RIGHT_ANKLE)
            knee_dist = abs(l_knee[0] - r_knee[0])
            ankle_dist = abs(l_ankle[0] - r_ankle[0])
            if ankle_dist > 0 and knee_dist < ankle_dist * 0.7:
                feedback_list.append("⚠ 膝盖内扣")
                status = "warning"

            l_sh = get_norm(lms, PL.LEFT_SHOULDER)
            l_hip = get_norm(lms, PL.LEFT_HIP)
            back_angle = abs(np.degrees(np.arctan2(l_sh[0]-l_hip[0], l_hip[1]-l_sh[1])))
            if back_angle > 45:
                feedback_list.append("⚠ 上身过度前倾")
                status = "warning"

            knee_ang = calc_angle(get_norm(lms, PL.LEFT_HIP), l_knee, l_ankle)
            if 60 < knee_ang < 100:
                feedback_list.append(f"✓ 下蹲深度合适（{int(knee_ang)}°）")
            elif knee_ang >= 100:
                feedback_list.append(f"💡 可再蹲低些（{int(knee_ang)}°）")

        elif exercise == "俯卧撑":
            l_sh = get_norm(lms, PL.LEFT_SHOULDER)
            l_hip = get_norm(lms, PL.LEFT_HIP)
            l_ankle = get_norm(lms, PL.LEFT_ANKLE)
            body_ang = calc_angle(l_sh, l_hip, l_ankle)
            if body_ang < 160:
                feedback_list.append("⚠ 身体不在直线")
                status = "warning"
            else:
                feedback_list.append("✓ 身体保持直线")

            elb_ang = calc_angle(l_sh, get_norm(lms, PL.LEFT_ELBOW), get_norm(lms, PL.LEFT_WRIST))
            feedback_list.append(f"肘部 {int(elb_ang)}°")

        elif exercise == "哑铃弯举":
            l_sh = get_norm(lms, PL.LEFT_SHOULDER)
            l_elb = get_norm(lms, PL.LEFT_ELBOW)
            elb_drift = abs(l_elb[0] - l_sh[0])
            if elb_drift > 0.08:
                feedback_list.append("⚠ 上臂在摆动")
                status = "warning"
            else:
                feedback_list.append("✓ 上臂稳定")
            elb_ang = calc_angle(l_sh, l_elb, get_norm(lms, PL.LEFT_WRIST))
            feedback_list.append(f"肘角 {int(elb_ang)}°")

        elif exercise == "硬拉":
            l_sh = get_norm(lms, PL.LEFT_SHOULDER)
            l_hip = get_norm(lms, PL.LEFT_HIP)
            l_knee = get_norm(lms, PL.LEFT_KNEE)
            back_ang = calc_angle(l_sh, l_hip, l_knee)
            if 50 < back_ang < 130:
                feedback_list.append("⚠ 注意背部挺直，避免弓背")
                status = "warning"
            else:
                feedback_list.append("✓ 髋部姿势良好")

        if not feedback_list:
            feedback_list.append("✓ 姿态正常")

    except Exception:
        feedback_list = ["分析中..."]

    return {
        "status": status,
        "feedback": " | ".join(feedback_list[:2]),
        "details": feedback_list,
    }


# ============ 轨迹追踪 ============
class TrajectoryTracker:
    def __init__(self, max_len=30):
        self.max_len = max_len
        self.trails = {
            "LEFT_WRIST": deque(maxlen=max_len),
            "RIGHT_WRIST": deque(maxlen=max_len),
            "LEFT_KNEE": deque(maxlen=max_len),
            "RIGHT_KNEE": deque(maxlen=max_len),
        }

    def update(self, landmarks):
        """存归一化坐标，便于复用到任意尺寸画布"""
        for name in self.trails:
            enum = getattr(PL, name)
            lm = landmarks[enum.value]
            self.trails[name].append((lm.x, lm.y))

    def get_history(self):
        return {k: list(v) for k, v in self.trails.items()}

    def clear(self):
        for k in self.trails:
            self.trails[k].clear()
