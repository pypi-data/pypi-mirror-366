###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sarapy.mlProcessors import PlantinFMCreator
import pickle

class PlantinClassifier(BaseEstimator, TransformerMixin):
    """Clase para implementar el pipeline de procesamiento de datos para la clasificación del tipo de operación para plantines."""
    
    def __init__(self, classifier_file = ""):
        """Constructor de la clase PlantinClassifier.
        
        Args:
            - classifier_file: String con el nombre del archivo que contiene el clasificador entrenado. El archivo a cargar es un archivo .pkl.
        """

        #cargo el clasificador con pickle. Usamos try para capturar el error FileNotFoundError
        try:
            with open(classifier_file, 'rb') as file:
                self._pipeline = pickle.load(file)
            print("Clasificador cargado con éxito.")
        except FileNotFoundError:
            print("El archivo no se encuentra en el directorio actual.")
        
    def classify(self, feature_matrix, dst_pt, inest_pt,
                update_samePlace:bool = True, update_dstpt: bool = True,
                umbral_proba = 0.85, **kwargs):
        """Genera la clasificación de las operaciones para plantines.
        
        - feature_matrix: Es un array con los datos (strings) provenientes de la base de datos histórica.
        La forma de newData debe ser (n,3). Las columnas de newData deben ser,
                - 1: deltaO
                - 2: ratio_dCdP
                - 3: distancias
        - dst_pt: Array con las distorsiones de plantín.
        - inest_pt: Array con flag de inestabilidad de plantín.

        kwargs: Diccionario con los argumentos necesarios para la clasificación.

        NOTA: Estas características son necesarias en base a la última versión del modelo de clasificación.
        """

        self.clasificaiones = self._pipeline.predict(feature_matrix)
        self.probas = self._pipeline.predict_proba(feature_matrix)

        if update_samePlace:
            self.grouped_ops = self.groupOpsSamePlace(feature_matrix, **kwargs)
            self.clasificaiones = self.updateLabelsSamePlace(self.clasificaiones, self.grouped_ops)

        if update_dstpt:
            self.clasificaiones = self.updateLabelsFromDSTPT(self.clasificaiones, dst_pt, inest_pt, umbral_proba)

        return self.clasificaiones
    
    def groupOpsSamePlace(self, X, useRatioStats = True, std_weight=1, useDistancesStats = True,
                          ratio_dcdp_umbral=0.1, dist_umbral=0.5):
        """
        Función que agrupa las operaciones que se realizaron en el mismo lugar o que sean de limpieza.
        Se entiende por operación en el mismo lugar aquellas operaciones que tengan distancias entre sí menores a 0.5.
        La función tomará las operaciones que tengan distancias menores a 0.5 y la operación anterior, dado que se supone que la 
        operación anterior se corresponde a un nuevo sitio de plantado.

        Las operaciones de limpieza son aquellas que tienen un ratio_dCdP menor a 0.3

        Args:
        - X: Array con las features de operaciones. Las columnas son deltaO, ratio_dCdP y distances.
        - useRatioStats: Booleano para usar o no las estadísticas. Por defecto es True.
        - std_weight: Peso para la desviación estándar. Por defecto es 1.
        - ratio_dcdp_umbral: Umbral para el ratio_dCdP. Por defecto es 0.1.
        - dist_umbral: Umbral para la distancia (en metros). Por defecto es 0.5.
        
        Retorna:
        - Una lista con los índices de las operaciones agrupadas.
        """

        if useRatioStats:
            median_ratio_dcdp = np.median(X[:,1])
            std_ratio_dcdp = np.std(X[:,1])
            ratio_dcdp_umbral = median_ratio_dcdp - std_weight*std_ratio_dcdp

        if useDistancesStats:
            median_dist = np.median(X[:,2])
            # std_dist = np.std(X[:,2])
            dist_umbral = median_dist #- std_weight*std_dist

        ##recorro las operaciones y comparo la actual con la siguiente. Si la distancia es menor a 0.5, la agrupo.
        ##Si el ratio_dCdP es menor a 0.3, la agrupo.
        grouped_ops = []
        distancias = X[:,2]
        ratio_dcdp = X[:,1]
        flag_cleaning = True
        for i in range(1,X.shape[0]):
            if flag_cleaning:
                sub_group = []
            if distancias[i] < dist_umbral and ratio_dcdp[i] < ratio_dcdp_umbral:
                flag_cleaning = False
                sub_group.append(i-1)
                sub_group.append(i)
            else:
                flag_cleaning = True
                if len(sub_group) > 0:
                    grouped_ops.append(sub_group)

        ##recorro grouped_ops y elimino los elementos que se repiten dentro de cada subgrupo y ordeno los indices dentro de cada subgrupo
        for i in range(len(grouped_ops)):
            grouped_ops[i] = list(set(grouped_ops[i]))
            grouped_ops[i].sort()

        return grouped_ops

    def updateLabelsSamePlace(self, labels, ops_grouped):
        """
        Función para actualizar las etiquetas de las operaciones agrupadas en el mismo lugar.

        Args:
        - labels: Array con las etiquetas de las operaciones.
        - indexes: Array con los índices correspondientes a operaciones repetidas
        """
        new_labels = labels.copy()
        for indexes in ops_grouped:
            new_labels[indexes[0]] = 1
            new_labels[indexes[1:]] = 0

        return new_labels
    
    def updateLabelsFromDSTPT(self, labels, dst_pt, inest_pt, umbral_proba = 0.85):
        """
        Función para actualizar las etiquetas de las operaciones que tengan distorsiones de plantín.
        """
        new_labels = labels.copy()
        
        ##filtro si dst_pt es menor a 7 y si inest_pt es 0
        new_labels[(dst_pt < 4) & (inest_pt == 0)] = 0

        ##si inest_pt 1 es y umbral_proba es menor a umbra_proba, entonces la operación es 0
        new_labels[(inest_pt == 1) & (self.probas[:,1] < umbral_proba)] = 0

        return new_labels
    
if __name__ == "__main__":
    import os
    import pandas as pd
    import numpy as np
    from sarapy.preprocessing import TransformInputData
    from sarapy.mlProcessors import PlantinFMCreator
    import sarapy.utils.getRawOperations as getRawOperations
    from sarapy.mlProcessors import PlantinClassifier

    fmcreator = PlantinFMCreator.PlantinFMCreator(imputeDistances=False)
    tindata = TransformInputData.TransformInputData()

    data_path = os.path.join(os.getcwd(), "examples\\2024-10-15\\UPM015N\\data.json")
    historical_data_path = os.path.join(os.getcwd(), "examples\\2024-10-15\\UPM015N\\historical-data.json")
    raw_data = pd.read_json(data_path, orient="records").to_dict(orient="records")
    raw_data2 = pd.read_json(historical_data_path, orient="records").to_dict(orient="records")

    raw_ops = np.array(getRawOperations.getRawOperations(raw_data, raw_data2))
    raw_X = tindata.fit_transform(raw_ops)[:,2:]

    X, dst_pt, inest_pt = fmcreator.fit_transform(raw_X)

    rf_clf_nu = PlantinClassifier.PlantinClassifier(classifier_file='modelos\\pipeline_rf.pkl') ##wu = no update
    rf_clf_wu = PlantinClassifier.PlantinClassifier(classifier_file='modelos\\pipeline_rf.pkl') ##wu = with update

    print(rf_clf_nu.classify(X, dst_pt, inest_pt, update_samePlace = False, update_dstpt=False).mean())
    print(rf_clf_wu.classify(X, dst_pt, inest_pt, update_samePlace=True, update_dstpt=True,
    useRatioStats=True, useDistancesStats=True,umbral_proba=0.8).mean()) 
