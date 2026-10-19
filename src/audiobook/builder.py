"""使用Edge TTS生成多角色音频，并创建分段同步时间轴。"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any


EMOTION_ADJUSTMENTS: dict[str, dict[str, int]] = {
    "平静": {"rate": -2, "pitch": 0, "volume": 0},
    "温柔": {"rate": -4, "pitch": -1, "volume": -1},
    "好奇": {"rate": 0, "pitch": 3, "volume": 0},
    "低语": {"rate": -12, "pitch": -2, "volume": -10},
    "紧张": {"rate": 3, "pitch": 4, "volume": 0},
    "思考": {"rate": -7, "pitch": -1, "volume": -2},
    "兴奋": {"rate": 8, "pitch": 6, "volume": 2},
    "坚定": {"rate": -1, "pitch": -2, "volume": 3},
    "安心": {"rate": -6, "pitch": -2, "volume": -1},
}


def load_script(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("voices"), dict):
        raise ValueError("脚本必须包含voices对象")
    segments = payload.get("segments")
    if not isinstance(segments, list) or len(segments) < 3:
        raise ValueError("脚本至少需要3个分段")

    voices = payload["voices"]
    used_roles: set[str] = set()
    for expected_id, segment in enumerate(segments, start=1):
        if not isinstance(segment, dict):
            raise ValueError("每个分段必须是对象")
        if segment.get("id") != expected_id:
            raise ValueError("分段id必须从1开始连续排列")
        role = str(segment.get("role", ""))
        text = str(segment.get("text", "")).strip()
        emotion = str(segment.get("emotion", ""))
        if role not in voices:
            raise ValueError(f"分段{expected_id}使用了未配置角色：{role}")
        if not text:
            raise ValueError(f"分段{expected_id}正文为空")
        if emotion not in EMOTION_ADJUSTMENTS:
            raise ValueError(f"分段{expected_id}使用了未知情感：{emotion}")
        used_roles.add(role)

    if len(used_roles) < 3:
        raise ValueError("至少需要3个角色使用不同音色")
    used_voices = {voices[role]["voice"] for role in used_roles}
    if len(used_voices) < 3:
        raise ValueError("至少需要3种不同音色")
    return payload


def find_ffmpeg() -> Path:
    configured = os.getenv("FFMPEG_BINARY", "").strip()
    candidates = [
        Path(configured) if configured else None,
        Path(found) if (found := shutil.which("ffmpeg")) else None,
        Path(r"D:\JianyingPro\6.6.0.12145\ffmpeg.exe"),
        Path(r"D:\Trae CN\resources\app\bin\ffmpeg.exe"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "找不到ffmpeg。请安装ffmpeg或在FFMPEG_BINARY环境变量中填写完整路径。"
    )


def _combine_setting(base: str, adjustment: int, suffix: str) -> str:
    match = re.fullmatch(r"([+-]?\d+)" + re.escape(suffix), base.strip())
    if not match:
        raise ValueError(f"无效语音参数：{base}")
    value = int(match.group(1)) + adjustment
    return f"{value:+d}{suffix}"


def segment_voice_settings(
    voice_config: dict[str, Any], emotion: str
) -> dict[str, str]:
    adjustment = EMOTION_ADJUSTMENTS[emotion]
    return {
        "voice": str(voice_config["voice"]),
        "rate": _combine_setting(str(voice_config.get("rate", "+0%")), adjustment["rate"], "%"),
        "pitch": _combine_setting(str(voice_config.get("pitch", "+0Hz")), adjustment["pitch"], "Hz"),
        "volume": _combine_setting(str(voice_config.get("volume", "+0%")), adjustment["volume"], "%"),
    }


async def _synthesize_one(text: str, output: Path, settings: dict[str, str]) -> None:
    try:
        import edge_tts
    except ImportError as exc:
        raise RuntimeError("缺少edge-tts，请先安装requirements.txt") from exc

    communicate = edge_tts.Communicate(text=text, **settings)
    await communicate.save(str(output))


async def _synthesize_segments(
    script: dict[str, Any], parts_dir: Path, force: bool
) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    voices = script["voices"]
    for segment in script["segments"]:
        output = parts_dir / f"{segment['id']:03d}-{segment['role']}.mp3"
        settings = segment_voice_settings(voices[segment["role"]], segment["emotion"])
        if force or not output.exists() or output.stat().st_size < 1_000:
            print(
                f"[{segment['id']:02d}/{len(script['segments'])}] "
                f"{segment['role']} [{segment['emotion']}]"
            )
            await _synthesize_one(segment["text"], output, settings)
        prepared.append({**segment, "file": output, "settings": settings})
    return prepared


def _assemble(
    prepared: list[dict[str, Any]], output_mp3: Path, timeline_path: Path, ffmpeg: Path
) -> dict[str, Any]:
    try:
        from mutagen.mp3 import MP3
    except ImportError as exc:
        raise RuntimeError("缺少mutagen，请先安装requirements.txt") from exc

    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    normalized_dir = output_mp3.parent / "wav-parts"
    silence_dir = output_mp3.parent / "wav-silence"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    silence_dir.mkdir(parents=True, exist_ok=True)

    def wav_duration(path: Path) -> float:
        with wave.open(str(path), "rb") as wav_file:
            return wav_file.getnframes() / wav_file.getframerate()

    normalized_files: dict[int, Path] = {}
    for segment in prepared:
        wav_path = normalized_dir / f"{segment['id']:03d}-{segment['role']}.wav"
        source_path = segment["file"]
        if (
            not wav_path.exists()
            or wav_path.stat().st_size < 1_000
            or wav_path.stat().st_mtime < source_path.stat().st_mtime
        ):
            subprocess.run(
                [
                    str(ffmpeg),
                    "-y",
                    "-loglevel",
                    "error",
                    "-i",
                    str(source_path),
                    "-vn",
                    "-ar",
                    "24000",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    str(wav_path),
                ],
                check=True,
            )
        normalized_files[int(segment["id"])] = wav_path

    pause_values = {800, *(int(item.get("pause_ms", 650)) for item in prepared)}
    silence_files: dict[int, Path] = {}
    for pause_ms in sorted(pause_values):
        silence_path = silence_dir / f"silence-{pause_ms}ms.wav"
        if not silence_path.exists() or silence_path.stat().st_size < 500:
            subprocess.run(
                [
                    str(ffmpeg),
                    "-y",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "anullsrc=r=24000:cl=mono",
                    "-t",
                    f"{pause_ms / 1000:.3f}",
                    "-c:a",
                    "pcm_s16le",
                    str(silence_path),
                ],
                check=True,
            )
        silence_files[pause_ms] = silence_path

    intro_silence = silence_files[800]
    cursor_seconds = wav_duration(intro_silence)
    concat_files = [intro_silence]
    timeline: list[dict[str, Any]] = []

    for segment in prepared:
        normalized_file = normalized_files[int(segment["id"])]
        clip_duration = wav_duration(normalized_file)
        start_seconds = cursor_seconds
        end_seconds = start_seconds + clip_duration
        pause_ms = int(segment.get("pause_ms", 650))
        pause_file = silence_files[pause_ms]
        pause_duration = wav_duration(pause_file)
        concat_files.extend([normalized_file, pause_file])
        timeline.append(
            {
                "id": segment["id"],
                "chapter": segment.get("chapter", "正文"),
                "role": segment["role"],
                "emotion": segment["emotion"],
                "text": segment["text"],
                "start": round(start_seconds, 3),
                "end": round(end_seconds, 3),
                "duration": round(clip_duration, 3),
                "voice": segment["settings"]["voice"],
                "rate": segment["settings"]["rate"],
                "pitch": segment["settings"]["pitch"],
                "volume": segment["settings"]["volume"],
            }
        )
        cursor_seconds = end_seconds + pause_duration

    concat_path = output_mp3.parent / "concat-list.txt"
    concat_path.write_text(
        "".join(f"file '{path.resolve().as_posix()}'\n" for path in concat_files),
        encoding="utf-8",
    )
    try:
        import lameenc
    except ImportError as exc:
        raise RuntimeError("缺少lameenc，请先安装requirements.txt") from exc

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(128)
    encoder.set_in_sample_rate(24000)
    encoder.set_channels(1)
    encoder.set_quality(2)
    with output_mp3.open("wb") as output_file:
        for wav_path in concat_files:
            with wave.open(str(wav_path), "rb") as wav_file:
                while frames := wav_file.readframes(24_000):
                    output_file.write(encoder.encode(frames))
        output_file.write(encoder.flush())
    duration_seconds = round(float(MP3(output_mp3).info.length), 3)
    report = {
        "title": "小雨和月光脚印",
        "duration_seconds": duration_seconds,
        "duration_display": f"{int(duration_seconds // 60)}分{int(duration_seconds % 60):02d}秒",
        "roles": sorted({item["role"] for item in timeline}),
        "voice_count": len({item["voice"] for item in timeline}),
        "segment_count": len(timeline),
        "segments": timeline,
    }
    timeline_path.parent.mkdir(parents=True, exist_ok=True)
    timeline_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def build_audiobook(
    script_path: Path,
    output_mp3: Path,
    timeline_path: Path,
    parts_dir: Path,
    *,
    force: bool = False,
) -> dict[str, Any]:
    script = load_script(script_path)
    parts_dir.mkdir(parents=True, exist_ok=True)
    prepared = asyncio.run(_synthesize_segments(script, parts_dir, force))
    report = _assemble(prepared, output_mp3, timeline_path, find_ffmpeg())
    if report["duration_seconds"] < 180:
        raise RuntimeError(
            f"成品仅{report['duration_display']}，未达到课程要求的3分钟。"
        )
    return report
