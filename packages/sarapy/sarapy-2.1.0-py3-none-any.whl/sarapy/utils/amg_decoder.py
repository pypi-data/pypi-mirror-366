from dateutil import parser


"""
En 'estructura_datos' se registra cuantos bits se ocupan para cada dato.
Por ejemplo, los primeros 6 bits para anio, los siguientes 4 para mes y asi.
"""

estructura_datos = {
    "anio": 6,
    "mes": 4,
    "dia": 5,
    "hora": 5,
    "minutos": 6,
    "segundos": 6,
    "operacion": 16,
    "PT": 2,
    "FR": 2,
    "OR": 2,
    "MO": 2,
    "TLM_NPDP": 64,
    "TLM_GPDP": 16,
    "ID_NPDP": -1,
    "ID_OPRR": -1,
    "ID_GPDP": -1,
    "ID_CDLL": -1,
    "size_GNSS": 16,
    "Latitud": 32,
    "Longitud": 32,
    "Precision": 32,  
}  # Agregar mas campos segun sea necesario


def extraer_bits(trama, inicio, n_bits):
    try:
        byte_index = inicio // 8
        bit_offset = inicio % 8

        valor = 0
        bits_procesados = 0
        while bits_procesados < n_bits:
            byte_actual = trama[byte_index]
            bits_restantes = n_bits - bits_procesados
            bits_a_extraer = min(bits_restantes, 8 - bit_offset)

            mascara = (1 << bits_a_extraer) - 1
            bits_extraidos = (byte_actual >> (8 - bit_offset - bits_a_extraer)) & mascara

            valor = (valor << bits_a_extraer) | bits_extraidos

            bits_procesados += bits_a_extraer
            byte_index += 1
            bit_offset = 0

        return valor
    except IndexError as ex:
        raise ex
    except Exception as ex:
        print(f"Error inesperado en extraer_bits: {ex}")
        raise ex


def process_dynamic_id(trama, inicio):
    # Lee el primer byte para determinar la longitud del ID
    longitud_id_bytes = extraer_bits(trama, inicio, 8)  # 8 bits = 1 byte
    inicio += 8  # Avanza el indice de inicio 8 bits para pasar al contenido del ID

    # Ahora, extrae el ID basandose en la longitud obtenida
    id_value = extraer_bits(trama, inicio, longitud_id_bytes * 8)  # Convierte la longitud a bits
    inicio += longitud_id_bytes * 8  # Avanza el indice de inicio para pasar al final del ID

    return id_value, inicio


def process_data(trama):
    
    if not isinstance(trama, bytes):
        raise ValueError("La trama debe ser un bytearray")
    
    inicio = 0
    resultado = {}
    for campo, n_bits in estructura_datos.items():
        try:
            if n_bits == -1:  # Verifica si el campo es dinamico
                resultado[campo], inicio = process_dynamic_id(trama, inicio)
            else:
                if campo == "TLM_NPDP" or campo == "TLM_GPDP":
                    resultado[campo] = trama[inicio // 8: (inicio + n_bits) // 8]
                else:
                    resultado[campo] = extraer_bits(trama, inicio, n_bits)  
                inicio += n_bits
            if campo == "Precision":
                # Suponiendo que size_GNSS sigue inmediatamente despues de Precision
                raw = trama[inicio // 8: (inicio // 8 ) + resultado["size_GNSS"] - 12]
                resultado["RAW"] = raw
        except IndexError as ex:
            print(f"Error al procesar campo {campo}: {ex}. Posiblemente la trama es mas corta de lo esperado.")
            break  # Salir del bucle en caso de un error de indice
        except Exception as ex:
            print(f"Error inesperado al procesar campo {campo}: {ex}")
            break  # Salir del bucle en caso de errores inesperados
    
    if len(set(estructura_datos.keys()) - set(resultado.keys())) == 0:
    
        anio = 2020 + resultado["anio"]
        mes = str(resultado["mes"]).zfill(2)
        dia = str(resultado["dia"]).zfill(2)
        hora = str(resultado["hora"]).zfill(2)
        minutos = str(resultado["minutos"]).zfill(2)
        segundos = str(resultado["segundos"]).zfill(2)
        resultado["date_oprc"] = parser.parse(f"{anio}-{mes}-{dia}T{hora}:{minutos}:{segundos}+00:00")
        
        resultado["Latitud"] = (resultado["Latitud"] - 2 ** 32) / 10 ** 7
        resultado["Longitud"] = (resultado["Longitud"] - 2 ** 32) / 10 ** 7
        
        del resultado["anio"]
        del resultado["mes"]
        del resultado["dia"]
        del resultado["hora"]
        del resultado["minutos"]
        del resultado["segundos"]
        del resultado["size_GNSS"]
        
        return resultado

