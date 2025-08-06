import streamlit as st
import requests
import math
import tweepy
import pandas as pd
import spacy
from collections import Counter
from alpha_vantage.foreignexchange import ForeignExchange
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# --- CARGAR MODELO DE LENGUAJE (Se ejecuta una sola vez) ---
@st.cache_resource
def load_spacy_model():
    return spacy.load("es_core_news_sm")

nlp = load_spacy_model()

# --- DEFINICIÓN DE FUNCIONES (El Cerebro) ---

def capturar_ruido_linguistico():
    # ... (sin cambios, la dejamos como está)
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

def capturar_energia_economica(api_key):
    # ... (sin cambios)
    try:
        fe = ForeignExchange(key=api_key)
        data, _ = fe.get_currency_exchange_rate(from_currency='EUR', to_currency='USD')
        return float(data['5. Exchange Rate'])
    except Exception as e:
        return 0

# --- NUEVA FUNCIÓN DE SÍNTESIS ---
def sintetizar_conceptos(api_key, api_secret, access_token, access_secret, intencion, n_topics=5):
    try:
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth)
        
        tweets = api.search_tweets(q=f"{intencion} -is:retweet", lang="es", count=100, tweet_mode="extended")
        
        if not tweets:
            return {"temas": ["No se encontraron conversaciones."], "entidades": ["N/A"]}

        textos_tweets = [tweet.full_text for tweet in tweets]

        # 1. Topic Modeling
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english') # Usamos 'english' como base, se puede mejorar
        tfidf = vectorizer.fit_transform(textos_tweets)
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=0)
        lda.fit(tfidf)
        
        feature_names = vectorizer.get_feature_names_out()
        temas = []
        for topic_idx, topic in enumerate(lda.components_):
            top_words = " ".join([feature_names[i] for i in topic.argsort()[:-6:-1]])
            temas.append(f"Tema {topic_idx + 1}: {top_words}")

        # 2. Named Entity Recognition
        texto_completo = " ".join(textos_tweets)
        doc = nlp(texto_completo)
        entidades = [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE']] # Personas, Organizaciones, Lugares
        conteo_entidades = Counter(entidades).most_common(5)
        
        return {"temas": temas, "entidades": [f"{ent[0]} ({ent[1]})" for ent in conteo_entidades]}

    except Exception as e:
        return {"temas": [f"Error en la síntesis: {e}"], "entidades": ["Error"]}

# --- INTERFAZ ---
st.set_page_config(page_title="Oráculo Sincrónico", layout="wide")
st.title("Oráculo Sincrónico")
intencion_usuario = st.text_input("Define tu intención o el concepto a sintonizar:", "tecnología")

# --- PROCESO DE SINTONIZACIÓN ---
if st.button("Sintonizar"):
    with st.spinner("Sintonizando y sintetizando conceptos..."):
        # Recuperar claves
        ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage_key"]
        TWITTER_API_KEY = st.secrets["twitter_api_key"]
        TWITTER_API_SECRET = st.secrets["twitter_api_key_secret"]
        TWITTER_ACCESS_TOKEN = st.secrets["twitter_access_token"]
        TWITTER_ACCESS_SECRET = st.secrets["twitter_access_token_secret"]
        
        # Capturar datos básicos (podemos eliminarlos en el futuro o mantenerlos)
        energia_economica = capturar_energia_economica(ALPHA_VANTAGE_API_KEY)
        
        # El nuevo sintetizador
        resultado_sintesis = sintetizar_conceptos(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, intencion_usuario)
        
        # Presentar el Diagnóstico
        st.subheader("Diagnóstico del Sintetizador - Nivel 4")
        st.metric(label="Energía Económica (EUR/USD)", value=f"{energia_economica:.4f}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Temas Ocultos en la Conversación")
            st.write(resultado_sintesis["temas"])
        with col2:
            st.subheader("Actores Principales Mencionados")
            st.write(resultado_sintesis["entidades"])
            
        st.success("Síntesis conceptual completada.")
