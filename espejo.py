import streamlit as st
import requests
import math
import tweepy
from collections import Counter
from alpha_vantage.foreignexchange import ForeignExchange
from textblob import TextBlob # Necesitaremos TextBlob para el análisis de sentimiento

# --- PASO 1: DEFINICIÓN DE FUNCIONES (El Cerebro) ---

# Función para calcular la entropía de Shannon (sin cambios)
def calcular_entropia(texto):
    if not texto:
        return 0
    conteo = Counter(texto)
    probabilidades = [c / len(texto) for c in conteo.values()]
    entropia = -sum(p * math.log2(p) for p in probabilidades)
    return entropia

# Función para capturar ruido lingüístico (sin cambios)
def capturar_ruido_linguistico():
    try:
        S = requests.Session()
        URL = "https://es.wikipedia.org/w/api.php"
        PARAMS = { "action": "query", "format": "json", "list": "random", "rnnamespace": "0", "rnlimit": "1" }
        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()
        RANDOM_TITLE = DATA['query']['random'][0]['title']
        URL_PAGE = "https://es.wikipedia.org/wiki/" + RANDOM_TITLE
        page = requests.get(URL_PAGE)
        return page.text
    except Exception as e:
        return f"Error: {e}"

# Función para capturar energía económica (sin cambios)
def capturar_energia_economica(api_key):
    try:
        fe = ForeignExchange(key=api_key)
        data, _ = fe.get_currency_exchange_rate(from_currency='EUR', to_currency='USD')
        return float(data['5. Exchange Rate'])
    except Exception as e:
        return 0

# --- NUEVA FUNCIÓN ---
# Función para capturar y analizar el sentimiento social
def capturar_sentimiento_social(api_key, api_secret, access_token, access_secret, intencion):
    try:
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth)
        
        # Buscamos tweets recientes en español que contengan la "intención"
        tweets = api.search_tweets(q=intencion, lang="es", count=100, tweet_mode="extended")
        
        texto_tweets = " ".join(tweet.full_text for tweet in tweets)
        
        # Analizamos el sentimiento del texto compilado
        analisis = TextBlob(texto_tweets)
        return analisis.sentiment.polarity # Devuelve un valor entre -1 (muy negativo) y 1 (muy positivo)
    except Exception as e:
        return 0

# --- PASO 2: CONFIGURACIÓN DE LA INTERFAZ ---

st.set_page_config(page_title="Oráculo Sincrónico", layout="wide")
st.title("Oráculo Sincrónico")

# --- NUEVO ELEMENTO DE INTERFAZ ---
# Campo de texto para que el usuario defina su intención
intencion_usuario = st.text_input("Define tu intención o el concepto a sintonizar:", "esperanza")

# --- PASO 3: EL PROCESO DE SINTONIZACIÓN ---

if 'sintonizado' not in st.session_state:
    st.session_state.sintonizado = False

if st.button("Sintonizar"):
    st.session_state.sintonizado = True

if st.session_state.sintonizado:
    with st.spinner("Sintonizando con los flujos de datos..."):
        
        # Recuperar todas las claves de los secrets
        ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage_key"]
        TWITTER_API_KEY = st.secrets["twitter_api_key"]
        TWITTER_API_SECRET = st.secrets["twitter_api_key_secret"]
        TWITTER_ACCESS_TOKEN = st.secrets["twitter_access_token"]
        TWITTER_ACCESS_SECRET = st.secrets["twitter_access_token_secret"]
        
        # Capturar los datos
        ruido_wiki = capturar_ruido_linguistico()
        ruido_forex = capturar_energia_economica(ALPHA_VANTAGE_API_KEY)
        sentimiento_social = capturar_sentimiento_social(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, intencion_usuario)
        
        # Procesar con el Sintetizador
        entropia_linguistica = calcular_entropia(ruido_wiki)
        energia_economica = ruido_forex
        
        # Presentar el Diagnóstico
        st.subheader("Diagnóstico del Sintetizador - Nivel 2")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Complejidad Lingüística (Entropía)", value=f"{entropia_linguistica:.4f} bits")
        with col2:
            st.metric(label="Energía Económica (EUR/USD)", value=f"{energia_economica:.4f}")
        with col3:
            st.metric(label="Sentimiento Social (Polaridad)", value=f"{sentimiento_social:.4f}")

        st.success("Sintonización completada.")
