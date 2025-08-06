import math
from collections import Counter

# --- 5. Sintetizador Nivel 1 ---

def calcular_entropia(data):
    """
    Calcula la Entropía de Shannon para una lista de texto.
    Mide la diversidad y la incertidumbre de la información.
    """
    if not data or isinstance(data, dict):
        return 0
    counts = Counter(data)
    total_items = len(data)
    probabilities = [count / total_items for count in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    return entropy

def calcular_energia_economica(data):
    """
    Extrae el valor numérico de la tasa de cambio como indicador de energía.
    """
    if isinstance(data, dict) and "5. Exchange Rate" in data:
        try:
            return float(data["5. Exchange Rate"])
        except (ValueError, TypeError):
            return 0
    return 0

# --- 6. Procesar el "Ruido" con el Sintetizador ---

# Usamos los datos capturados en el paso anterior
entropia_linguistica = calcular_entropia(ruido_wiki)
energia_economica = calcular_energia_economica(ruido_forex)


# --- 7. Presentar el Primer Diagnóstico ---

print("--- [ DIAGNÓSTICO DEL SINTETIZADOR - NIVEL 1 ] ---")
print(f"🌀 Complejidad Lingüística (Entropía): {entropia_linguistica:.4f} bits")
print(f"⚡ Energía Económica (EUR/USD): {energia_economica:.4f}")
