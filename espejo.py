import streamlit as st
import requests
import tweepy
from alpha_vantage.foreignexchange import ForeignExchange
from textblob import TextBlob

# --- DEFINICIÓN DE FUNCIONES ---
def capturar_energia_economica(api_key):
    try:
        fe = ForeignExchange(key=api_key)
        data, _ = fe.get_currency_exchange_rate(from_currency='EUR', to_currency='USD')
        return float(data['5. Exchange Rate'])
    except Exception as e:
        st.error(f"Error al contactar API de Alpha Vantage: {e}")
        return 0

def sintetizar_sentimiento(api_key, api_secret, access_token, access_secret, intencion):
    try:
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        tweets = api.search_tweets(q=f"{intencion} -is:retweet", lang="es", count=100, tweet_mode="extended")
        
        if not tweets:
            return 0 # Retorna neutralidad si no hay tweets
        
        texto_completo = " ".join(tweet.full_text for tweet in tweets)
        analisis = TextBlob(texto_completo)
        return analisis.sentiment.polarity
        
    except Exception as e:
        st.error(f"Error al contactar API de Twitter/X: {e}")
        return 0

# --- INTERFAZ ---
st.set_page_config(page_title="Oráculo Sincrónico", layout="wide")
st.title("Oráculo Sincrónico")
st.subheader("Sintetizador de Sentimiento - Nivel 3")
intencion_usuario = st.text_input("Define tu intención o el concepto a sintonizar:", "futuro")

if st.button("Sintonizar"):
    with st.spinner("Sintonizando y sintetizando sentimiento..."):
        # Recuperar claves
        ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage_key"]
        TWITTER_API_KEY = st.secrets["twitter_api_key"]
        TWITTER_API_SECRET = st.secrets["twitter_api_key_secret"]
        TWITTER_ACCESS_TOKEN = st.secrets["twitter_access_token"]
        TWITTER_ACCESS_SECRET = st.secrets["twitter_access_token_secret"]
        
        # Capturar y sintetizar datos
        energia_economica = capturar_energia_economica(ALPHA_VANTAGE_API_KEY)
        sentimiento_social = sintetizar_sentimiento(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, intencion_usuario)
        
        # Presentar el diagnóstico
        st.header("Diagnóstico del Sintetizador")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Energía Económica (EUR/USD)", value=f"{energia_economica:.4f}")
        with col2:
            st.metric(label="Sentimiento Social (Polaridad)", value=f"{sentimiento_social:.4f}")
            
        st.success("Sintonización completada.")
