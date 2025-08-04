###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md

import numpy as np
from geopy.distance import geodesic
from sklearn.base import BaseEstimator, TransformerMixin
import warnings

class GeoProcessor(BaseEstimator, TransformerMixin):
    """La clase GeoProcessor se encarga de gestionar los datos de georreferenciación."""
    
    def __init__(self):
        """Inicializa la clase GeoProcessor."""
        
        self._points = None #np.array de tuplas con las coordenadas de latitud y longitud
        self.is_fitted = False

    @staticmethod
    def getDistance(point1: float, point2: float) ->float:
        """Calcula la distancia elipsoidal (en metros) entre los puntos p1 y p2 donde cada punto
        está representado como un array con un valor de latitud y otro de longitud. 

        Parametros
            point1 (float): array con los valores de latitud y longitud del punto 1
            point2 (float): array con los valores de latitud y longitud del punto 2

        Returns:
            float con las distancias entre los dos puntos
        """
        
        ##aplicamos la función geodesic
        return geodesic(point1, point2).meters
        
    def fit(self, X: np.array, y=None)-> np.array:
        """fittea el objeto
        
        - X: array con los puntos de latitud y longitud. Shape (n, 2)
        """
        ##asserteamos que X sea un np.array
        assert isinstance(X, np.ndarray), "X debe ser un np.array"
        ##asserteamos que X tenga dos columnas
        assert X.ndim == 2, "X debe ser de la forma (n, 2)"
        ##chequeamos que X tenga una sola fila, si es así, enviamos un warning
        if X.shape[0] == 1:
            warnings.warn("En GeoProcesor.fit(): X tiene una sola fila, por lo tanto no se puede computar la distancia entre los puntos.\
                          \n Se devolverá un array con un solo valor de 0.0.")

        self._points = X
        self.is_fitted = True
        
    def transform(self, X, y=None):
        """Transforma los datos de X en distancias entre los puntos.
        
        - X: array con los puntos de latitud y longitud. Shape (n, 2)-
        
        Returns:
            np.array: np.array con las distancias entre los dos puntos
        """
        if not self.is_fitted:
            raise RuntimeError("El modelo no ha sido fitteado.")
        
        if self._points.shape[0] >= 2:
            ##calculamos la distancia entre los puntos de latitud y longitud dentro de X
            self._distances = np.array([self.getDistance(point1, point2) for point1, point2 in zip(self.points[1:],self.points)]).round(2)
            #agrego un cero al inicio de la lista de distancias ya que el primer punto no tiene una operación previo con la cual comparar
            self._distances = np.insert(self._distances, 0, 0)
        
        elif self._points.shape[0] == 1:
            self._distances = np.array([0])
        
        return self._distances

    def fit_transform(self, X, y=None):
        """Fit y transforma los datos de X en distancias entre los puntos.
        
        - X: datos de entrenamiento
        
        Returns:
            np.array: np.array con las distancias entre los dos puntos
        """
        X = self.sanityCheck(X)
        self.fit(X)
        return self.transform(self.points)
    
    def sanityCheck(self, X):
        """Chequea que los datos de latitud y lingitud estén en rangos válidos.

        - Latitud: -90 a 90
        - Longitud: -180 a 180
        
        - X: array con los puntos de latitud y longitud. Shape (n, 2)
        """
        ##calculo los valores medios de latitud y longitud sin contar los valores de latitud fuera de rango (-90, 90)
        ##y los valores de longitud fuera de rango (-180, 180)

        mask_lat = (X[:, 0] >= -90) & (X[:, 0] <= 90)
        mask_lon = (X[:, 1] >= -180) & (X[:, 1] <= 180)

        X_temp = X[mask_lat & mask_lon]
        self.media_lat = np.mean(X_temp[:, 0])
        self.media_lon = np.mean(X_temp[:, 1])

        ##mensaje de warning si hay valores de latitud fuera de rango
        if not mask_lat.all():
            warnings.warn("Hay valores de latitud fuera de rango. Se reemplazarán por el valor medio de latitud.")

        ##mensaje de warning si hay valores de longitud fuera de rango
        if not mask_lon.all():
            warnings.warn("Hay valores de longitud fuera de rango. Se reemplazarán por el valor medio de longitud.")

        ##reemplazo los valores de latitud y longitud fuera de rango por los valores medios
        X[~mask_lat, 0] = self.media_lat
        X[~mask_lon, 1] = self.media_lon

        return X
        
    @property
    def points(self):
        """Devuelve los puntos de georreferenciación."""
        return self._points
    
    @property
    def distances(self):
        """Devuelve las distancias entre los puntos."""
        ##chqueamos que el modelo haya sido fitteado
        if not self.is_fitted:
            warnings.warn("El modelo no ha sido fitteado.")
            return None
        else:
            return self._distances
        
        
if __name__ == "__main__":

    import pandas as pd
    import numpy as np
    import os
    path = os.path.join(os.getcwd(), "examples\\volcado_17112023_NODE_processed.csv")
    raw_data = pd.read_csv(path, sep=";", ).to_numpy()

    ga = GeoProcessor()

    puntos = raw_data[50:60, 4:6]

    ga.fit(puntos)
    print(ga.transform(puntos))
    print(ga.fit_transform(puntos))
    print(ga.distances)
    punto_referencia = puntos[0]
    
    sample = np.array([[-32.329910, -57.229061]])
    
    ga2 = GeoProcessor()
    ga2.fit(sample)
    ga2.points
    print(ga2.fit_transform(sample))
    print(ga2.distances)