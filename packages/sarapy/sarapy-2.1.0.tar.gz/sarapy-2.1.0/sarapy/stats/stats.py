import numpy as np
from scipy.stats import skew, kurtosis, gaussian_kde
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)

def getMA(data, window_size=104, mode='same'):
    """
    Función para calcular la media móvil de una serie temporal.
    data: numpy array con los datos de la serie temporal
    window_size: tamaño de la ventana para calcular la media móvil
    """
    return np.convolve(data, np.ones(window_size)/window_size, mode=mode)

def probabilidadEmpirica(data:np.ndarray, umbral):
    """
    Función para calcular la probabilidad empírica de un valor en una serie temporal.
    data: numpy array con los datos de la serie temporal
    umbral: valor umbral para calcular la probabilidad empírica
    """
    return data[data>umbral]/data.shape[0]

def penalizacion(alpha, skewness, beta, kurtosis):
    """
    Función para calcular la penalización de una serie temporal.
    alpha: valor de penalización
    skewness: asimetría de la serie temporal
    kurtosis: curtosis de la serie temporal
    """
    return np.exp(-alpha * np.abs(skewness)) * np.exp(-beta * np.abs(kurtosis))

def probSaturacion(probEmpirica, penalizacion):
    """
    Función para calcular la probabilidad de saturación de una serie temporal.
    probEmpirica: probabilidad empírica de la serie temporal
    penalizacion: penalización de la serie temporal
    """
    return probEmpirica * penalizacion

def estimarKDE(distorsion_data, method="scott"):
    """
    Recibe una serie o array de valores dstpt de un nodo.
    Retorna una función de densidad KDE evaluable.
    """
    kde = gaussian_kde(distorsion_data, bw_method=method)
    return kde

def saturationProbability(distorsion_data, saturation_mode = "alto", umbrales = (1,14), alpha=0.5, beta=0.2):
    """
    Calcula la probabilidad de que una ventana esté saturada.
    - distorsion_data: array de valores dstpt.
    - saturation_mode: modo de saturación, puede ser "bajo", "alto" o "ambos".
    - umbrales: tupla con los valores de umbral bajo y alto.
    - kde: booleano, si se debe calcular la densidad de probabilidad.
    - alpha, beta: coeficientes de penalización para skewness y curtosis.

    Devuelve un diccionario con los componentes y la probabilidad final.
    """
    ##chequeo si saturation_mode es válido
    if saturation_mode not in ["bajo", "alto", "ambos"]:
        raise ValueError("saturation_mode debe ser 'bajo', 'alto' o 'ambos'.")
    if distorsion_data.shape[0] == 0:
        raise ValueError("La distorsion_data no puede estar vacía.")
    if distorsion_data.shape[0] < 50:
        logging.warning("La distorsion_data tiene menos de 50 elementos. Los resultados pueden no ser representativos.")
    
    ventana_filtered = distorsion_data.copy()
    if saturation_mode == "bajo":
        ventana_filtered = ventana_filtered[ventana_filtered < umbrales[0]]
    elif saturation_mode == "alto":
        ventana_filtered = ventana_filtered[ventana_filtered > umbrales[1]]
    elif saturation_mode == "ambos":
        ventana_filtered = ventana_filtered[(ventana_filtered < umbrales[0]) | (ventana_filtered > umbrales[1])]

    ##chequeo si la ventana filtrada está vacía
    if ventana_filtered.shape[0] == 0:
        logging.warning("Ventana filtrada vacía. Se retornará 0.0.")
        return 0.0

    skew_val = skew(ventana_filtered)
    kurt_val = kurtosis(ventana_filtered)

    pena = penalizacion(alpha, skew_val, beta, kurt_val)
    ##chequeo que pena no sea nan, sino reemplazo por 1
    if np.isnan(pena):
        logging.warning("La penalización es NaN. Se reemplazará por 1.")
        pena = 1.0
    # Probabilidad
    proba_empirica = ventana_filtered.shape[0]/distorsion_data.shape[0]
    prob_saturacion = proba_empirica * pena
  
    logging.debug(f"Ventana filtrada: {ventana_filtered.shape[0]}, {distorsion_data.shape[0]}, {proba_empirica}, {pena}")
    return prob_saturacion

def movingProbability(distorsion_data, window_size=104, **kwargs):
    """
    Calcula la probabilidad de saturación de una serie temporal de distorsión.
    La ventana se mueve sin solapamiento (stride = window_size) y sin padding, 
    pero incluye el remanente final si queda un bloque incompleto.
    
    Params:
    - distorsion_data: array de valores dstpt.
    - window_size: tamaño de la ventana.
    - kwargs: parámetros adicionales para saturationProbability.
    
    Devuelve:
    - probabilities: array de probabilidades por ventana (incluye parcial).
    - probas_array: array de salida mismo tamaño que distorsion_data.
    """
    
    total_length = len(distorsion_data)
    n_windows = total_length // window_size
    remainder = total_length % window_size
    
    total_blocks = n_windows + (1 if remainder > 0 else 0)
    
    probabilities = np.zeros(total_blocks)
    probas_array = np.zeros_like(distorsion_data)   
    
    for i in range(n_windows):
        start = i * window_size
        end = start + window_size
        ventana = distorsion_data[start:end]
        probabilities[i] = saturationProbability(ventana, **kwargs)
        probas_array[start:end] = probabilities[i]
    
    # Procesamos el bloque final (parcial) si existe
    if remainder > 0:
        start = n_windows * window_size
        end = total_length
        ventana = distorsion_data[start:end]
        probabilities[-1] = saturationProbability(ventana, **kwargs)
        probas_array[start:end] = probabilities[-1]
    
    return probabilities, probas_array

def resumen_sensor(df, values_col = "dstpt", pctbajo_value = 1, pctalto_value = 14):
    """
    Función para obtener un resumen estadístico de los valores de un sensor.
    valores: numpy array con los valores del sensor
    Retorna un diccionario con la media, desviación estándar, asimetría, curtosis y porcentajes de valores bajos y altos.
    """
    
    pctbajo = lambda x: np.mean(np.array(x) < pctbajo_value)
    pctbajo.__name__ = "pct_bajo"
    pctalto = lambda x: np.mean(np.array(x) > pctalto_value)
    pctalto.__name__ = "pct_alto"
    funciones = ["count","mean", "std", "min", "max", skew, kurtosis, pctbajo, pctalto]
    table = df[[values_col,"nodo"]].pivot_table(index="nodo", values=values_col, aggfunc=funciones, fill_value=0).reset_index()
    return table

def detectar_secuencia_saturada(valores, umbral_bajo=1, umbral_alto=14, longitud_min=10):
    """
    Función para detectar si hay una secuencia de valores por debajo o por encima de los umbrales.
    valores: numpy array con los valores del sensor
    umbral_bajo: valor por debajo del cual se considera que el sensor está saturado
    umbral_alto: valor por encima del cual se considera que el sensor está saturado
    longitud_min: longitud mínima de la secuencia para considerarla saturada

    Return
    -------
    bool: True si hay una secuencia de valores por debajo o por encima de los umbrales, False en caso contrario.
    Esta función busca secuencias de valores por debajo del umbral bajo o por encima del umbral alto.
    """
    estado = (np.array(valores) < umbral_bajo) | (np.array(valores) > umbral_alto)
    sec_actual = 0
    for val in estado:
        if val:
            sec_actual += 1
            if sec_actual >= longitud_min:
                return True
        else:
            sec_actual = 0
    return False

if __name__ == "__main__":
    #cargo archivo examples\volcado_17112023_NODE_processed.csv
    from sarapy.utils.plotting import plotTemporalData, heatmapAlphavsBeta
    import pandas as pd
    import numpy as np
    import os
    import sarapy.utils.getRawOperations as getRawOperations
    from sarapy.dataProcessing import OpsProcessor
    from sarapy.preprocessing import TransformInputData
    from sarapy.dataProcessing import TLMSensorDataProcessor

    tlmsde = TLMSensorDataProcessor.TLMSensorDataProcessor()

    nodo = "UPM025N"

    data_path = os.path.join(os.getcwd(), f"examples\\2025-04-10\\{nodo}\\data.json")
    historical_data_path = os.path.join(os.getcwd(), f"examples\\2025-04-10\\{nodo}\\historical-data.json")

    raw_data = pd.read_json(data_path, orient="records").to_dict(orient="records")
    raw_data2 = pd.read_json(historical_data_path, orient="records").to_dict(orient="records")

    transform_input_data = TransformInputData.TransformInputData()

    raw_ops = getRawOperations.getRawOperations(raw_data, raw_data2)
    datum = transform_input_data.fit_transform(raw_ops)[:,2]
    telemetria = tlmsde.fit_transform(datum)
    mode = telemetria[:,tlmsde.dataPositions["MODEFlag"]]
    dstpt = telemetria[:,tlmsde.dataPositions["DSTRPT"]]

    op = OpsProcessor.OpsProcessor(classifier_file='modelos\\pipeline_rf.pkl', imputeDistances = False,
                                   regresor_file='modelos\\regresor.pkl', poly_features_file='modelos\\poly_features.pkl')
    op.operationsDict
    data_processed = op.processOperations(raw_ops)

    #paso la lista de operaciones a un dataframe
    df = pd.DataFrame(data_processed)
    df["mode"] = mode
    df["dstpt"] = dstpt
    df["nodo"] = nodo
    df["dstpt_ma"] = getMA(df["dstpt"].values, window_size=104, mode='same')
    ##me quedo con los datos donde mode==0
    df = df[df["mode"] == 0]
    
    #calculo el resumen del sensor
    resumen = resumen_sensor(df, values_col="dstpt_ma", pctbajo_value=1, pctalto_value=14.6)
    print(resumen)
    #calculo la probabilidad de saturación
    ma = df["dstpt_ma"].values
    prob_saturacion = saturationProbability(ma, saturation_mode="alto", umbrales=(1, 14),
                                               alpha=0.2, beta=0.2)
    
    print(f"Probabilidad de saturación: {prob_saturacion}")

    ventana = 104
    probs, array_probs = movingProbability(ma[100:2500], window_size=ventana, saturation_mode="alto", alpha=0.05, beta=0.05, umbrales=(1, 14.9))

    # heatmapAlphavsBeta(ma, saturationProbability)

    import matplotlib.pyplot as plt
    ##grafico ma[100:2500] y array_probs en una misma figura pero array_probs en el eje y derecho
    fig, ax1 = plt.subplots(figsize=(15, 10))
    ax1.plot(ma[100:2500], label='MA', color='blue')
    ax1.set_xlabel("Operación")
    ax1.set_ylabel("MA", color='blue')
    # ax1.set_ylim(12, 15)
    ax1.tick_params(axis='y', labelcolor='blue')
    ax2 = ax1.twinx()
    ax2.plot(array_probs, label='Probabilidad de saturación', color='grey')
    3#agrego ahline con array_probs.mean()
    ax2.axhline(y=array_probs.mean(), color='black', linestyle=':', label='Media de probabilidad',linewidth=3)
    ax2.set_ylabel("Probabilidad de saturación", color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    ax1.axhline(y=1, color='green', linestyle='--', label='Umbral bajo')
    ax1.axhline(y=14, color='red', linestyle='--', label='Umbral alto')
    ax1.set_title(f"Análisis de {nodo} - DSTPT")
    ax1.legend(loc='lower left')
    ax2.legend(loc='lower right')
    plt.show()

    colors = ["#e71616","#63d536"]
    plotTemporalData(df, nodos = [nodo], columnas = ["dstpt_ma"], title = "DSTPT",sameFig = False, show = True,
                    save = False, filename = "dstpt_plot.png", figsize=(15, 10), colors=colors)
