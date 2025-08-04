import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import datetime

class TransformToOutputData(BaseEstimator, TransformerMixin):
    """Método para transformar los datos recibidos a una lista de diccionarios
        
        Args:
            - dataToTransform: array con los datos de las operaciones clasificadas.
            Actualmente el array de dataToTransform es de (n,5) con las columnas siguientes
            
                - 0: timestamp
                - 1: tag_seedling
                - 2: tag_fertilizer           
        Returns:
            Retorna una lista de diccionarios con la siguiente estructura
        """

    def __init__(self):
        """
        Constructor de la clase TransformToOutputData.
        
        Args:
            - features_list: Lista con los nombres de las columnas a extraer de los datos recibidos de cada operación.
        """
        self.is_fitted = False
        
    def fit(self, X:np.array, y = None):
        """
        Args:
            - X: array con los datos de las operaciones clasificadas.
            Actualmente el array de dataToTransform es de (n,5) con las columnas siguientes
            
                - 0: timestamp
                - 1: tag_seedling
                - 2: tag_fertilizer       
        """
        self.is_fitted = True
        keys = ["timestamp","tag_seedling", "tag_fertilizer"]        
        self.temp_df = pd.DataFrame(X, columns = keys)

        ##convierto las columnas "timestamp", "tag_seedling" a int
        for col in ["tag_seedling"]:
            self.temp_df[col] = self.temp_df[col].astype(float).astype(int)
        ##convierto la columna "tag_fertilizer" a float de y redondeo a 3 decimales
        self.temp_df["tag_fertilizer"] = self.temp_df["tag_fertilizer"].astype(float).round(3)

        return self
    
    def transform(self, X:np.array):
        """
        Args:
            - X: array con los datos de las operaciones clasificadas.
            Actualmente el array de dataToTransform es de (n,5) con las columnas siguientes
            
                - 0: timestamp
                - 1: tag_seedling
                - 2: tag_fertilizer              
        Returns:
            Retorna una lista de diccionarios donde cada diccionario contiene los datos de una operación para los campos mencionados anteriormente.
        """

        return self.temp_df.to_dict(orient = "records")
    
    def fit_transform(self, X:np.array, y = None):
        """
        Args:
            - X: array con los datos de las operaciones clasificadas.
            Actualmente el array de dataToTransform es de (n,5) con las columnas siguientes
            
                - 0: timestamp
                - 1: tag_seedling
                - 2: tag_fertilizer         
        Returns:
            Retorna una lista de diccionarios donde cada diccionario contiene los datos de una operación para los campos mencionados anteriormente.
        """
        self.fit(X)
        return self.transform(X)
