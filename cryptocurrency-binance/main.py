from indicators import calculate_sma, calculate_ema, calculate_rsi, calculate_bollinger_bands, calculate_macd
from kalman_filter import KalmanFilter
import time
from datetime import datetime, timedelta, timezone
import requests
from requests.auth import HTTPBasicAuth
from btc import get_historical_prices, get_latest_price,  get_latest_volume

# Instancias del filtro de Kalman para 30 días y 5 minutos
kf = KalmanFilter()
#obtener el historico de los precios
historical_data = get_historical_prices()
# Cargar el historial inicial de 
btc_prices = []
btc_prices = get_historical_prices()
print("Iniciando monitoreo de precios de BTC cada 1 minuto...")
while True:
    #obtener hora actual
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Obtener el precio actual
    latest_price = get_latest_price()
    #obtener el ultimo volumen
    latest_volume = get_latest_volume()
    if latest_price is not None:
        btc_prices.append(latest_price) #añadir el ultimo precio alfinal de la lista
        # Realizar la predicción con el filtro de Kalman para datos de 30 días
        predicted_price_historical = kf.filter(btc_prices)

        print(f"Precio actual de Bitcoin: {latest_price:.2f} USD")
        print(f"Predicción Filto Kalman: {predicted_price_historical}")
        #obtener utiimo valor del volumen
        if btc_prices is not None:
            # Calcular indicadores técnicos
            sma_7 = calculate_sma(btc_prices, 7)
            sma_30 = calculate_sma(btc_prices, 30)
            ema_20 = calculate_ema(btc_prices, 20)
            ema_50 = calculate_ema(btc_prices, 50)
            ema_100 = calculate_ema(btc_prices, 100)
            ema_200 = calculate_ema(btc_prices, 200)
            upper_band, lower_band = calculate_bollinger_bands(btc_prices)
            macd, signal_line = calculate_macd(btc_prices)
            rsi = calculate_rsi(btc_prices, 14)
            #obtener ultimo valor del MACD y SIGNAL LINE
            last_MACD = macd[-1]
            last_signal_line = signal_line[-1]
            #obtener ultimos valores de EMA 20, 50, 100 y 200
            last_ema_20 = ema_20[-1]
            last_ema_50 = ema_50[-1]
            last_ema_100 = ema_100[-1]
            last_ema_200 = ema_200[-1]
            #obtener valor del ultimo RSI
            last_rsi = rsi[-1]

            print(f"Volumen 24h: {latest_volume}")
            print(f"MACD {last_MACD}")
            print(f"RSI: {last_rsi}")
            print(f"Ultimos EMA por periodo -- EMA 20: {last_ema_20} -- EMA 50:  {last_ema_50} -- EMA 100: {last_ema_100} -- EMA 200: {last_ema_200}")


            def evaluar_rsi(last_rsi):
                if last_rsi < 30:
                    mensaje = "Señal de sobreventa. Posible subida de precio."
                    valor = 1
                elif last_rsi > 70:
                    mensaje = "Señal de sobrecompra. Posible bajada de precio."
                    valor = -1
                else:
                    mensaje = "RSI en rango normal."
                    valor = -1
                return mensaje, valor

            def evaluar_macd(macd, signal_line):
                """
                Cruce del MACD sobre la línea de señal indica una posible subida de precios
                Cruce del MACD por debajo de la línea de señal indica una posible bajada de precios
                """
                if macd[-1] > signal_line[-1]:
                    mensaje = "Señal de compra: posible subida de precio."
                    valor = 1
                elif macd[-1] < signal_line[-1]:
                    mensaje = "Señal de venta: posible bajada de precio."
                    valor = -1
                else:
                    mensaje = "Equilibrio"
                    valor = 0
                return mensaje, valor

            def evaluar_emas(precio_actual, ema_20, ema_50, ema_100, ema_200):

                """
                Cuando el precio actual está por encima de las EMAs, indica un posible movimiento alcista.
                Cuando el precio actual está por debajo de las EMAs, indica un posible movimiento bajista
                """
                if precio_actual > ema_20 and precio_actual > ema_50 and precio_actual > ema_100 and precio_actual > ema_200:
                    mensaje =  "Señal de compra: posible subida de precio."
                    valor = 1
                elif precio_actual < ema_20 and precio_actual < ema_50 and precio_actual < ema_100 and precio_actual < ema_200:
                    mensaje =  "Señal de venta: posible bajada de precio."
                    valor = -1
                else:
                    mensaje =  "Equilibrio."
                    valor = 0
                return mensaje, valor

            def evaluar_promedio_ema(precio_actual, ema_20, ema_50, ema_100, ema_200):
                """
                Compara el precio actual con el promedio de las EMAs.
                """
                promedio_ema = (ema_20 + ema_50 + ema_100 + ema_200) / 4
                if precio_actual > promedio_ema:
                    mensaje =  "Posible tendencia alcista."
                    valor = 0
                elif precio_actual < promedio_ema:
                    mensaje = "Posible tendencia bajista."
                    valor = -1
                else:
                    mensaje =  " No se detecta una tendencia clara."
                    valor = 0
                return mensaje, valor
                    
            #Llamadas a las funciones
            mensaje_rsi, valor_rsi = evaluar_rsi(last_rsi)
            mensaje_macd, valor_macd = evaluar_macd(macd, signal_line)
            mensaje_emas, valor_emas = evaluar_emas(latest_price, last_ema_20, last_ema_50, last_ema_100, last_ema_200)
            mensaje_promedio_emas, valor_promedio_emas = evaluar_promedio_ema(latest_price, last_ema_20, last_ema_50, last_ema_100, last_ema_200)

            def indicador_compra_venta_ponderado(valor_macd, valor_emas, valor_promedio_emas, valor_rsi):
                # Definir los pesos de cada indicador
                peso_macd = 0.4
                peso_emas = 0.3
                peso_rsi = 0.1
                peso_promedio_emas = 0.1

                # Obtener los mensajes y valores de cada evaluación
                valor_macd = valor_macd
                valor_emas = valor_emas
                valor_promedio_emas = valor_promedio_emas
                valor_rsi = valor_rsi
                
                # Calcular la señal ponderada
                señal_total = (valor_macd * peso_macd +
                            valor_emas * peso_emas +
                             + valor_rsi * peso_rsi )

                # Determinar la acción basada en el resultado ponderado
                if señal_total > 0.3:
                    decision_final = "Compra"
                elif señal_total < -0.3:
                    decision_final = "Venta"
                else:
                    decision_final = "Mantener"

                return decision_final

            decision_final = indicador_compra_venta_ponderado(valor_macd, valor_emas, valor_promedio_emas, valor_rsi)

            # Mostrar los resultados (opcional)
            print(f"Evaluacion MACD: {mensaje_macd}")
            print(f"Evaluccion EMAS:{mensaje_emas}")
            print(f"Evaluacion promedio EMAS: {mensaje_promedio_emas}")
            print(f"Evaluacion RSI: {mensaje_rsi}")
            print(f"Evaluacion Indicadores: {decision_final}")
            #print(f"MACD:{macd}")
            #print(five_minute_data)
            #muestras de EMA
            #print("EMA para 20 periodos:", ema_20)
            #print("EMA para 50 periodos:", ema_50)
            #print("EMA para 100 periodos:", ema_100)
            #print("EMA para 200 periodos:", ema_200)
            
    else:
        print("No se pudieron obtener datos históricos para 30 días.")
    ## CREAR TICKET DE JIRA
    # Variables de configuración
    JIRA_URL = ''  # URL de tu instancia de Jira
    EMAIL = ''
    API_TOKEN = ''
    PROJECT_KEY = ''  # Clave de tu proyecto de Jira

    def create_jira_ticket(price_actual, predicted_price, last_rsi, diferencia, last_volume, last_MACD, last_ema_20, last_ema_50, last_ema_100, last_ema_200, mensaje_macd, mensaje_emas, mensaje_promedio_emas, last_signal_line, decision_final, mensaje_rsi):
        url = f"{JIRA_URL}/rest/api/3/issue"

        # Estructura de datos para la solicitud
        payload = {
            "fields": {
                "project": {
                    "key": PROJECT_KEY
                },
                "summary": "Ticket Prediccion BTC",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Subido correctamente"
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": "Task"
                }
            }
        }

        # Campos personalizados
        if price_actual is not None:
            payload["fields"]["customfield_10038"] = price_actual
        if predicted_price is not None:
            payload["fields"]["customfield_10039"] = predicted_price
        if last_rsi is not None:
            payload["fields"]["customfield_10040"] = last_rsi
        if diferencia is not None:
            payload["fields"]["customfield_10041"] = diferencia
        if last_volume is not None:
            payload["fields"]["customfield_10043"] = last_volume
        if last_MACD is not None:
            payload["fields"]["customfield_10042"] = last_MACD        
        if last_ema_20 is not None:
            payload["fields"]["customfield_10047"] = last_ema_20 
        if last_ema_50 is not None:
            payload["fields"]["customfield_10046"] = last_ema_50 
        if last_ema_100 is not None:
            payload["fields"]["customfield_10045"] = last_ema_100  
        if last_ema_200 is not None:
            payload["fields"]["customfield_10044"] = last_ema_200  
        if mensaje_macd is not None:
            payload["fields"]["customfield_10048"] = mensaje_macd
        if mensaje_emas is not None:
            payload["fields"]["customfield_10049"] = mensaje_emas
        if mensaje_promedio_emas is not None:
            payload["fields"]["customfield_10050"] = mensaje_promedio_emas
        if last_signal_line is not None:
            payload["fields"]["customfield_10051"] = last_signal_line
        if decision_final is not None:
            payload["fields"]["customfield_10052"] = decision_final
        if mensaje_rsi is not None:
            payload["fields"]["customfield_10053"] = mensaje_rsi
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Realizar la solicitud POST
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                auth=HTTPBasicAuth(EMAIL, API_TOKEN)
            )
            if response.status_code == 201:
                print("Ticket creado correctamente en Jira.")
                ticket_key = response.json().get("key")
                print(f"ID del ticket: {ticket_key}")
            else:
                print(f"Error al crear ticket en Jira: {response.status_code}")
                print(response.json())
        except Exception as e:
            print(f"Error al realizar la solicitud: {e}")

    # Calcular diferencia entre precio actual y precio de predicción
    diferencia = abs(predicted_price_historical - latest_price) if predicted_price_historical and latest_price else None

    # Crear ticket en Jira
    if latest_price is not None and predicted_price_historical is not None:
        create_jira_ticket(latest_price, predicted_price_historical, last_rsi, diferencia, latest_volume, last_MACD, last_ema_20, last_ema_50, last_ema_100, last_ema_200, mensaje_macd, mensaje_emas, mensaje_promedio_emas, last_signal_line, decision_final, mensaje_rsi)
    
    # Obtener datos de 5 minutos
    print("*********************************************************************")

    # Esperar 5 minutos antes de la siguiente actualización
    time.sleep(60)
