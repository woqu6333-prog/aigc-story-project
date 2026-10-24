"""按MiniMax H3 Ref2VA六段规范构造儿童故事镜头提示词。"""

from __future__ import annotations


def build_ref2va_prompt(
    *,
    character_name: str,
    action: str,
    scene: str,
    mood: str,
    duration: int = 5,
) -> str:
    if duration < 4 or duration > 15:
        raise ValueError("H3单镜头时长必须在4到15秒之间")
    return f"""subject_definitions:
<Subject 1> is {character_name}, the young girl defined by <Picture 1>, with a short black bob, two gold crescent hair clips, a bright yellow raincoat with navy toggles, a teal crossbody bag with an orange dinosaur patch, white socks, and glossy red rain boots. Her identity, age, hairstyle, outfit colors, bag, and childlike watercolor-animation proportions remain unchanged.
<Subject 2> is the moonlit forest environment and composition in <Picture 2>, with wet leaves, a muddy path, tiny three-toed footprints, warm fireflies, blue night trees, and a large full moon.
<Picture 2> is the first-frame composition anchor for [Shot 1].

summary:
[reference generation + keyframe completion] A {duration}-second children's storybook animation begins exactly from <Picture 2>. <Subject 1> performs one clear action—{action}—inside <Subject 2>, while the camera makes one restrained movement and the environment responds naturally.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, short black hair, crescent clips, yellow raincoat, teal dinosaur bag, white socks, red boots, age, and watercolor-animation identity stay consistent.
<Subject 2> (appears in [Shot 1]): fully_preserved - the wet moonlit forest, muddy path, small three-toed footprints, fireflies, blue trees, and full moon remain recognizable.
<Picture 2> ([Shot 1] first frame): fully_preserved - the opening composition, subject placement, lighting direction, and forest layout match the reference frame before motion begins.

detailed_description:
The target video uses a polished children's picture-book animation style matching the references, with tactile watercolor-and-gouache textures, soft volumetric moonlight, stable anatomy, and coherent motion. The emotional tone is {mood}. The entire clip is one continuous shot with no cut, no transformation, and no new character.

[Shot 1] The shot begins exactly from <Picture 2>. <Subject 1> occupies the same position and scale as in the reference frame inside <Subject 2>. For the first second she holds the reference pose steadily, then {action}. Her head, shoulders, elbows, fingers, coat hem, bag strap, and boots move with small physically plausible childlike motion; her face stays on-model and her eyes blink once naturally. The teal bag remains attached across her body and the orange dinosaur patch never changes. Wet leaves shift under a faint breeze, two or three fireflies drift slowly without multiplying, and one raindrop falls from a leaf into the puddle, creating a small circular ripple. The tiny three-toed footprints remain fixed in the mud and do not crawl or transform. The camera performs only a very slow five-percent push-in toward her face and pointing hand, with no orbit, no whip pan, and no sudden zoom. By the final second she settles into a readable pose and looks toward the next footprint, creating a clean continuation point. No lip-synced dialogue, no text, no subtitles, no extra limbs, no duplicated child, no costume change, no melting objects, and no fantasy explosion.

overall_soundscape:
Quiet moonlit forest ambience with soft leaves, distant insects, a tiny water droplet, one gentle puddle ripple, subtle raincoat fabric movement, and light boot contact with damp ground. No dialogue and no singing.

non_diegetic_music:
A delicate audience-only score at a slow tempo, led by celesta and soft pizzicato strings, beginning almost inaudibly and ending on one warm unresolved note suitable for continuing the story."""
