# AI 珠宝设计白模工作流

项目入口：[珠宝设计 Skill](skills/jewelry-design/SKILL.md)。根目录 AGENTS.md 指引后续项目任务读取它。
这是项目内 Skill 源码，未安装到全局技能目录，未声称应用已自动注册新技能。

## 直接调用
在本项目中可以说：
> 按项目珠宝设计 Skill 执行，启动珠宝3D白模 Agent。读取 projects/<项目名> 的全部需求和引用资料，先输出白模初稿，记录尺寸假设、元素方向和相机。只输出中性白模。

或直接引用 `skills/jewelry-design/SKILL.md` 的完整路径。
Agent 的岗位指令在 [white-model-agent.md](skills/jewelry-design/agents/white-model-agent.md)。它是可复用的任务角色与委派说明，不是常驻运行的后台服务。

## 本轮建立的能力
- 需求与资料按当前项目归档，旧案例不自动继承。
- 尺寸允许先假设再优化，确认项/来源标注/假设/实测分别记录。
- 有方向的装饰实例各有基线，防止改动造成倒置、镜像和翻面；整体旋转、换相机不误判。
- Blender 实际几何锚点和相机导出脚本，方向比较与历史版本防覆盖工具。
- 概念、几何、打印候选、生产审核分阶段，不把白模精细度等同于可制造性。
- 默认仅白/灰不透明模型；材质意向只入规格。

## 用法
以下在项目根目录执行；项目目录应先存在。
```
python3 skills/jewelry-design/scripts/workflow.py new-version projects/<项目名> --reason '建立首版白模'
python3 skills/jewelry-design/scripts/workflow.py inventory projects/<项目名> --out projects/<项目名>/versions/v001/input-inventory.json
python3 skills/jewelry-design/scripts/test_workflow.py
```
方向证据的设置和 Blender 调用见 [方向协议](skills/jewelry-design/references/orientation.md)。
本次建立工作流，不自动创建男款戒指设计，也不把鸢尾花作为所有后续项目的固定元素。
