# MiniMax H3 真实动态镜头验证

## 目标

解决早期视频只是静态图片平移、缩放的问题。使用作业2角色设定图和第一幕场景图，通过本地 ComfyUI 的 MiniMax H3 Ref2VA 生成角色真实动作、环境变化与原生声音。

## 已验证配置

| 参数 | 值 |
| --- | --- |
| 模式 | Ref2VA（角色图 + 场景首帧） |
| 显卡 | RTX 4060 Laptop 8GB |
| 时长 | 5秒 |
| 帧率 | 24fps |
| 预览分辨率 | 0.2MP，约608×352 |
| LoRA | Turbo 4步 |
| 调度器 | `simple` |
| 实测耗时 | 约100秒 |

第一次实验把Turbo 4步与 `normal` 调度器组合，结果出现严重方块和马赛克，判定不可用。改成 `simple` 调度器后，人物脸部、黄色雨衣、恐龙挎包、红雨靴和月光森林均保持稳定，动作与水滴、萤火虫等环境运动正常。

## 代码结构

- `src/h3_video/prompt.py`：生成Ref2VA要求的六段英文提示词。
- `src/h3_video/workflow.py`：把ComfyUI界面工作流转换为API格式并注入参数。
- `src/h3_video/client.py`：上传参考图、排队、轮询和下载视频。
- `scripts/generate_h3_clip.py`：命令行生成单镜头。
- `scripts/run_app.py`：提供网页异步任务接口。
- `src/motion_web/`：播放缓存样片并现场生成新镜头。

## 运行

先启动已经安装好H3节点和模型的ComfyUI，确保监听 `127.0.0.1:8188`，再运行：

```powershell
.\.venv\Scripts\python.exe scripts\run_app.py
```

打开 `http://127.0.0.1:8000/motion/`。如果页面显示“H3已就绪”，可点击按钮生成5秒镜头。

也可以命令行运行：

```powershell
.\.venv\Scripts\python.exe scripts\generate_h3_clip.py `
  --duration 5 `
  --quality fast `
  --output outputs\video\h3\my-shot.mp4
```

## 答辩策略

- 先播放仓库中的已验证样片，保证展示不受现场等待影响。
- 再点击生成一个5秒镜头，展示网页、Python后端与ComfyUI的真实连接。
- 等待期间讲解参考图一致性、六段Prompt、工作流转换和失败调参过程。
- 60秒完整H3成片需要多个镜头，预计耗时约20分钟以上，应提前生成并缓存，不在现场从零开始。
