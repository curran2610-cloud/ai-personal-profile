# 不要给 Codex 瞎装 skill：视频内容拆解与实操清单

来源视频：
`/Users/kunkun/Downloads/不要给Codex瞎装skill_codex插件_codex_skill_AI工作流_codex剪视频.mp4`

## 1. 视频核心观点

这条视频的重点不是“多装 skill”，而是“按视频生产流程拆 skill”。

作者的意思是：Codex 的 skill 不应该混成一个万能包。应该把视频生产拆成若干明确场景，每个 skill 只负责一个稳定任务，例如剪口播、生成素材、批量出片、生成视频提示词、做字幕等。

一句话总结：

> 不要瞎装；先定义工作流，再按节点装 skill。

## 2. 视频里提到的 skill/能力类型

### 2.1 剪口播类

用途：
- 剪掉口误
- 去掉重复
- 去掉长停顿
- 保留重点句
- 生成或修正字幕

适用场景：
- 真人口播
- 课程切片
- 访谈切片
- AI 工具讲解视频

视频里的提示：
- 有些 skill 是帮你剪口播的
- 在什么场景下该用哪个 skill，要先分清楚

### 2.2 批量视频类

用途：
- 批量生成同一类视频
- 做每周 AI 工具榜
- 做趋势榜、排行、周数据、分析型内容

适用场景：
- 周更栏目
- 榜单号
- 工具测评号
- 数据解读号

视频里出现的例子：
- 每周 AI 工具榜
- 批量
- 排行
- 周数据

### 2.3 素材生成类

用途：
- 没有视频素材时，把文章、脚本、提示词转成素材
- 生成图片、视频、音乐、音效

视频里提到或出现：
- HyperFrames
- Generative Media Skills
- 图像
- 视频
- 声音
- 即梦 Seedance

注意：
这些更像“素材补丁包”，不建议拿它单独完成整条视频。

### 2.4 后期剪辑类

用途：
- 字幕
- 调色
- 图表动画
- 标签
- 导入、剪辑、调色、字幕、导出

视频里出现：
- Video Use
- 视频素材
- 字幕样式
- 图表库

### 2.5 视频提示词类

用途：
- 把文字脚本改写成适合视频生成模型的 prompt
- 投喂给即梦、Seedance、Runway、Veo、Sora 等视频模型

视频里出现：
- prompt
- 即梦 Seedance
- 再把生成的提示词用于生成

## 3. 当前 Codex 已有/已装 skill 对照

### 3.1 原本已装

个人 skills：
- `cinematic-video-prompt-engineer`

适合做：
- 把剧情、场景、短视频想法改成视频生成模型 prompt
- 可用于 Seedance、Kling、Veo、Sora、Runway、即梦等

系统内置：
- `imagegen`
- `openai-docs`
- `plugin-creator`
- `skill-creator`
- `skill-installer`

插件临时能力：
- `documents`
- `pdf`
- `presentations`
- `spreadsheets`
- `browser`
- `chrome`

### 3.2 本次已安装

已安装到 `/Users/kunkun/.codex/skills/`：

- `transcribe`
- `speech`
- `screenshot`

用途：

`transcribe`
- 转录音频/视频为文字
- 后续可做逐字稿、字幕稿、切片点

`speech`
- 生成 AI 配音
- 可做旁白、口播、解说音频

`screenshot`
- 截桌面、窗口或局部图
- 可用于实操过程截图、素材采集、界面验证

注意：
新安装的 skill 通常需要重启 Codex 后才会自动出现在可用技能列表里。

## 4. 没有安装的，不应该硬装的

视频里有些词不是 Codex skill，而是外部工具或能力方向：

- HyperFrames：外部视频/素材生成工具
- Remotion：代码化视频生成框架
- Video Use：视频使用/剪辑类能力概念，未确认是当前 Codex 官方 skill
- 即梦 Seedance：外部视频生成模型/平台
- Generative Media Skills：泛指生成式媒体能力，不等于一个具体可安装 skill

这些不应该直接当成 Codex skill 瞎装。正确做法是：

1. 先确定我们要做哪类视频
2. 再决定是用外部平台、脚本、插件，还是自定义 skill
3. 如果流程稳定，再把它沉淀成自己的 Codex skill

## 5. 建议实操流程

### 阶段 A：拆内容

输入：
- 一个选题
- 一段视频
- 一篇文章
- 一个工具介绍

输出：
- 标题
- 口播稿
- 分镜脚本
- 素材需求表
- 视频生成 prompt

可用 skill：
- `transcribe`
- `cinematic-video-prompt-engineer`

### 阶段 B：生成素材

输入：
- 分镜脚本
- 每个镜头的画面描述
- 风格要求

输出：
- 视频生成 prompt
- 图片生成 prompt
- 音效/配乐需求
- B-roll 素材清单

可用 skill：
- `cinematic-video-prompt-engineer`
- `imagegen`
- `speech`

### 阶段 C：剪辑与字幕

输入：
- 原视频
- 口播音频
- 转录稿
- 分镜表
- 素材文件

输出：
- 字幕稿
- 剪辑点
- 口播清理建议
- 后期包装清单

可用 skill：
- `transcribe`
- `screenshot`

### 阶段 D：批量出片

输入：
- 选题列表
- 固定视频结构
- 固定字幕/标题模板
- 固定 prompt 模板

输出：
- 每条视频的脚本
- 每条视频的素材表
- 批量生成任务清单

建议后续自定义 skill：
- `weekly-ai-tool-rank-video`
- `short-video-script-to-shotlist`
- `talking-head-cleanup-plan`
- `seedance-prompt-pack`

## 6. 下一步实操建议

先不要创建很多 skill。

建议先做一个最小闭环：

1. 选一个视频选题
2. 让 Codex 写 60 秒口播稿
3. 拆成 6 到 8 个镜头
4. 每个镜头生成 Seedance/即梦 prompt
5. 生成配音稿
6. 产出字幕稿
7. 整理成剪辑执行表

跑通以后，再把稳定步骤沉淀成自定义 skill。

## 7. 当前环境限制

当前检查结果：

- `OPENAI_API_KEY` 未配置
- Python `openai` 包未安装

所以 `transcribe` 和 `speech` 现在还不能直接调用 OpenAI API。

要启用它们：

```bash
python3 -m pip install openai
export OPENAI_API_KEY="你的 key"
```

不要把 key 发到聊天里。配置到本机环境变量后，再让 Codex 继续跑转录或配音即可。
