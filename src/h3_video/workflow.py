"""把ComfyUI界面工作流转换为API工作流，并注入H3镜头参数。"""

from __future__ import annotations

import copy
from typing import Any


NON_EXECUTABLE_TYPES = {"MarkdownNote", "Note", "Reroute"}


def convert_ui_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    """转换LiteGraph保存格式为ComfyUI `/prompt` 所需格式。"""
    links = {int(link[0]): link for link in workflow.get("links", [])}
    api: dict[str, Any] = {}
    for node in workflow.get("nodes", []):
        node_type = str(node.get("type", ""))
        if node_type in NON_EXECUTABLE_TYPES or int(node.get("mode", 0)) == 2:
            continue
        inputs: dict[str, Any] = {}
        widget_values = list(node.get("widgets_values") or [])
        widget_index = 0
        for input_spec in node.get("inputs", []):
            widget = input_spec.get("widget")
            widget_value = None
            if widget is not None and widget_index < len(widget_values):
                widget_value = widget_values[widget_index]
                widget_index += 1
            link_id = input_spec.get("link")
            if link_id is not None:
                link = links[int(link_id)]
                inputs[str(input_spec["name"])] = [str(link[1]), int(link[2])]
            elif widget is not None:
                inputs[str(input_spec["name"])] = widget_value
        api[str(node["id"])] = {
            "class_type": node_type,
            "inputs": inputs,
            "_meta": {"title": node.get("title") or node_type},
        }
    return api


def build_h3_api_workflow(
    workflow: dict[str, Any],
    *,
    prompt: str,
    character_image: str,
    scene_image: str,
    duration: int = 5,
    megapixels: float = 0.2,
    seed: int = 20261024,
    filename_prefix: str = "video/Story_H3",
    quality: str = "fast",
) -> dict[str, Any]:
    if duration < 4 or duration > 15:
        raise ValueError("H3单镜头时长必须在4到15秒之间")
    if megapixels < 0.2 or megapixels > 0.98:
        raise ValueError("测试分辨率应在0.2到0.98百万像素之间")
    if quality not in {"fast", "full"}:
        raise ValueError("quality必须是fast或full")
    api = convert_ui_workflow(copy.deepcopy(workflow))
    required = {"92", "115", "124", "129", "132", "136", "138", "146", "157", "158"}
    missing = sorted(required - set(api))
    if missing:
        raise ValueError(f"H3工作流缺少关键节点：{', '.join(missing)}")

    api["138"]["inputs"]["value"] = prompt
    api["132"]["inputs"]["value"] = float(duration)
    api["115"]["inputs"].update({"aspect_ratio": "16:9 (Widescreen)", "megapixels": float(megapixels), "multiple": 32})
    api["146"]["inputs"]["value"] = quality == "fast"
    api["124"]["inputs"]["scheduler"] = "simple" if quality == "fast" else "normal"
    api["129"]["inputs"]["noise_seed"] = int(seed)
    api["157"]["inputs"]["image"] = character_image
    api["158"]["inputs"]["image"] = scene_image
    api["92"]["inputs"]["filename_prefix"] = filename_prefix

    # 测试镜头只使用两个明确的参考源，避免无关示例图污染生成。
    for node_id in ("160", "161"):
        api.pop(node_id, None)
    api["136"]["inputs"].pop("ref_images.ref_image_2", None)
    api["136"]["inputs"].pop("ref_images.ref_image_3", None)
    api["136"]["inputs"]["ref_image_size"] = "match"
    return api
