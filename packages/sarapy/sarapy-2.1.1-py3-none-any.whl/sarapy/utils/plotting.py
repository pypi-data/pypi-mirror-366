
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
def plotTemporalData(df, columnas, nodos = None, title = "DSTPT", xlabel = "Operación", ylabel = "DSTPT",limit_lines=(1,14),
                     sameFig = False, show = True, save = False, filename = "dstpt_plot.png", figsize=(15, 10), colors="blue"):
    """
    Grafica los datos de dstpt de los nodos temporalmente.
    
    Parámetros:
    ---------
    df : DataFrame
        DataFrame con los datos a graficar. Los nodos deben estar en una columna llamada "nodo".
    nodos : list, opcional
        Lista de nodos a graficar. Si es None, se grafican todos los nodos.
    columnas : list
        Lista de columnas a graficar. Por defecto es ["dstpt"].
    title : str, opcional
        Título de la gráfica. Por defecto es "DSTPT".
    xlabel : str, opcional
        Etiqueta del eje x. Por defecto es "X-axis".
    ylabel : str, opcional
        Etiqueta del eje y. Por defecto es "Y-axis".
    sameFig : bool, opcional
        Si es True, se grafican todos los nodos en la misma figura. Por defecto es False.
    """
    if nodos is None:
        nodos = df["nodo"].unique()

    if len(nodos) == 1:
        sameFig = True

    if sameFig:
        fig, ax = plt.subplots(figsize=figsize)
        ##grafico todos los nodos en la misma figura
        ##Grafico cada columna en la misma figura
        for nodo in nodos:
            for j, columna in enumerate(columnas):
                data_nodo = df[df["nodo"]==nodo][columnas].values
                ax.plot(data_nodo, label=nodo, color=colors[j])
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        #agrego lineas horizontales en los limites
        ax.axhline(y=limit_lines[0], color='b', linestyle='--')
        ax.axhline(y=limit_lines[1], color='b', linestyle='--')
        ax.legend()
        if save:
            plt.savefig(filename)
        if show:
            plt.show()
    else:
        ##grafico cada nodo en un axis diferente
        fig, axs = plt.subplots(len(nodos), 1, figsize=figsize)
        ##grafico cada nodo en un mismo axis y cada columna con un color diferente
        for i, nodo in enumerate(nodos):
            for j, columna in enumerate(columnas):
                data_nodo = df[df["nodo"]==nodo][columna].values
                axs[i].plot(data_nodo, label=columna, color=colors[j])
            axs[i].axhline(y=limit_lines[0], color='b', linestyle='--')
            axs[i].axhline(y=limit_lines[1], color='b', linestyle='--')
            axs[i].set_ylabel(ylabel)
            axs[i].set_xticks([])
            axs[i].text(len(data_nodo)*1.1, 0.9, f"{nodo}", ha='right', va='top', fontsize=10,
                        bbox=dict(facecolor='#c1ddf7', alpha=1, edgecolor='black', boxstyle='round,pad=0.3'))
            # axs[i].legend()
        ##activo xticks en el último eje
        axs[i].set_xlabel(xlabel)
        if save:
            plt.savefig(filename)
        if show:
            plt.show()

def heatmapAlphavsBeta(data, saturationProbability):
# Definimos grilla de alpha y beta
    alpha_vals = np.linspace(0, 1, 20)
    beta_vals = np.linspace(0, 1, 20)

    # Creamos matriz de resultados
    Psat_matrix = np.zeros((len(alpha_vals), len(beta_vals)))

    for i, alpha in enumerate(alpha_vals):
        for j, beta in enumerate(beta_vals):
            Psat_matrix[i, j] = saturationProbability(data, saturation_mode="alto", umbrales=(1, 14),
                                               alpha=alpha, beta=beta)

    # Graficamos el heatmap
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(figsize=(10, 8))
    sns.heatmap(Psat_matrix, xticklabels=np.round(beta_vals, 2), yticklabels=np.round(alpha_vals, 2), cmap="YlOrRd")
    plt.title("Evolución de Psat en función de α (vertical) y β (horizontal)")
    plt.xlabel(r"$\beta$ (peso de kurtosis)")
    plt.ylabel(r"$\alpha$ (peso de skewness)")
    plt.show()