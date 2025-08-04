###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class FertilizerImputer(BaseEstimator, TransformerMixin):
    """Clase para imputar los datos de fertilizante.
    
    La idea principal es poder relevar la presencia o no de Fertilizante en la operación."""

    def __init__(self, n_next_ops, min_dist_level = 3, keepDims = False, columnToImpute = 0):
        """Constructor de la clase FertilizerImputer.
        
        Args:
            - n_prev_ops: Número de operaciones siguientes a considerar.
            - min_dist_level: Nivel mínimo de distorsión para considerar que hay fertilizante.
            - columnToImpute: Columna a imputar.
            - keepDims: Si es True, se mantienen las dimensiones del array de entrada. Si es False, se devuelve un array de una dimensión.
        """
        self.n_next_ops = n_next_ops
        self.min_dist_level = min_dist_level
        self._keepDims = keepDims
        self._columnToImpute = columnToImpute
        self.is_fitted = False
        self._dataPositions = {"fertilizante":0}

    def fit(self, X:np.array, y = None):
        """Fittea el objeto
        
        Params:
            - X: Es un array con los datos provenientes (strings) de la base de datos histórica. La forma de X es (n,1)
                - 0: Fertilizante
        """
        self._fertilizante = X[:,0]