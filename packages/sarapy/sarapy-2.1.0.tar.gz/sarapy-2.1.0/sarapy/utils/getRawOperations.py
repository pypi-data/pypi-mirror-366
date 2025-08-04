import pandas as pd
from sarapy.utils import amg_ppk
import os
def getRawOperations(data, historical_data):
    """
    Args:
        data_file: Lista de diccionarios con la data
        historical_data_file: Lista de diccionarios con historical_data

    Returns the raw operations from the database.
    """
    hash_table = {}
    for datum in data:
        hash_table[datum["timestamp"]] = {"id_db_dw": datum["id"], "id_db_h": 0, "serialized_datum": ""}
    for historical_datum in historical_data:
        if historical_datum["timestamp"] in hash_table:
            hash_table[historical_datum["timestamp"]].update({"id_db_h": historical_datum["id"], "serialized_datum": historical_datum["datum"]})
    ppk_results = amg_ppk.main(hash_table, [])  # ToDo: PPK (Fernando)

    return ppk_results