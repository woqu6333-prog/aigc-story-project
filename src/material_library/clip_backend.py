"""可选的真实 OpenCLIP 图文向量后端。

默认演示不下载大模型。安装 torch 与 open_clip_torch 后，可由后续脚本调用本类把
图片和查询编码到同一向量空间。导入模块本身不会下载模型。
"""

from __future__ import annotations

from pathlib import Path


class ClipUnavailableError(RuntimeError):
    """本机未安装真实CLIP运行依赖。"""


class OpenClipBackend:
    def __init__(self, model_name: str = "ViT-B-32", pretrained: str = "laion2b_s34b_b79k") -> None:
        try:
            import open_clip  # type: ignore[import-not-found]
            import torch  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ClipUnavailableError(
                "真实CLIP需要另行安装torch和open_clip_torch；当前可继续使用零下载降级后端。"
            ) from exc
        self.torch = torch
        self.open_clip = open_clip
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, pretrained=pretrained, device=self.device
        )
        self.tokenizer = open_clip.get_tokenizer(model_name)

    def encode_text(self, text: str) -> list[float]:
        with self.torch.inference_mode():
            tokens = self.tokenizer([text]).to(self.device)
            vector = self.model.encode_text(tokens)
            vector = vector / vector.norm(dim=-1, keepdim=True)
        return vector[0].cpu().tolist()

    def encode_image(self, path: Path) -> list[float]:
        from PIL import Image

        image = self.preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(self.device)
        with self.torch.inference_mode():
            vector = self.model.encode_image(image)
            vector = vector / vector.norm(dim=-1, keepdim=True)
        return vector[0].cpu().tolist()
