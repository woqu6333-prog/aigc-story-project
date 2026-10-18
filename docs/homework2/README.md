# 作业2：角色一致的儿童故事绘本

## 作业成果

本作业把作业1的结构化故事 JSON 转换为三幅场景插画，并排版成支持翻页、键盘操作和打印导出 PDF 的网页绘本。

- 绘本标题：《小雨和月光脚印》
- 场景数量：3，每个场景至少1张配图
- 一致性方案：角色设定图 + 固定角色描述 + 每幕复用参考图 + 固定画风
- 网页地址：部署后访问 `/picturebook/`
- 故事输入：`outputs/stories/homework2-demo-story.json`
- 图片输出：`outputs/images/homework2/`
- 配图提示词：`outputs/prompts/homework2-illustration-prompts.json`

> 当前未配置真实文本 API，因此本次使用经过作业1数据模型校验的示例故事作为演示输入，不把它冒充为云端模型实测结果。接入 API 后可直接替换同结构 JSON。

## 怎么运行

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe scripts\prepare_illustration_prompts.py
.\.venv\Scripts\python.exe scripts\build_static.py
.\.venv\Scripts\python.exe -m http.server 8000 -d dist
```

浏览器打开：

```text
http://localhost:8000/picturebook/
```

操作方法：

- 点击“上一页 / 下一页”翻页；
- 键盘方向键也能翻页；
- 点击圆点可跳转到任意页面；
- 点击“打印 / 导出 PDF”，在浏览器打印窗口选择“另存为 PDF”。

## 从作业1到作业2的数据流

```text
作业1故事 JSON
  → Pydantic 校验
  → 提取 characters / scenes / visual_prompt
  → 固定角色锁定词和绘画风格
  → 生成角色设定图
  → 每幕引用同一设定图生成场景插画
  → 网页绘本排版
  → 浏览器导出 PDF
```

## 角色一致性方法

角色设定固定为：7岁中国女孩、黑色齐下巴短发、左侧两枚金色月牙发夹、黄色连帽雨衣、青绿色恐龙挎包、白袜、红雨靴。

每张图同时使用三层约束：

1. **视觉参考**：先生成多视角角色设定图，三幅场景都引用同一张设定图。
2. **文字锁定**：每个 Prompt 重复完整外貌，不使用“小雨同上”等模糊表达。
3. **风格锁定**：统一横版3:2、水彩/水粉/彩铅质感、月光森林色调和儿童绘本比例。

网页最后一页把设定图和三幅成图放在同一屏幕中，作为一致性对比图。详细分析见 [`character-consistency.md`](character-consistency.md)。

## 代码位置

| 文件 | 用途 |
| --- | --- |
| `src/illustration/prompt_builder.py` | 从故事场景创建带角色锁定词的提示词 |
| `scripts/prepare_illustration_prompts.py` | 校验故事 JSON 并输出提示词清单 |
| `src/picturebook/` | 网页绘本 HTML、CSS、JavaScript 源码 |
| `scripts/build_static.py` | 将主页、绘本和图片同步到 `dist/` |
| `tests/test_homework2.py` | 检查故事、图片、提示词与绘本完整性 |

## 重新替换故事的方法

1. 使用作业1生成新的 JSON，保证字段结构不变。
2. 运行 `prepare_illustration_prompts.py` 得到每幕 Prompt。
3. 先生成角色设定图，再把它作为所有场景图的参考图。
4. 把图片依次命名为 `scene-01.png`、`scene-02.png`……放到 `outputs/images/homework2/`。
5. 修改绘本正文后重新运行 `build_static.py`。

## 说明

本作业没有使用 MiniMax H3 视频模型。作业2只需要静态配图，用图像生成方式更快、更符合任务，也便于后续作业3配音和作业4剪辑复用。
