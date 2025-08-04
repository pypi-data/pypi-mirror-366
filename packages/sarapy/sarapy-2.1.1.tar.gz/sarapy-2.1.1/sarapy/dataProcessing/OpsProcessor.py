###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md
import numpy as np
import pandas as pd
from sarapy.mlProcessors import PlantinFMCreator
from sarapy.mlProcessors import PlantinClassifier
from sarapy.preprocessing import TransformInputData, TransformToOutputData
from sarapy.mlProcessors import FertilizerFMCreator, FertilizerTransformer
import logging

##nivel de logging en warning para evitar mensajes de advertencia de sklearn
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

class OpsProcessor():
    """Clase para procesar las operaciones de los operarios. La información se toma de la base de datos
    hostórica y se procesa para obtener un array con las operaciones clasificadas para cada operario.
    
    La clase recibe una muestra desde la base de datos histórica y la procesa para obtener las
    operaciones clasificadas para cada operario. Se clasifican las operaciones desde el punto de vista
    del plantín y del fertilizante. La clasificación del tipo de operación respecto de plantín se hace
    con el pipeline para plantín, idem para el fertilizante.
    """
    
    def __init__(self, **kwargs):
        """Constructor de la clase OpsProcessor.
        
        Args:
            - kwargs: Diccionario con los argumentos necesarios instanciar algunas clases.
        """

        plclass_map = {"classifier_file"}

        kwargs_plclass = {}
        ##recorro kwargs y usando plclass_map creo un nuevo diccionario con los valores que se pasaron
        for key, value in kwargs.items():
            if key in plclass_map:
                kwargs_plclass[key] = value

        fmcreator_map = {"imputeDistances", "distanciaMedia", "umbral_precision",
                         "dist_mismo_lugar", "max_dist", "umbral_ratio_dCdP", "deltaO_medio"}
        fmcreator_kargs = {}
        ##recorro kwargs y usando fmcreator_map creo un nuevo diccionario con los valores que se pasaron
        for key, value in kwargs.items():
            if key in fmcreator_map:
                fmcreator_kargs[key] = value
        
        self._plantin_classifier = PlantinClassifier.PlantinClassifier(**kwargs_plclass)
        self.plantinFMCreator = PlantinFMCreator.PlantinFMCreator(**fmcreator_kargs)
        
        ##mapa de argumentos para FertilizerTransformer
        ft_map = {"regresor_file", "poly_features_file"}
        ft_kwargs = {}
        ##recorro kwargs y usando ft_map creo un nuevo diccionario con los valores que se pasaron
        for key, value in kwargs.items():
            if key in ft_map:
                ft_kwargs[key] = value

        self._ftfmcreator = FertilizerFMCreator.FertilizerFMCreator()
        self._fertilizer_transformer = FertilizerTransformer.FertilizerTransformer(**ft_kwargs)
        
        self._operationsDict = {} ##diccionario de operarios con sus operaciones
        self._platin_classifiedOperations = np.array([]) ##array con las operaciones clasificadas para plantin
        self._fertilizer_classifiedOperations = np.array([]) ##array con las operaciones clasificadas para plantin
        self._last_row_db = 0 ##indicador de la última fila de los datos extraidos de la base de datos histórica
        self.transformInputData = TransformInputData.TransformInputData()
        self.transformToOutputData = TransformToOutputData.TransformToOutputData()
        
    def processOperations(self, data, **kwargs):
        """Método para procesar las operaciones de los operarios.

        Se toma una nueva muestra y se procesa la información para clasificar las operaciones considerando el
        plantín y por otro lado el fertilizante.
        Se retorna un array con las clasificaciones concatenadas, manteniendo el orden de las operaciones por operario.

        Args:
            - data: Lista de diccionario. Cada diccionario tiene la forma.
            Ejemplo (NOTA: El salto de línea es agregado para mejorar la legibilidad):
            [
            {"id": 6, "receiver_timestamp": "2025-06-21T15:51:36.527825+00:00", "timestamp": "2025-06-21T15:51:01.000002+00:00", "datum": null,
            "csv_datum": "2025-06-21T15:51:01.000002+00:00,2,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,-58.0321,-33.2471,
            1,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,0,0,0,0,1,0,0,1,1,0,3,0,0,0,0,3,0,0,0,0,0,1,0,0,0,0,0.0000,0.0000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", 
            "longitude": null, "latitude": null, "accuracy": null, "tag_seedling": null, "tag_fertilizer": null}
            ]
            
        Returns:
            Lista de diccionarios con las clasificaciones. Cada diccionario tiene la forma
            [{"timestamp": "2025-05-27T21:42:38.000002+00:00", "tag_seedling": 1, "tag_fertilizer": gramos (float)},...]
        """
        
        ##chqueo que newSample no esté vacío
        if len(data) != 0:
            newSample = self.transformInputData.transform(data)

            #Si tenemos nuevas operaciones, actualizamos el diccionario de operaciones
            self.updateOperationsDict(newSample) #actualizamos diccionario interno de la clase
            pl_clas = self.classifyForPlantin(**kwargs) #clasificamos las operaciones para plantín

            #estimamos los gramos de fertilizante
            ft_grams = self._fertilizer_transformer.transform(newSample)
            logging.debug(f"Fertilizer grams shape: {ft_grams.shape}")
            id_db_h_nums, id_db_dw_nums = self.getActualOperationsNumbers() #obtenemos los números de operaciones desde el diccionario de operaciones
            logging.debug(f"ID_DB_H shape: {id_db_h_nums.shape}, ID_DB_DW shape: {id_db_dw_nums.shape}")
            date_oprc = pd.DataFrame(newSample)["date_oprc"].values.reshape(-1, 1) ##extraigo las fechas de operación de la muestra
            timestamps = pd.DataFrame(newSample)["timestamp"].values.reshape(-1, 1) ##extraigo los timestamps de la muestra
            
            return self.transformToOutputData.fit_transform(np.column_stack((timestamps,
                                                                             pl_clas,
                                                                             ft_grams)))
        else:
            self.resetAllNewSamplesValues()
            return None
        
    def updateOperationsDict(self, newSample):
        """Actualiza el diccionario de operaciones.
        
        Args:
            - newSample: lista de diccionarios con los datos de  las operaciones.

        """
        nodos_recibidos = np.array([row["ID_NPDP"] for row in newSample]) ##nodos recibidos en la muestra
        ID_NPDPs_newOperations = np.unique(nodos_recibidos) ##identificadores de operarios con nuevas operaciones en la muestra
        logging.debug(f"Received nodes: {ID_NPDPs_newOperations}")

        ##chqueo si estos ID_NPDPs ya están en el diccionario, sino los agrego
        for ID_NPDP in ID_NPDPs_newOperations:
            if ID_NPDP not in self._operationsDict:
                #El diccionario contiene la siguiente información:
                #sample_ops: lista de diccionarios con los datos de las operaciones.
                #last_oprc: diccionario con la última operación registrada.
                #first_day_op_classified: booleano para saber si es la primera operación del día que fue clasificada
                self._operationsDict[ID_NPDP] = {"sample_ops": None,
                                                 "last_oprc": None, 
                                                 "first_day_op_classified": False,
                                                 "new_sample": False,
                                                 "id_db_h": None,
                                                 "id_db_dw": None} #inicio del diccionario anidado para el nuevo operario
                
        ##actualizo el diccionario con las operaciones nuevas para aquellos operarios que correspondan
        for ID_NPDP in ID_NPDPs_newOperations:
            sample_ops = newSample
            id_db_h = np.array([row["id_db_h"] for row in newSample]) ##extraigo los id_db_h de la muestra
            id_db_dw = np.array([row["id_db_dw"] for row in newSample])
            ##actualizo el diccionario
            self._operationsDict[ID_NPDP]["sample_ops"] = sample_ops
            self._operationsDict[ID_NPDP]["id_db_h"] = np.astype(id_db_h, str) ##convierto a int
            self._operationsDict[ID_NPDP]["id_db_dw"] = np.astype(id_db_dw, str) ##convierto a int
            ##chequeo si tenemos última operación, si es así, asignamos dicha operación en la primera fila de sample_ops
            last_op = self._operationsDict[ID_NPDP]["last_oprc"]
            ###si last_op es not None y last_op no está vacía, entonces concatenamos last_op con sample_ops
            if last_op is not None and len(last_op) != 0:
                self._operationsDict[ID_NPDP]["sample_ops"] += last_op ##concatenamos la última operación con las nuevas operaciones
                
        self.updateNewSamplesValues(ID_NPDPs_newOperations) #actualizo el estado de 'new_sample' en el diccionario de operaciones
        self.updateLastOperations(ID_NPDPs_newOperations) #actualizo la última operación de una muestra de operaciones en el diccionario de operaciones

    def classifyForPlantin(self, **kwargs):
        """Método para clasificar las operaciones para plantín.
        Se recorre el diccionario de operaciones y se clasifican las operaciones para plantín.

        Args:
            - kwargs: Diccionario con los argumentos necesarios para la clasificación. Se utiliza para pasar argumentos a los métodos de clasificación.

        Returns:
            - plantinClassifications: np.array con las clasificaciones de las operaciones para plantín.
        """

        key_classify_map = {"feature_matrix", "update_samePlace",
                            "useRatioStats", "std_weight", "useDistancesStats",
                            "ratio_dcdp_umbral", "dist_umbral"}
        
        ##recorro kwargs y usando key_classify_map creo un nuevo diccionario con los valores que se pasaron
        classify_kwargs = {}
        for key, value in kwargs.items():
            if key in key_classify_map:
                classify_kwargs[key] = value

        ##creamos/reiniciamos el array con las clasificaciones de las operaciones para plantín
        plantinClassifications = None
        
        ##me quedo con los ID_NPDPs que tengan _operationsDict[ID_NPDP]["new_sample"] iguales a True
        ops_with_new_sample = [ID_NPDP for ID_NPDP in self._operationsDict.keys() if self.operationsDict[ID_NPDP]["new_sample"]]

        for ID_NPDP in ops_with_new_sample:#self.operationsDict.keys():
            ##clasificamos las operaciones para plantín
            operations = self._operationsDict[ID_NPDP]["sample_ops"]
            logging.debug(f"Número de operaciones para el nodo {ID_NPDP}: {len(operations)}")
            features, dst_pt, inest_pt = self.plantinFMCreator.fit_transform(operations)
            logging.debug(f"Features shape for {ID_NPDP}: {features.shape}")
            classified_ops = self._plantin_classifier.classify(features, dst_pt, inest_pt, **classify_kwargs)
            logging.debug(f"Classified operations shape for {ID_NPDP}: {classified_ops.shape}")
            
            ##chequeo si first_day_op_classified es True, si es así, no se considera la primera fila de las classified_ops
            if self._operationsDict[ID_NPDP]["first_day_op_classified"]:
                classified_ops = classified_ops[1:]

            ##actualizo las operaciones que hayan sido hardcodeadas luego de despertar y/o reiniciar la electrónica
            classified_ops = self.updateAfterAwake(classified_ops)
                
            plantinClassifications = np.concatenate((plantinClassifications, classified_ops)) if plantinClassifications is not None else classified_ops
            
            self._operationsDict[ID_NPDP]["first_day_op_classified"] = True

        return plantinClassifications
            
    def updateLastOperations(self, ID_NPDPs_newOperations):
        """Método para actualizar la última operación de una muestra de operaciones en el diccionario de operaciones

        Args:
            - newSample: lista de diccionarios con los datos de  las operaciones.
        """
        
        for ID_NPDP in ID_NPDPs_newOperations:
            self._operationsDict[ID_NPDP]["last_oprc"] = self._operationsDict[ID_NPDP]["sample_ops"][-1]
    
    def updateNewSamplesValues(self, ID_NPDPs_newOperations):
        """Método para actualizar el estado de 'new_sample' del diccionario de operaciones.

        Args:
            - ID_NPDPs_newOperations: lista con los ID_NPDPs que tienen nuevas operaciones.
        """

        ##recorro el diccionario de operaciones y actualizo el estado de 'new_sample' a
        ##True para los ID_NPDPs que tienen nuevas operaciones y a False para los que no tienen nuevas operaciones
        for ID_NPDP in self._operationsDict.keys():
            if ID_NPDP in ID_NPDPs_newOperations:
                logging.debug(f"Actualizando 'new_sample' para nodo: {ID_NPDP}")
                self._operationsDict[ID_NPDP]["new_sample"] = True
            else:
                self._operationsDict[ID_NPDP]["new_sample"] = False
    
    def resetAllNewSamplesValues(self):
        """Método para resetar todos los valores de new_sample en el diccionario de operaciones.
        """
        
        for ID_NPDP in self._operationsDict.keys():
            self._operationsDict[ID_NPDP]["new_sample"] = False

    def getActualOperationsNumbers(self):
        """Método para obtener los números de operaciones desde el diccionario de operaciones para aquellos operarios que
        tienen nuevas operaciones en la muestra."""
        
        id_db_h_list = np.array([])
        id_db_dw_list = np.array([])
        for ID_NPDP in self._operationsDict.keys():
            if self._operationsDict[ID_NPDP]["new_sample"]:
                logging.debug(f"Obteniendo números de operaciones para el ID_NPDP: {ID_NPDP}")
                id_db_h_list = np.append(id_db_h_list, self._operationsDict[ID_NPDP]["id_db_h"].flatten())
                id_db_dw_list = np.append(id_db_dw_list, self._operationsDict[ID_NPDP]["id_db_dw"].flatten())

        return id_db_h_list.astype(int), id_db_dw_list.astype(int)
    
    def updateFirstDayOp(self):
        """Método para actualizar el indicador de si es la primera operación del día para cada operario en el diccionario de operaciones.
        """

        for ID_NPDP in self._operationsDict.keys():
            self._operationsDict[ID_NPDP]["first_day_op_classified"] = False
    
    def cleanSamplesOperations(self):
        """Método para limpiar las operaciones de un operario en el diccionario de operaciones.

        Args:
            - newSample: lista con los datos (numpy.array de strings) de las operaciones.
            La forma de cada dato dentro de la lista newSample es (n,6). Las columnas de newSample son,
            
                - 0: id_db_h
                - 1: ID_NPDP
                - 2: TLM_NPDP
                - 3: date_oprc
                - 4: latitud
                - 5: longitud
                - 6: Precision
        """

        for ID_NPDP in self._operationsDict.keys():
            self._operationsDict[ID_NPDP]["sample_ops"] = None

    def updateAfterAwake(self, classified_ops):
        """
        Función para actualizar las operaciones que hayan sido hardcodeadas luego de despertar y/o reiniciar la electrónica.

        Se chequea la bandera MODE de los datos de telemetría entregados por la electrónica.

        Args:
        - classified_ops: np.array con las operaciones clasificadas.

        Returns:
        - classified_ops: np.array con las operaciones clasificadas.
        """

        ##me quedo con los índices donde N_MODE es igual a 1
        mask = self.plantinFMCreator.tlmDataProcessor["N_MODE",:]==1
        classified_ops[mask] = 0 ##hardcodeo las operaciones que hayan sido clasificadas como 1
        return classified_ops
            
    @property
    def operationsDict(self):
        return self._operationsDict
    

if __name__ == "__main__":
    import pandas as pd
    import json
    import logging
    

    historical_data_path = "examples/2025-06-21/UPM000N/historical-data.json"
    with open(historical_data_path, 'r') as file:
        samples = json.load(file)

    samples1 = samples

    op = OpsProcessor(classifier_file='modelos\\pipeline_rf.pkl', imputeDistances = False,
                      regresor_file='modelos\\regresor.pkl', poly_features_file='modelos\\poly_features.pkl')
    
    print(op.processOperations(samples[:20]))
    # op.processOperations(samples2)