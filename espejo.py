import streamlit as st
import requests
from alpha_vantage.foreignexchange import ForeignExchange
import pandas as pd
from pytrends.request import TrendReq

# --- DEFINICIÓN DE FUNCIONES ---
def capturar_energia_economica(api_key):
    try:
        fe = ForeignExchange(key=api_key)
        data, _ = fe.get_currency_exchange_rate(from_currency='EUR', to_currency='USD')
        return float(data['5. Exchange Rate'])
    except Exception as e:
        st.error(f"Error al contactar API de Alpha Vantage: {e}")
        return 0

# --- NUEVA FUNCIÓN ---
# Mide el interés colectivo en conceptos relacionados
def sintetizar_interes_colectivo(intencion):
    try:
        pytrends = TrendReq(hl='es-MX', tz=360)
        
        # Comparamos la intención principal con dos conceptos relacionados
        kw_list = [intencion, "incertidumbre", "oportunidad"]
        pytrends.build_payload(kw_list, cat=0, timeframe='now 1-d', geo='MX', gprop='')
        
        # Obtenemos el interés a lo largo del último día
        interest_over_time_df = pytrends.interest_over_time()

        if interest_over_time_df.empty:
            return pd.DataFrame({'Concepto': ['Sin Datos'], 'Interés': [0]})

        # Devolvemos el promedio de interés para cada concepto
        avg_interest = interest_over_time_df.mean().reset_index()
        avg_interest.columns = ['Concepto', 'Interés']
        return avg_interest

    except Exception as e:
        st.error(f"Error al contactar Google Trends: {e}")
        return pd.DataFrame({'Concepto': ['Error'], 'Interés': [0]})


# --- INTERFAZ ---
st.set_page_config(page_title="Oráculo Sincrónico", layout="wide")
st.title("Oráculo Sincrónico")
st.subheader("Sintetizador de Interés Colectivo")
intencion_usuario = st.text_input("Define tu intención o el concepto a sintonizar:", "futuro")

if st.button("Sintonizar"):
    with st.spinner("Sintonizando y sintetizando interés colectivo..."):
        # Recuperar claves
        ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage_key"]
        
        # Capturar y sintetizar datos
        energia_economica = capturar_energia_economica(ALPHA_VANTAGE_API_KEY)
        interes_colectivo_df = sintetizar_interes_colectivo(intencion_usuario)
        
        # Presentar el diagnóstico
        st.header("Diagnóstico del Sintetizador")
        st.metric(label="Energía Económica (EUR/USD)", value=f"{energia_economica:.4f}")

        st.subheader("Distribución del Interés Colectivo (Últimas 24h en México)")
        
        if not interes_colectivo_df.empty and 'isPartial' in interes_colectivo_df.columns:
             interes_colectivo_df = interes_colectivo_df.drop(columns=['isPartial'])

        st.bar_chart(interes_colectivo_df.set_index('Concepto'))
            
        st.success("Sintonización completada.")
