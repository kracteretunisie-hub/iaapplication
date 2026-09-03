import os
import streamlit as st

# ---------------------------------------------------
# CONFIGURATION PAGE
# ---------------------------------------------------

st.set_page_config(
    page_title="IA Video Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 IA Video Generator")
st.write("Crée une vidéo avec l'intelligence artificielle.")

# ---------------------------------------------------
# RECUPERER LA CLE AVANT D'IMPORTER fal_client
# ---------------------------------------------------

if "FAL_KEY" not in st.secrets:
    st.error("❌ FAL_KEY absente dans Streamlit Secrets.")
    st.stop()

fal_key = str(st.secrets["FAL_KEY"])

# Nettoyer espaces et retours à la ligne accidentels
fal_key = fal_key.replace("\n", "").replace("\r", "").strip()

if not fal_key:
    st.error("❌ FAL_KEY est vide.")
    st.stop()

# IMPORTANT :
# définir FAL_KEY AVANT import fal_client
os.environ["FAL_KEY"] = fal_key

import fal_client

# ---------------------------------------------------
# INFORMATIONS DE DIAGNOSTIC
# ---------------------------------------------------

st.success("✅ Clé fal.ai chargée")

# On n'affiche jamais la vraie clé
st.caption(f"Clé détectée : {len(fal_key)} caractères")

# ---------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------

prompt = st.text_area(
    "Décrivez votre vidéo",
    placeholder=(
        "Exemple : une femme avec une longue robe rouge tourne "
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

generate_audio = st.checkbox(
    "Générer aussi l'audio",
    value=False
)

negative_prompt = st.text_input(
    "Éléments à éviter",
    value="blur, low quality, distorted face, deformed hands"
)

# ---------------------------------------------------
# CONVERSION PARAMETRES
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
# GENERATION VIDEO
# ---------------------------------------------------

if st.button(
    "🎬 Générer la vidéo",
    type="primary",
    use_container_width=True
):

    if not prompt.strip():
        st.warning("⚠️ Écris d'abord une description.")
        st.stop()

    status = st.empty()

    status.info(
        "⏳ Connexion à fal.ai et génération de la vidéo..."
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

                        status.info(
                            f"⏳ {message}"
                        )

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
        # VERIFICATION RESULTAT
        # ---------------------------------------------------

        if not result:
            status.empty()
            st.error("❌ Aucun résultat reçu.")
            st.stop()

        if "video" not in result:
            status.empty()

            st.error(
                "❌ fal.ai a répondu mais aucune vidéo "
                "n'a été retournée."
            )

            st.json(result)

            st.stop()

        video_url = result["video"].get("url")

        if not video_url:
            status.empty()
            st.error("❌ URL vidéo introuvable.")
            st.json(result)
            st.stop()

        # ---------------------------------------------------
        # SUCCES
        # ---------------------------------------------------

        status.success("✅ Vidéo générée avec succès !")

        st.subheader("🎥 Votre vidéo")

        st.video(video_url)

        st.write("**Prompt :**", prompt)
        st.write("**Durée :**", duration, "secondes")
        st.write("**Format :**", aspect_ratio)

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

            st.error("❌ fal.ai refuse toujours la clé.")

            st.write(
                "La clé est bien chargée par Streamlit, "
                "mais fal.ai ne la reconnaît pas."
            )

            st.info(
                "Vérifie que tu as créé une clé avec le scope API "
                "et que tu as copié la clé complète."
            )

        elif (
            "insufficient" in error_message.lower()
            or "balance" in error_message.lower()
            or "credits" in error_message.lower()
        ):

            st.error("💳 Crédits fal.ai insuffisants.")

            st.info(
                "Ton compte fal.ai doit avoir des crédits "
                "pour utiliser ce modèle."
            )

        elif "timeout" in error_message.lower():

            st.error(
                "⏱️ La génération a dépassé le temps maximum."
            )

        else:

            st.error(
                "❌ Une autre erreur est survenue."
            )

            st.exception(e)
