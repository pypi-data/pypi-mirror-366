import pickle
from sarapy.dataProcessing import TLMSensorDataProcessor

class FertilizerTransformer:
    """
    Clase para tomar los valores de distorsión de fertilizante y transformarlos a gramos
    """

    def __init__(self, regresor_file, poly_features_file):
        """Constructor de la clase FertilizerImputer.

        Args:
            - regresor: Regresor que transforma los valores de distorsión a gramos.
            - poly_features: Grado del polinomio a utilizar en la transformación de los datos.        
        """
        ##cargo el regresor con pickle. Usamos try para capturar el error FileNotFoundError
        try:
            with open(regresor_file, 'rb') as file:
                self._regresor = pickle.load(file)
            print("Regresor cargado con éxito.")
        except FileNotFoundError:
            print("El archivo no se encuentra en el directorio actual.")

        ##cargo las características polinómicas con pickle. Usamos try para capturar el error FileNotFoundError
        try:
            with open(poly_features_file, 'rb') as file:
                self._poly_features = pickle.load(file)
            print("Características polinómicas cargadas con éxito.")
        except FileNotFoundError:
            print("El archivo no se encuentra en el directorio actual.")
            
        self.fertilizer_grams = None ##cuando no se ha transformado ningún dato, se inicializa en None


    def transform(self, data):
        """Transforma los datos de distorsión de fertilizante a gramos.

        Params:
            - data: Es una lista de diccionarios (como un JSON) con los datos de telemetría.

        Returns:
            - 0: Array con los valores de distorsión de fertilizante transformados a gramos.
        """
        tlmDataProcessor = TLMSensorDataProcessor.TLMSensorDataProcessor(data)
        X = tlmDataProcessor["SC_FT",:]
        X_poly = self._poly_features.fit_transform(X.reshape(-1, 1))
        self.fertilizer_grams = self._regresor.predict(X_poly)

        ##retorno con shape (n,)
        return self.fertilizer_grams.reshape(-1,)
    
if __name__ == "__main__":
    import pandas as pd
    import json
    from sarapy.preprocessing import TransformInputData

    historical_data_path = "examples/2025-06-21/UPM000N/historical-data.json"
    with open(historical_data_path, 'r') as file:
        historical_data = json.load(file)

    ##cargo en un diccionario sarapy\preprocessing\telemetriaDataPosition.json
    data_positions = json.load(open("sarapy/preprocessing/telemetriaDataPosition.json", 'r'))
    transform_input_data = TransformInputData.TransformInputData()
    transformed_data = transform_input_data.transform(historical_data)

    fertransformer = FertilizerTransformer(regresor_file='modelos\\regresor.pkl', poly_features_file='modelos\\poly_features.pkl')
    gramos = fertransformer.transform(transformed_data)
    print(gramos[:10])