"""把作业1的结构化故事转换为角色一致的绘本配图提示词。"""

from __future__ import annotations

from typing import Any


CHARACTER_LOCK = (
    "小雨是7岁中国女孩，黑色齐下巴短发，左侧恰好两枚金色月牙发夹；"
    "穿黄色连帽雨衣、白袜和红色雨靴，斜挎青绿色小包，包面有橙色剑龙图案。"
    "每幅图必须保持年龄、脸型、发型、发夹数量、服装颜色和挎包图案一致。"
)

STYLE_LOCK = (
    "横版3:2儿童绘本插画，柔和水彩、水粉与彩铅质感，温暖的编辑插画风格，"
    "人物比例自然，月光森林色调统一，为中文正文保留安静留白；"
    "画面中不要出现文字、水印、恐怖元素或多余人物。"
)


def build_prompt_manifest(story: dict[str, Any]) -> dict[str, Any]:
    """根据作业1 JSON 创建可复现的角色设定与分镜提示词清单。"""

    scenes = story.get("scenes", [])
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("story.scenes 必须是非空列表")

    scene_prompts: list[dict[str, Any]] = []
    for scene in scenes:
        if not isinstance(scene, dict):
            raise ValueError("每个 scene 必须是对象")
        scene_id = scene.get("scene_id")
        visual_prompt = str(scene.get("visual_prompt", "")).strip()
        mood = str(scene.get("mood", "")).strip()
        if not isinstance(scene_id, int) or scene_id < 1 or not visual_prompt:
            raise ValueError("scene 需要有效的 scene_id 和 visual_prompt")

        scene_prompts.append(
            {
                "scene_id": scene_id,
                "output_file": f"scene-{scene_id:02d}.png",
                "reference_image": "xiaoyu-character-sheet.png",
                "prompt": (
                    f"{CHARACTER_LOCK} 场景内容：{visual_prompt}。"
                    f"情绪：{mood}。{STYLE_LOCK}"
                ),
                "negative_constraints": [
                    "改变主角发型或服装",
                    "增加或减少月牙发夹",
                    "丢失恐龙挎包",
                    "画面文字或水印",
                    "真实恐龙或怪兽",
                ],
            }
        )

    return {
        "story_title": story.get("title", "未命名故事"),
        "method": "角色设定图作为每个场景的参考图，并复用同一角色锁定词与风格锁定词",
        "character_lock": CHARACTER_LOCK,
        "style_lock": STYLE_LOCK,
        "scenes": scene_prompts,
    }
