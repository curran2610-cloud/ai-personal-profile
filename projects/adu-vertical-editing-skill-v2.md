---
name: adu-vertical-editing
description: 为站长在阿杜导演台制作、重构或修改抖音竖屏口播、文案配音、热点解说与高定工艺拆解视频（1080×1920）。当用户要求开剪新片、替换实拍空镜、重构2.5D动效排版、制作海报级开头、按审美反馈精修当前阿杜工程、或复用「破防信息流/清醒黑白灰」体系时必须触发。仅用于竖屏视频剪辑与动效工程，不用于纯文案翻译或无时间线的静态海报。
metadata:
  version: "2.0.0"
---

# 站长竖屏剪辑执行手册（Grade-A 门禁版）

阿杜导演台是主工程与交付位置。严禁触发最终导出（由用户在阿杜内点击）。用户本轮指定的工程、素材与措辞优先级高于一切历史案例。

---

## 一、永不触犯 10 条硬红线（开工前锁死，全程不得违背）

1. **视觉锚点先行**：开场（`0–2.8s`）先锁死屏幕正中 `44%–56%` 的 **8–11 字**两行短标题（`AlimamaFangYuan` + SVG `stroke-linejoin="round"` 圆角三层花字），再向中心收拢上下贴纸；严禁长句塞标题或单侧孤悬留空。
2. **向心聚拢 × 1:2.5 纵深**：开场贴纸的人物朝向、手势与道具线条必须向正中标题聚拢，严禁上下同向斜飞；保持上小下大 `1:2.5` 前后空间感，前景人物面部高于字幕带。
3. **主体纯轮廓 × 描边自适应**：贴纸可含主体+核心道具（如车+人），但必须沿真实轮廓精抠，**严禁把砖墙/车库门等方形脏背景剪进贴纸**；按素材气质灵活选用手撕纸毛边、平滑白边或无边投影，且同帧风格统一。
4. **信息依次释放 × 单品递进强调**：证据与卖点按叙事节奏分步释放，严禁在开头剧透复用后文实锤截图；核心单品允许通过「全景 → 放大局部 → 旋转特写 → 对比」递进式多次出现，禁止无增量的原地平铺重复。
5. **实体 100% 强一致**：选材绝不凭文件名盲配，必须抽帧核验真实款型、材质与工序（说 925 素银绝不配镶钻/绿松石，说抛光绝不配非抛光轮）。
6. **0 内部闪切**：所有 B-roll 落轨前必跑 `scripts/check_internal_cuts.py`，确保截取区间内为单一连贯镜头，杜绝 `< 1.2s` 晃眼闪切。
7. **清醒黑白灰 90-8-2**：全片 90% 石墨黑/冷银灰/暖白 + 8% 逐镜头校准的真实材质本色 + 2% 暖黄高亮/克制红印章；禁止暗红雾霾与花哨色偏。
8. **物理单曲线 × 实体不透明分幕**：推进/2.5D 运镜必须用单一连续缓动曲线（防两段式顿挫）；分幕离场卡片保持 `opacity: 1` 实体滑出（防底字透出重影）；**全局禁用 `backdrop-filter`**。
9. **同底对比零拆抠 × 零截断**：同背景对比图严禁拆成两半重拼；完整吊坠/刻字严禁 `cover` 截断。
10. **字幕带绝对洁净**：自带底部花字的素材严禁全屏铺底（必须入中上部卡片）；每次交付前必出带 `captions: true` 的预览帧，确认 0 文字碰撞。

---

## 二、5 阶段强制执行流水线（未过当前门禁，严禁进入下一阶段）

### 阶段 1：定轨与配音（Audio & Rhythm Lock）
- **必读**：若属热点混剪/信息流，读 [破防信息流模板](references/template-pofang-feed.md)；若属真人口播，读 [剪辑总纲](references/master-principles.md) 与 [通用风格基调](references/style-baseline.md)。
- **动作**：确认口播（优先本地豆包 `zh_female_mizai_uranus_bigtts` 或原声精剪）、对齐 `1.1×` 紧凑气口、BGM 连续闪避（不动原情绪曲结构）、生成 `4.2 kHz` 丝绒低通独立音效轨。
- **过关门禁**：音轨峰值达标（口播 `-3~-4 dB`、BGM `-6 dB`、音效 `-3 dB`），无多余长空白（`>0.35s`）。

### 阶段 2：选材与去闪切（Footage Curation）
- **必读**：[高质素材筛选与建库规范](references/footage-curation.md)。
- **动作**：按逐字稿实体名词抽帧核验本地实拍；落轨前对全部候选 B-roll 跑 `python3 scripts/check_internal_cuts.py`。
- **过关门禁**：实体 100% 匹配 + 截取区间 0 内部硬切 + 底部自带字素材全部归入中上部卡片路线。

### 阶段 3：海报级开头编排（Poster-Grade Opener，`0–2.8s`）
- **必读**：[爆款海报级开头与贴纸设计规范](references/poster-opener-design.md)。
- **动作**：用 `python3 scripts/make_torn_sticker.py` 沿主体轮廓精抠贴纸（按气质选 `--edge torn|white|none`）；先锁正中 8–11 字 SVG 圆角双描边花字，再按向心矢量摆位上下贴纸。
- **过关门禁**：渲染 `1.20s` 带字幕预览并通过**「3 秒眯眼重心测试」**（第一眼落点必为正中短标题，无脏矩形背景，无墨镜/字幕遮挡）。

### 阶段 4：中后段 2.5D 排版与调色（Motion & Color）
- **必读**：[安全区与动效因果衔接](references/motion-choreography-and-safezone.md)、[潮流高定调色规范](references/color-grading-and-tone.md)；需重构高级版式时按需读 [顶流视觉组件库](references/creator-component-library.md)。
- **动作**：常规双卡严守抖音安全区 `x: 80–940px`；2.5D 长文聚光遵循「黑场随卡片同步压下 → 锁稳后再划荧光笔」；取消机械固定顶栏；逐镜头校准 B-roll 色温与饱和度。
- **过关门禁**：无轨道重叠、无半透明重影、无无意义大块死黑空带、核心信息停留 `1.2–2.2s`。

### 阶段 5：双层审美自检与交付（Dual-Layer Critic & Delivery）
- **必读**：[双层成片审美质检官](references/aesthetic-critic.md)。
- **动作**：在阿杜导演对开头、转场、2.5D 聚光、所有 B-roll 与结尾批量出 `look`（`captions: true`）并逐帧肉眼核验；发现任何瑕疵先自修再复检。
- **过关门禁**：阿杜回执全帧 `no words in the picture run into the subtitle line` + 双层质检 100% 通过；交付时附上可点击预览帧链接，绝不输出任何口令或密钥。

---

## 三、扁平资源索引（1 层直达，按阶段按需读取）

| 类型 | 文件路径 | 何时读取 |
| :--- | :--- | :--- |
| 必读总纲 | [references/master-principles.md](references/master-principles.md) | 任意新片立项、对齐留人与认知节拍 |
| 选材门禁 | [references/footage-curation.md](references/footage-curation.md) | 阶段 2 挑选实拍与证据图前 |
| 开头海报 | [references/poster-opener-design.md](references/poster-opener-design.md) | 阶段 3 设计开场贴纸与短标题前 |
| 安全区与动效 | [references/motion-choreography-and-safezone.md](references/motion-choreography-and-safezone.md) | 阶段 4 编写 HTML Motion 与转场前 |
| 调色与光学 | [references/color-grading-and-tone.md](references/color-grading-and-tone.md) | 阶段 4 统一黑白灰与校色 B-roll 前 |
| 顶流组件库 | [references/creator-component-library.md](references/creator-component-library.md) | 需调用大字穿人/撕纸/卡片墙等组件时 |
| 破防模板 | [references/template-pofang-feed.md](references/template-pofang-feed.md) | 热点混剪/配音信息流片型 |
| 双层质检官 | [references/aesthetic-critic.md](references/aesthetic-critic.md) | 阶段 5 交付前强制自审 |
| 知识与工具 | [references/knowledge-map.md](references/knowledge-map.md) / [references/editors.md](references/editors.md) / [references/production.md](references/production.md) | 查业务背景、AE/Fusion 协作或分镜表时 |
| 切点扫描脚本 | [scripts/check_internal_cuts.py](scripts/check_internal_cuts.py) | 阶段 2 落轨前扫描 B-roll 内部硬切 |
| 轮廓贴纸脚本 | [scripts/make_torn_sticker.py](scripts/make_torn_sticker.py) | 阶段 3 精抠主体轮廓并生成撕纸/白边贴纸 |
