"""本地多模态素材库：文本向量检索、图像检索与素材生成。"""

from __future__ import annotations

import json
import math
import re
import struct
import wave
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont


ALIASES = {
    "太空": ["宇宙", "星球", "火箭", "银河", "星空"],
    "宇宙": ["太空", "星球", "火箭"],
    "森林": ["树林", "小鹿", "树木", "自然"],
    "海底": ["海洋", "鲸鱼", "珊瑚", "潜水"],
    "海洋": ["海底", "鲸鱼", "珊瑚"],
    "友谊": ["朋友", "伙伴", "合作", "分享"],
    "勇气": ["勇敢", "冒险", "挑战"],
    "环保": ["自然", "守护", "保护", "垃圾"],
    "魔法": ["奇幻", "城堡", "精灵", "星光"],
    "恐龙": ["远古", "化石", "侏罗纪"],
    "女孩": ["小女孩", "少女"],
    "男孩": ["小男孩", "少年"],
}


STORY_TEMPLATES = [
    ("tpl-space", "会唱歌的星球", "太空冒险", "孩子乘火箭寻找失落的星光，在陌生星球学会勇气与倾听。", ["太空", "火箭", "星球", "勇气", "音乐"]),
    ("tpl-forest", "月光森林的约定", "森林友谊", "两个性格不同的伙伴循着月光脚印，合作送迷路的小鸟回家。", ["森林", "月光", "友谊", "小鸟", "合作"]),
    ("tpl-ocean", "珊瑚城清洁队", "海洋环保", "孩子与小鲸鱼清理漂浮垃圾，让黯淡的珊瑚重新发光。", ["海底", "鲸鱼", "珊瑚", "环保", "守护"]),
    ("tpl-dino", "恐龙谷的最后一颗蛋", "远古冒险", "小小考古迷穿越恐龙谷，护送一颗蛋回到温暖巢穴。", ["恐龙", "化石", "冒险", "守护", "远古"]),
    ("tpl-castle", "倒着走的魔法城堡", "奇幻成长", "城堡里的时间突然倒流，主角通过观察规律解开魔法谜题。", ["魔法", "城堡", "谜题", "成长", "奇幻"]),
    ("tpl-cloud", "云朵邮差", "天空旅行", "孩子驾驶纸飞机穿过云海，把一封迟到的道歉信送到彩虹镇。", ["天空", "云朵", "飞行", "善意", "彩虹"]),
    ("tpl-snow", "雪国的小太阳", "冰雪互助", "主角寻找能融化孤独的太阳种子，把温暖分享给雪国居民。", ["冰雪", "冬天", "太阳", "分享", "温暖"]),
    ("tpl-city", "停电夜的萤火地图", "城市探索", "停电后，孩子们跟随萤火虫地图帮助邻居找到回家的路。", ["城市", "夜晚", "萤火虫", "互助", "探索"]),
    ("tpl-farm", "会说话的种子", "田园自然", "一颗种子告诉主角四季的秘密，孩子学会耐心照料与等待。", ["农场", "种子", "植物", "自然", "耐心"]),
    ("tpl-music", "丢失的七个音符", "音乐奇遇", "七个音符躲进不同场景，主角用想象力找回完整旋律。", ["音乐", "乐器", "想象", "冒险", "合作"]),
]


CHARACTERS = [
    ("char-girl", "小星", "勇敢的短发女孩，喜欢天文与画画", ["女孩", "勇气", "太空", "画画"]),
    ("char-boy", "阿川", "细心的小男孩，随身带着观察笔记", ["男孩", "观察", "自然", "成长"]),
    ("char-bird", "蓝羽", "会说话的蓝色小鸟，机灵但偶尔胆小", ["小鸟", "森林", "朋友", "蓝色"]),
    ("char-whale", "泡泡", "爱唱歌的小鲸鱼，熟悉每一片珊瑚", ["鲸鱼", "海洋", "音乐", "环保"]),
    ("char-robot", "咔嗒", "圆滚滚的维修机器人，擅长解谜", ["机器人", "太空", "科技", "谜题"]),
    ("char-fox", "橙尾", "热心的小狐狸，跑得快又会认路", ["狐狸", "森林", "友谊", "冒险"]),
    ("char-dino", "豆角龙", "温柔的绿色小恐龙，害怕打雷", ["恐龙", "绿色", "勇气", "远古"]),
    ("char-fairy", "露珠", "守护植物的叶片精灵", ["精灵", "魔法", "植物", "环保"]),
    ("char-cat", "墨点", "爱读书的黑猫侦探", ["猫", "侦探", "城市", "谜题"]),
    ("char-cloud", "绵绵", "能够变成各种形状的小云朵", ["云朵", "天空", "想象", "友谊"]),
    ("char-penguin", "点点", "会制作雪橇的小企鹅", ["企鹅", "冰雪", "互助", "旅行"]),
    ("char-seed", "芽芽", "会悄悄说话的金色种子", ["种子", "农场", "自然", "耐心"]),
]


SCENES = [
    ("scene-launch", "星光发射台", "银白火箭停在蓝紫色夜空下，星尘沿跑道流动。", ["太空", "火箭", "夜晚", "星空"]),
    ("scene-moonforest", "月光森林", "高大树木围住一条发光小路，叶间落下柔和月光。", ["森林", "月光", "树木", "夜晚"]),
    ("scene-coral", "珊瑚花园", "彩色珊瑚与鱼群围绕透明海底城，光束穿过水面。", ["海底", "珊瑚", "鱼", "海洋"]),
    ("scene-dinovalley", "恐龙山谷", "蕨类植物、火山与巨大的脚印延伸到远方。", ["恐龙", "远古", "山谷", "冒险"]),
    ("scene-castle", "星砂城堡", "紫色高塔漂浮在云上，窗户里飞出金色魔法。", ["城堡", "魔法", "奇幻", "云朵"]),
    ("scene-cloud", "彩虹云海", "纸飞机穿过粉蓝云层，远处架着一座彩虹桥。", ["天空", "云朵", "彩虹", "飞行"]),
    ("scene-snow", "极光雪原", "雪屋散落在蓝色雪地，绿色极光横跨天空。", ["冰雪", "极光", "冬天", "企鹅"]),
    ("scene-city", "萤火城市", "停电后的街道被萤火虫点亮，窗户像星星一样闪烁。", ["城市", "夜晚", "萤火虫", "探索"]),
    ("scene-farm", "四季农场", "麦田、果树与小木屋围绕会发光的种子。", ["农场", "植物", "种子", "自然"]),
    ("scene-river", "会唱歌的小河谷", "清澈河流绕过草地，音符形水花跃出水面。", ["河流", "音乐", "自然", "山谷"]),
    ("scene-library", "午夜图书馆", "书架延伸到星空，发光书页组成旋转楼梯。", ["图书馆", "夜晚", "魔法", "谜题"]),
    ("scene-lighthouse", "云海灯塔岛", "金色灯塔立在漂浮小岛，云海中有鲸形影子。", ["灯塔", "天空", "云朵", "冒险"]),
]


IMAGE_SPECS = [
    ("img-space-rocket", "星光火箭起航", "space", ["太空", "火箭", "星球", "勇气"]),
    ("img-space-planets", "彩色星球相遇", "space", ["宇宙", "星球", "银河", "探索"]),
    ("img-space-robot", "机器人修理站", "robot", ["机器人", "太空", "科技", "合作"]),
    ("img-space-moon", "月球上的脚印", "moon", ["月球", "太空", "脚印", "冒险"]),
    ("img-forest-path", "月光森林小路", "forest", ["森林", "月光", "小路", "勇气"]),
    ("img-forest-bird", "蓝鸟回家", "bird", ["森林", "小鸟", "友谊", "鸟巢"]),
    ("img-forest-fox", "狐狸与萤火虫", "forest", ["森林", "狐狸", "萤火虫", "朋友"]),
    ("img-forest-river", "森林音乐河", "river", ["森林", "河流", "音乐", "自然"]),
    ("img-ocean-whale", "唱歌的小鲸鱼", "ocean", ["海洋", "鲸鱼", "音乐", "朋友"]),
    ("img-ocean-coral", "发光珊瑚城", "ocean", ["海底", "珊瑚", "环保", "鱼群"]),
    ("img-ocean-sub", "潜水艇探险", "submarine", ["海底", "潜水艇", "探索", "冒险"]),
    ("img-ocean-clean", "海洋清洁队", "ocean", ["海洋", "环保", "守护", "合作"]),
    ("img-magic-castle", "云上魔法城堡", "castle", ["魔法", "城堡", "云朵", "奇幻"]),
    ("img-magic-library", "会飞的图书馆", "library", ["魔法", "图书馆", "书", "想象"]),
    ("img-magic-dragon", "小龙点亮星灯", "dragon", ["小龙", "魔法", "星光", "勇气"]),
    ("img-magic-rainbow", "彩虹邮局", "rainbow", ["彩虹", "云朵", "善意", "飞行"]),
    ("img-dino-valley", "绿色恐龙谷", "dino", ["恐龙", "山谷", "远古", "探险"]),
    ("img-snow-aurora", "极光下的小企鹅", "snow", ["冰雪", "企鹅", "极光", "互助"]),
    ("img-farm-seed", "会发光的种子", "farm", ["农场", "种子", "植物", "耐心"]),
    ("img-city-firefly", "萤火虫城市地图", "city", ["城市", "萤火虫", "夜晚", "互助"]),
]


SOUND_SPECS = [
    ("sfx-forest", "月夜森林", ["森林", "夜晚", "虫鸣", "自然"], (523.25, 659.25)),
    ("sfx-space", "星际低鸣", ["太空", "宇宙", "科技", "神秘"], (110.0, 164.81)),
    ("sfx-ocean", "温柔海浪", ["海洋", "海底", "水", "放松"], (220.0, 293.66)),
    ("sfx-magic", "魔法闪光", ["魔法", "奇幻", "星光", "铃声"], (784.0, 1046.5)),
    ("sfx-rain", "屋檐小雨", ["雨天", "自然", "安静", "睡前"], (196.0, 246.94)),
]


def _tokenize(text: str) -> list[str]:
    value = re.sub(r"\s+", "", text.lower())
    words = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]+", value)
    tokens: list[str] = []
    for word in words:
        if re.fullmatch(r"[\u4e00-\u9fff]+", word):
            tokens.extend(list(word))
            tokens.extend(word[i : i + 2] for i in range(max(0, len(word) - 1)))
            tokens.append(word)
        else:
            tokens.append(word)
    for key, values in ALIASES.items():
        if key in value:
            for alias in values:
                tokens.extend(_tokenize_without_alias(alias))
    return tokens


def _tokenize_without_alias(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]+", text.lower())
    tokens: list[str] = []
    for word in words:
        if re.fullmatch(r"[\u4e00-\u9fff]+", word):
            tokens.extend(list(word))
            tokens.extend(word[i : i + 2] for i in range(max(0, len(word) - 1)))
            tokens.append(word)
        else:
            tokens.append(word)
    return tokens


class TfidfEncoder:
    """无需下载模型的字符/词组 TF-IDF 向量器。"""

    def __init__(self) -> None:
        self.vocabulary: list[str] = []
        self.idf: dict[str, float] = {}

    def fit(self, documents: Iterable[str]) -> None:
        docs = [set(_tokenize(text)) for text in documents]
        doc_count = len(docs)
        frequencies = Counter(token for doc in docs for token in doc)
        self.vocabulary = sorted(frequencies)
        self.idf = {
            token: math.log((1 + doc_count) / (1 + frequencies[token])) + 1
            for token in self.vocabulary
        }

    def encode(self, text: str) -> list[float]:
        counts = Counter(_tokenize(text))
        values = [counts[token] * self.idf.get(token, 0.0) for token in self.vocabulary]
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [round(value / norm, 7) for value in values]


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


@dataclass
class SearchResult:
    item: dict[str, Any]
    score: float


class MaterialLibrary:
    """读取索引并执行自然语言多模态检索。"""

    def __init__(self, index_path: Path) -> None:
        self.index_path = Path(index_path)
        self.data = json.loads(self.index_path.read_text(encoding="utf-8"))
        self.encoder = TfidfEncoder()
        self.encoder.vocabulary = self.data["vector_index"]["vocabulary"]
        self.encoder.idf = self.data["vector_index"]["idf"]

    def search(self, query: str, *, kind: str | None = None, limit: int = 5) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("检索内容不能为空")
        query_vector = self.encoder.encode(query)
        items = self.data["items"]
        if kind:
            items = [item for item in items if item["type"] == kind]
        ranked = [SearchResult(item, cosine(query_vector, item["vector"])) for item in items]
        ranked.sort(key=lambda result: (-result.score, result.item["id"]))
        return ranked[:limit]

    def recommend(self, query: str) -> dict[str, Any]:
        templates = self.search(query, kind="template", limit=3)
        characters = self.search(query, kind="character", limit=3)
        scenes = self.search(query, kind="scene", limit=3)
        images = self.search(query, kind="image", limit=6)
        sounds = self.search(query, kind="sound", limit=2)
        return {
            "query": query,
            "backend": self.data["image_search_backend"],
            "materials": {
                "templates": [_result_dict(item) for item in templates],
                "characters": [_result_dict(item) for item in characters],
                "scenes": [_result_dict(item) for item in scenes],
                "images": [_result_dict(item) for item in images],
                "sounds": [_result_dict(item) for item in sounds],
            },
            "advice": {
                "story_structure": f"参考《{templates[0].item['title']}》的三幕结构：遇到问题—尝试合作—完成成长。",
                "visual_direction": f"以“{images[0].item['title']}”为首图，统一主角服装、色板和镜头风格。",
                "audio_direction": f"环境底音选用“{sounds[0].item['title']}”，对白优先保持清晰。",
            },
        }


def _result_dict(result: SearchResult) -> dict[str, Any]:
    return {**{key: value for key, value in result.item.items() if key != "vector"}, "score": round(result.score, 4)}


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _draw_scene(path: Path, title: str, motif: str, index: int) -> None:
    palettes = [
        ((20, 29, 75), (103, 83, 199), (255, 213, 120)),
        ((20, 79, 72), (61, 153, 112), (250, 232, 145)),
        ((13, 78, 125), (52, 169, 192), (255, 181, 110)),
        ((70, 39, 106), (178, 101, 184), (255, 225, 146)),
        ((101, 57, 43), (213, 128, 76), (248, 225, 167)),
    ]
    top, bottom, accent = palettes[index % len(palettes)]
    width, height = 960, 640
    image = Image.new("RGB", (width, height), top)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / (height - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        draw.line((0, y, width, y), fill=color)
    # 星光/气泡背景
    for n in range(34):
        x = (n * 149 + index * 71) % width
        y = (n * 83 + index * 47) % 430
        radius = 2 + (n % 4)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 246, 207))
    horizon = 430
    if motif in {"forest", "bird", "river", "farm", "dino"}:
        draw.rectangle((0, horizon, width, height), fill=(29, 92, 69))
        for x in range(30, width, 100):
            draw.rectangle((x, 220, x + 28, 500), fill=(55, 58, 52))
            draw.ellipse((x - 55, 150, x + 85, 330), fill=(36, 120, 78))
    elif motif in {"ocean", "submarine"}:
        draw.rectangle((0, 390, width, height), fill=(9, 92, 139))
        for x in range(40, width, 90):
            draw.ellipse((x, 475 + (x % 3) * 15, x + 55, 610), fill=(241, 111, 104))
    elif motif in {"snow"}:
        draw.polygon([(0, 440), (220, 330), (420, 450), (650, 300), (960, 430), (960, 640), (0, 640)], fill=(224, 240, 248))
    else:
        draw.ellipse((-120, 450, 1080, 800), fill=(34, 42, 88))

    cx, cy = 480, 315
    if motif in {"space", "moon"}:
        draw.ellipse((650, 80, 840, 270), fill=accent)
        draw.polygon([(cx, 130), (cx - 65, 360), (cx + 65, 360)], fill=(235, 241, 246))
        draw.ellipse((cx - 38, 210, cx + 38, 286), fill=(85, 170, 221))
        draw.polygon([(cx - 65, 330), (cx - 125, 410), (cx - 54, 380)], fill=(239, 106, 90))
        draw.polygon([(cx + 65, 330), (cx + 125, 410), (cx + 54, 380)], fill=(239, 106, 90))
        draw.polygon([(cx - 28, 360), (cx, 455), (cx + 28, 360)], fill=(255, 190, 72))
    elif motif == "robot":
        draw.rounded_rectangle((350, 185, 610, 450), radius=55, fill=(219, 235, 240), outline=accent, width=12)
        draw.ellipse((395, 255, 455, 315), fill=(42, 87, 119)); draw.ellipse((505, 255, 565, 315), fill=(42, 87, 119))
        draw.arc((410, 300, 550, 390), 15, 165, fill=(42, 87, 119), width=10)
    elif motif in {"ocean", "submarine"}:
        draw.ellipse((260, 210, 700, 470), fill=(81, 190, 210), outline=(220, 250, 250), width=9)
        draw.ellipse((570, 260, 735, 370), fill=(81, 190, 210))
        draw.ellipse((330, 280, 385, 335), fill=(20, 65, 90))
        draw.arc((350, 310, 510, 410), 10, 160, fill=(20, 65, 90), width=9)
    elif motif == "castle" or motif == "library":
        draw.rectangle((330, 230, 630, 500), fill=(222, 187, 231))
        for x in (330, 455, 560):
            draw.rectangle((x, 140, x + 70, 500), fill=(196, 154, 220))
            draw.polygon([(x - 10, 140), (x + 35, 70), (x + 80, 140)], fill=accent)
        draw.rounded_rectangle((445, 365, 520, 500), radius=30, fill=(71, 45, 105))
    elif motif == "bird":
        draw.ellipse((360, 235, 600, 420), fill=(76, 174, 221))
        draw.ellipse((520, 190, 680, 340), fill=(76, 174, 221))
        draw.polygon([(665, 255), (740, 285), (665, 305)], fill=accent)
        draw.ellipse((610, 230, 625, 245), fill=(20, 35, 52))
    elif motif == "dino":
        draw.ellipse((285, 245, 650, 480), fill=(104, 188, 102))
        draw.ellipse((570, 140, 760, 330), fill=(104, 188, 102))
        draw.ellipse((650, 200, 668, 218), fill=(20, 50, 35))
        draw.polygon([(300, 300), (120, 210), (270, 410)], fill=(104, 188, 102))
    elif motif == "dragon":
        draw.ellipse((300, 230, 650, 470), fill=(120, 195, 126))
        draw.polygon([(360, 240), (420, 120), (470, 250)], fill=(248, 177, 91))
        draw.polygon([(590, 320), (760, 250), (630, 390)], fill=(120, 195, 126))
    elif motif == "rainbow":
        for offset, color in enumerate([(242, 96, 96), (250, 176, 80), (248, 226, 101), (99, 191, 125), (99, 161, 224)]):
            draw.arc((180 + offset * 10, 110 + offset * 10, 780 - offset * 10, 650 - offset * 10), 180, 360, fill=color, width=18)
    elif motif == "snow":
        draw.ellipse((360, 210, 600, 500), fill=(38, 58, 82))
        draw.ellipse((400, 250, 560, 450), fill=(245, 246, 238))
        draw.ellipse((420, 275, 440, 295), fill=(20, 25, 30)); draw.ellipse((520, 275, 540, 295), fill=(20, 25, 30))
        draw.polygon([(472, 310), (520, 330), (472, 350)], fill=(246, 174, 59))
    elif motif == "city":
        for x, h in [(80, 260), (220, 340), (380, 240), (535, 380), (725, 300)]:
            draw.rectangle((x, height - h, x + 135, height), fill=(31, 44, 74))
            for wx in range(x + 18, x + 110, 35):
                for wy in range(height - h + 25, height - 25, 45):
                    draw.rectangle((wx, wy, wx + 14, wy + 20), fill=accent)
    else:
        draw.ellipse((350, 220, 610, 480), fill=accent)
        draw.ellipse((425, 275, 475, 325), fill=(35, 53, 69)); draw.ellipse((520, 275, 570, 325), fill=(35, 53, 69))

    # 底部标题卡
    draw.rounded_rectangle((42, 515, 918, 610), radius=24, fill=(10, 20, 42, 220))
    draw.text((72, 540), title, font=_font(34), fill=(255, 250, 231))
    draw.text((790, 548), f"#{index + 1:02d}", font=_font(24), fill=accent)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def _write_sound(path: Path, frequencies: tuple[float, float], index: int) -> None:
    sample_rate = 22050
    duration = 3.0
    frames = bytearray()
    for sample in range(int(sample_rate * duration)):
        t = sample / sample_rate
        pulse = math.sin(2 * math.pi * frequencies[0] * t) * 0.18
        shimmer = math.sin(2 * math.pi * frequencies[1] * t) * (0.06 + 0.03 * math.sin(2 * math.pi * 0.5 * t))
        envelope = min(1.0, t * 3) * min(1.0, (duration - t) * 2)
        value = int(max(-1, min(1, (pulse + shimmer) * envelope)) * 32767)
        frames.extend(struct.pack("<h", value))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(frames)


def _item(item_id: str, kind: str, title: str, description: str, tags: list[str], asset: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"id": item_id, "type": kind, "title": title, "description": description, "tags": tags}
    if asset:
        result["asset"] = asset
    result["search_text"] = " ".join([title, description, *tags])
    return result


def build_library(output_dir: Path) -> Path:
    """生成20张图、5段音效以及可直接检索的JSON索引。"""
    output_dir = Path(output_dir)
    image_dir = output_dir / "assets" / "images"
    sound_dir = output_dir / "assets" / "sounds"
    items: list[dict[str, Any]] = []
    for item_id, title, genre, description, tags in STORY_TEMPLATES:
        items.append(_item(item_id, "template", title, f"{genre}。{description}", tags))
    for item_id, title, description, tags in CHARACTERS:
        items.append(_item(item_id, "character", title, description, tags))
    for item_id, title, description, tags in SCENES:
        items.append(_item(item_id, "scene", title, description, tags))
    for index, (item_id, title, motif, tags) in enumerate(IMAGE_SPECS):
        filename = f"{item_id}.png"
        _draw_scene(image_dir / filename, title, motif, index)
        items.append(_item(item_id, "image", title, "儿童绘本扁平插画，可作为场景构图与色板参考。", tags, f"assets/images/{filename}"))
    for index, (item_id, title, tags, frequencies) in enumerate(SOUND_SPECS):
        filename = f"{item_id}.wav"
        _write_sound(sound_dir / filename, frequencies, index)
        items.append(_item(item_id, "sound", title, "3秒原创合成环境音，可循环作为场景氛围底音。", tags, f"assets/sounds/{filename}"))

    encoder = TfidfEncoder()
    encoder.fit(item["search_text"] for item in items)
    for item in items:
        item["vector"] = encoder.encode(item["search_text"])
    index_data = {
        "version": 1,
        "name": "星光故事屋多模态素材库",
        "image_search_backend": "visual-semantic-fallback",
        "backend_note": "默认使用图像人工语义标签与本地TF-IDF共同空间；代码和文档保留OpenCLIP升级接口，不虚报未执行的CLIP结果。",
        "counts": {kind: sum(item["type"] == kind for item in items) for kind in ["template", "character", "scene", "image", "sound"]},
        "aliases": ALIASES,
        "vector_index": {"method": "character-bigram-tfidf-cosine", "vocabulary": encoder.vocabulary, "idf": encoder.idf},
        "items": items,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.json"
    index_path.write_text(json.dumps(index_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return index_path
