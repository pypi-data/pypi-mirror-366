###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class DistancesImputer(BaseEstimator, TransformerMixin):
    """La clase DistancesImputer se encarga de imputar/modificar los datos de telemetría entregados por el sistema. Se utilizan las clases TLMSensorDataExtractor, TimeSeriesProcessor y GeoProcessor para realizar las transformaciones necesarias y luego aplicar las modificaciones necesarias en base a las reglas definidas luego del análisis estadístico.
    """
    
    def __init__(self, distanciaMedia:float = 1.8, umbral_precision:float = 0.3,
                 dist_mismo_lugar:float = 0.0, max_dist = 100,
                 umbral_ratio_dCdP:float = 0.5, deltaO_medio = 4, keepDims = False, columnToImpute = 0):
        """Constructor de la clase PlantinDataImputer.
        
        Args:
            - distanciaMedia: Distancia media entre operaciones.
            - umbral_precision: Umbral para considerar que dos operaciones son el mismo lugar.
            - dist_mismo_lugar: Distancia para considerar que dos operaciones son el mismo lugar.
            - umbral_ratio_dCdP: Umbral para el ratio entre el delta de caminata y el delta de pico abierto.
            - deltaO_medio: delta de operación medio entre operaciones.
            - columnToImpute: Columna a imputar.
            - keepDims: Si es True, se mantienen las dimensiones del array de entrada. Si es False, se devuelve un array de una dimensión.
        """
        
        self.is_fitted = False
        self._distanciaMedia = distanciaMedia
        self._umbral_precision = umbral_precision
        self._max_dist = max_dist
        self._dist_mismo_lugar = dist_mismo_lugar
        self._umbral_ratio_dCdP = umbral_ratio_dCdP
        self._deltaO_medio = deltaO_medio
        self._keepDims = keepDims
        self._columnToImpute = columnToImpute
        self._dataPositions = {"distancias":0} #posición de los datos en el array devuelto por transform()
        
    def fit(self, X:np.array, y = None):
        """Fittea el objeto
        
        Params:
            - X: Es un array con los datos provenientes (strings) de la base de datos histórica. La forma de X es (n,6)Las columnas de X son,
                - 0: distancia entre operaciones
                - 1: presición del GPS
                - 2: GNSSflag. Nandera para saber si hay dato GPS, donde 0 es que hay dato y 1 que no hay dato
                - 3: FIX bandera para tipo de fijación GNSS (ver valores enhttps://trello.com/c/M6DWjpwr/70-definici%C3%B3n-metadatos-a-relevar)
                - 4: deltaO
                - 5: ratio_dCdP
                
        NOTA: En versiones futuras se considerarán los datos de la posición (vertical, horizontal, etc) del sarapico
        """
        
        ##agregar asserts y warnings
        
        self._distancias = X[:,0] #distancias
        self._precision = X[:,1]
        self._GNSSflag = X[:,2]
        self._FIX = X[:,3]
        self._deltaO = X[:,4]
        self._ratio_dCdP = X[:,5]
        
    def transform(self, X:np.array, y = None):
        """Aplica las imputaciones para transformar el objeto y retorna el array transformado.
        
        Args:
            - X: Es un array con los datos provenientes (strings) de la base de datos histórica. La forma de X es (n,6)Las columnas de X son,
            
        Returns:
            - updatedDistances: Array con las distancias imputadas.
        """
        self._updatedDistances = self._imputeDistance()
        ##si keepDims es True, devolvemos x con las mismas dimensiones que el array de entrada. Los valores de self._updatedDistances se colocan en self._columnToImpute
        if not self._keepDims:
            return self._updatedDistances

        else:
            X[:,self._columnToImpute] = self._updatedDistances
            return X
        
    def fit_transform(self, X:np.array, y = None):
        """Fitea y aplica las imputaciones para transformar el objeto. Retorna el array transformado.
        
        Args:
            - X: Es un array con los datos provenientes (strings) de la base de datos histórica. La forma de X es (n,6)Las columnas de X son,
            
        Returns:
            - updatedDistances: Array con las distancias imputadas.
        """
        self.fit(X)
        return self.transform(X)
    
    def _imputeDistance(self):
        """Imputa la distancia entre operaciones.
        
        Si GNSSflag = 0, hay dato GPS, si GNSSflag = 1, no hay dato GPS.
        Si la precisión es menor al umbral del mismo lugar entonces se considera que la precision es buena.

        Luego, 

        Caso 0: GNSSflag = 0 y precision < umbral_precision -> la distancia no cambia
        Caso 1: GNSSflag = 0 y precision > umbral_precision -> la distancia se reemplazará por la distancia media si el ratio_dCdP es mayor al umbral_ratio_dCdP, sino por la distancia umbral_precision
        """
        caso1_indexes = np.where((self._GNSSflag == 0) & (self._precision > self._umbral_precision) & (self._distancias < self._max_dist))
        caso2_indexes = np.where((self._GNSSflag == 0) & (self._precision > self._umbral_precision) & (self._distancias > self._max_dist))
        caso3_indexes = np.where((self._GNSSflag == 1))
        
        #copiamos self._distances en updatedDistances
        updatedDistances = self._distancias
        
        if len(caso1_indexes[0]) > 0:
            updatedDistances[caso1_indexes] = np.vectorize(lambda ratio: self._dist_mismo_lugar
                                                        if ratio < self._umbral_ratio_dCdP
                                                        else self._distanciaMedia)(self.ratio_dCdP[caso1_indexes])
            
        if len(caso2_indexes[0]) > 0:
            updatedDistances[caso2_indexes] = np.vectorize(lambda ratio: self._dist_mismo_lugar
                                                        if ratio < self._umbral_ratio_dCdP
                                                        else self._max_dist)(self.ratio_dCdP[caso2_indexes])
            
        if len(caso3_indexes[0]) > 0:
            updatedDistances[caso3_indexes] = np.vectorize(lambda ratio: self._dist_mismo_lugar
                                                        if ratio < self._umbral_ratio_dCdP
                                                        else self._distanciaMedia)(self.ratio_dCdP[caso3_indexes])
        
        return updatedDistances
    
    @property
    def distancias(self):
        return self._distancias
    
    @property
    def precision(self):
        return self._precision
    
    @property
    def GNSSflag(self):
        return self._GNSSflag
    
    @property
    def FIX(self):
        return self._FIX
    
    @property
    def deltaO(self):
        return self._deltaO
    
    @property
    def ratio_dCdP(self):
        return self._ratio_dCdP
    
    @property
    def updatedDistances(self):
        return self._updatedDistances
    

if __name__ == "__main__":
    from sarapy.dataProcessing import TimeSeriesProcessor, GeoProcessor
    from sarapy.dataProcessing import TLMSensorDataProcessor
    tlmda = TLMSensorDataProcessor.TLMSensorDataProcessor()
    tsa = TimeSeriesProcessor.TimeSeriesProcessor()
    gpa = GeoProcessor.GeoProcessor()

    ##datos de ejemplo
    tlmsbp_sample = np.array(['0010001000010010110000011000000111111101001000000000000000000000',
                              '0010001000010100110000011000000111111101001000000000000000000000',
                              '0010001000010000110000011000000111111101001000000000000000000000',
                              '0010001000011010110000011000110111111101001000000000000000000000'])
    
    date_oprc = np.array([35235, 35240, 35244, 35248])
    lats = np.array(["-32.331093", "-32.331116", "-32.341131", "-32.331146"]).astype(float)
    lons = np.array(["-57.229733", "-57.229733", "-57.229733", "-57.22974"]).astype(float)

    precisiones = np.array([0.1, 12, 0.1, 1])

    tlmda_data = tlmda.fit_transform(tlmsbp_sample)
    timesAC = tlmda.ESTAC

    time_data = np.hstack((date_oprc.reshape(-1, 1), timesAC.reshape(-1, 1)))
    tsa_data = tsa.fit_transform(time_data)

    ##genero puntos donde la primer columna es latitud y la segunda longitud
    puntos = np.hstack((lats.reshape(-1, 1), lons.reshape(-1, 1)))
    distancias = gpa.fit_transform(puntos)

    X = np.hstack((distancias.reshape(-1, 1),
                   precisiones.reshape(-1, 1),
                   tlmda.GNSSFlag.reshape(-1,1),
                   tlmda.FIX.reshape(-1,1), tsa.deltaO.reshape(-1,1),
                   tsa.ratio_dCdP.reshape(-1,1)))
    
    distanceimputer = DistancesImputer()
    distanceimputer.fit(X)

    print(distanceimputer.transform(X))
    print(distanceimputer.fit_transform(X))