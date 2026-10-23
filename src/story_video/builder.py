"""将绘本图片、作业3配音、原创音乐和字幕合成为故事短视频。"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import wave
from array import array
from pathlib import Path
from typing import Any

from audiobook.builder import find_ffmpeg


WIDTH = 1280
HEIGHT = 720
FPS = 24
INTRO_SECONDS = 4.0
GAP_SECONDS = 0.6
OUTRO_SECONDS = 5.0

SELECTED_SEGMENTS = [
    {"id": 1, "image": "scene-01.png", "label": "雨后的月光森林"},
    {"id": 3, "image": "scene-01.png", "label": "奇怪的三趾脚印"},
    {"id": 7, "image": "scene-02.png", "label": "知更鸟的请求"},
    {"id": 8, "image": "scene-02.png", "label": "一起寻找伙伴"},
    {"id": 17, "image": "scene-03.png", "label": "找到被困的小蓝鸟"},
    {"id": 22, "image": "scene-03.png", "label": "蓝蓝重新展开翅膀"},
    {"id": 30, "image": "scene-03.png", "label": "真正的勇气"},
]


def _split_text(text: str, max_chars: int = 18) -> list[str]:
    pieces = [part for part in re.split(r"(?<=[，。！？；])", text) if part]
    result: list[str] = []
    current = ""
    for piece in pieces:
        if len(current) + len(piece) <= max_chars:
            current += piece
            continue
        if current:
            result.append(current)
            current = ""
        while len(piece) > max_chars:
            result.append(piece[:max_chars])
            piece = piece[max_chars:]
        current = piece
    if current:
        result.append(current)
    return result or [text]


def create_video_plan(timeline_path: Path) -> dict[str, Any]:
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    by_id = {int(item["id"]): item for item in timeline["segments"]}
    cursor = INTRO_SECONDS
    sections: list[dict[str, Any]] = []
    subtitles: list[dict[str, Any]] = []

    for selection in SELECTED_SEGMENTS:
        source = by_id[selection["id"]]
        duration = float(source["duration"])
        section = {
            **selection,
            "role": source["role"],
            "emotion": source["emotion"],
            "text": source["text"],
            "source_start": float(source["start"]),
            "source_end": float(source["end"]),
            "start": round(cursor, 3),
            "end": round(cursor + duration, 3),
            "duration": duration,
        }
        sections.append(section)

        chunks = _split_text(source["text"])
        weights = [max(1, len(re.sub(r"[，。！？；]", "", chunk))) for chunk in chunks]
        weight_sum = sum(weights)
        subtitle_cursor = cursor
        for index, (chunk, weight) in enumerate(zip(chunks, weights)):
            if index == len(chunks) - 1:
                chunk_end = cursor + duration
            else:
                chunk_end = subtitle_cursor + duration * weight / weight_sum
            subtitles.append(
                {
                    "role": source["role"],
                    "emotion": source["emotion"],
                    "text": chunk,
                    "start": round(subtitle_cursor, 3),
                    "end": round(chunk_end, 3),
                }
            )
            subtitle_cursor = chunk_end
        cursor += duration + GAP_SECONDS

    duration_seconds = cursor - GAP_SECONDS + OUTRO_SECONDS
    return {
        "title": "小雨和月光脚印｜故事精华",
        "resolution": f"{WIDTH}x{HEIGHT}",
        "fps": FPS,
        "intro_seconds": INTRO_SECONDS,
        "gap_seconds": GAP_SECONDS,
        "outro_seconds": OUTRO_SECONDS,
        "duration_seconds": round(duration_seconds, 3),
        "sections": sections,
        "subtitles": subtitles,
    }


def _font_path(bold: bool = False) -> Path:
    candidates = (
        [Path(r"C:\Windows\Fonts\msyhbd.ttc"), Path(r"C:\Windows\Fonts\simhei.ttf")]
        if bold
        else [Path(r"C:\Windows\Fonts\msyh.ttc"), Path(r"C:\Windows\Fonts\simsun.ttc")]
    )
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("找不到可显示中文的微软雅黑或黑体字体")


def _cover_image(source: Path, title: str, subtitle: str, output: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
    except ImportError as exc:
        raise RuntimeError("缺少Pillow，请先安装requirements.txt") from exc

    image = Image.open(source).convert("RGB")
    image = ImageOps.fit(image, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    image = ImageEnhance.Brightness(image).enhance(0.56)
    overlay = Image.new("RGBA", image.size, (9, 14, 35, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for x in range(WIDTH):
        alpha = int(170 * (1 - x / WIDTH) + 30)
        overlay_draw.line((x, 0, x, HEIGHT), fill=(8, 13, 34, alpha))
    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(str(_font_path(True)), 68)
    subtitle_font = ImageFont.truetype(str(_font_path()), 26)
    tag_font = ImageFont.truetype(str(_font_path(True)), 18)
    draw.rounded_rectangle((74, 86, 315, 126), radius=20, fill=(246, 202, 104, 238))
    draw.text((95, 94), "AIGC课程 · 作业4", font=tag_font, fill=(17, 22, 42))
    draw.text((74, 205), title, font=title_font, fill="white")
    draw.text((78, 306), subtitle, font=subtitle_font, fill=(230, 232, 242))
    draw.line((78, 365, 530, 365), fill=(246, 202, 104), width=4)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, quality=94)


def _subtitle_image(item: dict[str, Any], output: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("缺少Pillow，请先安装requirements.txt") from exc

    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    body_font = ImageFont.truetype(str(_font_path(True)), 32)
    meta_font = ImageFont.truetype(str(_font_path(True)), 19)
    text = str(item["text"])
    text_box = draw.textbbox((0, 0), text, font=body_font)
    text_width = text_box[2] - text_box[0]
    box_width = min(1140, max(620, text_width + 230))
    left = (WIDTH - box_width) // 2
    top = 565
    right = left + box_width
    bottom = 680
    draw.rounded_rectangle((left, top, right, bottom), radius=26, fill=(10, 15, 36, 218))
    draw.rounded_rectangle((left + 20, top + 19, left + 150, top + 54), radius=17, fill=(246, 202, 104, 242))
    draw.text((left + 38, top + 25), str(item["role"]), font=meta_font, fill=(17, 22, 42))
    emotion = f"[{item['emotion']}]"
    draw.text((left + 168, top + 26), emotion, font=meta_font, fill=(194, 198, 214))
    draw.text(((WIDTH - text_width) / 2, top + 65), text, font=body_font, fill="white")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def _generate_bgm(output: Path, duration: float, sample_rate: int = 24_000) -> None:
    chords = [
        (261.63, 329.63, 392.00),
        (220.00, 261.63, 329.63),
        (174.61, 220.00, 261.63),
        (196.00, 246.94, 293.66),
    ]
    total_frames = int(duration * sample_rate)
    samples = array("h")
    fade_seconds = 2.5
    for frame in range(total_frames):
        time = frame / sample_rate
        chord = chords[int(time // 8) % len(chords)]
        slow_pulse = 0.72 + 0.28 * math.sin(2 * math.pi * time / 6) ** 2
        value = sum(math.sin(2 * math.pi * frequency * time) for frequency in chord)
        value += 0.25 * math.sin(2 * math.pi * chord[0] * 2 * time)
        sparkle = 0.0
        if int(time * 2) % 16 == 0:
            sparkle = 0.18 * math.sin(2 * math.pi * 1046.5 * time)
        envelope = min(1.0, time / fade_seconds, (duration - time) / fade_seconds)
        sample = int(32767 * 0.07 * max(0.0, envelope) * (slow_pulse * value / 3.25 + sparkle))
        samples.append(max(-32768, min(32767, sample)))
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())


def _run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def _encoder_args(encoder: str) -> list[str]:
    if encoder == "h264_nvenc":
        return ["-c:v", encoder, "-preset", "p4", "-cq", "23", "-b:v", "0"]
    if encoder == "h264_mf":
        return ["-c:v", encoder, "-b:v", "5M"]
    return ["-c:v", "mpeg4", "-q:v", "3"]


def _select_encoder(ffmpeg: Path, temp_dir: Path) -> str:
    for encoder in ("h264_nvenc", "h264_mf", "mpeg4"):
        test_output = temp_dir / f"encoder-{encoder}.mp4"
        command = [
            str(ffmpeg), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
            "color=c=black:s=160x90:r=24:d=0.2", *_encoder_args(encoder),
            "-pix_fmt", "yuv420p", str(test_output),
        ]
        if subprocess.run(command, capture_output=True).returncode == 0:
            return encoder
    raise RuntimeError("本机FFmpeg没有可用的MP4视频编码器")


def _build_voice_track(
    ffmpeg: Path, audiobook: Path, plan: dict[str, Any], output: Path, temp_dir: Path
) -> None:
    labels: list[str] = []
    filters = [f"anullsrc=r=24000:cl=mono:d={INTRO_SECONDS}[intro]"]
    labels.append("[intro]")
    for index, section in enumerate(plan["sections"]):
        filters.append(
            f"[0:a]atrim=start={section['source_start']}:end={section['source_end']},"
            f"asetpts=PTS-STARTPTS[voice{index}]"
        )
        labels.append(f"[voice{index}]")
        if index < len(plan["sections"]) - 1:
            filters.append(f"anullsrc=r=24000:cl=mono:d={GAP_SECONDS}[gap{index}]")
            labels.append(f"[gap{index}]")
    filters.append(f"anullsrc=r=24000:cl=mono:d={OUTRO_SECONDS}[outro]")
    labels.append("[outro]")
    filters.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[voiceout]")
    filter_path = temp_dir / "voice-filter.txt"
    filter_path.write_text(";\n".join(filters), encoding="utf-8")
    _run([
        str(ffmpeg), "-y", "-loglevel", "error", "-i", str(audiobook),
        "-filter_complex_script", str(filter_path), "-map", "[voiceout]",
        "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(output),
    ])


def _render_clip(
    ffmpeg: Path, image: Path, duration: float, output: Path, encoder: str, direction: int
) -> None:
    frames = max(1, round(duration * FPS))
    zoom_rate = 0.00018 if direction % 2 == 0 else 0.00012
    x_offset = "iw/2-(iw/zoom/2)" if direction % 2 == 0 else "iw-(iw/zoom)"
    video_filter = (
        f"scale=1536:1024,zoompan=z='min(1+on*{zoom_rate},1.08)':"
        f"x='{x_offset}':y='ih/2-(ih/zoom/2)':d=1:s={WIDTH}x{HEIGHT}:fps={FPS},"
        "format=yuv420p"
    )
    _run([
        str(ffmpeg), "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS),
        "-i", str(image), "-vf", video_filter, "-frames:v", str(frames),
        *_encoder_args(encoder), "-pix_fmt", "yuv420p", "-an", str(output),
    ])


def _concat_clips(ffmpeg: Path, clips: list[Path], output: Path, temp_dir: Path) -> None:
    manifest = temp_dir / "video-concat.txt"
    manifest.write_text(
        "".join(f"file '{clip.resolve().as_posix()}'\n" for clip in clips),
        encoding="utf-8",
    )
    _run([
        str(ffmpeg), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", str(manifest), "-c", "copy", str(output),
    ])


def _compose_final(
    ffmpeg: Path,
    base_video: Path,
    voice_track: Path,
    bgm: Path,
    subtitle_files: list[Path],
    plan: dict[str, Any],
    output: Path,
    encoder: str,
    temp_dir: Path,
) -> None:
    command = [
        str(ffmpeg), "-y", "-loglevel", "error", "-i", str(base_video),
        "-i", str(voice_track), "-i", str(bgm),
    ]
    for subtitle_file in subtitle_files:
        command.extend(["-loop", "1", "-framerate", str(FPS), "-i", str(subtitle_file)])

    filters = ["[0:v]setpts=PTS-STARTPTS[v0]"]
    previous = "v0"
    for index, subtitle in enumerate(plan["subtitles"]):
        output_label = f"v{index + 1}"
        filters.append(
            f"[{previous}][{index + 3}:v]overlay=0:0:"
            f"enable='between(t,{subtitle['start']},{subtitle['end']})':eof_action=pass[{output_label}]"
        )
        previous = output_label
    duration = float(plan["duration_seconds"])
    filters.extend(
        [
            "[1:a]aresample=48000,volume=1.0[voice]",
            f"[2:a]aresample=48000,volume=0.19,afade=t=in:st=0:d=2,"
            f"afade=t=out:st={max(0, duration - 3):.3f}:d=3[music]",
            "[voice][music]amix=inputs=2:duration=longest:dropout_transition=2:normalize=0[aout]",
        ]
    )
    filter_path = temp_dir / "final-filter.txt"
    filter_path.write_text(";\n".join(filters), encoding="utf-8")
    command.extend(
        [
            "-filter_complex_script", str(filter_path), "-map", f"[{previous}]", "-map", "[aout]",
            "-t", f"{duration:.3f}", "-r", str(FPS), *_encoder_args(encoder),
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(output),
        ]
    )
    _run(command)


def build_story_video(
    timeline_path: Path,
    audiobook_path: Path,
    images_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "temp"
    subtitle_dir = temp_dir / "subtitles"
    clip_dir = temp_dir / "clips"
    subtitle_dir.mkdir(parents=True, exist_ok=True)
    clip_dir.mkdir(parents=True, exist_ok=True)

    plan = create_video_plan(timeline_path)
    ffmpeg = find_ffmpeg()
    encoder = _select_encoder(ffmpeg, temp_dir)
    plan["video_encoder"] = encoder

    title_card = temp_dir / "title-card.jpg"
    outro_card = temp_dir / "outro-card.jpg"
    _cover_image(
        images_dir / "scene-01.png",
        "小雨和月光脚印",
        "一场关于观察、勇气与帮助的月光冒险",
        title_card,
    )
    _cover_image(
        images_dir / "scene-03.png",
        "真正的勇气",
        "在害怕的时候看清线索，认真思考，然后伸出帮助的手。",
        outro_card,
    )

    voice_track = temp_dir / "voice-track.wav"
    bgm = output_dir / "background-music.wav"
    _build_voice_track(ffmpeg, audiobook_path, plan, voice_track, temp_dir)
    _generate_bgm(bgm, float(plan["duration_seconds"]))

    clips: list[Path] = []
    intro_clip = clip_dir / "000-intro.mp4"
    _render_clip(ffmpeg, title_card, INTRO_SECONDS, intro_clip, encoder, 0)
    clips.append(intro_clip)
    for index, section in enumerate(plan["sections"], start=1):
        clip = clip_dir / f"{index:03d}-segment.mp4"
        clip_duration = float(section["duration"])
        if index < len(plan["sections"]):
            clip_duration += GAP_SECONDS
        _render_clip(
            ffmpeg,
            images_dir / section["image"],
            clip_duration,
            clip,
            encoder,
            index,
        )
        clips.append(clip)
    outro_clip = clip_dir / "999-outro.mp4"
    _render_clip(ffmpeg, outro_card, OUTRO_SECONDS, outro_clip, encoder, 8)
    clips.append(outro_clip)

    base_video = temp_dir / "base-video.mp4"
    _concat_clips(ffmpeg, clips, base_video, temp_dir)

    subtitle_files: list[Path] = []
    for index, subtitle in enumerate(plan["subtitles"], start=1):
        path = subtitle_dir / f"subtitle-{index:03d}.png"
        _subtitle_image(subtitle, path)
        subtitle_files.append(path)

    output_video = output_dir / "xiaoyu-story-video.mp4"
    _compose_final(
        ffmpeg,
        base_video,
        voice_track,
        bgm,
        subtitle_files,
        plan,
        output_video,
        encoder,
        temp_dir,
    )
    shutil.copy2(title_card, output_dir / "thumbnail.jpg")

    try:
        from mutagen.mp4 import MP4
    except ImportError as exc:
        raise RuntimeError("缺少mutagen，请先安装requirements.txt") from exc
    actual_duration = float(MP4(output_video).info.length)
    if actual_duration < 60:
        raise RuntimeError(f"成品仅{actual_duration:.1f}秒，未达到60秒课程要求")
    plan["actual_duration_seconds"] = round(actual_duration, 3)
    plan["output_file"] = output_video.name
    plan_path = output_dir / "video-plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan
