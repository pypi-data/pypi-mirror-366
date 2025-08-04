###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class TimeSeriesProcessor(BaseEstimator, TransformerMixin):
    """"
    - Autor: BALDEZZARI Lucas
    - Creación: 8 de enero de 2024
    """
    
    def __init__(self):
        """Inicializa la clase TimeSeriesProcessor."""
        
        self.is_fitted = False
        
        ##creamos un diccionario para saber la posición de cada dato dentro del array devuelto por transform()
        self._dataPositions = {
            "deltaO": 0, "deltaC": 1,
            "deltaP": 2, "ratio_dCdP": 3}
        
    def fit(self, X: np.array, y=None)-> np.array:
        """Fittea el objeto
        
            Args:
                - X es un array de strings de forma (n, 2) donde la primera columna es el tiempo y la segunda columna es el tiempo de pico abierto (en segundos).
        """

        ##asserteamos que X sea un np.array
        assert isinstance(X, np.ndarray), "X debe ser un np.array"
        ##asserteamos que X tenga dos columnas
        assert X.ndim == 2, "X debe ser de la forma (n, 2)"
                
        if X.shape[0] >= 2:
            self._deltaO = np.diff(X[:,0])
            self._deltaP = X[:,1]
            self._deltaC = self._deltaO - self._deltaP[1:]
            ##agregamos un 0 al principio de deltaO y deltaC
            self._deltaO = np.insert(self._deltaO, 0, 0)
            self._deltaC = np.insert(self._deltaC, 0, 0)
            ##computamos el ratio entre deltaC y deltaP. Usamos np.vectorize para que compute el ratio para cada elemento del array
            self._ratio_dCdP = self.compute_ratio_dCdP(self._deltaC, self._deltaP)
            ##cambiamos primer valor de ratio_dCdP por 1
            self._ratio_dCdP[0] = 1
            
        elif X.shape[0] == 1:
            self._deltaO = np.array([0])
            self._deltaC = np.array([0])
            self._deltaP = X[:,1]
            self._ratio_dCdP = np.array([1])
        
        self.is_fitted = True
    
    def transform(self, X: np.array):
        """Genera un array con los tiempos de operación, caminata, pico abierto y ratio_dCdP.
            Args:
                - X es un array de strings de forma (n, 2) donde la primera columna es el tiempo
                y la segunda columna es el tiempo de pico abierto (en segundos).

        Returns:
            - Un array de numpy de forma (n, 4) donde la primera columna es
            el tiempo de operación, la segunda columna es el tiempo de caminata,
            la tercera columna es el tiempo de pico abierto y la cuarta columna es
            el ratio entre el tiempo de caminata y el tiempo de pico abierto.
        """
        
        if not self.is_fitted:
            raise RuntimeError("El modelo no ha sido fitteado.")
        
        return np.hstack((self._deltaO.reshape(-1, 1),
                          self._deltaC.reshape(-1, 1),
                          self._deltaP.reshape(-1, 1),
                          self._ratio_dCdP.reshape(-1,1))).round(2)
    
    def fit_transform(self, X: np.array, y=None):
        """Genera un array con los tiempos de operación, caminata, pico abierto y ratio_dCdP.
            Args:
                - X es un array de strings de forma (n, 2) donde la primera columna es el tiempo
                y la segunda columna es el tiempo de pico abierto (en segundos).

        Returns:
            - Un array de numpy de forma (n, 4) donde la primera columna es
            el tiempo de operación, la segunda columna es el tiempo de caminata,
            la tercera columna es el tiempo de pico abierto y la cuarta columna es
            el ratio entre el tiempo de caminata y el tiempo de pico abierto.
        """
        self.fit(X)
        return self.transform(X)
           
    def compute_ratio_dCdP(self, deltaC, deltaP):
        """Devuelve el ratio entre el tiempo de caminata y el tiempo de pico abierto."""

        numerator = deltaC - deltaP
        denominator = deltaC + deltaP
        ##reemplazo valores 0 del denominador por 1
        denominator[denominator == 0] = 1
        return numerator/denominator
    
    @property
    def deltaO(self):
        """Devuelve el tiempo de operación."""
        return self._deltaO
    
    @property
    def deltaC(self):
        """Devuelve el tiempo de caminata."""
        return self._deltaC
    
    @property
    def deltaP(self):
        """Devuelve el tiempo de pico abierto."""
        return self._deltaP
    
    @property
    def ratio_dCdP(self):
        """Devuelve el ratio entre el tiempo de caminata y el tiempo de pico abierto."""
        return self._ratio_dCdP
    
    @property
    def dataPositions(self):
        """Devuelve el diccionario con las posiciones de los datos dentro del array devuelto por transform()."""
        return self._dataPositions
    
if __name__ == "__main__":
    
    import pandas as pd
    import numpy as np
    import os
    path = os.path.join(os.getcwd(), "examples\\volcado_17112023_NODE_processed.csv")
    raw_data = pd.read_csv(path, sep=";", ).to_numpy()
    timestamps = raw_data[50:60,3].astype(float)
    tlm_data = raw_data[50:60,2]
       
    from sarapy.dataProcessing import TLMSensorDataProcessor
    tlm_extractor = TLMSensorDataProcessor.TLMSensorDataProcessor()
    tlm_extractor.fit(tlm_data)
    
    deltaPicos = tlm_extractor.TIMEAC.astype(float)

    tmsp = TimeSeriesProcessor()
    
    #creamos un array con los timestamps y los tiempos de pico abierto de la forma (n, 2)
    X = np.hstack((timestamps.reshape(-1, 1), deltaPicos.reshape(-1, 1)))

    tmsp.fit(X)
    tmsp.transform(X)
    tmsp.fit_transform(X)
    print(tmsp.dataPositions)
    
    ### PROBAMOS QUÉ SUCEDE SI TENEMOS UNA SOLA FILA
    tlm_data2 = np.array(["0010001000001100110000001100001000000000000000001111111000110000"])
    timestamps2 = np.array([1697724423])
    
    tmsp2 = TimeSeriesProcessor() 
    tlm_extractor2 = TLMSensorDataProcessor.TLMSensorDataProcessor()
    
    tlm_extractor2.fit(tlm_data2)
    
    X2 = np.hstack((timestamps2.reshape(-1, 1), tlm_extractor2.TIMEAC.reshape(-1, 1)))
    
    tmsp2.fit(X2)
    tmsp2.transform(X2)