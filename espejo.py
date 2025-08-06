import streamlit as st
import requests
import math
import tweepy
import pandas as pd
from collections import Counter
from alpha_vantage.foreignexchange import ForeignExchange
from textblob import TextBlob

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

# --- FUNCIÓN ACTUALIZADA ---
# Ahora devuelve un desglose, no un solo número
def capturar_sentimiento_social(api_key, api_secret, access_token, access_secret, intencion):
    try:
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth)
        
        tweets = api.search_tweets(q=intencion, lang="es", count=100, tweet_mode="extended")
        
        if not tweets:
            return {"positivo": 0, "negativo": 0, "neutral": 100}

        positivo_count = 0
        negativo_count = 0
        neutral_count = 0

        for tweet in tweets:
            analisis = TextBlob(tweet.full_text)
            if analisis.sentiment.polarity > 0.05: # Umbral para considerar positivo
                positivo_count += 1
            elif analisis.sentiment.polarity < -0.05: # Umbral para considerar negativo
                negativo_count += 1
            else:
                neutral_count += 1
        
        total = len(tweets)
        return {
            "positivo": (positivo_count / total) * 100,
            "negativo": (negativo_count / total) * 100,
            "neutral": (neutral_count / total) * 100
        }
    except Exception as e:
        return {"positivo": 0, "negativo": 0, "neutral": 100} # Devuelve neutralidad en caso de error

# --- PASO 2: CONFIGURACIÓN DE LA INTERFAZ ---

st.set_page_config(page_title="Oráculo Sincrónico", layout="wide")
st.title("Oráculo Sincrónico")
intencion_usuario = st.text_input("Define tu intención o el concepto a sintonizar:", "futuro")

# --- PASO 3: EL PROCESO DE SINTONIZACIÓN ---

if 'sintonizado' not in st.session_state:
    st.session_state.sintonizado = False

if st.button("Sintonizar"):
    st.session_state.sintonizado = True

if st.session_state.sintonizado:
    with st.spinner("Sintonizando con los flujos de datos..."):
        
        # Recuperar las claves
        ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage_key"]
        TWITTER_API_KEY = st.secrets["twitter_api_key"]
        TWITTER_API_SECRET = st.secrets["twitter_api_key_secret"]
        TWITTER_ACCESS_TOKEN = st.secrets["twitter_access_token"]
        TWITTER_ACCESS_SECRET = st.secrets["twitter_access_token_secret"]
        
        # Capturar los datos
        ruido_wiki = capturar_ruido_linguistico()
        ruido_forex = capturar_energia_economica(ALPHA_VANTAGE_API_KEY)
        distribucion_sentimiento = capturar_sentimiento_social(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, intencion_usuario)
        
        # Procesar con el Sintetizador
        entropia_linguistica = calcular_entropia(ruido_wiki)
        energia_economica = ruido_forex
        
        # --- PRESENTACIÓN ACTUALIZADA ---
        st.subheader("Diagnóstico del Sintetizador - Nivel 3")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(label="Complejidad Lingüística (Entropía)", value=f"{entropia_linguistica:.4f} bits")
        with col2:
            st.metric(label="Energía Económica (EUR/USD)", value=f"{energia_economica:.4f}")

        st.subheader("Distribución del Sentimiento Social")
        
        # Crear un DataFrame para la gráfica
        sentimiento_df = pd.DataFrame({
            'Sentimiento': ['Positivo', 'Negativo', 'Neutral'],
            'Porcentaje': [distribucion_sentimiento['positivo'], distribucion_sentimiento['negativo'], distribucion_sentimiento['neutral']]
        })
        
        # Mostrar gráfica de barras
        st.bar_chart(sentimiento_df.set_index('Sentimiento'))
        
        st.success("Sintonización completada.")
