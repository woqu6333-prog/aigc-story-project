# 作业3：多角色儿童故事有声书

## 作业成果

本作业把作业1/2的《小雨和月光脚印》扩写为多角色配音脚本，使用4种中文音色生成完整 MP3，并制作了能够逐句同步高亮、点击跳转的有声书网页。

| 指标 | 实际成果 |
| --- | --- |
| 成品时长 | 8分57秒（课程要求不少于3分钟） |
| 角色数量 | 4个：旁白、小雨、月光知更鸟、蓝蓝 |
| 不同音色 | 4种 Edge TTS 中文神经网络音色 |
| 情感类型 | 9种：平静、温柔、好奇、低语、紧张、思考、兴奋、坚定、安心 |
| 同步文本 | 30段时间轴，播放自动高亮，点击台词可跳转 |
| 背景音效 | 本版未加入，避免遮挡对白；该项在课程要求中为可选 |

主要交付物：

- `outputs/audio/homework3/audiobook.mp3`：最终有声书；
- `outputs/audio/homework3/timeline.json`：网页同步时间轴；
- `outputs/stories/homework3-audiobook-script.json`：角色、情感和台词脚本；
- `src/audiobook/`：音频生成与拼接代码；
- `src/audiobook_web/`：同步有声书网页源码；
- `docs/homework3/voice-map.md`：音色映射与情感参数说明。

## 直接查看

先在项目根目录构建并启动：

```powershell
.\.venv\Scripts\python.exe scripts\build_static.py
.\.venv\Scripts\python.exe scripts\run_app.py --no-build
```

打开：

```text
http://127.0.0.1:8000/audiobook/
```

点击播放器开始后，右侧正文会自动跟随声音高亮。点击任意一句台词，可以从该句的时间点开始播放。

## 从脚本重新生成音频

首次安装依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

生成或重新拼接：

```powershell
.\.venv\Scripts\python.exe scripts\generate_audiobook.py
```

程序会缓存30个角色分段。未加 `--force` 时会复用缓存，只重新拼接；修改了台词并希望重新请求 TTS 时执行：

```powershell
.\.venv\Scripts\python.exe scripts\generate_audiobook.py --force
```

注意：Edge TTS 需要联网。分段缓存生成后，后续拼接与网页播放均可离线进行。

## 技术流程

```text
作业1/2故事
  → 扩写为30段角色脚本
  → 校验至少3个角色和3种音色
  → 情感标签换算为语速 / 音高 / 音量调整
  → Edge TTS逐段生成MP3并缓存
  → FFmpeg统一为24kHz单声道WAV
  → lameenc编码为128kbps MP3
  → 生成JSON时间轴
  → 网页播放器按currentTime同步高亮
```

先转成统一 WAV 再编码，是为了消除多个 MP3 直接拼接产生的时间戳和编码延迟误差。最终音频通过 FFmpeg 完整解码检查，时间轴最后一句与成品末尾只相差结尾停顿约1.25秒。

## 课程要求对照

| 课程要求 | 完成情况 |
| --- | --- |
| 至少3个角色、使用不同音色 | 已完成，4个角色、4种音色 |
| 台词带情感标注 | 已完成，脚本每段都有情感字段 |
| 情感与声音匹配 | 已按情感调整语速、音高和音量；提交前仍需学生试听复核 |
| 总时长不少于3分钟 | 已完成，8分57秒 |
| 输出MP3 | 已完成 |
| 音色映射表 | 已完成，见 `voice-map.md` |
| 同步高亮网页（可选） | 已完成 |
| 背景音效（可选） | 暂不加入，优先保证对白清晰 |

## 提交前人工检查

1. 从头听一遍，确认人物姓名读音和停顿自然；
2. 检查“小雨”和“蓝蓝”的声线是否足够区分；
3. 在电脑和手机宽度各打开一次同步网页；
4. 录制演示时展示音色表、脚本情感标签、播放器自动高亮和代码结构；
5. 把本人实际试听后的评价和修改继续写入 AI 协作日志。
