import streamlit as st
import requests
import math
from collections import Counter
from alpha_vantage.foreignexchange import ForeignExchange

# --- PASO 1: DEFINICIÓN DE FUNCIONES (El Cerebro) ---

# Función para calcular la entropía de Shannon
def calcular_entropia(texto):
    if not texto:
        return 0
    conteo = Counter(texto)
    probabilidades = [c / len(texto) for c in conteo.values()]
    entropia = -sum(p * math.log2(p) for p in probabilidades)
    return entropia

# Función para capturar ruido lingüístico desde Wikipedia
def capturar_ruido_linguistico():
    try:
        S = requests.Session()
        URL = "https://es.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "query",
            "format": "json",
            "list": "random",
            "rnnamespace": "0",
            "rnlimit": "1"
        }
        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()
        RANDOM_TITLE = DATA['query']['random'][0]['title']
        
        URL_PAGE = "https://es.wikipedia.org/wiki/" + RANDOM_TITLE
        page = requests.get(URL_PAGE)
        return page.text
    except Exception as e:
        return f"Error al capturar ruido lingüístico: {e}"

# Función para capturar energía económica
def capturar_energia_economica(api_key):
    try:
        fe = ForeignExchange(key=api_key)
        data, _ = fe.get_currency_exchange_rate(from_currency='EUR', to_currency='USD')
        exchange_rate = float(data['5. Exchange Rate'])
        return exchange_rate
    except Exception as e:
        return 0

# --- PASO 2: CONFIGURACIÓN DE LA INTERFAZ (El Espejo) ---

st.set_page_config(page_title="Oráculo Sincrónico", layout="wide")

st.title("Oráculo Sincrónico")
st.write("Define tu intención y sintoniza con el flujo de información del universo.")

# --- PASO 3: EL PROCESO DE SINTONIZACIÓN ---

if 'sintonizado' not in st.session_state:
    st.session_state.sintonizado = False

# Botón para activar el Oráculo
if st.button("Sintonizar"):
    st.session_state.sintonizado = True

# Si el usuario ha presionado el botón...
if st.session_state.sintonizado:
    with st.spinner("Sintonizando con los flujos de datos... por favor, espera."):
        
        # Recuperar la API key de los secrets de Streamlit
        ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage_key"]

        # Capturar el "ruido" de las fuentes
        ruido_wiki = capturar_ruido_linguistico()
        ruido_forex = capturar_energia_economica(ALPHA_VANTAGE_API_KEY)

        # Procesar el "ruido" con el Sintetizador
        entropia_linguistica = calcular_entropia(ruido_wiki)
        energia_economica = ruido_forex
        
        # Presentar el Diagnóstico
        st.subheader("Diagnóstico del Sintetizador - Nivel 1")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(label="Complejidad Lingüística (Entropía)", value=f"{entropia_linguistica:.4f} bits")
            st.info("Mide la aleatoriedad y la cantidad de información en el flujo de lenguaje actual.")

        with col2:
            st.metric(label="Energía Económica (EUR/USD)", value=f"{energia_economica:.4f}")
            st.info("Representa la tensión y el flujo de valor en el sistema financiero global.")

        st.success("Sintonización completada. El universo ha respondido.")
