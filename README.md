# 星光故事屋

《AIGC应用开发实践》课程主线项目。当前版本已完成第1–8周范围：作业0网页、作业1结构化故事生成器、作业2角色一致绘本、作业3多角色有声书、作业4短视频、作业5多模态素材检索、作业6可干预故事Agent，以及第8周答辩资料。

用户填写主角姓名、年龄、兴趣、场景和主题。网页既可使用零成本离线演示，也可通过本地Python后端安全调用作业1大模型API，并继续查看作业2绘本、作业3有声书和作业4短视频成果。

## 在线体验

- 作业0故事网页：<https://woqu6333-prog.github.io/aigc-story-project/>
- 作业2网页绘本：<https://woqu6333-prog.github.io/aigc-story-project/picturebook/>
- 作业3同步有声书：<https://woqu6333-prog.github.io/aigc-story-project/audiobook/>
- 作业4故事短视频：<https://woqu6333-prog.github.io/aigc-story-project/video/>
- 作业5多模态素材库：<https://woqu6333-prog.github.io/aigc-story-project/library/>
- 作业6故事Agent：<https://woqu6333-prog.github.io/aigc-story-project/agent/>
- H3真实动态镜头：<https://woqu6333-prog.github.io/aigc-story-project/motion/>

## 当前功能

- 支持主角姓名、年龄、兴趣、故事场景、主题和自由剧情设想
- 支持浏览器语音识别，把口述剧情直接填入创作卡片
- 支持“勇气冒险”“友谊成长”“自然守护”三种主题
- 不同主题具有不同故事内容和视觉配色
- 对空输入和年龄范围进行校验
- 自动识别真实API模式和离线演示模式
- 支持重新生成、复制故事、下载 TXT/JSON
- 支持可选的第二次AI文学润色，并在润色后重新校验JSON
- 自动保存最近一次输入和故事
- 支持电脑和手机尺寸
- 离线模式不上传用户信息、不产生API费用
- API密钥仅由本地Python读取，不进入浏览器和GitHub
- 作业1支持三种 Prompt 策略、严格 JSON 校验和自动修复
- 作业2包含角色设定图、三幅一致性场景图和六页交互绘本
- 绘本支持按钮、方向键翻页以及浏览器打印为 PDF
- 作业3包含4种角色音色、30段情感台词和8分57秒MP3
- 有声书支持逐句同步高亮、自动跟随和点击台词跳转
- 作业4自动复用绘本、配音和时间轴，生成2分18秒故事短视频
- 视频包含动态推拉画面、原创背景音乐、41段烧录字幕和H.264/AAC编码
- 作业5包含10个模板、12个人物、12个场景、20张图和5段音效
- 支持自然语言向量检索、分类筛选、音效试听与结构化创作建议
- 作业6使用LangChain Core注册5个工具并支持中途修改人物或场景
- 已生成2套完整Agent案例，每套含故事、3张图、MP3、MP4和工具日志
- MiniMax H3 Ref2VA 已完成真实动态镜头验证；本机网页可排队生成5秒新镜头

## 快速运行

### 方法一：直接打开

进入 `dist/` 目录，双击 `index.html`；绘本建议使用下方本地服务器方式打开。

### 方法二：静态服务器运行（离线演示）

在项目根目录执行：

```bash
python -m http.server 8000 -d dist
```

然后访问：

```text
http://localhost:8000
```

作业2绘本地址：

```text
http://localhost:8000/picturebook/
```

作业3有声书地址：

```text
http://localhost:8000/audiobook/
```

作业4视频地址：

```text
http://localhost:8000/video/
```

作业5与作业6：

```text
http://localhost:8000/library/
http://localhost:8000/agent/
http://localhost:8000/motion/
```

### 方法三：本地API网站运行（推荐）

推荐在 [Google AI Studio](https://aistudio.google.com/) 创建 Gemini API 密钥。本项目兼容 [Gemini官方OpenAI兼容端点](https://ai.google.dev/gemini-api/docs/openai/)，只需在本地 `.env` 填一行（不要把真实值提交到GitHub）：

```dotenv
GEMINI_API_KEY=你的密钥
```

也可以根据 `.env.example` 配置其他 OpenAI 兼容服务。然后执行：

```powershell
.\.venv\Scripts\python.exe scripts\run_app.py
```

打开 `http://127.0.0.1:8000`。页面显示绿色“真实API模式”后，故事生成和“AI润色”会调用作业1代码；如果没有配置API，网站会自动保留离线演示功能。

## 使用方法

1. 输入主角名字，例如“小雨”。
2. 输入3～12岁的整数年龄。
3. 输入一种兴趣，例如“恐龙”或“画画”。
4. 输入或点击“说出剧情”口述完整设想。
5. 选择一个故事主题并点击“生成结构化故事”。
6. API模式下可以点击“AI润色”进行第二次文学编辑。
7. 确认故事后点击“打开网页绘本”，查看作业2成果。
8. 点击“播放有声书”，查看作业3多角色配音与同步文本。
9. 点击“播放故事视频”，查看作业4自动剪辑成果。
10. 打开“素材库”，输入自然语言创意并筛选多模态素材。
11. 打开“Agent”，查看计划、中途干预和两套完整案例。
12. 打开“AI动态镜头”，播放H3样片；ComfyUI在线时可现场生成一个5秒镜头。

## 项目结构

```text
aigc_story_project/
├─ src/web/                  # 作业0网站源码（唯一编辑位置）
│  ├─ index.html
│  └─ assets/
│     ├─ style.css
│     └─ app.js
├─ src/illustration/         # 作业2角色一致性提示词生成
├─ src/picturebook/          # 作业2网页绘本源码
├─ src/audiobook/            # 作业3音频生成和时间轴逻辑
├─ src/audiobook_web/        # 作业3同步有声书网页
├─ src/story_video/           # 作业4自动剪辑、字幕与音乐生成
├─ src/video_web/             # 作业4视频展示网页
├─ src/material_library/      # 作业5素材、向量检索与可选OpenCLIP后端
├─ src/library_web/           # 作业5检索网页
├─ src/story_agent/           # 作业6 LangChain工具与Agent状态机
├─ src/agent_web/             # 作业6交互展示网页
├─ src/h3_video/              # H3提示词、工作流转换与ComfyUI客户端
├─ src/motion_web/            # 真实动态镜头展示与现场生成网页
├─ dist/                     # 可直接运行和提交演示的静态网站
├─ scripts/
│  ├─ build_static.py        # 构建主页、网页绘本与有声书
│  ├─ generate_audiobook.py  # 生成多角色MP3和同步时间轴
│  ├─ generate_video.py      # 生成故事短视频
│  ├─ build_material_library.py # 构建作业5素材与向量索引
│  ├─ run_agent.py           # 运行作业6完整Agent案例
│  ├─ prepare_illustration_prompts.py
│  └─ run_app.py             # 统一网站与作业1本地API后端
├─ tests/
│  ├─ test_homework0.py
│  ├─ test_integrated_app.py
│  ├─ test_story_generator.py
│  └─ test_homework2.py
│  └─ test_homework3.py
│  └─ test_homework4.py
├─ docs/homework0/
│  ├─ ai-log.md
│  ├─ demo-script.md
│  └─ test-report.md
├─ docs/homework1/           # 作业1说明、Prompt对比和AI日志
├─ docs/homework2/           # 作业2说明、一致性报告和AI日志
├─ docs/homework3/           # 作业3说明、音色映射、AI日志和讲稿
├─ docs/homework4/           # 作业4说明、流程、AI日志和讲稿
├─ docs/homework5/           # 作业5构建、评估与AI日志
├─ docs/homework6/           # 作业6架构、案例与AI日志
├─ docs/week8/               # 答辩讲稿、Q&A、检查清单与项目总结
├─ outputs/                  # 故事JSON、配图和提示词成果
├─ requirements.txt
└─ README.md
```

修改 `src/web/` 后，执行以下命令重新生成 `dist/`：

```bash
python scripts/build_static.py
```

## 运行测试

使用项目虚拟环境运行完整测试：

```bash
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

## 作业0要求对照

| 课程要求 | 实现情况 |
| --- | --- |
| 输入主角名字、年龄、兴趣、故事主题 | 已完成 |
| 输出可交互故事页面 | 已完成 |
| 至少支持3种故事主题 | 已完成，共3种 |
| 页面美观、交互友好 | 已完成响应式绘本风格界面 |
| 代码仓库和使用说明 | 已完成本地仓库与README |
| 2分钟内演示视频 | 已准备演示讲稿，录屏需学生本人完成 |

## AI协作说明

初始版本由学生提供课程目标和功能边界，Codex协助完成需求拆解、代码、测试及文档。真实协作过程记录在 [`docs/homework0/ai-log.md`](docs/homework0/ai-log.md)。

如果教师要求必须体现 Trae 的使用，应当将本仓库导入 Trae，进行本人实际完成的修改和调试，并把真实过程补充进AI协作日志；不要把未发生的操作写进日志。

作业1具体运行和查看方法见 [`docs/homework1/README.md`](docs/homework1/README.md)，后续分别见 [`docs/homework2/README.md`](docs/homework2/README.md)、[`docs/homework3/README.md`](docs/homework3/README.md)、[`docs/homework4/README.md`](docs/homework4/README.md)、[`docs/homework5/README.md`](docs/homework5/README.md) 和 [`docs/homework6/README.md`](docs/homework6/README.md)。答辩入口见 [`docs/week8/README.md`](docs/week8/README.md)。

## 当前状态与后续优化

- 作业0–4：已整合为“创意输入 → 结构化故事 → 绘本成果 → 多角色有声书 → 故事短视频”的统一网站
- 作业1：三种Prompt、自由剧情输入、因果链约束、结构校验、自动修复和可选二次润色已完成；待学生本人创建免费Gemini密钥产生真实对比数据
- 作业2：角色设定、三幕配图、网页绘本、方案文档与测试已完成，后续接入动态配图服务
- 作业3：4角色配音、情感参数、8分57秒MP3和同步高亮网页已完成
- 作业4：2分18秒短视频、原创音乐、烧录字幕、自动剪辑脚本与网页已完成
- 作业5：59条素材、自然语言向量检索、3组评估已完成；真实OpenCLIP作为可选升级，默认结果明确标记为降级后端
- 作业6：5工具、人工干预、2套完整案例和运行日志已完成；故事工具会在配置API后实时创作，未配置时明确使用因果兜底
- H3技术验证：5秒Ref2VA动态镜头约100秒完成，网页现场生成链路已实测；60秒完整片建议预生成缓存
- 第8周：8–10分钟讲稿、问答、检查清单和项目总结已完成；需要学生本人练习并按真实理解调整
