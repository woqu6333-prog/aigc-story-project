# 作业5：儿童故事多模态素材检索系统

## 已完成内容

- 10个故事模板、12个人物设定、12个场景描述
- 20张可直接查看的原创程序化绘本素材图
- 5段可试听的原创合成环境音（WAV）
- 自然语言查询、中文同义词扩展、TF-IDF向量与余弦相似度排序
- 同时返回模板、人物、场景、插画、音效和结构化创作建议
- 3组查询评估与浏览器交互页面
- 可选真实 OpenCLIP 后端代码；默认环境不自动下载大模型

## 查看成果

先在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe scripts\build_material_library.py
.\.venv\Scripts\python.exe scripts\build_static.py
.\.venv\Scripts\python.exe -m http.server 8000 -d dist
```

浏览器打开：

```text
http://127.0.0.1:8000/library/
```

可依次点击“太空冒险”“森林友谊”“海洋环保”三个查询，并切换“插画”“音效”等分类。

## 素材与索引位置

```text
outputs/library/homework5/
├─ index.json               # 59条素材、词表、IDF与向量
├─ evaluation.json          # 3组查询评估原始数据
└─ assets/
   ├─ images/               # 20张PNG
   └─ sounds/               # 5段WAV
```

## 关于CLIP的真实说明

课程要求图像素材使用CLIP特征检索。本项目已经在 `src/material_library/clip_backend.py` 提供真实 OpenCLIP 图文编码后端，但当前电脑的项目虚拟环境和ComfyUI独立环境都没有可直接导入的PyTorch/OpenCLIP，因此默认演示使用“人工语义标签 + 本地TF-IDF共同向量空间”的零下载后端。

这不是把降级方案冒充CLIP。网页和 `index.json` 都会显示当前后端名 `visual-semantic-fallback`。如果答辩评分必须现场展示真实CLIP，可另建带GPU依赖的环境：

```powershell
pip install torch open_clip_torch
```

第一次创建 `OpenClipBackend` 时会下载所选预训练权重；不建议在没有稳定网络的答辩现场临时下载。当前静态成果不依赖这一步，也不会产生API费用。

## 关键设计

1. 用中文字符、双字词组、完整词和同义词扩展减少中文分词依赖。
2. 所有类型进入同一TF-IDF向量空间，查询向量与素材向量计算余弦相似度。
3. 图片默认用标题和经过人工校对的视觉标签建立语义向量；真实CLIP后端可将图片像素和查询文本投影到共同空间。
4. 检索结果不是简单列表，还会生成故事结构、视觉方向和声音氛围建议。

## 课程要求对照

| 要求 | 实现 |
| --- | --- |
| 至少10个故事模板 | 10个 |
| 至少20张图片 | 20张PNG |
| 至少5个音效 | 5段3秒WAV |
| 自然语言查询 | 已完成 |
| 文本向量检索 | 本地TF-IDF + cosine |
| 图像检索 | 默认语义视觉向量；真实OpenCLIP接口已提供 |
| 素材列表与生成建议 | 已完成 |
| 至少3组评估 | 已完成 |

