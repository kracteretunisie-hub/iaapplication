import os
import streamlit as st
import fal_client

# ---------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------

st.set_page_config(
    page_title="IA Video Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 IA Video Generator")

st.write(
    "Décris la vidéo que tu veux créer et l'intelligence artificielle "
    "va générer une vidéo automatiquement."
)

# ---------------------------------------------------
# RÉCUPÉRATION DE LA CLÉ API
# ---------------------------------------------------

try:
    FAL_KEY = st.secrets["FAL_KEY"]
    os.environ["FAL_KEY"] = FAL_KEY
except Exception:
    st.error(
        "La clé API FAL_KEY n'est pas configurée. "
        "Ajoute-la dans les Secrets de Streamlit."
    )
    st.stop()


# ---------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------

prompt = st.text_area(
    "Décrivez votre vidéo",
    placeholder=(
        "Exemple : Une femme portant une longue robe rouge tourne "
        "lentement dans une rue de Paris au coucher du soleil, "
        "style cinématographique."
    ),
    height=150
)

duration_label = st.selectbox(
    "Durée",
    [
        "5 secondes",
        "10 secondes"
    ]
)

format_label = st.selectbox(
    "Format",
    [
        "16:9 - YouTube",
        "9:16 - TikTok / Reels",
        "1:1 - Instagram"
    ]
)

audio = st.checkbox(
    "Générer aussi l'audio",
    value=False
)

negative_prompt = st.text_input(
    "Éléments à éviter",
    value="blur, distort, low quality, deformed hands, bad anatomy"
)


# ---------------------------------------------------
# CONVERSION DES OPTIONS
# ---------------------------------------------------

if duration_label == "5 secondes":
    duration = "5"
else:
    duration = "10"


if format_label.startswith("16:9"):
    aspect_ratio = "16:9"

elif format_label.startswith("9:16"):
    aspect_ratio = "9:16"

else:
    aspect_ratio = "1:1"


# ---------------------------------------------------
# GÉNÉRATION VIDÉO
# ---------------------------------------------------

if st.button(
    "🎬 Générer la vidéo",
    type="primary",
    use_container_width=True
):

    if not prompt.strip():
        st.warning("Veuillez d'abord écrire une description de vidéo.")

    else:

        progress_message = st.empty()

        progress_message.info(
            "⏳ Génération en cours... Cela peut prendre plusieurs minutes."
        )

        try:

            def on_queue_update(update):

                if isinstance(update, fal_client.InProgress):

                    if update.logs:

                        last_log = update.logs[-1]

                        if isinstance(last_log, dict):

                            message = last_log.get(
                                "message",
                                "Génération en cours..."
                            )

                            progress_message.info(
                                "⏳ " + message
                            )


            result = fal_client.subscribe(
                "fal-ai/kling-video/v3/standard/text-to-video",

                arguments={
                    "prompt": prompt,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "generate_audio": audio,
                    "negative_prompt": negative_prompt,
                    "cfg_scale": 0.5
                },

                with_logs=True,

                on_queue_update=on_queue_update,

                client_timeout=900
            )


            # -----------------------------------------
            # RÉCUPÉRER L'URL DE LA VIDÉO
            # -----------------------------------------

            video_url = result["video"]["url"]

            progress_message.success(
                "✅ Vidéo générée avec succès !"
            )


            # -----------------------------------------
            # AFFICHER LA VIDÉO
            # -----------------------------------------

            st.video(video_url)


            # -----------------------------------------
            # AFFICHER LES INFORMATIONS
            # -----------------------------------------

            st.subheader("Informations")

            st.write("**Prompt :**")
            st.write(prompt)

            st.write(
                f"**Durée :** {duration} secondes"
            )

            st.write(
                f"**Format :** {aspect_ratio}"
            )


            # -----------------------------------------
            # LIEN VIDÉO
            # -----------------------------------------

            st.link_button(
                "⬇️ Ouvrir / télécharger la vidéo",
                video_url,
                use_container_width=True
            )


        except Exception as e:

            progress_message.empty()

            st.error(
                "❌ Une erreur est survenue pendant la génération."
            )

            st.exception(e)
