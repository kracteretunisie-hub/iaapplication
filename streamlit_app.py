import os
import streamlit as st
import fal_client

# ---------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="IA Video Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 IA Video Generator")

st.write(
    "Crée une vidéo avec l'intelligence artificielle."
)

# ---------------------------------------------------
# VERIFICATION DE LA CLE FAL
# ---------------------------------------------------

if "FAL_KEY" not in st.secrets:
    st.error("❌ FAL_KEY absente dans Streamlit Secrets.")
    st.info(
        'Va dans Streamlit Cloud > Settings > Secrets et ajoute :\n\n'
        'FAL_KEY = "ta_cle_fal"'
    )
    st.stop()

fal_key = str(st.secrets["FAL_KEY"]).strip()

if not fal_key:
    st.error("❌ La clé FAL_KEY est vide.")
    st.stop()

# Envoi de la clé au client fal.ai
os.environ["FAL_KEY"] = fal_key

st.success("✅ Clé fal.ai détectée")

# ---------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------

prompt = st.text_area(
    "Décrivez votre vidéo",
    placeholder=(
        "Exemple : une femme avec une longue robe rouge "
        "tourne lentement dans une rue de Paris, "
        "style cinématographique"
    ),
    height=140
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

generate_audio = st.checkbox(
    "Générer aussi l'audio",
    value=False
)

negative_prompt = st.text_input(
    "Éléments à éviter",
    value="blur, low quality, distorted face, deformed hands"
)

# ---------------------------------------------------
# CONVERSION DES PARAMETRES
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
# GENERATION
# ---------------------------------------------------

if st.button(
    "🎬 Générer la vidéo",
    type="primary",
    use_container_width=True
):

    if not prompt.strip():
        st.warning("⚠️ Écris d'abord une description de vidéo.")
        st.stop()

    status = st.empty()

    status.info(
        "⏳ Génération en cours... "
        "Cela peut prendre plusieurs minutes."
    )

    try:

        def on_queue_update(update):
            try:
                if isinstance(update, fal_client.InProgress):
                    if update.logs:
                        last_log = update.logs[-1]

                        if isinstance(last_log, dict):
                            message = last_log.get(
                                "message",
                                "Génération en cours..."
                            )

                            status.info(
                                f"⏳ {message}"
                            )
            except Exception:
                pass

        result = fal_client.subscribe(
            "fal-ai/kling-video/v3/standard/text-to-video",
            arguments={
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "generate_audio": generate_audio,
                "negative_prompt": negative_prompt,
                "cfg_scale": 0.5
            },
            with_logs=True,
            on_queue_update=on_queue_update,
            client_timeout=900
        )

        # ---------------------------------------------------
        # VERIFICATION DU RESULTAT
        # ---------------------------------------------------

        if not result:
            status.empty()
            st.error("❌ Aucun résultat reçu de fal.ai.")
            st.stop()

        if "video" not in result:
            status.empty()

            st.error(
                "❌ fal.ai a répondu, mais aucune vidéo "
                "n'a été retournée."
            )

            st.write("Réponse reçue :")
            st.json(result)

            st.stop()

        video = result["video"]

        if not isinstance(video, dict):
            status.empty()
            st.error("❌ Format de réponse vidéo inattendu.")
            st.json(result)
            st.stop()

        video_url = video.get("url")

        if not video_url:
            status.empty()
            st.error("❌ URL de vidéo introuvable.")
            st.json(result)
            st.stop()

        # ---------------------------------------------------
        # SUCCES
        # ---------------------------------------------------

        status.success("✅ Vidéo générée avec succès !")

        st.subheader("🎥 Votre vidéo")

        st.video(video_url)

        st.subheader("Informations")

        st.write("**Prompt :**")
        st.write(prompt)

        st.write(
            f"**Durée :** {duration} secondes"
        )

        st.write(
            f"**Format :** {aspect_ratio}"
        )

        if generate_audio:
            st.write("**Audio :** oui")
        else:
            st.write("**Audio :** non")

        st.link_button(
            "⬇️ Ouvrir la vidéo",
            video_url,
            use_container_width=True
        )

    # ---------------------------------------------------
    # ERREURS
    # ---------------------------------------------------

    except Exception as e:

        status.empty()

        error_message = str(e)

        if "invalid key credentials" in error_message.lower():

            st.error(
                "❌ Clé fal.ai invalide."
            )

            st.warning(
                "Crée une nouvelle clé API sur fal.ai, "
                "puis remplace FAL_KEY dans Streamlit Secrets."
            )

        elif (
            "insufficient" in error_message.lower()
            or "balance" in error_message.lower()
            or "credits" in error_message.lower()
        ):

            st.error(
                "💳 Ton compte fal.ai n'a probablement "
                "pas assez de crédits."
            )

            st.info(
                "Ajoute des crédits sur ton compte fal.ai "
                "puis réessaie."
            )

        elif "timeout" in error_message.lower():

            st.error(
                "⏱️ La génération a pris trop de temps."
            )

            st.info(
                "Réessaie avec une vidéo plus courte."
            )

        else:

            st.error(
                "❌ Une erreur est survenue pendant "
                "la génération."
            )

            st.exception(e)
