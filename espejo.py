import streamlit as st
import requests
import math
import tweepy
import pandas as pd
import spacy
import textstat
from collections import Counter
from alpha_vantage.foreignexchange import ForeignExchange

# --- CARGAR MODELO DE LENGUAJE (Se ejecuta una sola vez) ---
@st.cache_resource
def load_spacy_model():
    # Le decimos a textstat que use el modelo de spaCy para español
    textstat.set_lang("es_ES")
    return spacy.load("es_core_news_sm")

nlp = load_spacy_model()

# --- DEFINICIÓN DE FUNCIONES (El Cerebro) ---

def capturar_energia_economica(api_key):
    # ... (sin cambios)
    try:
        fe = ForeignExchange(key=api_key)
        data, _ = fe.get_currency_exchange_rate(from_currency='EUR', to_currency='USD')
        return float(data['5. Exchange Rate'])
    except Exception as e:
        return 0

# --- FUNCIÓN DE SÍNTESIS DE NIVEL 5 ---
def sintetizar_realidad(api_key, api_secret, access_token, access_secret, intencion):
    try:
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Obtenemos tweets y la información del autor
        tweets = api.search_tweets(q=f"{intencion} -is:retweet", lang="es", count=100, tweet_mode="extended")
        
        if not tweets:
            return {"sistemico": "No se encontraron conversaciones.", "organico": "N/A", "contaminacion": 0}

        textos_sistemicos = []
        textos_organicos = []

        for tweet in tweets:
            # Filtro: ¿Es un actor del sistema?
            # Criterios: Verificado, más de 10,000 seguidores, o fuente conocida (ej. "Twitter for Advertisers")
            es_sistemico = (
                tweet.user.verified or
                tweet.user.followers_count > 10000 or
                tweet.source in ["Twitter for Advertisers", "Twitter Media Studio"]
            )
            
            if es_sistemico:
                textos_sistemicos.append(tweet.full_text)
            else:
                textos_organicos.append(tweet.full_text)

        # 1. Analizar el discurso "Orgánico" (el ruido más puro)
        if textos_organicos:
            texto_completo_organico = " ".join(textos_organicos)
            doc_organico = nlp(texto_completo_organico)
            entidades_organicas = Counter([ent.text for ent in doc_organico.ents if ent.label_ in ['PERSON', 'ORG', 'GPE']]).most_common(5)
            # Medimos la complejidad del lenguaje orgánico
            complejidad_organica = textstat.flesch_reading_ease(texto_completo_organico)
            resultado_organico = {
                "entidades": [f"{ent[0]} ({ent[1]})" for ent in entidades_organicas],
                "complejidad": f"{complejidad_organica:.2f} (Flesch Ease)"
            }
        else:
            resultado_organico = {"entidades": ["N/A"], "complejidad": "N/A"}

        # 2. Analizar el discurso "Sistémico"
        if textos_sistemicos:
            texto_completo_sistemico = " ".join(textos_sistemicos)
            doc_sistemico = nlp(texto_completo_sistemico)
            entidades_sistemicas = Counter([ent.text for ent in doc_sistemico.ents if ent.label_ in ['PERSON', 'ORG', 'GPE']]).most_common(5)
            # Medimos la complejidad del lenguaje sistémico
            complejidad_sistemica = textstat.flesch_reading_ease(texto_completo_sistemico)
            resultado_sistemico = {
                "entidades": [f"{ent[0]} ({ent[1]})" for ent in entidades_sistemicas],
                "complejidad": f"{complejidad_sistemica:.2f} (Flesch Ease)"
            }
        else:
            resultado_sistemico = {"entidades": ["N/A"], "complejidad": "N/A"}

        # 3. Calcular el Índice de Contaminación
        total_tweets = len(textos_sistemicos) + len(textos_organicos)
        if total_tweets > 0:
            indice_contaminacion = (len(textos_sistemicos) / total_tweets) * 100
        else:
            indice_contaminacion = 0

        return {
            "sistemico": resultado_sistemico,
            "organico": resultado_organico,
            "contaminacion": indice_contaminacion
        }

    except Exception as e:
        return {"sistemico": {"entidades": [f"Error: {e}"], "complejidad": "Error"}, "organico": {"entidades": ["Error"], "complejidad": "Error"}, "contaminacion": -1}

# --- INTERFAZ ---
st.set_page_config(page_title="Oráculo Sincrónico", layout="wide")
st.title("Oráculo Sincrónico")
st.subheader("Filtro de Realidad - Nivel 5")
intencion_usuario = st.text_input("Define tu intención o el concepto a sintonizar:", "libertad")

# --- PROCESO DE SINTONIZACIÓN ---
if st.button("Sintonizar"):
    with st.spinner("Aplicando filtro de realidad..."):
        # Recuperar claves
        ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage_key"]
        TWITTER_API_KEY = st.secrets["twitter_api_key"]
        TWITTER_API_SECRET = st.secrets["twitter_api_key_secret"]
        TWITTER_ACCESS_TOKEN = st.secrets["twitter_access_token"]
        TWITTER_ACCESS_SECRET = st.secrets["twitter_access_token_secret"]
        
        # Datos básicos
        energia_economica = capturar_energia_economica(ALPHA_VANTAGE_API_KEY)
        
        # El nuevo sintetizador
        resultado_sintesis = sintetizar_realidad(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, intencion_usuario)
        
        # Presentar el Diagnóstico
        st.header("Diagnóstico del Sintetizador")
        st.metric(label="Energía Económica (EUR/USD)", value=f"{energia_economica:.4f}")
        st.metric(label="Índice de Contaminación Sistémica", value=f"{resultado_sintesis['contaminacion']:.2f}%")
        st.info("Este índice mide qué porcentaje de la conversación está siendo impulsado por actores del 'sistema' (medios, corporaciones, cuentas verificadas).")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Realidad Orgánica (El Ruido 'Puro')")
            st.write("**Actores Principales:**", ", ".join(resultado_sintesis["organico"]["entidades"]))
            st.write("**Complejidad Lingüística:**", resultado_sintesis["organico"]["complejidad"])
        with col2:
            st.subheader("Realidad Sistémica (La Narrativa Oficial)")
            st.write("**Actores Principales:**", ", ".join(resultado_sintesis["sistemico"]["entidades"]))
            st.write("**Complejidad Lingüística:**", resultado_sintesis["sistemico"]["complejidad"])
            
        st.success("Filtro de realidad aplicado.")
