import streamlit as st
import numpy as np
import imageio.v2 as imageio

from PIL import Image, ImageDraw, ImageFont
from tempfile import NamedTemporaryFile
import hashlib
import math
import os
import textwrap


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IA Video Generator Free",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 IA Video Generator")
st.write("Crée gratuitement une petite vidéo animée à partir de ton texte.")

st.success("✅ Version gratuite — aucune clé API nécessaire")


# ============================================================
# FORMULAIRE
# ============================================================

prompt = st.text_area(
    "Décrivez votre vidéo",
    placeholder=(
        "Exemple : une femme avec une longue robe rouge "
        "marche dans Paris au coucher du soleil"
    ),
    height=140
)

duration = st.selectbox(
    "Durée",
    [
        5,
        10
    ],
    format_func=lambda x: f"{x} secondes"
)

format_video = st.selectbox(
    "Format",
    [
        "16:9 - YouTube",
        "9:16 - TikTok / Reels",
        "1:1 - Instagram"
    ]
)

show_text = st.checkbox(
    "Afficher le texte dans la vidéo",
    value=True
)


# ============================================================
# CHOISIR LA TAILLE
# ============================================================

def get_video_size(format_name):

    if format_name.startswith("16:9"):
        return 640, 360

    elif format_name.startswith("9:16"):
        return 360, 640

    else:
        return 512, 512


# ============================================================
# CREER DES VALEURS A PARTIR DU PROMPT
# ============================================================

def prompt_seed(text):

    digest = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    return int(
        digest[:8],
        16
    )


# ============================================================
# TEXTE
# ============================================================

def draw_centered_text(
    draw,
    text,
    width,
    height
):

    try:
        font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            max(20, width // 25)
        )
    except:
        font = ImageFont.load_default()

    max_chars = max(
        15,
        width // 18
    )

    wrapped = textwrap.wrap(
        text,
        width=max_chars
    )

    wrapped = wrapped[:4]

    line_height = max(
        30,
        height // 18
    )

    total_height = (
        len(wrapped)
        * line_height
    )

    y = (
        height
        - total_height
    ) // 2

    for line in wrapped:

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        text_width = (
            bbox[2]
            - bbox[0]
        )

        x = (
            width
            - text_width
        ) // 2

        # ombre
        draw.text(
            (
                x + 2,
                y + 2
            ),
            line,
            font=font,
            fill=(0, 0, 0)
        )

        # texte principal
        draw.text(
            (
                x,
                y
            ),
            line,
            font=font,
            fill=(255, 255, 255)
        )

        y += line_height


# ============================================================
# GENERER UNE IMAGE
# ============================================================

def create_frame(
    width,
    height,
    frame_number,
    total_frames,
    prompt,
    seed,
    display_text
):

    rng = np.random.default_rng(
        seed
    )

    t = (
        frame_number
        / total_frames
    )

    # Couleurs déterminées par le prompt
    base_1 = rng.integers(
        20,
        180,
        size=3
    )

    base_2 = rng.integers(
        80,
        240,
        size=3
    )

    frame = np.zeros(
        (
            height,
            width,
            3
        ),
        dtype=np.uint8
    )

    # --------------------------------------------------------
    # FOND EN DEGRADE ANIME
    # --------------------------------------------------------

    for y in range(height):

        ratio = (
            y
            / max(
                1,
                height - 1
            )
        )

        wave = (
            math.sin(
                t
                * math.pi
                * 2
                + ratio
                * 3
            )
            * 0.15
        )

        ratio2 = np.clip(
            ratio + wave,
            0,
            1
        )

        color = (
            base_1
            * (
                1
                - ratio2
            )
            +
            base_2
            * ratio2
        )

        frame[
            y,
            :,
            :
        ] = color.astype(
            np.uint8
        )

    image = Image.fromarray(
        frame
    )

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    # --------------------------------------------------------
    # LUMIERE CENTRALE ANIMEE
    # --------------------------------------------------------

    center_x = int(
        width
        * (
            0.5
            +
            0.15
            * math.sin(
                t
                * math.pi
                * 2
            )
        )
    )

    center_y = int(
        height
        * (
            0.45
            +
            0.1
            * math.cos(
                t
                * math.pi
                * 2
            )
        )
    )

    for radius in range(
        int(width * 0.30),
        10,
        -20
    ):

        alpha = int(
            4
            +
            (
                radius
                / width
            )
            * 18
        )

        draw.ellipse(
            [
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius
            ],
            fill=(
                255,
                255,
                255,
                alpha
            )
        )

    # --------------------------------------------------------
    # PARTICULES
    # --------------------------------------------------------

    particle_rng = np.random.default_rng(
        seed + 999
    )

    particle_count = 35

    for i in range(
        particle_count
    ):

        start_x = particle_rng.random()
        start_y = particle_rng.random()

        speed = (
            0.05
            +
            particle_rng.random()
            * 0.20
        )

        x = int(
            (
                start_x
                +
                math.sin(
                    t * 5 + i
                )
                * 0.03
            )
            * width
        )

        y_position = (
            start_y
            -
            t * speed
        ) % 1

        y = int(
            y_position
            * height
        )

        radius = int(
            1
            +
            particle_rng.random()
            * 4
        )

        draw.ellipse(
            [
                x - radius,
                y - radius,
                x + radius,
                y + radius
            ],
            fill=(
                255,
                255,
                255,
                100
            )
        )

    # --------------------------------------------------------
    # CINEMA BARS POUR 16:9
    # --------------------------------------------------------

    if width > height:

        bar_height = int(
            height
            * 0.07
        )

        draw.rectangle(
            [
                0,
                0,
                width,
                bar_height
            ],
            fill=(
                0,
                0,
                0,
                180
            )
        )

        draw.rectangle(
            [
                0,
                height - bar_height,
                width,
                height
            ],
            fill=(
                0,
                0,
                0,
                180
            )
        )

    # --------------------------------------------------------
    # TEXTE
    # --------------------------------------------------------

    if display_text:

        # panneau sombre transparent
        margin = int(
            width
            * 0.08
        )

        panel_height = int(
            height
            * 0.35
        )

        panel_top = (
            height
            - panel_height
        ) // 2

        draw.rounded_rectangle(
            [
                margin,
                panel_top,
                width - margin,
                panel_top + panel_height
            ],
            radius=20,
            fill=(
                0,
                0,
                0,
                75
            )
        )

        draw_centered_text(
            draw,
            prompt,
            width,
            height
        )

    return np.asarray(
        image.convert("RGB")
    )


# ============================================================
# CREER LA VIDEO
# ============================================================

def generate_video(
    prompt,
    duration,
    format_video,
    display_text
):

    width, height = get_video_size(
        format_video
    )

    fps = 20

    total_frames = (
        duration
        * fps
    )

    seed = prompt_seed(
        prompt
    )

    temp_file = NamedTemporaryFile(
        suffix=".mp4",
        delete=False
    )

    temp_path = temp_file.name

    temp_file.close()

    writer = imageio.get_writer(
        temp_path,
        fps=fps,
        codec="libx264",
        quality=7,
        macro_block_size=None
    )

    progress = st.progress(
        0
    )

    status = st.empty()

    for frame_number in range(
        total_frames
    ):

        frame = create_frame(
            width,
            height,
            frame_number,
            total_frames,
            prompt,
            seed,
            display_text
        )

        writer.append_data(
            frame
        )

        percentage = int(
            (
                frame_number + 1
            )
            / total_frames
            * 100
        )

        progress.progress(
            percentage
        )

        status.write(
            f"🎬 Création de la vidéo : {percentage}%"
        )

    writer.close()

    progress.empty()

    status.success(
        "✅ Vidéo terminée !"
    )

    return temp_path


# ============================================================
# BOUTON
# ============================================================

if st.button(
    "🎬 Générer gratuitement",
    type="primary",
    use_container_width=True
):

    if not prompt.strip():

        st.warning(
            "Écris d'abord une description."
        )

    else:

        try:

            video_path = generate_video(
                prompt,
                duration,
                format_video,
                show_text
            )

            st.subheader(
                "🎥 Votre vidéo"
            )

            st.video(
                video_path
            )

            with open(
                video_path,
                "rb"
            ) as video_file:

                video_bytes = (
                    video_file.read()
                )

            st.download_button(
                "⬇️ Télécharger la vidéo MP4",
                data=video_bytes,
                file_name="ma_video.mp4",
                mime="video/mp4",
                use_container_width=True
            )

            st.info(
                "Cette version fonctionne sans API et sans crédits."
            )

        except Exception as e:

            st.error(
                "Une erreur est survenue."
            )

            st.exception(
                e
            )
