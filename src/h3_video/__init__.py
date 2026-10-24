"""MiniMax H3本地ComfyUI视频生成适配器。"""

from .client import ComfyUIClient
from .prompt import build_ref2va_prompt
from .workflow import build_h3_api_workflow, convert_ui_workflow

__all__ = ["ComfyUIClient", "build_ref2va_prompt", "build_h3_api_workflow", "convert_ui_workflow"]
