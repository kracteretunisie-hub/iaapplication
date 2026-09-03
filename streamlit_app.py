import streamlit as st

st.set_page_config(
    page_title="IA Video",
    page_icon="🎬"
)

st.title("🎬 IA Video Generator")
st.write("Créez une vidéo avec l'intelligence artificielle.")

prompt = st.text_area(
    "Décrivez votre vidéo",
    placeholder="Exemple : une voiture futuriste roulant dans Tokyo la nuit..."
)

duration = st.selectbox(
    "Durée",
    ["5 secondes", "10 secondes"]
)

format_video = st.selectbox(
    "Format",
    ["16:9 - YouTube", "9:16 - TikTok / Reels", "1:1 - Instagram"]
)

if st.button("🎬 Générer la vidéo"):
    if not prompt:
        st.warning("Veuillez décrire la vidéo.")
    else:
        st.info("Génération de la vidéo...")
        st.write("Prompt :", prompt)
        st.write("Durée :", duration)
        st.write("Format :", format_video)
