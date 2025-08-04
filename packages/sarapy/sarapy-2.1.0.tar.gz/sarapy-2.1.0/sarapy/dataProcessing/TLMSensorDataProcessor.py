###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md
import numpy as np
import pandas as pd

class TLMSensorDataProcessor():
    """- Autor: BALDEZZARI Lucas

    Estar clase sirve para entegar los datos de telemetría como un array de numpy. La idea es
    poder acceder a los datos a través de indexación, ejemplos:
    tlm_data[["INST_PT","INST_FT"],:] en este caso se obtienen los datos de las columnas INST_PT e INST_FT
    
    """
    
    def __init__(self, data:list):
        """Constructor de la clase MetadataManager
        
        Args:
         - data: Es una lista de diccionarios (como un JSON) con los datos de telemetría.
        """
        #convierto a un DataFrame de pandas
        self.data = pd.DataFrame(data)
        self.keys = self.data.columns.tolist()

    def getData(self):
        """Devuelve los datos de telemetría como un numpy array.
        
        Los datos se retornan como un array de numpy, donde cada fila es una operación y cada columna es un sensor.
        Es decir, los datos son de la forma (n_operaciones, n_columnas).
        """
        return self.data.values

    def __getitem__(self, key):
        """
        Permite indexar el objeto como un array o DataFrame.

        Ejemplos:
            obj[["col1", "col2"], :]       -> columnas col1 y col2, todas las filas
            obj[:, :100]                   -> todas las columnas, primeras 100 filas
            obj[:]                         -> todo
            obj[["col1"], :50]             -> columna col1, primeras 50 filas
        """
        if isinstance(key, tuple): ##reviso si es una tupla
            ##se supone que key es una tupla de la forma (cols, rows)
            if len(key) != 2:
                raise ValueError("La clave debe ser una tupla de la forma (cols, rows)")
            cols, rows = key

            # Columnas
            if isinstance(cols, list) or isinstance(cols, str):
                selected_cols = cols
            elif cols == slice(None):  # equivalente a ":"
                selected_cols = self.data.columns
            else:
                raise TypeError(f"Tipo de indexado de columnas no soportado: {type(cols)}")

            # Filas
            if isinstance(rows, int) or isinstance(rows, slice):
                #retornamos de la forma (n_operaciones, n_columnas)
                return self.data.loc[rows, selected_cols].values
            else:
                raise TypeError(f"Tipo de indexado de filas no soportado: {type(rows)}")

        elif isinstance(key, slice):
            # Caso para todas las filas y columnas
            # Retornamos de la forma (n_operaciones, n_columnas)
            return self.data.iloc[key].values

        else:
            raise TypeError("La indexación debe ser una tupla (cols, rows) o un slice ':'")
    
if __name__ == "__main__":
    import pandas as pd
    import json
    from sarapy.preprocessing import TransformInputData

    historical_data_path = "examples/2025-06-21/UPM000N/historical-data.json"
    with open(historical_data_path, 'r') as file:
        historical_data = json.load(file)

    inputData_transformer = TransformInputData.TransformInputData()
    data = inputData_transformer.transform(historical_data)
    
    tlm_processor = TLMSensorDataProcessor(data=data)
    print(tlm_processor.data.head())
    tlm_processor[:, :10].shape

    tlm_processor[["id_db_dw", "id_db_h"], :5]#.shape
    tlm_processor.keys
    tlm_processor["longitud",:]
    