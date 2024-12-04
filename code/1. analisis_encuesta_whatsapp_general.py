#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 16:40:32 2024

@author: leidygomez
"""

import pandas as pd
import matplotlib.pyplot as plt
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from gensim import matutils, models
import numpy as np
import openai
import os

path = '/Users/leidygomez/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data'


#funcion para openai
gpt_model = "gpt-4o-mini"
openai.api_key = os.getenv("openai_key")

def aplicar_prompt(texto, prompt):
    """
    Utilizes the OpenAI API to process text with a given prompt.
    """
    try:
        # Formatear la solicitud para la API de OpenAI
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": texto}
        ]
        response = openai.chat.completions.create(
            model=gpt_model,
            messages=messages,
            temperature=0.3
        )
        # Obtener la respuesta del modelo
        resum = response.choices[0].message.content
        return resum
    except Exception as e:
        print(f"Error al procesar el texto: {e}")
        return texto  # Devuelve el texto original en caso de error









df = pd.read_csv(path +'/Inputs/Encuesta/Whatsapp/interacciones_chatbot_Encuesta_IcfesBot_2024-11-25_14-41-51.csv')

df = df.sort_values(by=['user', 'node_start'], ascending=[True, True])
df = df.fillna('')

df = df[~df['user'].isin(['whatsapp:+56975815720', 'whatsapp:+56985051369'])]



#total personas intervenidas
print(df['user'].nunique()) ##197874




print(df[(df['node_start'] == 'Inicio_Consent') & (df['node_end'] == 'Inicio_Consent')]['user'].nunique())
print(df[(df['node_start'] == 'Inicio_Consent') & (df['node_end'] != 'Inicio_Consent')]['user'].nunique())
print(df[(df['node_start'] == 'Inicio_Consent') & (df['node_end'] == 'Consentimiento')]['user'].nunique())
print(df[(df['node_start'] == 'Inicio_Consent') & (df['node_end'] == 'No_Acepta')]['user'].nunique())

# Iterar desde P1 hasta P14
for i in range(1, 15):
    node = f'P{i}'
    
    # Cuántos llegaron al nodo
    unique_same = df[(df['node_start'] == node) & (df['node_end'] == node)]['user'].nunique()
    
    # Cuántos contestaron el nodo
    unique_different = df[(df['node_start'] == node) & (df['node_end'] != node)]['user'].nunique()
    
    # Imprimir resultados
    print(f"Para {node}:")
    print(f"  Llegaron a {node}: {unique_same}")
    print(f"  Respondieron a {node}: {unique_different}")



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






###Analizando las respuestas abiertas


#P4_1
P4_1 = df[(df['node_start'] == 'P4_1') & (df['node_end'] != 'P4_1') & (df['message']!='')]
P4_1 = P4_1[['message']]


#Nube de palabras
# Define stop words
stop_words = set(stopwords.words('spanish'))

# Define preprocess of text without stemming
def preprocess_text1(text):
    tokens = word_tokenize(text.lower())  # Tokenization and lowercase conversion
    tokens = [token for token in tokens if token.isalnum() and token not in stop_words]  # Dropping stopwords 
    return tokens

P4_1['tokens1'] = P4_1['message'].apply(preprocess_text1)

# Join all tokens into a space-separated text string
tokens_concatenados_corregidos = [' '.join(tokens) for tokens in P4_1['tokens1']]

# Create a word cloud with the most frequently used words
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(tokens_concatenados_corregidos))

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()


P4_1['unos'] = 1
P4_1 = P4_1.groupby('unos')['message'].apply(' , '.join).reset_index()

for index, row in P4_1.iterrows():
    text = row['message']

promt = """
Eres un experto en resumir respuestas de encuesta de estudiantes que van a salir a educación superior. La pregunta que se les hizo fue ¿Cuándo prefieres recibir información sobre las opciones para ingresar a la educación superior?. El siguiente texto contiene todas las respuestas que dieron los estudiantes a esta pregunta, me puedes resumir qué es lo que piensan los estudiantes sobre esto, cuáles fueron las respuestas más comunes.
"""
summaries1 = aplicar_prompt(text, promt)

promt = """
Eres un experto en resumir respuestas de encuesta de estudiantes que van a salir a educación superior. La pregunta que se les hizo fue ¿Cuándo prefieres recibir información sobre las opciones para ingresar a la educación superior?. El siguiente texto contiene todas las respuestas que dieron los estudiantes a esta pregunta, me podrías decir cuál fue la respuesta más común.
"""
summaries2 = aplicar_prompt(text, promt)





#P5_1
P5_1 = df[(df['node_start'] == 'P5_1') & (df['node_end'] != 'P5_1') & (df['message']!='')]
P5_1 = P5_1[['message']]


#Nube de palabras
P5_1['tokens1'] = P5_1['message'].apply(preprocess_text1)



# Join all tokens into a space-separated text string
tokens_concatenados_corregidos = [' '.join(tokens) for tokens in P5_1['tokens1']]

# Create a word cloud with the most frequently used words
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(tokens_concatenados_corregidos))

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig(path + '/Outputs/analisis_resultados_encuesta/Whatsapp/plots/wordcloud_P5_1.png', format="png", dpi=300)
plt.show()


#Generando resumen con openai
P5_1['unos'] = 1
P5_1 = P5_1.groupby('unos')['message'].apply(' , '.join).reset_index()

for index, row in P5_1.iterrows():
    text = row['message']

promt = """
Eres un experto en resumir respuestas de encuesta de estudiantes que van a salir a educación superior. La pregunta que se les hizo fue ¿Qué tipo de información te resultó más difícil de encontrar en tu proceso de investigación para acceder a la Educación Superior?. El siguiente texto contiene todas las respuestas que dieron los estudiantes a esta pregunta, me puedes resumir qué es lo que piensan los estudiantes sobre esto, cuáles fueron las respuestas más comunes.
"""
summaries1 = aplicar_prompt(text, promt)

promt = """
Eres un experto en resumir respuestas de encuesta de estudiantes que van a salir a educación superior. La pregunta que se les hizo fue ¿Qué tipo de información te resultó más difícil de encontrar en tu proceso de investigación para acceder a la Educación Superior?. El siguiente texto contiene todas las respuestas que dieron los estudiantes a esta pregunta, me podrías decir cuál fue la respuesta más común.
"""
summaries2 = aplicar_prompt(text, promt)



from wordcloud import STOPWORDS

# Define a list of words to exclude
excluded_words = {"universidad", "carrera", "estudiar", "universidades"}  # Añade las palabras que quieras excluir

# Add these words to the default stopwords
stopwords = STOPWORDS.union(excluded_words)

# Create a word cloud with the stopwords
wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords).generate(' '.join(tokens_concatenados_corregidos))

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig(path + '/Outputs/analisis_resultados_encuesta/Whatsapp/plots/wordcloud_P5_1.png', format="png", dpi=300)
plt.show()




#P7_1
P7_1 = df[(df['node_start'] == 'P7_1') & (df['node_end'] != 'P7_1') & (df['message']!='')]
P7_1 = P7_1[['message']]


#Nube de palabras
P7_1['tokens1'] = P7_1['message'].apply(preprocess_text1)

# Join all tokens into a space-separated text string
tokens_concatenados_corregidos = [' '.join(tokens) for tokens in P7_1['tokens1']]

# Create a word cloud with the most frequently used words
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(tokens_concatenados_corregidos))

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig(path + '/Outputs/analisis_resultados_encuesta/Whatsapp/plots/wordcloud_P7_1.png', format="png", dpi=300)
plt.show()


#Generando resumen con openai
P7_1['unos'] = 1
P7_1 = P7_1.groupby('unos')['message'].apply(' , '.join).reset_index()

for index, row in P7_1.iterrows():
    text = row['message']

promt = """
Eres un experto en resumir respuestas de encuesta de estudiantes que van a salir a educación superior. La pregunta que se les hizo fue ¿Cuál es la razón principal por la que no puedes mudarte para ingresar a la Educación Superior?. El siguiente texto contiene todas las respuestas que dieron los estudiantes a esta pregunta, me puedes resumir qué es lo que piensan los estudiantes sobre esto, cuáles fueron las respuestas más comunes.
"""
summaries1 = aplicar_prompt(text, promt)

promt = """
Eres un experto en resumir respuestas de encuesta de estudiantes que van a salir a educación superior. La pregunta que se les hizo fue ¿Cuál es la razón principal por la que no puedes mudarte para ingresar a la Educación Superior?. El siguiente texto contiene todas las respuestas que dieron los estudiantes a esta pregunta, me podrías decir cuál fue la respuesta más común.
"""
summaries2 = aplicar_prompt(text, promt)






#P8_1
P8_1 = df[(df['node_start'] == 'P8_1') & (df['node_end'] != 'P8_1') & (df['message']!='')]
P8_1 = P8_1[['message']]


#Nube de palabras
P8_1['tokens1'] = P8_1['message'].apply(preprocess_text1)

# Join all tokens into a space-separated text string
tokens_concatenados_corregidos = [' '.join(tokens) for tokens in P8_1['tokens1']]

# Create a word cloud with the most frequently used words
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(tokens_concatenados_corregidos))

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig(path + '/Outputs/analisis_resultados_encuesta/Whatsapp/plots/wordcloud_P8_1.png', format="png", dpi=300)
plt.show()


#Generando resumen con openai
P8_1['unos'] = 1
P8_1 = P8_1.groupby('unos')['message'].apply(' , '.join).reset_index()

for index, row in P8_1.iterrows():
    text = row['message']

promt = """
Eres un experto en resumir respuestas de encuesta de estudiantes que van a salir a educación superior. La pregunta que se les hizo fue ¿Por qué no estás postulando a la educación superior?. El siguiente texto contiene todas las respuestas que dieron los estudiantes a esta pregunta, me puedes resumir qué es lo que piensan los estudiantes sobre esto, cuáles fueron las respuestas más comunes.
"""
summaries1 = aplicar_prompt(text, promt)

promt = """
Eres un experto en resumir respuestas de encuesta de estudiantes que van a salir a educación superior. La pregunta que se les hizo fue ¿Por qué no estás postulando a la educación superior?. El siguiente texto contiene todas las respuestas que dieron los estudiantes a esta pregunta, me podrías decir cuál fue la respuesta más común.
"""
summaries2 = aplicar_prompt(text, promt)











#Caracteristicas
df3 = pd.read_csv(path + '/Outputs/students/base_envio_caracteristicas.csv')
df['phone'] = df['user'].apply(lambda x: int(''.join(re.findall(r'\d+', x))))
df = pd.merge(df, df3, on='phone', how='left', indicator=True)



