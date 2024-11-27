import numpy as np

class KalmanFilter:
    def __init__(self):
        # Inicializar con valores estándar
        self.predicted_price = 0.0  # Precio predicho inicial
        self.estimate_covariance = 1.0  # Covarianza estimada inicial
        self.process_variance = 1e-1  # Varianza del proceso (ajustable  1e - 5 a 1e- 1) Por defectO: 1e-1
        self.measurement_variance = 1e-3  # Varianza de la medición (ajustable  1e - 5 a 1e- 1) 1e-3
        
        # Matrices necesarias para la actualización del filtro
        self.H = np.array([[1]])  # Matriz de observación que relaciona el estado con la medición
        self.R = np.array([[self.measurement_variance]])  # Varianza de la medición en forma de matriz
        self.P = np.array([[self.estimate_covariance]])  # Covarianza estimada en forma de matriz
        self.x = np.array([[self.predicted_price]])  # Estado inicial en forma de matriz

    def predict(self, prices):
        """
        Realiza la predicción de precios basada en los datos previos y el filtro de Kalman.

        :param prices: Lista de precios (datos de entrada)
        :return: Predicción del siguiente valor de precio
        """
        for price in prices:
            # Predicción del estado (precio)
            # Se mantiene el precio predicho actual (sin cambio)
            self.predicted_price = self.predicted_price  
            
            # Se actualiza la covarianza estimada
            self.estimate_covariance += self.process_variance  # Agrega la varianza del proceso

            # Cálculo de la ganancia de Kalman
            kalman_gain = self.estimate_covariance / (self.estimate_covariance + self.measurement_variance)
            
            # Actualiza la predicción del precio con la medición actual
            self.predicted_price += kalman_gain * (price - self.predicted_price)
            
            # Actualiza la covarianza estimada con la ganancia de Kalman
            self.estimate_covariance *= (1 - kalman_gain)

        # Retorna solo el último valor de predicción
        return self.predicted_price
    
    def update(self, observed_price):
        """
        Actualiza el filtro de Kalman con el precio observado.

        :param observed_price: El precio observado (float)
        """
        # Calcula la ganancia de Kalman
        S = self.H @ self.P @ self.H.T + self.R  # Innovación (residual)
        K = self.P @ self.H.T @ np.linalg.inv(S)  # Ganancia de Kalman
        
        # Actualiza el estado con la observación
        y = np.array([[observed_price]]) - (self.H @ self.x)  # Error de predicción
        self.x += K @ y  # Actualización del estado

        # Actualiza la covarianza estimada
        self.P = (np.eye(1) - K @ self.H) @ self.P

    def filter(self, prices):
        """
        Filtra una lista de precios utilizando el filtro de Kalman.

        :param prices: Lista de precios a filtrar
        :return: La última predicción de precio
        """
        predictions = []  # Lista para almacenar las predicciones
        for price in prices:
            # Predice el próximo valor utilizando el precio actual
            predicted_price = self.predict([price])  
            self.update(price)  # Actualiza el filtro con la observación
            predictions.append(predicted_price)  # Guarda la última predicción
        
        # Retorna solo la última predicción
        return predictions[-1] if predictions else None

