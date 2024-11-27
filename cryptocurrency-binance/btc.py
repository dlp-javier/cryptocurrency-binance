import requests
import time

# Lista para almacenar los precios de cierre de BTC/USDT cada minuto
btc_prices = []

def get_historical_prices():
    """
    Obtiene los precios de cierre de las últimas 24 horas a intervalos de 1 minuto.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",  # Intervalo de 1 minuto para obtener datos precisos en 24 horas
        "limit": 1440      # 1440 minutos en 24 horas
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # Extraer solo los precios de cierre
        prices = [float(candle[4]) for candle in data]
        print(f"Historial inicial de precios cargado: {len(prices)} datos")
        return prices
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el historial de precios: {e}")
        return []

def get_latest_price():
    """
    Obtiene el precio de cierre actual de BTC/USDT.
    """
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {
        "symbol": "BTCUSDT"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        price = float(data["price"])
        print(f"Precio actual de BTC/USDT: {price}")
        return price
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el precio actual: {e}")
        return None


import requests

def get_latest_volume():
    """
    Obtiene el último valor de volumen de BTC/USDT en un intervalo de 1 minuto.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 1  # Solo queremos la última vela
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        latest_volume = float(data[0][5])  # Volumen de la última vela
        print(f"Último volumen de BTC/USDT: {latest_volume}")
        return latest_volume
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el último volumen: {e}")
        return None


