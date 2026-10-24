# 作业6：交互式多模态故事Agent

## 已完成内容

- 使用 LangChain Core 的 `StructuredTool` 注册5个工具
- 规则规划器把创意拆成检索、写作、配图、配音、视频5步
- 接受“主角改成女孩”“场景换到海底”等中途干预
- 修改后清空失效的素材、故事和媒体状态，再重新执行
- 两套完整案例，每套包含JSON故事、3张图、MP3、MP4、状态快照和完整工具日志
- 网页展示计划、干预前后对比、两套案例视频

## 查看成果

```powershell
.\.venv\Scripts\python.exe scripts\build_static.py
.\.venv\Scripts\python.exe -m http.server 8000 -d dist
```

打开 `http://127.0.0.1:8000/agent/`。

## 自己运行一个新案例

```powershell
.\.venv\Scripts\python.exe scripts\run_agent.py `
  --case-id case-03-dino `
  --idea "一个男孩在恐龙谷保护最后一颗蛋" `
  --intervene "主角改成女孩，名字改成安安"
```

第一次生成旁白需要联网访问免费的 Edge TTS。视频由本地FFmpeg和显卡编码，未调用MiniMax H3，因此一分钟案例通常可在较短时间内完成。

只检查规划和干预、不生成媒体：

```powershell
.\.venv\Scripts\python.exe scripts\run_agent.py --case-id test-plan --idea "太空冒险" --intervene "场景换到海底" --plan-only
```

## 五个工具

| 工具 | 输入 | 输出 |
| --- | --- | --- |
| `retrieve_materials` | 创意、人物、场景、主题 | 作业5素材推荐 |
| `write_structured_story` | 最新状态与素材 | 三幕JSON故事 |
| `illustrate_scenes` | 故事JSON | 3张统一风格PNG |
| `synthesize_narration` | 故事JSON | 中文旁白MP3 |
| `compose_story_video` | 场景图与旁白 | H.264/AAC MP4 |

## 成果位置

```text
outputs/agent/homework6/
├─ case-01-space/       # 男孩 → 女孩小星，约58.9秒
└─ case-02-ocean/       # 月光森林 → 海底珊瑚城，约57.6秒
```

每个目录都有 `agent-state.json` 与 `workflow-log.json`，可以在答辩时证明计划、人工干预和工具调用顺序。

