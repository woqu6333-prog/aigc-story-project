"""使用 LangChain Core 工具接口编排故事、配图、配音和视频。"""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from langchain_core.tools import StructuredTool
from mutagen.mp3 import MP3

from audiobook.builder import find_ffmpeg
from material_library import MaterialLibrary
from material_library.library import _draw_scene
from story_generator.client import OpenAICompatibleClient
from story_generator.config import ConfigurationError, LLMConfig
from story_generator.models import StoryRequest
from story_generator.prompts import PromptStrategy
from story_generator.service import StoryGenerator


TOOL_NAMES = [
    "retrieve_materials",
    "write_structured_story",
    "illustrate_scenes",
    "synthesize_narration",
    "compose_story_video",
]


@dataclass
class AgentState:
    case_id: str
    idea: str
    protagonist: str = "小星"
    protagonist_profile: str = "勇敢、好奇的8岁女孩，黄色外套，蓝色小背包"
    setting: str = "星光发射台与遥远星球"
    theme: str = "勇气与友谊"
    status: str = "created"
    plan: list[dict[str, str]] = field(default_factory=list)
    materials: dict[str, Any] = field(default_factory=dict)
    story: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    workflow_log: list[dict[str, Any]] = field(default_factory=list)


class StoryCreationAgent:
    """规则规划器 + LangChain工具层，支持执行前中途修改状态。"""

    def __init__(self, project_root: Path, *, enable_cloud_story: bool = True) -> None:
        self.project_root = Path(project_root)
        self.enable_cloud_story = enable_cloud_story
        self.library_path = self.project_root / "outputs" / "library" / "homework5" / "index.json"
        if not self.library_path.exists():
            raise FileNotFoundError("请先运行 scripts/build_material_library.py")
        self.library = MaterialLibrary(self.library_path)
        self.tools = self._create_tools()

    def _create_tools(self) -> dict[str, StructuredTool]:
        functions: dict[str, tuple[Callable[..., str], str]] = {
            "retrieve_materials": (self._retrieve_materials, "根据自然语言创意检索模板、人物、场景、插画和音效。"),
            "write_structured_story": (self._write_story, "根据人物、场景和主题生成包含三幕场景与寓意的结构化JSON故事。"),
            "illustrate_scenes": (self._illustrate, "为结构化故事的每一幕生成角色一致的本地绘本图。"),
            "synthesize_narration": (self._narrate, "把故事旁白转换为可播放的中文MP3。"),
            "compose_story_video": (self._compose_video, "把场景图片和旁白自动合成为MP4故事视频。"),
        }
        return {
            name: StructuredTool.from_function(func=func, name=name, description=description)
            for name, (func, description) in functions.items()
        }

    def create_state(self, case_id: str, idea: str) -> AgentState:
        if not re.fullmatch(r"[a-z0-9-]{3,40}", case_id):
            raise ValueError("case_id只能包含小写字母、数字和短横线")
        if not idea.strip():
            raise ValueError("故事创意不能为空")
        state = AgentState(case_id=case_id, idea=idea.strip())
        if "男孩" in idea:
            state.protagonist = "阿川"
            state.protagonist_profile = "细心、勇敢的8岁男孩，绿色外套，棕色小背包"
        if "海" in idea:
            state.setting = "发光的海底珊瑚城"
            state.theme = "环保与合作"
        elif "森林" in idea:
            state.setting = "雨后的月光森林"
            state.theme = "友谊与勇气"
        elif "恐龙" in idea:
            state.setting = "长满蕨类植物的恐龙山谷"
        return state

    def plan(self, state: AgentState) -> list[dict[str, str]]:
        state.plan = [
            {"step": "1", "tool": "retrieve_materials", "purpose": "检索可复用素材"},
            {"step": "2", "tool": "write_structured_story", "purpose": "生成三幕JSON故事"},
            {"step": "3", "tool": "illustrate_scenes", "purpose": "生成一致性场景图"},
            {"step": "4", "tool": "synthesize_narration", "purpose": "生成中文旁白"},
            {"step": "5", "tool": "compose_story_video", "purpose": "合成最终MP4"},
        ]
        state.status = "planned"
        self._log(state, "planner", "completed", {"idea": state.idea}, {"steps": len(state.plan)})
        return state.plan

    def intervene(self, state: AgentState, instruction: str) -> dict[str, Any]:
        """处理中途自然语言修改，并清除会失效的下游状态。"""
        before = {"protagonist": state.protagonist, "profile": state.protagonist_profile, "setting": state.setting, "theme": state.theme}
        text = instruction.strip()
        if not text:
            raise ValueError("干预指令不能为空")
        if "女孩" in text:
            state.protagonist = "小星"
            state.protagonist_profile = "勇敢、好奇的8岁女孩，黄色外套，蓝色小背包"
        if "男孩" in text:
            state.protagonist = "阿川"
            state.protagonist_profile = "细心、勇敢的8岁男孩，绿色外套，棕色小背包"
        name_matches = re.findall(r"(?:主角(?:改成|叫)|名字(?:改成|叫))([\u4e00-\u9fff]{1,6})", text)
        chosen_names = [name for name in name_matches if name not in {"女孩", "男孩", "女生", "男生"}]
        if chosen_names:
            state.protagonist = chosen_names[-1]
        scene_map = {
            "海底": ("发光的海底珊瑚城", "环保与合作"),
            "森林": ("雨后的月光森林", "友谊与勇气"),
            "太空": ("星光发射台与遥远星球", "勇气与友谊"),
            "恐龙": ("长满蕨类植物的恐龙山谷", "勇气与守护"),
            "城堡": ("漂浮在云海上的魔法城堡", "想象与成长"),
        }
        for keyword, (setting, theme) in scene_map.items():
            if keyword in text:
                state.setting, state.theme = setting, theme
                break
        after = {"protagonist": state.protagonist, "profile": state.protagonist_profile, "setting": state.setting, "theme": state.theme}
        if before == after:
            raise ValueError("没有识别到可执行修改，可尝试“主角改成女孩，场景换到海底”")
        state.materials = {}
        state.story = {}
        state.artifacts = {}
        state.status = "intervened"
        self._log(state, "human_intervention", "completed", {"instruction": text, "before": before}, {"after": after, "invalidated": ["materials", "story", "artifacts"]})
        return after

    def run(self, state: AgentState) -> AgentState:
        if not state.plan:
            self.plan(state)
        output_dir = self.project_root / "outputs" / "agent" / "homework6" / state.case_id
        output_dir.mkdir(parents=True, exist_ok=True)
        state.status = "running"

        state.materials = self._invoke(
            state,
            "retrieve_materials",
            {"query": f"{state.idea}；主角{state.protagonist}；场景{state.setting}；主题{state.theme}"},
        )
        state.story = self._invoke(
            state,
            "write_structured_story",
            {
                "idea": state.idea,
                "protagonist": state.protagonist,
                "profile": state.protagonist_profile,
                "setting": state.setting,
                "theme": state.theme,
                "materials_json": json.dumps(state.materials, ensure_ascii=False),
            },
        )
        story_path = output_dir / "story.json"
        story_path.write_text(json.dumps(state.story, ensure_ascii=False, indent=2), encoding="utf-8")
        state.artifacts["story"] = str(story_path.relative_to(self.project_root)).replace("\\", "/")

        image_result = self._invoke(state, "illustrate_scenes", {"story_json": json.dumps(state.story, ensure_ascii=False), "output_dir": str(output_dir)})
        state.artifacts.update(image_result)
        audio_result = self._invoke(state, "synthesize_narration", {"story_json": json.dumps(state.story, ensure_ascii=False), "output_dir": str(output_dir)})
        state.artifacts.update(audio_result)
        video_result = self._invoke(
            state,
            "compose_story_video",
            {"images_json": json.dumps(state.artifacts["images"], ensure_ascii=False), "audio_path": str(self.project_root / state.artifacts["audio"]), "output_dir": str(output_dir)},
        )
        state.artifacts.update(video_result)
        state.status = "completed"
        self._save_state(state, output_dir)
        return state

    def _invoke(self, state: AgentState, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            raw = self.tools[tool_name].invoke(inputs)
            result = json.loads(raw)
        except Exception as exc:
            self._log(state, tool_name, "failed", inputs, {"error": str(exc)}, time.perf_counter() - started)
            self._save_state(state, self.project_root / "outputs" / "agent" / "homework6" / state.case_id)
            raise
        self._log(state, tool_name, "completed", inputs, self._summarize(result), time.perf_counter() - started)
        return result

    def _retrieve_materials(self, query: str) -> str:
        return json.dumps(self.library.recommend(query), ensure_ascii=False)

    def _write_story(self, idea: str, protagonist: str, profile: str, setting: str, theme: str, materials_json: str) -> str:
        materials = json.loads(materials_json)
        helper = materials["materials"]["characters"][0]["title"]
        scene_ref = materials["materials"]["scenes"][0]["title"]
        interest = self._infer_interest(idea)
        course_theme = "环保" if "环保" in theme else ("友谊" if "友谊" in theme else "勇气")
        config = None
        if self.enable_cloud_story:
            try:
                config = LLMConfig.from_env()
            except (ConfigurationError, ValueError):
                config = None

        if config is not None:
            request = StoryRequest(
                hero_name=protagonist,
                hero_age=8,
                interest=interest,
                setting=setting,
                theme=course_theme,
                story_length="短篇",
                target_age=8,
                plot_idea=idea,
            )
            result = StoryGenerator(
                OpenAICompatibleClient(config), max_retries=config.max_retries
            ).generate(request, PromptStrategy.ROLE_CONSTRAINTS)
            generated = result.story
            return json.dumps(
                {
                    "title": generated.title,
                    "idea": idea,
                    "theme": theme,
                    "characters": [
                        {
                            "name": character.name,
                            "role": "主角" if character.name == protagonist else "伙伴",
                            "description": f"{character.traits}；{character.appearance}",
                        }
                        for character in generated.characters
                    ],
                    "scenes": [
                        {
                            "id": scene.scene_id,
                            "title": scene.description,
                            "setting": setting,
                            "content": scene.text,
                            "emotion": scene.mood,
                            "visual_prompt": scene.visual_prompt,
                        }
                        for scene in generated.scenes
                    ],
                    "moral": generated.moral,
                    "generation": {
                        "mode": "cloud-llm",
                        "model": config.model,
                        "strategy": result.strategy.value,
                        "attempts": result.attempts,
                        "material_backend": materials["backend"],
                    },
                },
                ensure_ascii=False,
            )

        story = {
            "title": f"{protagonist}解决了{scene_ref}的难题",
            "idea": idea,
            "theme": theme,
            "characters": [
                {"name": protagonist, "role": "主角", "description": profile},
                {"name": helper, "role": "伙伴", "description": "来自素材库的向导伙伴，善于发现线索。"},
            ],
            "scenes": [
                {"id": 1, "title": "明确问题", "setting": setting, "content": f"{protagonist}来到{setting}，事情正像创意里描述的那样发生：{idea}。{protagonist}没有立刻行动，而是先和{helper}确认目标，并记下现场已经出现的三条线索。", "emotion": "好奇而谨慎"},
                {"id": 2, "title": "从失败中找到缺口", "setting": setting, "content": f"{protagonist}第一次尝试只用到了自己熟悉的{interest}知识，却因为忽略其中一条线索而失败。{helper}没有直接给答案，而是指出前后矛盾的地方。两人重新比较刚才的结果，终于找到了失败的具体原因。", "emotion": "紧张到专注"},
                {"id": 3, "title": "用已有线索解决问题", "setting": setting, "content": f"这一次，{protagonist}把{interest}知识、伙伴的提醒和第一幕记录的线索组合起来，完成了一个安全可行的办法。问题被解决后，{protagonist}也明白，真正的{theme}来自认真观察、承认失败并和伙伴一起修正。", "emotion": "释然与温暖"},
            ],
            "moral": f"{theme}不是口号，而是在遇到困难时做出的每一个小选择。",
            "generation": {"mode": "offline-causal-fallback", "material_backend": materials["backend"]},
        }
        return json.dumps(story, ensure_ascii=False)

    @staticmethod
    def _infer_interest(idea: str) -> str:
        for keyword in ("恐龙", "画画", "音乐", "足球", "星星", "机器人", "海洋", "动物", "阅读", "科学"):
            if keyword in idea:
                return keyword
        return "观察和探索"

    def _illustrate(self, story_json: str, output_dir: str) -> str:
        story = json.loads(story_json)
        destination = Path(output_dir)
        image_dir = destination / "images"
        setting = story["scenes"][0]["setting"]
        if "海" in setting:
            motifs = ["submarine", "ocean", "ocean"]
        elif "森林" in setting:
            motifs = ["forest", "bird", "river"]
        elif "恐龙" in setting:
            motifs = ["dino", "forest", "dino"]
        elif "城堡" in setting:
            motifs = ["castle", "library", "dragon"]
        else:
            motifs = ["space", "robot", "moon"]
        paths = []
        for index, (scene, motif) in enumerate(zip(story["scenes"], motifs)):
            path = image_dir / f"scene-{index + 1:02d}.png"
            _draw_scene(path, f"{story['characters'][0]['name']} · {scene['title']}", motif, index + 2)
            paths.append(str(path.relative_to(self.project_root)).replace("\\", "/"))
        return json.dumps({"images": paths}, ensure_ascii=False)

    def _narrate(self, story_json: str, output_dir: str) -> str:
        story = json.loads(story_json)
        destination = Path(output_dir)
        audio_path = destination / "narration.mp3"
        text = f"{story['title']}。" + "。".join(scene["content"] for scene in story["scenes"]) + f"。故事里的小星光：{story['moral']}"

        async def synthesize() -> None:
            import edge_tts

            speech = edge_tts.Communicate(text=text, voice="zh-CN-XiaoxiaoNeural", rate="-8%", pitch="+0Hz", volume="+0%")
            await speech.save(str(audio_path))

        destination.mkdir(parents=True, exist_ok=True)
        if not audio_path.exists() or audio_path.stat().st_size < 2_000:
            asyncio.run(synthesize())
        duration = round(MP3(audio_path).info.length, 3)
        return json.dumps({"audio": str(audio_path.relative_to(self.project_root)).replace("\\", "/"), "audio_duration_seconds": duration}, ensure_ascii=False)

    def _compose_video(self, images_json: str, audio_path: str, output_dir: str) -> str:
        images = [self.project_root / path for path in json.loads(images_json)]
        destination = Path(output_dir)
        audio = Path(audio_path)
        video_path = destination / "story-video.mp4"
        ffmpeg = find_ffmpeg()
        duration = MP3(audio).info.length
        segment_duration = max(3.0, duration / len(images))
        temp_dir = destination / "video-parts"
        temp_dir.mkdir(parents=True, exist_ok=True)
        clips: list[Path] = []
        for index, image in enumerate(images):
            clip = temp_dir / f"part-{index + 1:02d}.mp4"
            subprocess.run(
                [str(ffmpeg), "-y", "-loglevel", "error", "-loop", "1", "-framerate", "24", "-i", str(image), "-t", f"{segment_duration:.3f}", "-vf", "scale=960:540:force_original_aspect_ratio=increase,crop=960:540,format=yuv420p", "-c:v", "h264_nvenc", "-preset", "p4", "-an", str(clip)],
                check=True,
            )
            clips.append(clip)
        concat_file = temp_dir / "concat.txt"
        concat_file.write_text("".join(f"file '{clip.as_posix()}'\n" for clip in clips), encoding="utf-8")
        base_video = temp_dir / "base.mp4"
        subprocess.run([str(ffmpeg), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(base_video)], check=True)
        subprocess.run([str(ffmpeg), "-y", "-loglevel", "error", "-i", str(base_video), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(video_path)], check=True)
        return json.dumps({"video": str(video_path.relative_to(self.project_root)).replace("\\", "/"), "video_duration_seconds": round(duration, 3)}, ensure_ascii=False)

    @staticmethod
    def _summarize(result: dict[str, Any]) -> dict[str, Any]:
        summary: dict[str, Any] = {"keys": list(result)}
        if "title" in result:
            summary["title"] = result["title"]
        if "images" in result:
            summary["image_count"] = len(result["images"])
        for key in ("audio", "video", "backend"):
            if key in result:
                summary[key] = result[key]
        return summary

    @staticmethod
    def _log(state: AgentState, action: str, status: str, inputs: dict[str, Any], outputs: dict[str, Any], elapsed: float = 0.0) -> None:
        state.workflow_log.append({"sequence": len(state.workflow_log) + 1, "action": action, "status": status, "elapsed_seconds": round(elapsed, 3), "inputs": inputs, "outputs": outputs})

    def _save_state(self, state: AgentState, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "agent-state.json").write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2), encoding="utf-8")
        (output_dir / "workflow-log.json").write_text(json.dumps(state.workflow_log, ensure_ascii=False, indent=2), encoding="utf-8")
