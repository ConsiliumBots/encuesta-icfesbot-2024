import pandas as pd
import matplotlib.pyplot as plt
import re
import pyreadstat
from matplotlib.cm import get_cmap

# Ruta base
ruta = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data'

# Cargar los datos de interacciones del chatbot
df = pd.read_csv(ruta + '/Inputs/Encuesta/Whatsapp/interacciones_chatbot_Encuesta_IcfesBot_2024-11-25_14-41-51.csv')
df = df.sort_values(by=['user', 'node_start'], ascending=[True, True])
df = df.fillna('')
df = df[~df['user'].isin(['whatsapp:+56975815720', 'whatsapp:+56985051369'])]

# Extraer las respuestas de P14
respuestas_p14 = df[(df['node_start'] == 'P14') & (df['node_end'] != 'P14') & (df['button'] != '')]
mapa_p14 = dict(zip(respuestas_p14['user'], respuestas_p14['button']))

# Mapear las respuestas de P14 al dataframe principal
df['respuesta_P14'] = df['user'].map(mapa_p14)

# Agrupar respuestas en Heterosexual y No-Heterosexual
df['grupo_P14'] = df['respuesta_P14'].apply(
    lambda x: 'Heterosexual' if x == 'Heterosexual' else 'No-Heterosexual'
)

# Definir colores para los dos grupos
mapa_colores = {'Heterosexual': 'blue', 'No-Heterosexual': 'red'}

# Ajustar el ancho de las barras para hacerlas más delgadas
ancho_barras = 0.2

# Iterar sobre los nodos para generar gráficos
for i in range(1, 15):
    nodo = f'P{i}'
    
    # Filtrar respuestas predefinidas para el nodo actual
    datos_filtrados = df[(df['node_start'] == nodo) & (df['node_end'] != nodo) & (df['button'] != '')]

    # Agrupar respuestas por `grupo_P14` y `button`
    agrupado = datos_filtrados.groupby(['grupo_P14', 'button']).size().unstack(fill_value=0)
    porcentaje_agrupado = agrupado.div(agrupado.sum(axis=1), axis=0) * 100

    # Preparar posiciones horizontales de las barras para diferenciarlas
    x = range(len(porcentaje_agrupado.columns))
    
    # Graficar las barras superpuestas
    plt.figure(figsize=(12, 8))
    for idx, (grupo_p14, fila) in enumerate(porcentaje_agrupado.iterrows()):
        posiciones = [pos + (idx * ancho_barras) for pos in x]
        plt.bar(
            posiciones, fila, width=ancho_barras, color=mapa_colores.get(grupo_p14, "gray"),
            alpha=0.8, label=f'{grupo_p14}', edgecolor='black'
        )

    # Ajustar las posiciones del eje x para mejor espaciado
    plt.xticks([pos + (ancho_barras * (len(porcentaje_agrupado.index) - 1) / 2) for pos in x], porcentaje_agrupado.columns, rotation=45, ha='right')

    # Agregar títulos y etiquetas
    plt.title(f'Respuestas para {nodo} según grupo P14 (Heterosexual/No-Heterosexual)', fontsize=16)
    plt.xlabel('Respuestas', fontsize=14)
    plt.ylabel('Porcentaje', fontsize=14)
    plt.legend(title='Grupo P14', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Guardar el gráfico
    plt.tight_layout()
    ruta_grafico = ruta + f'/Outputs/analisis_resultados_encuesta/Whatsapp/plots/frecuencia_{nodo}_por_grupo_p14.png'
    plt.savefig(ruta_grafico, format="png", dpi=300)
    plt.close()

    print(f"Gráfico guardado para {nodo} en {ruta_grafico}")

    # Guardar respuestas de texto no estructurado para el nodo actual
    respuestas_no_estructuradas = df[(df['node_start'] == nodo) & (df['node_end'] != nodo) & (df['description'] == '')]
    respuestas_no_estructuradas = respuestas_no_estructuradas[['message']]
    respuestas_no_estructuradas = respuestas_no_estructuradas[respuestas_no_estructuradas['message'] != '']
    ruta_csv = ruta + f'/Outputs/analisis_resultados_encuesta/Whatsapp/text_answers/not_structured/{nodo}.csv'
    respuestas_no_estructuradas.to_csv(ruta_csv, index=False)
    print(f"Respuestas no estructuradas guardadas para {nodo} en {ruta_csv}")