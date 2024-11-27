import numpy as np

def calculate_sma(prices, window):
    sma = []
    for i in range(len(prices) - window + 1):
        window_avg = sum(prices[i:i + window]) / window
        sma.append(window_avg)
    return sma

def calculate_ema(prices, window):
    ema = []
    k = 2 / (window + 1)
    ema.append(sum(prices[:window]) / window)  # Inicializar EMA usando el SMA
    
    for price in prices[window:]:
        ema_value = (price - ema[-1]) * k + ema[-1]
        ema.append(ema_value)
    
    return ema

def calculate_rsi(prices, period=14):
    gains, losses = 0, 0
    
    # Calcular el promedio inicial de ganancias y pérdidas
    for i in range(1, period + 1):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains += change
        else:
            losses += abs(change)
    
    avg_gain = gains / period
    avg_loss = losses / period
    rsi = [100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss > 0 else 100]
    
    # Continuar con el resto de los precios
    for i in range(period, len(prices)):
        change = prices[i] - prices[i - 1]
        gain = max(0, change)
        loss = abs(min(0, change))
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
        rsi.append(100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss > 0 else 100)
    
    return rsi


def calculate_bollinger_bands(prices, window=20):
    sma = calculate_sma(prices, window)
    std_dev = [np.std(prices[i:i + window]) for i in range(len(prices) - window + 1)]
    upper_band = [s + (2 * sd) for s, sd in zip(sma, std_dev)]
    lower_band = [s - (2 * sd) for s, sd in zip(sma, std_dev)]
    
    return upper_band, lower_band

def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    short_ema = calculate_ema(prices, short_window)
    long_ema = calculate_ema(prices, long_window)
    macd = [s - l for s, l in zip(short_ema, long_ema)]
    
    signal_line = calculate_ema(macd, signal_window)
    
    return macd, signal_line
