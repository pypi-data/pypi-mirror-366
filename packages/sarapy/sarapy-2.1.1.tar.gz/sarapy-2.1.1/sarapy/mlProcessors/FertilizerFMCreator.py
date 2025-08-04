import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sarapy.dataProcessing import TLMSensorDataProcessor


class FertilizerFMCreator():
    """Clase para crear la matriz de características para el procesamiento del fertilizante"""

    def __init__(self):
        self._dataPositions = {"DST_FT": 0}
        self.dst_ft = None ##cuando no se ha transformado ningún dato, se inicializa en None

    def transform(self, X):
        """
        Transforma los datos de telemetría para retornar los datos de distorsión de fertilizante.

        Params:
            - X: Es un array con los datos de telemetría. La forma de X es (n,1)

        Returns:
            - dst_ft: Array con los valores de distorsión de fertilizante.
        """
        tlmDataExtractor = TLMSensorDataProcessor.TLMSensorDataProcessor()
        tlmdeDP = tlmDataExtractor.dataPositions #posiciones de los datos transformados de tlmDataExtractor

        tlmExtracted = tlmDataExtractor.fit_transform(X)

        self.dst_ft = tlmExtracted[:,tlmdeDP["DSTRFT"]]

        return self.dst_ft

if __name__ == "__main__":
    import os
    import pandas as pd
    import numpy as np
    from sarapy.preprocessing import TransformInputData
    from sarapy.mlProcessors import PlantinFMCreator
    import sarapy.utils.getRawOperations as getRawOperations
    tindata = TransformInputData.TransformInputData()

    ##cargo los archivos examples\2024-09-04\UPM001N\data.json y examples\2024-09-04\UPM001N\historical-data.json
    data_path = os.path.join(os.getcwd(), "examples\\2024-09-04\\UPM001N\\data.json")
    historical_data_path = os.path.join(os.getcwd(), "examples\\2024-09-04\\UPM001N\\historical-data.json")
    raw_data = pd.read_json(data_path, orient="records").to_dict(orient="records")
    raw_data2 = pd.read_json(historical_data_path, orient="records").to_dict(orient="records")

    raw_ops = np.array(getRawOperations.getRawOperations(raw_data, raw_data2))
    X = tindata.fit_transform(raw_ops) #transforma los datos de operaciones a un array de numpy
    
    from sarapy.mlProcessors import FertilizerFMCreator

    ftfmcreator = FertilizerFMCreator.FertilizerFMCreator()
    dst_ft = ftfmcreator.transform(X[:,2])
    print(dst_ft[:10]) #imprime los primeros 10 valores de DST_FT