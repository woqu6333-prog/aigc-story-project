# 作业1：结构化故事生成器

## 作业目标

使用 Python 直接调用 OpenAI 兼容大模型接口，根据主角、年龄、兴趣、场景、主题和篇幅生成符合课程结构的 JSON 儿童故事。

## 已实现功能

- `zero_shot`：零样本Prompt
- `few_shot`：带一个完整示例的少样本Prompt
- `role_constraints`：角色设定与详细约束Prompt
- Pydantic严格校验字段、类型、场景数量和连续编号
- 自动去除Markdown代码块并提取JSON
- JSON或字段校验失败时自动要求模型修复
- 兼容自定义 `base_url` 和模型名称
- 可选择是否启用服务商的JSON模式
- 自动保存故事JSON
- 三种Prompt使用同一输入批量对比并输出CSV指标

## 安装

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

然后编辑 `.env`，填写所选服务商的 `LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL`。

## 不调用API预览Prompt

```powershell
python scripts\generate_story.py `
  --name 小雨 `
  --age 7 `
  --interest 恐龙 `
  --setting 月光森林 `
  --theme 勇气 `
  --length 短篇 `
  --target-age 7 `
  --strategy role_constraints `
  --dry-run
```

## 生成故事

删除上面命令末尾的 `--dry-run` 即可调用真实API。结果默认保存到 `outputs/stories/`。

## 运行三种Prompt对比

```powershell
python scripts\compare_prompts.py `
  --name 小雨 `
  --age 7 `
  --interest 恐龙 `
  --setting 月光森林 `
  --theme 勇气 `
  --length 短篇 `
  --target-age 7
```

每种策略会生成一份 JSON，并产生 `automatic-metrics.csv`。内容质量仍需按照 [`prompt-comparison.md`](prompt-comparison.md) 人工打分。

## 安全说明

- 真实API密钥只写入本地 `.env`。
- `.env` 不会提交到GitHub。
- 截图、日志和演示视频中不得出现密钥。
- 如怀疑密钥泄露，应立即在服务商后台撤销并重新创建。
