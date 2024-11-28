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

# Load student characteristics data
df3 = pd.read_csv(path + '/Outputs/students/base_envio_caracteristicas.csv')

# Extract phone numbers from `user` in the chatbot data
df['phone'] = df['user'].apply(lambda x: int(''.join(re.findall(r'\d+', x))))

# Merge chatbot data with student characteristics on `phone`
df = pd.merge(df, df3, on='phone', how='left', indicator=True)

# Group by `estu_cod_reside_mcpio`
mcpio_groups = df['estu_cod_reside_mcpio'].dropna().unique()
colors = get_cmap("tab10")(range(len(mcpio_groups)))
color_mapping = dict(zip(mcpio_groups, colors))

# Adjust the bar width to make the bars thinner
bar_width = 0.2

# Iterate over nodes to generate graphs
for i in range(1, 15):
    node = f'P{i}'
    
    # Filter predefined responses for the current node
    filtered_data = df[(df['node_start'] == node) & (df['node_end'] != node) & (df['button'] != '')]

    # Group responses by `estu_cod_reside_mcpio` and `button`
    grouped = filtered_data.groupby(['estu_cod_reside_mcpio', 'button']).size().unstack(fill_value=0)
    grouped_percent = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Prepare horizontal bar positions for differentiation
    x = range(len(grouped_percent.columns))
    
    # Plot the superimposed bar chart
    plt.figure(figsize=(12, 8))
    for idx, (mcpio_group, row) in enumerate(grouped_percent.iterrows()):
        positions = [pos + (idx * bar_width) for pos in x]
        plt.bar(
            positions, row, width=bar_width, color=color_mapping.get(mcpio_group, "gray"),
            alpha=0.8, label=f'Municipio: {mcpio_group}', edgecolor='black'
        )

    # Adjust x-axis positions for better spacing
    plt.xticks([pos + (bar_width * (len(grouped_percent.index) - 1) / 2) for pos in x], grouped_percent.columns, rotation=45, ha='right')

    # Add titles and labels
    plt.title(f'Respuestas para {node} según municipio de residencia', fontsize=16)
    plt.xlabel('Respuestas', fontsize=14)
    plt.ylabel('Porcentaje', fontsize=14)
    plt.legend(title='Municipio de Residencia', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Save the plot
    plt.tight_layout()
    plot_path = path + f'/Outputs/analisis_resultados_encuesta/Whatsapp/plots/frecuencia_{node}_by_mcpio.png'
    plt.savefig(plot_path, format="png", dpi=300)
    plt.close()

    print(f"Saved plot for {node} at {plot_path}")

    # Save unstructured text responses for the current node
    unstructured_responses = df[(df['node_start'] == node) & (df['node_end'] != node) & (df['description'] == '')]
    unstructured_responses = unstructured_responses[['message']]
    unstructured_responses = unstructured_responses[unstructured_responses['message'] != '']
    csv_path = path + f'/Outputs/analisis_resultados_encuesta/Whatsapp/text_answers/not_structured/{node}_by_mcpio.csv'
    unstructured_responses.to_csv(csv_path, index=False)
    print(f"Saved unstructured responses for {node} at {csv_path}")