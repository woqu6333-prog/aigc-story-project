# 素材库构建记录

## 数据字段

每条素材包含：`id`、`type`、`title`、`description`、`tags`、`search_text`、`vector`，图像和声音额外包含 `asset`。

## 构建流程

```text
素材清单
  ├─ 生成20张960×640场景图
  ├─ 合成5段22050Hz单声道WAV
  ├─ 文本清洗与同义词扩展
  ├─ 拟合TF-IDF词表
  ├─ 生成L2归一化向量
  └─ 输出index.json和evaluation.json
```

构建命令：

```powershell
.\.venv\Scripts\python.exe scripts\build_material_library.py
```

程序化配图采用不同色板和可识别图形绘制火箭、机器人、森林、蓝鸟、鲸鱼、珊瑚、城堡、恐龙、企鹅与城市等场景。它们适合作为课程检索样例和构图卡，不宣称由扩散模型生成。

5段音效是本地正弦波叠加、包络处理后的原创环境氛围样例，可循环使用，无第三方版权素材。

