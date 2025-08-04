###Documentación en https://github.com/lucasbaldezzari/sarapy/blob/main/docs/Docs.md

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class TransformInputData(BaseEstimator, TransformerMixin):
    """
    Clase para transformar los datos de entrada a un formato utilizable para procesar las operaciones.
    """

    def __init__(self):
        """
        Inicializa la clase TransformToJson.

        Args:
            data_positions (dict): Diccionario con las posiciones de los datos en el formato JSON. Se utiliza para identificar
            la posición de cada dato en el JSON transformado. Diferentes transformadores pueden tener diferentes posiciones de datos.
        """
        # self.dataPositions = TransformInputData.data_positions  # Diccionario para almacenar las posiciones de los datos
        self.data_positions = { "Date_oprc": 0, "Operacion": 1, "SC_PT": 2, "DATA_PT": 3, "INST_PT": 4, "RES_PT": 5,
                               "CLMP_PT": 6, "SC_FT": 7, "DATA_FT": 8, "INST_FT": 9, "RES_FT": 10, "CLMP_FT": 11, "SC_GYRO_Z": 12,
                               "SC_GYRO_Y": 13, "SC_GYRO_X": 14, "DATA_GYRO": 15, "INST_GYRO": 16, "CLMP_GYRO": 17, "SC_ACCEL_Z": 18,
                               "SC_ACCEL_Y": 19, "SC_ACCEL_X": 20, "DATA_ACCEL": 21, "INST_ACCEL": 22, "CLMP_ACCEL": 23, "TIME_AC": 24,
                               "OPEN_AC": 25, "Longitud_N": 26, "Latitud_N": 27, "Precision_N": 28, "N_FIX": 29, "N_SIV": 30, "N_PDOP": 31,
                               "N_NBAT": 32, "N_SBAT": 33, "N_VBAT": 34, "N_CBAT": 35, "N_CHRG": 36, "ID_NPDP": 37, "N_MODE": 38, "N_RST": 39,
                               "N_FLASH": 40, "N_CLK": 41, "N_EST_GNSS": 42, "N_EST_NFC": 43, "N_EST_RF": 44, "N_EST_IMU": 45, "N_EST_BMS": 46,
                               "EST_CDC": 47, "N_ONLINE": 48, "N_RSSI": 49, "SEND_TRY": 50, "PMST": 51, "ID_OPRR": 52, "N_DATA_ID": 53,
                               "ID_GPDP": 54, "G_MODE": 55, "G_RST": 56, "G_FLASH": 57, "G_CLK": 58, "G_EST_4G": 59, "G_EST_NFC": 60,
                               "G_EST_IMU": 61,"G_EST_BMS": 62, "G_RSSI": 63, "G_NETWORK": 64, "G_ONLINE": 65, "G_SIGNAL": 66,
                               "G_MONEY": 67, "ID_CDLL": 68,"G_DATA_ID": 69, "Longitud_G": 70, "Latitud_G": 71, "Precision_G": 72,
                               "G_FIX": 73, "G_SIV": 74, "G_PDOP": 75, "G_NBAT": 76, "G_SBAT": 77, "G_VBAT": 78, "G_CBAT": 79, "G_CHRG": 80,
                               "VUX1": 81, "VUX2": 82, "VUX3": 83, "VUX4": 84, "VUX5": 85, "VUX6": 86, "VUX7": 87, "VUX8": 88,
                               "VUX9": 89, "VUX10": 90}
        self.dataFloat = ["latitud","longitud","Longitud_N","Latitud_N","Longitud_G","Latitud_G","date_oprc","Date_oprc"]
        self.dataString = ["timestamp"]

    def transform(self, X):
        """
        Método para transformar los datos en formato JSON.
        
        Args:
            X: Lista de diccionario. Cada diccionario tiene la forma.
            Ejemplo (NOTA: El salto de línea es agregado para mejorar la legibilidad):
            [
            {"id": 6, "receiver_timestamp": "2025-06-21T15:51:36.527825+00:00", "timestamp": "2025-06-21T15:51:01.000002+00:00", "datum": null,
            "csv_datum": "2025-06-21T15:51:01.000002+00:00,2,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,-58.0321,-33.2471,
            1,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,0,0,0,0,1,0,0,1,1,0,3,0,0,0,0,3,0,0,0,0,0,1,0,0,0,0,0.0000,0.0000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0", 
            "longitude": null, "latitude": null, "accuracy": null, "tag_seedling": null, "tag_fertilizer": null}
            ]

        NOTA: Cada diccionario debe tener, sí o sí, los siguientes keys (además de los que ya tiene csv_datum)
            - 0: id_db_h (sale de "id" dentro de los datos de entrada X)
            - 1: ID_NPDP  (sale de csv_datum)
            - 3: date_oprc (sale de csv_datum)
            - 4: latitud (sale de csv_datum)
            - 5: longitud (sale de csv_datum)
            - 6: precision (sale de csv_datum)
            - 7: FR
            - 8: id_db_dw (sale de "Operacion" dentro de csv_datum)
        
        Returns:
            Lista de diccionarios con los datos transformados. Básciamente se toma csv_datum y se agrega a cada uno de los diccionarios de la lista.
            Para esto, se usa el diccionario `dataPositions` para identificar las posiciones y qué son cada uno de los valores dentro de `csv_datum`.
            Los diccionarios dentro de la lista no tendrán csv_datum.
        """
        self.data_transformed = []
        dict_structre = {"id_db_h":None, "id_db_dw":None, "ID_NPDP":None,
                         "date_oprc":None, "latitud":None, "longitud":None,
                         "precision":None, "FR":None, "timestamp": None}
        
        ##agrego los keys que están en dataPositions con valores None
        for key in self.data_positions.keys():
            dict_structre[key] = None

        
        for row in X:
            # Crear un diccionario para almacenar los datos transformados
            data_dict = dict_structre.copy()
            # Asignar los valores de csv_datum a las posiciones correspondientes
            csv_datum = row.get("csv_datum", "")
            if csv_datum:
                values = csv_datum.split(',')
                for key, pos in self.data_positions.items():
                    if pos < len(values):
                        data_dict[key] = values[pos]
                    else:
                        data_dict[key] = None
            
            data_dict["id_db_h"] = row.get("id", None)
            data_dict["id_db_dw"] = data_dict.get("Operacion", None)
            data_dict["ID_NPDP"] = data_dict.get("ID_NPDP", None)
            ##convierto Date_oprc a un objeto datetime y paso a timestamp
            date_oprc = data_dict.get("Date_oprc", None)
            if date_oprc:
                try:
                    from dateutil import parser
                    data_dict["date_oprc"] = parser.isoparse(date_oprc).timestamp()
                except Exception as e:
                    print(f"Error parsing date_oprc: {e}")
                    data_dict["date_oprc"] = None
            else:
                data_dict["date_oprc"] = None
            data_dict["latitud"] = data_dict.get("Latitud_N", None)
            data_dict["longitud"] = data_dict.get("Longitud_N", None)
            data_dict["precision"] = data_dict.get("Precision_N", None)
            data_dict["Date_oprc"] = data_dict.get("date_oprc", None)
            data_dict["latitud"] = data_dict.get("Latitud_N", None)
            data_dict["longitud"] = data_dict.get("Longitud_N", None)
            data_dict["timestamp"] = row.get("timestamp", None)
            # data_dict["FR"] = row.get("tag_fertilizer", None)
            
            # Agregar el diccionario transformado a la lista
            self.data_transformed.append(data_dict)

        ##convierto los datos de self.dataFloat a float y el resto a int
        for data in self.data_transformed:
            for key, value in data.items():
                if key in self.dataFloat:
                    try:
                        data[key] = float(value) if value else None
                    except ValueError:
                        data[key] = None
                elif key in self.dataString:
                    try:
                        data[key] = str(value) if value else None
                    except ValueError:
                        data[key] = None
                else:
                    try:
                        data[key] = int(value) if value else None
                    except ValueError:
                        data[key] = None

        return self.data_transformed
    
if __name__ == "__main__":
    import pandas as pd
    import json

    historical_data_path = "examples/2025-06-21/UPM000N/historical-data.json"
    with open(historical_data_path, 'r') as file:
        historical_data = json.load(file)
    df = pd.DataFrame(historical_data)

    ##cargo en un diccionario sarapy\preprocessing\telemetriaDataPosition.json
    data_positions = json.load(open("sarapy/preprocessing/telemetriaDataPosition.json", 'r'))
    transform_input_data = TransformInputData()
    transformed_data = transform_input_data.transform(historical_data)
    print(transformed_data[-1])