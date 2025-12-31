# 复刻 SORA2 视频提示词专家模板

## 目录
- [模板说明](#模板说明)
- [Sora2 提示词核心原则](#sora2-提示词核心原则)
- [提示词结构模板](#提示词结构模板)
- [填写指南](#填写指南)
- [完整示例](#完整示例)

---

## 模板说明

### 用途
本模板用于分析上传的视频，提取并生成符合 Sora2 文生视频标准的详细提示词，以实现视频内容的高精度复刻。

### 适用场景
- 视频内容复刻与再创作
- 商业广告视频模仿
- 电影片段风格迁移
- 短视频创意复现
- 产品演示视频生成

### 核心优势
- 结构化三段式框架（风格-摄影-场景）
- 符合 Sora2 的五大支柱要求
- 时间轴精确分解
- 专业电影术语描述
- 世界模拟物理细节

---

## Sora2 提示词核心原则

### 五大支柱框架
1. **主体与角色**：清晰定义人物/物体的外观、服装、情感状态
2. **动作与运动**：使用具体动词描述正在发生的事情和交互方式
3. **环境与背景**：建立场景的位置、时间和氛围属性
4. **电影构图**：指定摄像机角度、运动和取景方式
5. **美学与风格**：确定视觉效果（真实感、动画、胶片类型）

### 世界模拟范式
Sora2 被理解为"世界模拟器"，有效提示应该：
- 提供初始条件和物理法则（重力、光线、反射）
- 明确物体如何相互作用
- 定义环境特性和材质属性
- 隐含或明确引导物理表现

### 提示词长度策略
- **创意探索型**（<120 词）：适合故事驱动、氛围营造的场景
- **精准执行型**（>200 词）：适合需要电影级控制和技术准确性的复刻

### 关键要点
- 使用具体、多维的描述而非抽象术语
- 包含感官细节（纹理、光线、声音）
- 明确摄像机指令显著提升视觉效果
- 避免过度复杂的物理描述
- 保持描述的清晰性和一致性

---

## 提示词结构模板

### 第一部分：Style（风格定义）

```markdown
### Style
* **Visual Texture（视觉纹理）:**
  [描述画面的质感特征：是真实拍摄、AI生成、动画风格？表面材质如何呈现？]
  示例：Photorealistic with cinematic digital polish / AI-generated hyper-realism / Hand-drawn animation style

* **Lighting Quality（光照质量）:**
  [描述光源类型、方向、强度和氛围]
  示例：Natural diffused light from windows / Cinematic golden hour lighting / Soft-box studio lighting

* **Color Palette（色彩调板）:**
  [列举主导色调和配色方案，使用具体色彩名称]
  示例：Vibrant and saturated - fiery red, deep purple, cobalt blue against neutral beige tones

* **Atmosphere（氛围）:**
  [用形容词描述整体情绪和感受]
  示例：Playful and enthusiastic / Nostalgic and cozy / Whimsical and heartwarming
```

### 第二部分：Cinematography（电影摄影）

```markdown
### Cinematography
* **Camera（摄像机运动）:**
  [描述摄像机的移动方式和拍摄手法]
  示例：Handheld with dynamic close-ups and slow zoom / Static medium shots with subtle drift / Smooth dolly tracking shot

* **Lens（镜头特性）:**
  [指定镜头类型、焦距和景深效果]
  示例：Standard smartphone wide-angle with deep focus / Macro lens for extreme details / 50mm portrait lens with shallow depth of field (bokeh)

* **Lighting（布光方案）:**
  [详细说明光照布置和效果]
  示例：Three-point lighting setup / Soft key light from side with rim lighting / Natural backlight creating silhouettes

* **Mood（情绪基调）:**
  [用精准词汇描述视觉情绪]
  示例：Upbeat and joyful / Intimate and satisfying / Energetic and masculine
```

### 第三部分：Scene Breakdown（场景分解）

```markdown
### Scene Breakdown

**Scene 1 (起始时间 - 结束时间):**
[用 1-3 句话描述场景的整体视觉呈现，包括主体、环境、关键元素]

**Actions（动作）:**
* [列举场景中发生的具体动作，使用精确动词]
* [描述人物/物体的移动轨迹和交互方式]
* [注明摄像机运动或视觉变化]

**Dialogue（对话）:**
* [如有人声对话，标注说话者和内容]
* [如无对话，标注"None"]

**Background Sound（背景音）:**
* [描述音乐类型、节奏、风格]
* [列举环境音效（如脚步声、风声、机械声）]

---

**Scene 2 (起始时间 - 结束时间):**
[重复上述结构]

**Actions:**
*
*

**Dialogue:**
*

**Background Sound:**
*

---

[根据视频长度继续添加 Scene 3, Scene 4...]
```

---

## 填写指南

### 第一步：整体观察（0-2 遍观看）
1. 确定视频的总体风格类型（真实拍摄/AI生成/动画）
2. 识别主要色调和光照特点
3. 记录摄像机的主要运动模式
4. 感受整体氛围和情绪

### 第二步：风格分析（填写 Style 部分）

#### Visual Texture 填写要点
- **真实拍摄**：描述画面清晰度、胶片/数码特征、表面材质细节
- **AI 生成**：注明是否有"蜡质感"、"梦幻感"、形变特征
- **动画风格**：说明是手绘/3D/像素风等

示例：
```
真实拍摄：Photorealistic with cinematic 4K clarity. Fabric textures show individual threading, metal surfaces exhibit authentic weathering and patina.

AI生成：AI-generated hyper-smooth imagery with slight waxy texture. Subtle morphing in fine details like fingers and hair, creating a dreamlike quality.
```

#### Lighting Quality 填写要点
- 光源位置（顶光/侧光/背光/环境光）
- 光照性质（硬光/柔光/自然光/人工光）
- 时间暗示（晨光/午后/黄昏/夜间）

示例：
```
Cinematic golden hour lighting streaming through large windows at a 45-degree angle, creating warm rim lighting and long dramatic shadows. Supplemented by soft fill light to maintain detail in shadow areas.
```

#### Color Palette 填写要点
- 使用具体色彩名称而非"鲜艳"、"暗淡"等抽象词
- 列举 3-5 个主导色
- 说明色彩对比度和饱和度

示例：
```
High-contrast palette dominated by racing red (#C80000) and chrome silver, with accents of deep espresso brown and matte black. Background features warm oak wood tones and soft cream whites.
```

#### Atmosphere 填写要点
- 使用 2-4 个形容词组合
- 结合视觉和情感层面
- 考虑目标受众感受

示例：
```
Playful, enthusiastic, and commercial-like, capturing childhood wonder and toy excitement.
Nostalgic and cozy yet industrious, evoking a quiet productive morning in a beloved workshop.
```

### 第三步：摄影分析（填写 Cinematography 部分）

#### Camera 填写要点
- 运动类型：静止/手持/稳定器/轨道/航拍
- 运动方式：推/拉/摇/移/升降/旋转
- 拍摄角度：平视/仰视/俯视/荷兰角

示例：
```
Handheld camera with organic micro-movements, featuring dynamic close-ups that gradually zoom into subject. Low-angle perspective (approximately 30 degrees below eye level) emphasizes product features. Transitions include smooth pans and a final 360-degree rotation.
```

#### Lens 填写要点
- 焦距类型：广角(<35mm)/标准(35-70mm)/长焦(>70mm)/微距
- 景深：浅景深(背景虚化)/深景深(全清晰)
- 特殊效果：鱼眼/移轴/变形宽银幕

示例：
```
50mm portrait lens (full-frame equivalent) with aperture at f/2.8, creating moderate depth of field. Foreground subject sharp with background softly blurred into creamy bokeh. Subtle lens breathing during zoom.
```

#### Lighting 填写要点
- 布光方案：单光源/三点布光/自然光/混合光
- 光比关系：高对比/低对比/平光
- 特殊效果：逆光剪影/伦勃朗光/蝴蝶光

示例：
```
Three-point lighting setup: warm 3200K key light from camera left at 45 degrees, soft white fill light at 50% intensity from camera right, cool-toned rim light from behind to separate subject from background. Practical lights (visible lamps) add ambient glow.
```

#### Mood 填写要点
- 用精准的形容词而非宽泛描述
- 考虑视觉节奏（快速/缓慢/紧张/松弛）
- 结合目标情感

示例：
```
Intimate, satisfying, and appreciative of craftsmanship with a slow, meditative pacing.
Energetic and humorous with rapid cuts and high-impact visuals designed for viral engagement.
```

### 第四步：场景分解（填写 Scene Breakdown 部分）

#### 时间划分原则
- 按场景切换点分段（镜头切换/环境变化/主体变化）
- 每个场景通常 2-8 秒
- 标注精确到秒（如 0:00s - 0:04s）

#### 场景描述要点
第一句话包含：
1. 场景主体（谁/什么）
2. 主体状态（外观/服装/情感）
3. 环境位置（哪里）
4. 正在发生的事（核心动作）

示例：
```
A bearded man in a brown workwear jacket sits at a rustic wooden table in a crowded cafe. He pours dark coffee from a glass carafe into a detailed, red V8 engine-shaped mug.
```

#### Actions 填写要点
- 使用主动语态和具体动词
- 按时间顺序列举
- 包含微小细节（手部动作/眼神/物体移动）
- 注明摄像机运动

示例：
```
* Child's finger gently presses the heart-shaped button on doll's chest
* Doll's LED light pulses with bright blue glow in sync with music beat
* Camera executes slow digital zoom (2x) toward doll's face
* Girl's expression transitions from focused concentration to delighted surprise
* Subtle breathing movement visible in girl's shoulders
```

#### Dialogue 填写要点
- 如有对话，标注说话者身份和语气
- 完整引用关键台词
- 注明语言（中文/英文/双语）
- 无对话时明确标注"None"

示例：
```
* Narrator (Warm, informative male voice): "Looking for a gift that makes auto mechanics smile?"
* Girl (Excited, high-pitched): "妈妈快看！它会唱歌！"
* None
```

#### Background Sound 填写要点
- 音乐：类型、节奏、乐器、情绪
- 环境音：具体声源和音效
- 人声：群体氛围声/脚步声/呼吸声
- 声音变化：渐强/渐弱/突然转变

示例：
```
* High-energy K-pop music with electronic beats (140 BPM), featuring female vocals singing in English and Korean. Synthesizer melody with prominent bass line.
* Ambient workshop sounds: distant bird chirps, soft wind through open window, faint metallic clinking of tools.
* Steam hissing sound effect (artificial, amplified) synced with visual steam clouds.
```

### 第五步：质量检查清单

完成填写后，检查以下要点：

- [ ] Visual Texture 是否包含材质和纹理细节？
- [ ] Lighting Quality 是否明确光源方向和性质？
- [ ] Color Palette 是否使用具体色彩名称（至少3个）？
- [ ] Camera 是否描述了运动方式和角度？
- [ ] Lens 是否说明了焦距和景深效果？
- [ ] 每个场景是否标注了准确时间戳？
- [ ] Actions 是否使用了具体动词而非抽象描述？
- [ ] 是否描述了物体间的物理交互（如适用）？
- [ ] 总字数是否达到精准执行要求（>200 词）？
- [ ] 描述是否具体到可以"看见"画面？

---

## 完整示例

以下是一个完整的提示词示例，用于复刻一个产品广告视频：

```markdown
### Style
* **Visual Texture:** Photorealistic with cinematic digital polish and commercial-grade finish. The ceramic mug surface exhibits high-relief 3D-molded textures that accurately mimic matte black ceramic and metallic chrome sheen. Workshop environments feature authentic details: fine sawdust particles suspended in light beams, pronounced wood grain textures on aged workbenches, and realistic fabric weave in clothing. Metal tools show subtle oxidation and wear patterns.

* **Lighting Quality:** Cinematic "golden hour" lighting scheme. Primary illumination comes from natural warm sunlight (approximately 3200K color temperature) streaming through large workshop windows at a 45-degree angle, creating soft rim lighting around the mug's chrome details and casting long, diffused shadows. Interior scenes utilize three-point lighting to maintain professional polish while preserving natural feel.

* **Color Palette:** High-contrast color scheme dominated by deep matte black (#1a1a1a) and warm amber tones (#d4a574). Accent colors include safety yellow (#ffd700) from tool details, industrial orange (#ff6600) from warning labels, and polished chrome silver with blue-white highlights. Background palette features weathered oak wood (#8b7355), concrete gray (#6b6b6b), and soft cream whites (#f5f5dc). Saturation is vibrant but controlled, avoiding oversaturation.

* **Atmosphere:** Nostalgic and cozy yet industrious and masculine. The video evokes the comforting feeling of a quiet, productive morning in a well-loved personal workshop. There's an appreciation for craftsmanship and blue-collar work culture, combined with the intimate satisfaction of a perfect coffee moment. The mood balances rugged authenticity with commercial appeal.

### Cinematography
* **Camera:** Combination of extreme macro close-ups and medium establishing shots. Primary camera movement is steady handheld with subtle organic micro-movements (approximately 1-2mm drift) to maintain a personal, "first-person observer" feel rather than sterile tripod rigidity. Includes one smooth dolly-in movement (0:01s-0:03s) and a slow circular pan (0:07s-0:09s) around the subject at approximately 15 degrees per second.

* **Lens:** Two lens setup: (1) 100mm macro lens for extreme detail shots of mug's embossed tools, with minimum focus distance of 30cm, producing sharp foreground with rapid focus fall-off; (2) 85mm portrait lens for medium shots to create moderate shallow depth of field, beautifully blurring workshop and kitchen backgrounds into creamy bokeh while maintaining subject sharpness. Both lenses shot at approximately f/2.8 to f/4 for optimal depth control.

* **Lighting:** Natural key light from camera-left window supplemented by soft fill card (silver reflector) camera-right to prevent shadow areas from going completely black. Strong practical sunlight serves as backlight and rim light, specifically highlighting steam rising from coffee and creating luminous edge definition on chrome tool details. Final kitchen scene adds warm overhead pendant lamp (practical light source visible in shot) for amber-toned ambient fill.

* **Mood:** Intimate, satisfying, and deeply appreciative of craftsmanship and traditional work culture. Visual pacing is slow and meditative (average shot length 3.5 seconds), allowing viewer to absorb details. The cinematography suggests professionalism and quality while maintaining warmth and accessibility.

---

### Scene Breakdown

**Scene 1 (0:00s - 0:01s):**
Extreme close-up establishing shot of the black ceramic toolbox mug. A weathered male hand with visible calluses enters frame from the right, index finger extended. The finger gently traces the tactile, embossed 3D tools built into the side of the cup, specifically lingering on a yellow tape measure relief and a pair of silver pliers. Warm directional sunlight from the left creates dynamic shadows that emphasize the depth and texture of the molded tool details. Background is completely defocused, showing only warm amber bokeh.

**Actions:**
* Weathered male hand enters frame with slow, deliberate movement
* Index finger makes contact with yellow tape measure embossment and traces its outline
* Finger shifts to probe the texture of molded pliers detail
* Hand subtly tilts mug 5-10 degrees to catch changing light
* Shadows shift across embossed surface as mug angle changes
* Camera executes slight forward dolly movement (5cm closer)

**Dialogue:**
* Narrator (Warm, informative male voice with slight rasp, suggesting middle-aged craftsman): "Looking for a gift that makes auto mechanics smile?"

**Background Sound:**
* Soft, lo-fi acoustic guitar background track begins (approximately 90 BPM, warm and inviting)
* Ambient workshop soundscape: distant bird chirps outside window, gentle wind rustle
* Very faint sound of finger sliding across ceramic texture (ASMR-quality foley)

---

**Scene 2 (0:01s - 0:07s):**
The shot pulls back to a medium view revealing a rustic, sun-drenched workshop environment. The same weathered hand now holds the black toolbox mug at chest height in the center of frame. The mug is filled with steaming hot dark coffee. Thick, wispy steam rises vertically from the liquid surface in slow, realistic tendrils. Background reveals aged wooden workbench, vintage hand tools hanging on pegboard, a weathered red metal toolbox (Milwaukee-style), and exposed wood beam ceiling. Dramatic sunbeams cut diagonally through the air from left to right, illuminating thousands of floating dust particles and the rising coffee steam, creating a volumetric light effect.

**Actions:**
* Hand holds mug steady in center frame with slight natural tremor (human realism)
* Thick coffee steam rises in complex, naturalistic patterns at approximately 3cm/second
* Floating sawdust particles drift slowly through sunbeams (Brownian motion physics)
* Camera executes slow horizontal pan from left to right (approximately 30-degree arc over 6 seconds)
* Background workshop elements gradually revealed: red toolbox, hanging wrenches, vintage hand saw
* Steam continues to billow, occasionally catching direct sunlight and glowing white

**Dialogue:**
* Narrator (Warm, informative, continuing): "This toolbox coffee mug is perfect. An 11-ounce cup designed like a mechanic's tool set. Funny, unique, and practical for daily coffee."

**Background Sound:**
* Lo-fi acoustic guitar track continues with added soft percussion layer
* Subtle hissing sound of hot steam rising (realistic, not exaggerated)
* Ambient workshop creaks and settling sounds
* Very faint wind chime from outside (adds nostalgic outdoor element)

---

**Scene 3 (0:07s - 0:11s):**
Setting transition to cozy home kitchen interior. The black toolbox mug is held in the foreground (lower right quadrant of frame) by the same hand. Camera angle shifts to over-the-shoulder perspective. Background shows a lived-in dining area: round wooden table with breakfast plates (eggs and toast visible), framed family photos on the wall, warm cream-colored walls, and a window with sheer curtains allowing diffused morning light. The lighting is softer and warmer than the workshop, suggesting domestic comfort. The mug is slowly rotated in hand to display different embossed tool details: hammer, flat-head screwdriver, adjustable wrench.

**Actions:**
* Hand rotates mug clockwise approximately 120 degrees over 4 seconds
* Different tool embossments come into view: hammer head, screwdriver handle, wrench jaws
* Subtle breathing movement visible in hand position (rises and falls 1-2mm)
* Chrome tool details catch and reflect window light as mug rotates, creating small light flares
* Steam continues to rise from coffee, though less dramatically than workshop scene
* Camera remains static with only minor handheld stabilization drift

**Dialogue:**
* Narrator (Warm, informative, voice beginning to fade): "Great for mechanics, DIY dads, or anyone who..."

**Background Sound:**
* Acoustic guitar music swells slightly, adding harmonic layer
* Ambient domestic kitchen sounds: distant refrigerator hum, clock ticking
* Subtle ceramic-on-skin friction sound as hand rotates mug
* Music begins to fade out as scene ends

---

**Scene 4 (0:11s - 0:13s):**
[如视频继续，按相同格式添加后续场景]
```

---

## 使用流程建议

### 对于程序开发者
当接收到用户上传的视频文件后，系统应：

1. **视频分析阶段**
   - 提取视频时长、分辨率、帧率
   - 识别场景切换点（使用场景检测算法）
   - 分析色彩分布和主导色调
   - 检测摄像机运动模式

2. **内容识别阶段**
   - 识别主要对象和人物
   - 检测动作和运动轨迹
   - 识别环境和背景元素
   - 提取音频特征（音乐/对话/音效）

3. **提示词生成阶段**
   - 使用本模板结构
   - 填充 Style 部分（基于视觉分析）
   - 填充 Cinematography 部分（基于摄像机数据）
   - 按时间轴生成 Scene Breakdown（基于场景切换）

4. **人工审核阶段**
   - 提供生成的提示词草稿
   - 允许用户编辑和优化
   - 验证物理逻辑和描述准确性

### 对于内容创作者
手动使用本模板时：

1. 观看目标视频 3-5 遍，分别关注：
   - 第 1 遍：整体感受和风格
   - 第 2 遍：摄像机和构图
   - 第 3 遍：逐帧场景和动作
   - 第 4-5 遍：细节补充

2. 按模板从上到下填写，不要跳跃

3. 使用具体描述替代抽象词汇：
   - ❌ "画面很美" → ✅ "Golden hour sunlight creates warm rim lighting and long shadows"
   - ❌ "镜头移动" → ✅ "Smooth dolly-in shot from 3 meters to 1 meter over 5 seconds"
   - ❌ "红色的" → ✅ "Fire engine red (#CE2029) with metallic flakes"

4. 完成后使用质量检查清单验证

---

## 进阶技巧

### 物理细节描述
Sora2 的世界模拟能力强大，描述物理交互可显著提升真实感：

```
优秀示例：
"As the ceramic mug is set down on the wooden table, it makes contact with a soft dampened thud. The coffee inside exhibits realistic liquid physics: a subtle surface ripple radiates outward from the center, and the liquid level tilts slightly before stabilizing due to inertial momentum. Micro-droplets adhere to the inner rim from previous sips."

基础示例：
"The mug is placed on the table. The coffee moves a little."
```

### 感官细节强化
虽然 Sora2 生成视频，但暗示其他感官可增强沉浸感：

```
触觉："The rough texture of the weathered ceramic suggests a satisfying grip"
听觉："The steam's soft hiss implies the coffee is at perfect drinking temperature"
嗅觉："Wisps of aromatic steam suggest dark roast with chocolate notes"
温度："Visible condensation on the mug's exterior indicates scalding-hot liquid within"
```

### 特殊效果处理
- **慢动作**：明确标注"Slow motion at 50% speed (shot at 60fps, played at 30fps)"
- **快动作**：标注"Time-lapse effect, 10x speed compression"
- **定格**：标注"Action freezes for 1.5 seconds while camera continues to move around subject"
- **转场**：描述"Cross-dissolve transition over 0.5 seconds" 或 "Hard cut"

### 避免常见错误
1. ❌ 使用过于宽泛的形容词（"好看"、"漂亮"、"酷炫"）
2. ❌ 忽略时间戳和场景时长
3. ❌ 遗漏摄像机运动描述
4. ❌ 忽视光源方向和性质
5. ❌ 使用技术术语而不解释效果（如仅写"使用伦勃朗布光"而不描述光影效果）
6. ❌ 场景描述过于简略（少于 50 词）
7. ❌ 忽略物体间的物理交互和因果关系

---

## 版本信息

- **模板版本**：v1.0
- **创建日期**：2025-12-31
- **适用于**：Sora2 文生视频模型
- **参考来源**：
  - [awesome_sora2_prompt](https://github.com/zhangchenchen/awesome_sora2_prompt)
  - 实际视频提示词分析（5 个样本案例）
  - Sora2 官方提示词指南

---

## 附录：快速参考表

### 常用摄像机运动英文术语
- Dolly in/out：推轨/拉轨
- Pan left/right：左摇/右摇
- Tilt up/down：上摇/下摇
- Tracking shot：跟踪镜头
- Crane shot：升降镜头
- Handheld：手持
- Steadicam：斯坦尼康稳定器
- Static/Fixed：固定镜头
- Zoom in/out：推焦/拉焦
- Orbit/Circular：环绕旋转

### 常用镜头类型
- Extreme wide shot (EWS)：大远景
- Wide shot (WS)：远景
- Medium shot (MS)：中景
- Close-up (CU)：特写
- Extreme close-up (ECU)：大特写
- Over-the-shoulder (OTS)：过肩镜头
- Point of view (POV)：主观镜头

### 常用光照术语
- Key light：主光
- Fill light：补光
- Rim light / Back light：轮廓光/背光
- Practical light：实用光源（画面中可见的灯）
- Golden hour：黄金时刻
- Blue hour：蓝调时刻
- High key：高调（明亮、低对比）
- Low key：低调（暗沉、高对比）

### 色彩情绪对照
- 红色系：激情、能量、警示、温暖
- 蓝色系：冷静、科技、忧郁、专业
- 黄色系：快乐、活力、温暖、注意
- 绿色系：自然、平静、生长、和谐
- 紫色系：神秘、奢华、创意、梦幻
- 橙色系：友好、热情、创造、活跃
- 黑白灰：经典、严肃、简约、永恒

---

**使用愉快！如有问题或改进建议，欢迎反馈。**
