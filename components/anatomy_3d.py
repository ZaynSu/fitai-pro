"""
Three.js 3D 人体解剖组件
通过 streamlit.components.v1.html 嵌入浏览器中渲染
接收 MediaPipe 33 个关键点的归一化坐标，实时驱动 3D 模型
"""
import streamlit.components.v1 as components
import json


def render_3d_anatomy(landmarks_data: list, exercise: str, height: int = 540):
    """
    渲染 3D 人体解剖图
    landmarks_data: [{x, y, z, visibility}, ...] 共33个点（MediaPipe格式）
    exercise: 当前动作名称，决定哪些肌肉高亮
    """
    landmarks_json = json.dumps(landmarks_data) if landmarks_data else "null"

    # 肌群高亮配置（与 muscle_tracker.py 保持一致）
    muscle_config = {
        "深蹲":     {"primary": ["quads", "glutes"], "secondary": ["hamstrings", "core", "calves"]},
        "俯卧撑":   {"primary": ["chest", "triceps"], "secondary": ["deltoids", "core"]},
        "哑铃弯举": {"primary": ["biceps"],            "secondary": ["forearms", "deltoids"]},
        "硬拉":     {"primary": ["glutes", "hamstrings", "lats"], "secondary": ["core", "forearms"]},
        "卧推":     {"primary": ["chest", "triceps"], "secondary": ["deltoids"]},
        "引体向上": {"primary": ["lats", "biceps"],   "secondary": ["forearms", "core"]},
    }
    cfg = muscle_config.get(exercise, muscle_config["深蹲"])
    config_json = json.dumps(cfg)

    html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin:0; padding:0; background:#0e1525; overflow:hidden; }}
  #container {{ width:100%; height:{height}px; position:relative; }}
  #info {{
    position:absolute; top:10px; left:14px; color:#8ca0b8;
    font-family:'Helvetica',sans-serif; font-size:12px; letter-spacing:1px;
    background:rgba(15,20,40,0.6); padding:6px 12px; border-radius:6px;
    border:1px solid #2a3a55; pointer-events:none;
  }}
  #legend {{
    position:absolute; bottom:10px; left:14px; color:#c8d8e8;
    font-family:'Helvetica',sans-serif; font-size:11px;
    background:rgba(15,20,40,0.6); padding:8px 12px; border-radius:6px;
    border:1px solid #2a3a55; pointer-events:none;
  }}
  .dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; vertical-align:middle; margin-right:6px; }}
  canvas {{ display:block; }}
</style>
</head>
<body>
<div id="container">
  <div id="info">3D ANATOMY · 拖动旋转视角 · 滚轮缩放</div>
  <div id="legend">
    <span class="dot" style="background:#ff3838"></span>主发力肌群 &nbsp;
    <span class="dot" style="background:#ffa030"></span>辅助肌群 &nbsp;
    <span class="dot" style="background:#5a6478"></span>未参与肌群
  </div>
</div>

<script type="importmap">
{{
  "imports": {{
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }}
}}
</script>

<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

const LANDMARKS = {landmarks_json};
const MUSCLE_CFG = {config_json};

// ========== 颜色定义 ==========
const COLOR_PRIMARY   = 0xff3838;  // 主发力 - 红
const COLOR_SECONDARY = 0xffa030;  // 辅助 - 橙
const COLOR_REST      = 0x5a6478;  // 未参与 - 灰
const COLOR_BONE      = 0xd4dae8;  // 骨骼/皮肤底色

// ========== 场景初始化 ==========
const container = document.getElementById('container');
const W = container.clientWidth;
const H = container.clientHeight;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0e1525);
scene.fog = new THREE.Fog(0x0e1525, 5, 15);

const camera = new THREE.PerspectiveCamera(45, W/H, 0.1, 100);
camera.position.set(0, 0.8, 4.5);

const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// ========== 灯光 ==========
scene.add(new THREE.AmbientLight(0x4a5878, 0.6));
const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(3, 5, 4);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(1024, 1024);
scene.add(dirLight);

const rimLight = new THREE.DirectionalLight(0x6080ff, 0.4);
rimLight.position.set(-3, 2, -3);
scene.add(rimLight);

// ========== 地面 ==========
const ground = new THREE.Mesh(
  new THREE.CircleGeometry(3, 32),
  new THREE.MeshStandardMaterial({{color:0x1a2235, roughness:0.9}})
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -1.6;
ground.receiveShadow = true;
scene.add(ground);

// ========== 控制器 ==========
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0, 0);
controls.minDistance = 2.5;
controls.maxDistance = 8;
controls.maxPolarAngle = Math.PI * 0.9;

// ========== 人体材质（每块肌肉一个独立 material 才能单独染色）==========
function makeMat(colorHex) {{
  return new THREE.MeshStandardMaterial({{
    color: colorHex,
    roughness: 0.55,
    metalness: 0.15,
    flatShading: false,
  }});
}}

const materials = {{
  // 主要肌群
  chest:      makeMat(COLOR_REST),
  deltoids_L: makeMat(COLOR_REST),
  deltoids_R: makeMat(COLOR_REST),
  biceps_L:   makeMat(COLOR_REST),
  biceps_R:   makeMat(COLOR_REST),
  triceps_L:  makeMat(COLOR_REST),
  triceps_R:  makeMat(COLOR_REST),
  forearms_L: makeMat(COLOR_REST),
  forearms_R: makeMat(COLOR_REST),
  lats_L:     makeMat(COLOR_REST),
  lats_R:     makeMat(COLOR_REST),
  core:       makeMat(COLOR_REST),
  glutes:     makeMat(COLOR_REST),
  quads_L:    makeMat(COLOR_REST),
  quads_R:    makeMat(COLOR_REST),
  hamstrings_L: makeMat(COLOR_REST),
  hamstrings_R: makeMat(COLOR_REST),
  calves_L:   makeMat(COLOR_REST),
  calves_R:   makeMat(COLOR_REST),
  // 中性部位
  head:       makeMat(COLOR_BONE),
  neck:       makeMat(COLOR_BONE),
  pelvis:     makeMat(COLOR_BONE),
}};

// ========== 应用肌肉高亮配置 ==========
// 肌群名 → materials 中对应的实际 material 列表
const muscleGroupMap = {{
  chest:      ['chest'],
  deltoids:   ['deltoids_L', 'deltoids_R'],
  biceps:     ['biceps_L', 'biceps_R'],
  triceps:    ['triceps_L', 'triceps_R'],
  forearms:   ['forearms_L', 'forearms_R'],
  lats:       ['lats_L', 'lats_R'],
  core:       ['core'],
  glutes:     ['glutes'],
  quads:      ['quads_L', 'quads_R'],
  hamstrings: ['hamstrings_L', 'hamstrings_R'],
  calves:     ['calves_L', 'calves_R'],
}};

function applyMuscleHighlight() {{
  // 先重置所有
  Object.values(materials).forEach(m => {{
    if (m !== materials.head && m !== materials.neck && m !== materials.pelvis) {{
      m.color.setHex(COLOR_REST);
    }}
  }});
  // 应用辅助色
  MUSCLE_CFG.secondary.forEach(g => {{
    (muscleGroupMap[g] || []).forEach(mk => {{
      if (materials[mk]) materials[mk].color.setHex(COLOR_SECONDARY);
    }});
  }});
  // 应用主色（覆盖辅助）
  MUSCLE_CFG.primary.forEach(g => {{
    (muscleGroupMap[g] || []).forEach(mk => {{
      if (materials[mk]) materials[mk].color.setHex(COLOR_PRIMARY);
    }});
  }});
}}
applyMuscleHighlight();

// ========== 构建人体（程序生成，每块肌肉独立 Mesh）==========
// 人体主容器（用于整体平移/旋转）
const human = new THREE.Group();
scene.add(human);

// 工具函数：创建胶囊状肌肉块
function makeCapsule(radius, length, mat) {{
  const geo = new THREE.CapsuleGeometry(radius, length, 6, 16);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  return mesh;
}}
function makeSphere(radius, mat) {{
  const geo = new THREE.SphereGeometry(radius, 24, 18);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  return mesh;
}}
function makeBox(w, h, d, mat) {{
  const geo = new THREE.BoxGeometry(w, h, d);
  geo.translate(0, -h/2, 0); // 让原点在顶端，方便旋转
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  return mesh;
}}

// ===== 头 =====
const head = makeSphere(0.18, materials.head);
head.position.set(0, 0.95, 0);
human.add(head);

// ===== 颈 =====
const neck = makeCapsule(0.07, 0.1, materials.neck);
neck.position.set(0, 0.78, 0);
human.add(neck);

// ===== 躯干分块（胸/腹/背） =====
// 胸肌 - 椭球扁平
const chestGeo = new THREE.SphereGeometry(0.28, 24, 16);
const chest = new THREE.Mesh(chestGeo, materials.chest);
chest.scale.set(1.0, 0.55, 0.45);
chest.position.set(0, 0.5, 0.07);
chest.castShadow = true;
human.add(chest);

// 核心（腹肌）
const core = new THREE.Mesh(
  new THREE.BoxGeometry(0.45, 0.5, 0.32),
  materials.core
);
core.position.set(0, 0.15, 0);
core.castShadow = true;
human.add(core);

// 背阔肌 - 左右两侧
const lats_L = new THREE.Mesh(
  new THREE.BoxGeometry(0.15, 0.55, 0.32),
  materials.lats_L
);
lats_L.position.set(-0.25, 0.32, -0.05);
lats_L.castShadow = true;
human.add(lats_L);
const lats_R = lats_L.clone();
lats_R.material = materials.lats_R;
lats_R.position.x = 0.25;
human.add(lats_R);

// ===== 骨盆 =====
const pelvis = new THREE.Mesh(
  new THREE.BoxGeometry(0.42, 0.2, 0.3),
  materials.pelvis
);
pelvis.position.set(0, -0.15, 0);
pelvis.castShadow = true;
human.add(pelvis);

// 臀肌
const glutes = new THREE.Mesh(
  new THREE.SphereGeometry(0.22, 20, 14),
  materials.glutes
);
glutes.scale.set(1.1, 0.5, 0.7);
glutes.position.set(0, -0.2, -0.08);
glutes.castShadow = true;
human.add(glutes);

// ===== 上肢（左右镜像构建）=====
function buildArm(side) {{
  const s = side === 'L' ? -1 : 1;
  const armGroup = new THREE.Group();
  armGroup.position.set(s * 0.32, 0.68, 0);

  // 肩部三角肌
  const deltoid = makeSphere(0.11, materials['deltoids_' + side]);
  deltoid.scale.set(1.0, 0.8, 1.0);
  armGroup.add(deltoid);

  // 上臂关节组（控制上臂旋转）
  const upperArm = new THREE.Group();
  upperArm.position.set(0, -0.05, 0);
  armGroup.add(upperArm);

  // 二头肌
  const biceps = makeCapsule(0.075, 0.28, materials['biceps_' + side]);
  biceps.position.set(s * 0.02, -0.18, 0.04);
  biceps.rotation.z = s * 0.05;
  upperArm.add(biceps);

  // 三头肌
  const triceps = makeCapsule(0.07, 0.28, materials['triceps_' + side]);
  triceps.position.set(s * -0.02, -0.18, -0.04);
  triceps.rotation.z = s * 0.05;
  upperArm.add(triceps);

  // 肘关节组
  const elbow = new THREE.Group();
  elbow.position.set(0, -0.36, 0);
  upperArm.add(elbow);

  // 前臂
  const forearm = makeCapsule(0.065, 0.27, materials['forearms_' + side]);
  forearm.position.set(0, -0.17, 0);
  elbow.add(forearm);

  // 手
  const hand = makeSphere(0.05, materials.head);
  hand.position.set(0, -0.36, 0);
  elbow.add(hand);

  armGroup.userData = {{ upperArm, elbow, side }};
  return armGroup;
}}

const arm_L = buildArm('L');
const arm_R = buildArm('R');
human.add(arm_L);
human.add(arm_R);

// ===== 下肢 =====
function buildLeg(side) {{
  const s = side === 'L' ? -1 : 1;
  const legGroup = new THREE.Group();
  legGroup.position.set(s * 0.13, -0.28, 0);

  // 大腿关节组
  const upperLeg = new THREE.Group();
  legGroup.add(upperLeg);

  // 股四头肌（前）
  const quads = makeCapsule(0.1, 0.42, materials['quads_' + side]);
  quads.position.set(0, -0.28, 0.04);
  upperLeg.add(quads);

  // 腘绳肌（后）
  const hamstrings = makeCapsule(0.09, 0.4, materials['hamstrings_' + side]);
  hamstrings.position.set(0, -0.28, -0.05);
  upperLeg.add(hamstrings);

  // 膝关节组
  const knee = new THREE.Group();
  knee.position.set(0, -0.52, 0);
  upperLeg.add(knee);

  // 小腿三头肌
  const calf = makeCapsule(0.08, 0.36, materials['calves_' + side]);
  calf.position.set(0, -0.22, 0);
  knee.add(calf);

  // 脚
  const foot = new THREE.Mesh(
    new THREE.BoxGeometry(0.1, 0.06, 0.18),
    materials.head
  );
  foot.position.set(0, -0.45, 0.04);
  foot.castShadow = true;
  knee.add(foot);

  legGroup.userData = {{ upperLeg, knee, side }};
  return legGroup;
}}

const leg_L = buildLeg('L');
const leg_R = buildLeg('R');
human.add(leg_L);
human.add(leg_R);

// ========== MediaPipe → 模型骨骼映射 ==========
// MediaPipe 33个关键点索引
const MP = {{
  NOSE: 0, LEFT_SHOULDER: 11, RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13, RIGHT_ELBOW: 14, LEFT_WRIST: 15, RIGHT_WRIST: 16,
  LEFT_HIP: 23, RIGHT_HIP: 24, LEFT_KNEE: 25, RIGHT_KNEE: 26,
  LEFT_ANKLE: 27, RIGHT_ANKLE: 28,
}};

function calcRotation(parent, child) {{
  // 由两个 landmark 计算肢体方向
  // 注意 MediaPipe Y 轴向下，要翻转
  const dx = child.x - parent.x;
  const dy = -(child.y - parent.y); // 翻转Y
  // 返回相对垂直向下的旋转角度（弧度）
  // 默认胶囊朝下时 angle = 0
  const angle = Math.atan2(dx, -dy);
  return angle;
}}

function applyPose(lms) {{
  if (!lms || lms.length < 33) return;

  // 整体方向：从 MediaPipe 坐标计算上身倾斜
  const lSh = lms[MP.LEFT_SHOULDER];
  const rSh = lms[MP.RIGHT_SHOULDER];
  const lHip = lms[MP.LEFT_HIP];
  const rHip = lms[MP.RIGHT_HIP];

  // 躯干倾斜（前后倾）
  const shCenter = {{x:(lSh.x+rSh.x)/2, y:(lSh.y+rSh.y)/2}};
  const hipCenter = {{x:(lHip.x+rHip.x)/2, y:(lHip.y+rHip.y)/2}};
  const trunkLean = Math.atan2(shCenter.x - hipCenter.x, -(shCenter.y - hipCenter.y));
  human.rotation.z = trunkLean * 0.8;

  // 左臂
  const lElb = lms[MP.LEFT_ELBOW];
  const lWri = lms[MP.LEFT_WRIST];
  const lUpperRot = calcRotation(lSh, lElb);
  const lForeRot = calcRotation(lElb, lWri);
  arm_L.userData.upperArm.rotation.z = -lUpperRot;
  arm_L.userData.elbow.rotation.z = -(lForeRot - lUpperRot);

  // 右臂
  const rElb = lms[MP.RIGHT_ELBOW];
  const rWri = lms[MP.RIGHT_WRIST];
  const rUpperRot = calcRotation(rSh, rElb);
  const rForeRot = calcRotation(rElb, rWri);
  arm_R.userData.upperArm.rotation.z = -rUpperRot;
  arm_R.userData.elbow.rotation.z = -(rForeRot - rUpperRot);

  // 左腿
  const lKn = lms[MP.LEFT_KNEE];
  const lAn = lms[MP.LEFT_ANKLE];
  const lUpLegRot = calcRotation(lHip, lKn);
  const lLowLegRot = calcRotation(lKn, lAn);
  leg_L.userData.upperLeg.rotation.z = -lUpLegRot;
  leg_L.userData.knee.rotation.z = -(lLowLegRot - lUpLegRot);

  // 右腿
  const rKn = lms[MP.RIGHT_KNEE];
  const rAn = lms[MP.RIGHT_ANKLE];
  const rUpLegRot = calcRotation(rHip, rKn);
  const rLowLegRot = calcRotation(rKn, rAn);
  leg_R.userData.upperLeg.rotation.z = -rUpLegRot;
  leg_R.userData.knee.rotation.z = -(rLowLegRot - rUpLegRot);
}}

if (LANDMARKS) {{
  applyPose(LANDMARKS);
}}

// ========== 渲染循环 ==========
function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
animate();

// ========== 窗口缩放响应 ==========
window.addEventListener('resize', () => {{
  const w = container.clientWidth;
  const h = container.clientHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}});
</script>
</body>
</html>
"""
    components.html(html_code, height=height + 10, scrolling=False)
