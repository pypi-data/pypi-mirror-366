###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sarapy.dataProcessing import TLMSensorDataProcessor, TimeSeriesProcessor, GeoProcessor

class PlantinFMCreator(BaseEstimator, TransformerMixin):
    """La clase FMCreator se encarga de crear la Feature Matrix (FM) a partir de los datos de telemetría.
    Se utilizan las clases TLMSensorDataProcessor, TimeSeriesProcessor y GeoProcessor para realizar las transformaciones necesarias.
    
    Versión 2.0.0
    
    En esta versión la matriz de características está formada por las siguientes variables
    
    - DST_PT: Distorsión de plantín
    - deltaO: delta operación
    - ratio_dCdP: Ratio entre el delta de caminata y delta de pico abierto
    - distances: Distancias entre operaciones
    - inest_pt: Inestabilidad del plantín
    """
    
    def __init__(self, imputeDistances = True, distanciaMedia:float = 1.8,
                 umbral_precision:float = 0.3, dist_mismo_lugar = 0.0, max_dist = 100,
                 umbral_ratio_dCdP:float = 0.5, deltaO_medio = 4):
        """Inicializa la clase FMCreator.
        
        Args:
            - imputeDistances: Si es True, se imputan las distancias entre operaciones. Si es False, no se imputan las distancias.
            - distanciaMedia: Distancia media entre operaciones.
            - umbral_precision: Umbral para considerar que dos operaciones son el mismo lugar.
            - umbral_ratio_dCdP: Umbral para el ratio entre el delta de caminata y el delta de pico abierto.
            - deltaO_medio: delta de operación medio entre operaciones.
        """
        
        self.is_fitted = False
        self.imputeDistances = imputeDistances
        self.distanciaMedia = distanciaMedia
        self.umbral_precision = umbral_precision
        self.dist_mismo_lugar = dist_mismo_lugar
        self.max_dist = max_dist
        self.umbral_ratio_dCdP = umbral_ratio_dCdP
        self.deltaO_medio = deltaO_medio
        
        ##creamos un diccionario para saber la posición de cada dato dentro del array devuelto por transform()
        self._dataPositions = {"DST_PT": 0, "deltaO": 2, "ratio_dCdP": 3, "distances": 4}
        
    def fit(self, X: np.array, y=None)-> np.array:
        """Fittea el objeto
        
        Params:
            - X: Es una lista de diccionarios (como un JSON) con los datos de telemetría.
        """
        self.is_fitted = True
        
    def transform(self, X: np.array, y = None):
        """Transforma los datos de X en la matriz de características.
        
        Params:
            - X: Es una lista de diccionarios (como un JSON) con los datos de telemetría.
                
        Returns:
                - 0: feature_matrix: (deltaO, ratio_dCdP, distances)
                - 1: dst_pt
                - 2: inest_pt
        """
        
        if not self.is_fitted:
            raise RuntimeError("El modelo no ha sido fitteado.")
        
        ##instanciamos los objetos a usar
        self.tlmDataProcessor = TLMSensorDataProcessor.TLMSensorDataProcessor(X)
        timeProcessor = TimeSeriesProcessor.TimeSeriesProcessor()
        tpDP = timeProcessor._dataPositions
        geoprocessor = GeoProcessor.GeoProcessor()
        

        date_oprc = self.tlmDataProcessor["date_oprc",:] #datos de fecha y hora de operación
        time_ac = self.tlmDataProcessor["TIME_AC",:] #datos de fecha y hora de operación en formato timestamp
        lats = self.tlmDataProcessor["latitud",:] #latitudes de las operaciones
        longs = self.tlmDataProcessor["longitud",:] #longitudes de las operaciones 
        self.dst_pt = self.tlmDataProcessor["SC_PT",:] #distorsión del plantín
        self.inest_pt = self.tlmDataProcessor["INST_PT",:] #inest 
        # precitions = X[:,4].astype(float) #precision del GPS   
        
        ##***** OBTENEMOS LOS DATOS PARA FITEAR LOS OBJETOS Y ASÍ PROCESAR LA FM *****
        
        ##fitteamos timeProcessor con los datos de fecha y hora de operación y los TIMEAC
        timeData = np.hstack((date_oprc.reshape(-1,1),time_ac.reshape(-1, 1)))
        
        self._timeDeltas = timeProcessor.fit_transform(timeData)
        
        ##fitteamos geoprocessor con las latitudes y longitudes
        points = np.hstack((lats.reshape(-1,1),longs.reshape(-1,1)))
        self._distances = geoprocessor.fit_transform(points)

        ##armamos la feature matrix
        self.featureMatrix = np.vstack((self._timeDeltas[:,tpDP["deltaO"]],
                                        self._timeDeltas[:,tpDP["ratio_dCdP"]],
                                        self._distances)).T
        
        return self.featureMatrix, self.dst_pt, self.inest_pt

    def fit_transform(self, X: np.array, y=None):
        """Fittea y transforma los datos de X en la matriz de características.
        
        Params:
            - X: Es una lista de diccionarios (como un JSON) con los datos de telemetría.
                
        Returns:
                - 0: feature_matrix: (deltaO, ratio_dCdP, distances)
                - 1: dst_pt
                - 2: inest_pt
        """
        self.fit(X)
        return self.transform(X)
    
    # @property
    # def tlmExtracted(self):
    #     """Devuelve los datos de telemetría extraídos."""
    #     return self.tlmExtracted
    
    @property
    def tlmdeDP(self):
        """Devuelve el diccionario con la posición de los datos dentro del array devuelto por transform()."""
        return self._tlmdeDP

    @property
    def timeDeltas(self):
        """Devuelve los datos de tiempo extraídos."""
        return self._timeDeltas
    
    @property
    def distances(self):
        """Devuelve las distancias entre operaciones."""
        return self._distances
    
    @property
    def dataPositions(self):
        """Devuelve el diccionario con la posición de los datos dentro del array devuelto por transform()."""
        return self._dataPositions
    
        
if __name__ == "__main__":
    import pandas as pd
    import json
    from sarapy.preprocessing import TransformInputData

    historical_data_path = "examples/2025-06-21/UPM000N/historical-data.json"
    with open(historical_data_path, 'r') as file:
        historical_data = json.load(file)
    df = pd.DataFrame(historical_data)

    ##cargo en un diccionario sarapy\preprocessing\telemetriaDataPosition.json
    data_positions = json.load(open("sarapy/preprocessing/telemetriaDataPosition.json", 'r'))
    transform_input_data = TransformInputData.TransformInputData()
    X = transform_input_data.transform(historical_data)
    
    fmcreator = PlantinFMCreator(imputeDistances=False)

    fm, dst_pt, inest_pt = fmcreator.fit_transform(X) 
    print(fm.shape)  # Debería ser (n_operaciones, 3)
