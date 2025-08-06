import streamlit as st
import requests
import tweepy
import pandas as pd
import spacy
from collections import Counter
from alpha_vantage.foreignexchange import ForeignExchange
from textblob import TextBlob

# --- CARGAR MODELO DE LENGUAJE ---
@st.cache_resource
def load_spacy_model():
    return spacy.load("es_core_news_sm")
nlp = load_spacy_model()

# --- DEFINICIÓN DE FUNCIONES ---
def capturar_energia_economica(api_key):
    try:
        fe = ForeignExchange(key=api_key)
        data, _ = fe.get_currency_exchange_rate(from_currency='EUR', to_currency='USD')
        return float(data['5. Exchange Rate'])
    except Exception as e:
        st.error(f"Error al contactar API de Alpha Vantage: {e}")
        return 0

def sintetizar_realidad(api_key, api_secret, access_token, access_secret, intencion):
    try:
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        tweets = api.search_tweets(q=f"{intencion} -is:retweet", lang="es", count=100, tweet_mode="extended")
        
        if not tweets:
            return {"sistemico": {"entidades": ["N/A"], "polaridad": 0}, "organico": {"entidades": ["N/A"], "polaridad": 0}, "contaminacion": 0}

        textos_sistemicos = []
        textos_organicos = []

        for tweet in tweets:
            es_sistemico = tweet.user.verified or tweet.user.followers_count > 10000
            if es_sistemico:
                textos_sistemicos.append(tweet.full_text)
            else:
                textos_organicos.append(tweet.full_text)

        def analizar_bloque(textos):
            if not textos:
                return {"entidades": ["N/A"], "polaridad": 0}
            
            texto_completo = " ".join(textos)
            doc = nlp(texto_completo)
            entidades = Counter([ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE']]).most_common(5)
            
            analisis = TextBlob(texto_completo)
            polaridad = analisis.sentiment.polarity
            
            return {
                "entidades": [f"{ent[0]} ({ent[1]})" for ent in entidades],
                "polaridad": polaridad
            }

        resultado_organico = analizar_bloque(textos_organicos)
        resultado_sistemico = analizar_bloque(textos_sistemicos)

        total_tweets = len(textos_sistemicos) + len(textos_organicos)
        indice_contaminacion = (len(textos_sistemicos) / total_tweets) * 100 if total_tweets > 0 else 0

        return {"sistemico": resultado_sistemico, "organico": resultado_organico, "contaminacion": indice_contaminacion}

    except Exception as e:
        st.error(f"Error al contactar API de Twitter/X: {e}")
        return {"sistemico": {"entidades": ["Error"], "polaridad": 0}, "organico": {"entidades": ["Error"], "polaridad": 0}, "contaminacion": -1}

# --- INTERFAZ ---
st.set_page_config(page_title="Oráculo Sincrónico", layout="wide")
st.title("Oráculo Sincrónico")
st.subheader("Filtro de Realidad - Nivel 5")
intencion_usuario = st.text_input("Define tu intención o el concepto a sintonizar:", "libertad")

if st.button("Sintonizar"):
    with st.spinner("Aplicando filtro de realidad..."):
        # Recuperar claves de los secrets de Streamlit
        ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage_key"]
        TWITTER_API_KEY = st.secrets["twitter_api_key"]
        TWITTER_API_SECRET = st.secrets["twitter_api_key_secret"]
        TWITTER_ACCESS_TOKEN = st.secrets["twitter_access_token"]
        TWITTER_ACCESS_SECRET = st.secrets["twitter_access_token_secret"]
        
        # Capturar y sintetizar datos
        energia_economica = capturar_energia_economica(ALPHA_VANTAGE_API_KEY)
        resultado_sintesis = sintetizar_realidad(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, intencion_usuario)
        
        # Presentar el diagnóstico
        st.header("Diagnóstico del Sintetizador")
        st.metric(label="Energía Económica (EUR/USD)", value=f"{energia_economica:.4f}")
        st.metric(label="Índice de Contaminación Sistémica", value=f"{resultado_sintesis['contaminacion']:.2f}%")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Realidad Orgánica")
            st.write("**Actores Principales:**", ", ".join(resultado_sintesis["organico"]["entidades"]))
            st.metric(label="Sentimiento (Polaridad)", value=f"{resultado_sintesis['organico']['polaridad']:.4f}")
        with col2:
            st.subheader("Realidad Sistémica")
            st.write("**Actores Principales:**", ", ".join(resultado_sintesis["sistemico"]["entidades"]))
            st.metric(label="Sentimiento (Polaridad)", value=f"{resultado_sintesis['sistemico']['polaridad']:.4f}")
            
        st.success("Filtro de realidad aplicado.")
