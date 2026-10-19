"""三种课程要求的Prompt策略。"""

from __future__ import annotations

import json
from enum import StrEnum
from typing import Any

from .models import StoryRequest


class PromptStrategy(StrEnum):
    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot"
    ROLE_CONSTRAINTS = "role_constraints"


SCHEMA_DESCRIPTION = """{
  "title": "故事标题",
  "characters": [
    {"name": "角色名", "traits": "性格特征", "appearance": "外貌描述"}
  ],
  "scenes": [
    {
      "scene_id": 1,
      "description": "当前场景的画面概述",
      "text": "该场景完整故事正文",
      "mood": "情绪基调",
      "visual_prompt": "适合文生图的中文画面Prompt"
    }
  ],
  "moral": "从情节自然得出的故事寓意"
}"""


FEW_SHOT_EXAMPLE = {
    "title": "乐乐和会记路的画笔",
    "characters": [
        {
            "name": "乐乐",
            "traits": "细心、愿意帮助别人",
            "appearance": "7岁女孩，黑色短发，黄色外套，背着画本",
        },
        {
            "name": "团团",
            "traits": "热情但容易着急",
            "appearance": "戴绿色围巾的棕色小熊",
        },
    ],
    "scenes": [
        {
            "scene_id": 1,
            "description": "乐乐在森林入口遇到迷路的小熊",
            "text": "喜欢画画的乐乐在森林入口写生时，遇见了找不到回家方向的小熊团团。",
            "mood": "好奇",
            "visual_prompt": "儿童绘本，森林入口，7岁黑色短发女孩拿着画本，戴绿色围巾的棕色小熊，温暖柔和色彩",
        },
        {
            "scene_id": 2,
            "description": "乐乐通过画画记录沿途标志",
            "text": "乐乐没有随便选择小路，而是把蘑菇、石桥和弯曲的大树依次画进地图。团团也认真补上自己记得的蓝色屋顶。",
            "mood": "专注",
            "visual_prompt": "儿童绘本，女孩和小熊蹲在林间观察手绘地图，旁边有蘑菇和石桥，画面清晰明亮",
        },
        {
            "scene_id": 3,
            "description": "两人根据地图找到小熊的家",
            "text": "他们把线索一一连起来，终于在溪流后找到了蓝色屋顶。团团明白了，遇到困难时先观察再合作，比着急乱跑更有用。",
            "mood": "喜悦",
            "visual_prompt": "儿童绘本，女孩和小熊在蓝色屋顶木屋前欢笑，夕阳森林，温馨结局",
        },
    ],
    "moral": "认真观察并与朋友合作，能帮助我们找到解决问题的方向。",
}


def request_as_text(request: StoryRequest) -> str:
    length_rules = {
        "短篇": "3个场景，每个场景约80至120字",
        "中篇": "4至5个场景，每个场景约120至180字",
        "长篇": "6至8个场景，每个场景约160至240字",
    }
    return "\n".join(
        [
            f"主角名字：{request.hero_name}",
            f"主角年龄：{request.hero_age}岁",
            f"主角兴趣：{request.interest}",
            f"故事场景：{request.setting}",
            f"故事主题：{request.theme}",
            f"篇幅：{request.story_length}（{length_rules[request.story_length]}）",
            f"目标读者：{request.target_age}岁儿童",
        ]
    )


def build_messages(strategy: PromptStrategy, request: StoryRequest) -> list[dict[str, str]]:
    builders = {
        PromptStrategy.ZERO_SHOT: _zero_shot,
        PromptStrategy.FEW_SHOT: _few_shot,
        PromptStrategy.ROLE_CONSTRAINTS: _role_constraints,
    }
    return builders[strategy](request)


def _zero_shot(request: StoryRequest) -> list[dict[str, str]]:
    return [
        {
            "role": "user",
            "content": (
                "请根据以下信息创作一个儿童故事，并严格输出合法JSON，不要输出Markdown代码块或其他解释。\n\n"
                f"{request_as_text(request)}\n\n输出JSON结构：\n{SCHEMA_DESCRIPTION}"
            ),
        }
    ]


def _few_shot(request: StoryRequest) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "你负责生成结构清楚、适合儿童阅读的故事JSON。只输出合法JSON。",
        },
        {
            "role": "user",
            "content": "下面是一份合格示例，请学习其结构、因果关系以及兴趣参与剧情的方式。",
        },
        {
            "role": "assistant",
            "content": json.dumps(FEW_SHOT_EXAMPLE, ensure_ascii=False),
        },
        {
            "role": "user",
            "content": (
                "现在根据以下新信息生成故事。不得照抄示例情节。只输出合法JSON。\n\n"
                f"{request_as_text(request)}\n\n输出JSON结构：\n{SCHEMA_DESCRIPTION}"
            ),
        },
    ]


def _role_constraints(request: StoryRequest) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是一名专业儿童文学作家和绘本分镜设计师。你的任务是写出安全、温暖、"
                "因果连贯且符合目标年龄理解能力的原创故事，并只输出合法JSON。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"请根据以下创作卡片生成结构化故事：\n{request_as_text(request)}\n\n"
                "创作约束：\n"
                "1. 先在内部确定起因、困难、尝试、解决和成长，再输出最终JSON，不展示思考过程。\n"
                "2. 主角的兴趣必须在关键场景中帮助观察、沟通或解决问题，不能只机械重复兴趣名称。\n"
                "3. 场景之间必须存在明确因果关系，不得突然增加关键人物、道具或能力。\n"
                "4. characters中必须包含主角，主角姓名在全文保持一致。\n"
                "5. scene_id必须从1开始连续递增。\n"
                "6. visual_prompt必须复述角色稳定外貌、环境、动作、画风和构图，不能使用代词指代主角。\n"
                "7. 避免暴力、恐怖、歧视、危险模仿和成人化内容。\n"
                "8. 寓意必须从故事情节自然得出，避免空洞说教。\n"
                "9. 正文要有可感知的动作、环境细节和自然对话，长短句交替；避免连续使用“然后、于是、最后”串联事件。\n"
                "10. 不要把人物设定逐项复述成说明书，不要在每个场景重复讲道理；通过选择、行动和结果表现成长。\n"
                "11. 每个场景都要推进情节：承接上一幕留下的线索，并为下一幕提供新的原因或目标。\n"
                "12. 严格按照下方结构输出JSON，不要Markdown代码块、注释或额外文字。\n\n"
                f"输出JSON结构：\n{SCHEMA_DESCRIPTION}"
            ),
        },
    ]


def build_polish_messages(
    request: StoryRequest, story: dict[str, Any]
) -> list[dict[str, str]]:
    """创建第二遍文学润色消息，保持结构和剧情事实不变。"""

    return [
        {
            "role": "system",
            "content": (
                "你是一名严谨的儿童文学编辑。请在不改变故事核心事件、人物关系、"
                "场景数量和JSON结构的前提下，让文字更自然、更有画面感。只输出合法JSON。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"读者与创作要求：\n{request_as_text(request)}\n\n"
                "润色规则：\n"
                "1. 保留title、characters、scenes、moral字段和所有scene_id。\n"
                "2. 保留原故事的线索、解决办法和结局，不添加突然出现的关键能力或道具。\n"
                "3. 把抽象说明改成动作、感官细节或简短自然的对话。\n"
                "4. 删除机械重复、口号式说教和过多的连接词。\n"
                "5. 主角兴趣仍必须真正帮助解决问题。\n"
                "6. visual_prompt同步反映润色后的场景，但保持人物外貌一致。\n"
                "7. 字数仍符合原定篇幅和目标年龄。\n"
                "8. 只输出完整合法JSON，不要解释修改过程。\n\n"
                f"待润色故事：\n{json.dumps(story, ensure_ascii=False)}\n\n"
                f"输出JSON结构：\n{SCHEMA_DESCRIPTION}"
            ),
        },
    ]


def build_repair_messages(
    original_messages: list[dict[str, str]], raw_response: str, error: str
) -> list[dict[str, str]]:
    repair_instruction = (
        "上一次输出未通过程序校验。请根据错误说明修复内容，并重新输出完整合法JSON。"
        "不要解释修改过程，不要输出Markdown。\n\n"
        f"校验错误：{error}\n\n"
        f"上一次输出：\n{raw_response}"
    )
    return [*original_messages, {"role": "assistant", "content": raw_response}, {"role": "user", "content": repair_instruction}]
