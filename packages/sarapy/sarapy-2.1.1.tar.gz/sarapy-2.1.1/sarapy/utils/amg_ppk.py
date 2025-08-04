from base64 import b64decode

from sarapy.utils import amg_decoder


def main(hash_table, ppk_data):

    ppk_results = []

    for hash_table_entry_values in hash_table.values():

        try:

            serialized_datum = hash_table_entry_values["serialized_datum"]
            raw_datum = bytes(b64decode(serialized_datum.encode("utf-8")))  # 'trama'
            datum = amg_decoder.process_data(raw_datum)

            if datum:

                longitude, latitude, accuracy = "", "", 0  # ToDo: PPK (Fernando)

                if longitude:
                    datum["Longitud"] = longitude
                if latitude:
                    datum["Latitud"] = latitude
                if accuracy != 0:
                    datum["Precision"] = accuracy

                ppk_results.append({
                    "id_db_dw": hash_table_entry_values["id_db_dw"],
                    "id_db_h": hash_table_entry_values["id_db_h"],
                    **datum
                })

        except Exception as ex:
            print(ex)

    return ppk_results
