import pandas as pd
import matplotlib.pyplot as plt
import re
import pyreadstat
from matplotlib.cm import get_cmap

path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data'

# Load the chatbot interaction data
df = pd.read_csv(path + '/Inputs/Encuesta/Whatsapp/interacciones_chatbot_Encuesta_IcfesBot_2024-11-25_14-41-51.csv')
df = df.sort_values(by=['user', 'node_start'], ascending=[True, True])
df = df.fillna('')
df = df[~df['user'].isin(['whatsapp:+56975815720', 'whatsapp:+56985051369'])]

# Extract P13 responses
p13_responses = df[(df['node_start'] == 'P13') & (df['node_end'] != 'P13') & (df['button'] != '')]
p13_mapping = dict(zip(p13_responses['user'], p13_responses['button']))

# Map P13 responses to the main dataframe
df['P13_response'] = df['user'].map(p13_mapping)

# Group P13 responses into Hombre, Mujer, and Otros
def categorize_sex(response):
    if response in ['Masculino']:
        return 'Hombre'
    elif response in ['Femenino']:
        return 'Mujer'
    else:
        return 'Otros'

df['P13_group'] = df['P13_response'].apply(categorize_sex)

# Define a colormap for the three groups
color_mapping = {'Hombre': 'blue', 'Mujer': 'pink', 'Otros': 'green'}

# Adjust the bar width to make the bars thinner
bar_width = 0.2

# Iterate over nodes to generate graphs
for i in range(1, 15):
    node = f'P{i}'
    
    # Filter predefined responses for the current node
    filtered_data = df[(df['node_start'] == node) & (df['node_end'] != node) & (df['button'] != '')]

    # Group responses by `P13_group` and `button`
    grouped = filtered_data.groupby(['P13_group', 'button']).size().unstack(fill_value=0)
    grouped_percent = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Prepare horizontal bar positions for differentiation
    x = range(len(grouped_percent.columns))
    
    # Plot the superimposed bar chart
    plt.figure(figsize=(12, 8))
    for idx, (p13_group, row) in enumerate(grouped_percent.iterrows()):
        positions = [pos + (idx * bar_width) for pos in x]
        plt.bar(
            positions, row, width=bar_width, color=color_mapping.get(p13_group, "gray"),
            alpha=0.8, label=p13_group, edgecolor='black'
        )

    # Adjust x-axis positions for better spacing
    plt.xticks([pos + (bar_width * (len(grouped_percent.index) - 1) / 2) for pos in x], grouped_percent.columns, rotation=45, ha='right')

    # Add titles and labels
    plt.title(f'Respuestas para {node} según sexo (Hombre/Mujer/Otros)', fontsize=16)
    plt.xlabel('Respuestas', fontsize=14)
    plt.ylabel('Porcentaje', fontsize=14)
    plt.legend(title='Sexo', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Save the plot
    plt.tight_layout()
    plot_path = path + f'/Outputs/analisis_resultados_encuesta/Whatsapp/plots/frecuencia_{node}_por_grupo_p13.png'
    plt.savefig(plot_path, format="png", dpi=300)
    plt.close()

    print(f"Saved plot for {node} at {plot_path}")

    # Save unstructured text responses for the current node
    unstructured_responses = df[(df['node_start'] == node) & (df['node_end'] != node) & (df['description'] == '')]
    unstructured_responses = unstructured_responses[['message']]
    unstructured_responses = unstructured_responses[unstructured_responses['message'] != '']
    csv_path = path + f'/Outputs/analisis_resultados_encuesta/Whatsapp/text_answers/not_structured/{node}.csv'
    unstructured_responses.to_csv(csv_path, index=False)
    print(f"Saved unstructured responses for {node} at {csv_path}")