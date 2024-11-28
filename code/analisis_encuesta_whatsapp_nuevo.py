import pandas as pd
import matplotlib.pyplot as plt
import re
import pyreadstat

path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data'


df = pd.read_csv(path +'/Inputs/Encuesta/Whatsapp/interacciones_chatbot_Encuesta_IcfesBot_2024-11-25_14-41-51.csv')
df = df.sort_values(by=['user', 'node_start'], ascending=[True, True])
df = df.fillna('')

df = df[~df['user'].isin(['whatsapp:+56975815720', 'whatsapp:+56985051369'])]

log_file = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Whatsapp/logs_icfes_filtered.sav'

# Load the file
data, meta = pyreadstat.read_sav(log_file)

# Find common unique users
common_users = set(df['user']).intersection(set(data['To']))
common_user_count = len(common_users)

# Output the result
print(f"Number of common unique users: {common_user_count}")

for i in range(1, 15):
    node = f'P{i}'

    #Para ver las respuestas que estaban predefinidas (son las que tienen el description con texto)
    print(df[((df['node_start'] == node) & (df['node_end'] != node)) & (df['button']!='')]['button'].value_counts())
    conteo_respuestas = df[((df['node_start'] == node) & (df['node_end'] != node)) & (df['button']!='')]['button'].value_counts()
    porcentajes_respuestas = (conteo_respuestas / conteo_respuestas.sum()) * 100
    
    # Crear el gráfico de barras
    plt.figure(figsize=(10, 6))
    porcentajes_respuestas.plot(kind='bar', color='skyblue')
    
    # Agregar títulos y etiquetas
    plt.title(f'Frecuencia de Respuestas {node}', fontsize=16)
    plt.xlabel('Respuestas', fontsize=14)
    plt.ylabel('Porcentaje', fontsize=14)
    
    # Agregar etiquetas de porcentaje sobre las barras
    for i, value in enumerate(porcentajes_respuestas):
        plt.text(i, value + 1, f'{value:.1f}%', ha='center', fontsize=10)
    
    # Mostrar el gráfico
    plt.xticks(rotation=45, ha='right')  # Rotar las etiquetas si son largas
    plt.tight_layout()
    plt.savefig(path + f'/Outputs/analisis_resultados_encuesta/Whatsapp/plots/frecuencia_{node}.png', format="png", dpi=300)
    
    respuestas_otras = df[((df['node_start'] == node) & (df['node_end'] != node)) & (df['description']=='')]
    respuestas_otras = respuestas_otras[['message']]
    respuestas_otras = respuestas_otras[respuestas_otras['message']!='']
    respuestas_otras.to_csv(path + f'/Outputs/analisis_resultados_encuesta/Whatsapp/text_answers/not_structured/{node}.csv')

#Caracteristicas
df3 = pd.read_csv(path + '/Outputs/students/base_envio_caracteristicas.csv')
df['phone'] = df['user'].apply(lambda x: int(''.join(re.findall(r'\d+', x))))
df = pd.merge(df, df3, on='phone', how='left', indicator=True)
