# 克罗心口播剪辑工程

## 用户要求
保留原始口播、语速、自然气口；使用用户提供的素材；参考 https://v.douyin.com/n7OHI_xkQVA/ 的剪辑包装。所有付费、积分操作需事先取得明确同意。未授权收费。

## 已验证
- 原视频：/Users/kunkun/Downloads/克罗心自动剪辑工作流/copy_BF503CC3-B59D-4BEC-8B71-CBFA248DDB1F_副本.MOV
- 1080×1920，时长 74.117007 秒；素材清单包含 254 个文件。
- 原声已转为 audio/vo-full.wav：44.1 kHz、单声道，不剪切、不变速。
- Node.js、Python、ffmpeg、ffprobe 可用。
- 文档附录两个 Skill 已原样安装到 /Users/kunkun/.codex/skills/voice-to-storyboard/SKILL.md 和 /Users/kunkun/.codex/skills/storyboard-to-chatcut/SKILL.md，逐字验证一致。

## 未完成
- ChatCut 官方安装器在沙箱中主动拒绝执行，应用未安装、MCP 未连接、无项目 ID。
- 用户需在系统终端运行官方安装命令：curl -fsSL https://chatcut.io/install.sh | sh
- 本地 faster-whisper 虚拟环境在当前聊天 work/whisper-env，依赖已安装并验证安装日志成功，large-v3 下载已启动，尚未完成转录。
- 用户无口播稿，需从实际口播转录；不编造文案与时间戳。
- 对标链接已解析为视频 7699416503216660657，但浏览器连续超时，尚未观看，不可声称已分析风格。
- 未生成分镜、字幕或 ChatCut 时间线，未导出、未发布。
