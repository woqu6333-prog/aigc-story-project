"""输入与输出数据模型。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class StoryRequest(StrictModel):
    hero_name: str = Field(min_length=1, max_length=20, description="主角名字")
    hero_age: int = Field(ge=3, le=15, description="主角年龄")
    interest: str = Field(min_length=1, max_length=30, description="主角兴趣")
    setting: str = Field(min_length=2, max_length=50, description="故事发生场景")
    theme: Literal["勇气", "友谊", "环保"]
    story_length: Literal["短篇", "中篇", "长篇"] = "中篇"
    target_age: int = Field(ge=3, le=12, description="目标读者年龄")

    @field_validator("hero_name", "interest", "setting")
    @classmethod
    def reject_control_characters(cls, value: str) -> str:
        if any(ord(character) < 32 for character in value):
            raise ValueError("不能包含控制字符")
        return value


class Character(StrictModel):
    name: str = Field(min_length=1, max_length=30)
    traits: str = Field(min_length=2, max_length=120)
    appearance: str = Field(min_length=2, max_length=200)


class Scene(StrictModel):
    scene_id: int = Field(ge=1)
    description: str = Field(min_length=5, max_length=300)
    text: str = Field(min_length=20, max_length=2000)
    mood: str = Field(min_length=1, max_length=30)
    visual_prompt: str = Field(min_length=10, max_length=600)


class StoryOutput(StrictModel):
    title: str = Field(min_length=2, max_length=80)
    characters: list[Character] = Field(min_length=1, max_length=8)
    scenes: list[Scene] = Field(min_length=3, max_length=8)
    moral: str = Field(min_length=5, max_length=300)

    @model_validator(mode="after")
    def validate_scene_ids(self) -> "StoryOutput":
        actual_ids = [scene.scene_id for scene in self.scenes]
        expected_ids = list(range(1, len(self.scenes) + 1))
        if actual_ids != expected_ids:
            raise ValueError(f"scene_id必须从1开始连续排列，当前为{actual_ids}")
        return self

    def ensure_request_alignment(self, request: StoryRequest) -> None:
        """检查模型结果是否至少保留主角名字和兴趣。"""

        character_names = {character.name for character in self.characters}
        if request.hero_name not in character_names:
            raise ValueError(f"characters中缺少主角：{request.hero_name}")

        combined_text = " ".join(scene.text for scene in self.scenes)
        if request.hero_name not in combined_text:
            raise ValueError("场景正文中没有出现主角名字")
        if request.interest not in combined_text:
            raise ValueError("主角兴趣没有进入故事情节")
