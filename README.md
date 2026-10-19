# 星光故事屋

《AIGC应用开发实践》课程主线项目。当前版本已完成作业0网页、作业1结构化故事生成器代码，以及作业2角色一致的网页绘本。

用户填写主角姓名、年龄、兴趣、场景和主题。网页既可使用零成本离线演示，也可通过本地Python后端安全调用作业1大模型API，并继续查看作业2绘本成果。

## 在线体验

- 作业0故事网页：<https://woqu6333-prog.github.io/aigc-story-project/>
- 作业2网页绘本：<https://woqu6333-prog.github.io/aigc-story-project/picturebook/>

## 当前功能

- 支持主角姓名、年龄、兴趣、故事场景和主题
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

### 方法三：本地API网站运行（推荐）

先根据 `.env.example` 配置本地 `.env`，再执行：

```powershell
.\.venv\Scripts\python.exe scripts\run_app.py
```

打开 `http://127.0.0.1:8000`。页面显示绿色“真实API模式”后，故事生成和“AI润色”会调用作业1代码；如果没有配置API，网站会自动保留离线演示功能。

## 使用方法

1. 输入主角名字，例如“小雨”。
2. 输入3～12岁的整数年龄。
3. 输入一种兴趣，例如“恐龙”或“画画”。
4. 选择一个故事主题。
5. 点击“生成结构化故事”。
6. API模式下可以点击“AI润色”进行第二次文学编辑。
7. 确认故事后点击“打开网页绘本”，查看作业2成果。

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
├─ dist/                     # 可直接运行和提交演示的静态网站
├─ scripts/
│  ├─ build_static.py        # 构建主页与网页绘本
│  ├─ prepare_illustration_prompts.py
│  └─ run_app.py             # 统一网站与作业1本地API后端
├─ tests/
│  ├─ test_homework0.py
│  ├─ test_integrated_app.py
│  ├─ test_story_generator.py
│  └─ test_homework2.py
├─ docs/homework0/
│  ├─ ai-log.md
│  ├─ demo-script.md
│  └─ test-report.md
├─ docs/homework1/           # 作业1说明、Prompt对比和AI日志
├─ docs/homework2/           # 作业2说明、一致性报告和AI日志
├─ outputs/                  # 故事JSON、配图和提示词成果
├─ requirements.txt
└─ README.md
```

修改 `src/web/` 后，执行以下命令重新生成 `dist/`：

```bash
python scripts/build_static.py
```

## 运行测试

本项目测试只使用 Python 标准库：

```bash
python -m unittest discover -s tests -p "test_*.py" -v
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

作业1具体运行和查看方法见 [`docs/homework1/README.md`](docs/homework1/README.md)，作业2见 [`docs/homework2/README.md`](docs/homework2/README.md)。

## 后续计划

- 作业0–2：已整合为“创意输入 → 结构化故事 → 绘本成果”的统一网站
- 作业1：三种Prompt、结构校验、自动修复和可选二次润色已完成；待配置免费云API产生真实实验数据
- 作业2：角色设定、三幕配图、网页绘本、方案文档与测试已完成，后续接入动态配图服务
- 作业3：生成多角色有声书
- 作业4：通过图片、音频、字幕自动剪辑故事视频
- 作业5：建立多模态故事素材检索系统
- 作业6：使用 Agent 框架编排完整创作流程
