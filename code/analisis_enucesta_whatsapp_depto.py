import pandas as pd
import matplotlib.pyplot as plt
import re
from matplotlib.cm import get_cmap


############# Número encuestas respondidas según departamento

import pandas as pd
import re

# Define the path to data
path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data'

# Load chatbot interaction data
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

# Define department mapping (Código Departamento to Nombre Departamento)
dept_mapping = {
    "05": "ANTIOQUIA",
    "08": "ATLÁNTICO",
    "11": "BOGOTÁ. D.C.",
    "13": "BOLÍVAR",
    "15": "BOYACÁ",
    "17": "CALDAS",
    "18": "CAQUETÁ",
    "19": "CAUCA",
    "20": "CESAR",
    "23": "CÓRDOBA",
    "25": "CUNDINAMARCA",
    "27": "CHOCÓ",
    "41": "HUILA",
    "44": "LA GUAJIRA",
    "47": "MAGDALENA",
    "50": "META",
    "52": "NARIÑO",
    "54": "NORTE DE SANTANDER",
    "63": "QUINDÍO",
    "66": "RISARALDA",
    "68": "SANTANDER",
    "70": "SUCRE",
    "73": "TOLIMA",
    "76": "VALLE DEL CAUCA",
    "81": "ARAUCA",
    "85": "CASANARE",
    "86": "PUTUMAYO",
    "88": "ARCHIPIÉLAGO DE SAN ANDRÉS. PROVIDENCIA Y SANTA CATALINA",
    "91": "AMAZONAS",
    "94": "GUAINÍA",
    "95": "GUAVIARE",
    "97": "VAUPÉS",
    "99": "VICHADA"
}

# Ensure `estu_cod_reside_depto` is zero-padded to 2 digits
df['estu_cod_reside_depto'] = df['estu_cod_reside_depto'].apply(lambda x: str(x).zfill(2))

# Map department codes to names
df['dept_name'] = df['estu_cod_reside_depto'].map(dept_mapping)

# Add "Sin departamento" for entries with missing department mapping
df['dept_name'].fillna('Sin departamento', inplace=True)

# Calculate the total number of surveyed individuals (*encuestados*) by department
total_surveyed = df.groupby('dept_name')['phone'].nunique().reset_index(name='Total Encuestados')

# Calculate fractions for all departments
total_surveyed['Fraction'] = total_surveyed['Total Encuestados'] / total_surveyed['Total Encuestados'].sum()

# Sort the table from highest to lowest by "Total Encuestados"
summary_table = total_surveyed.sort_values(by='Total Encuestados', ascending=False)

# Add a row for "Total"
total_row = pd.DataFrame({
    'dept_name': ['Total'], 
    'Total Encuestados': [summary_table['Total Encuestados'].sum()], 
    'Fraction': [summary_table['Fraction'].sum()]
})
summary_table = pd.concat([summary_table, total_row], ignore_index=True)

# Format fraction as percentage
summary_table['Fraction'] = summary_table['Fraction'].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else x)

# Rename columns for final output
summary_table.rename(columns={'dept_name': 'Departamento'}, inplace=True)

# Keep only required columns
summary_table = summary_table[['Departamento', 'Total Encuestados', 'Fraction']]

# Save table to CSV
output_table_path = path + '/Outputs/analisis_resultados_encuesta/Whatsapp/table_surveyed_with_department.csv'
summary_table.to_csv(output_table_path, index=False)
print(f"Summary table saved to {output_table_path}")


############# Respuesta a cada pregunta según departamento

# Define the path to data
path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data'

# Load chatbot interaction data
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

# Define department group mapping
dept_mapping = {
    '11': 'Bogotá',
    '05': 'Antioquia',
    '76': 'Valle del Cauca',
    '08': 'Atlántico',
}
df['dept_group'] = df['estu_cod_reside_depto'].apply(
    lambda x: dept_mapping.get(str(x).zfill(2), 'Otros')  # Group into 'Otros' if not explicitly mapped
)

# Define a colormap for the groups
dept_groups = df['dept_group'].unique()
colors = get_cmap("tab10")(range(len(dept_groups)))
color_mapping = dict(zip(dept_groups, colors))

# Adjust the bar width to make the bars narrower
bar_width = 0.1  # Further reduced for thinner bars

# Iterate over nodes to generate graphs
for i in range(1, 15):
    node = f'P{i}'
    
    # Filter predefined responses for the current node
    filtered_data = df[(df['node_start'] == node) & (df['node_end'] != node) & (df['button'] != '')]

    # Group responses by `dept_group` and `button`
    grouped = filtered_data.groupby(['dept_group', 'button']).size().unstack(fill_value=0)
    grouped_percent = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Prepare horizontal bar positions for differentiation
    x = range(len(grouped_percent.columns))
    
    # Plot the superimposed bar chart
    plt.figure(figsize=(12, 8))
    for idx, (dept_group, row) in enumerate(grouped_percent.iterrows()):
        positions = [pos + (idx * bar_width) for pos in x]
        plt.bar(
            positions, row, width=bar_width, color=color_mapping.get(dept_group, "gray"),
            alpha=0.8, label=f'{dept_group}', edgecolor='black'
        )

    # Adjust x-axis positions for better spacing
    plt.xticks([pos + (bar_width * (len(grouped_percent.index) - 1) / 2) for pos in x], grouped_percent.columns, rotation=45, ha='right')

    # Add titles and labels
    plt.title(f'Respuestas para {node} según grupo de departamento', fontsize=16)
    plt.xlabel('Respuestas', fontsize=14)
    plt.ylabel('Porcentaje', fontsize=14)
    plt.legend(title='Grupo de Departamento', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Save the plot
    plt.tight_layout()
    plot_path = path + f'/Outputs/analisis_resultados_encuesta/Whatsapp/plots/frecuencia_{node}_por_dept.png'
    plt.savefig(plot_path, format="png", dpi=300)
    plt.close()

    print(f"Saved plot for {node} at {plot_path}")

    # Save unstructured text responses for the current node
    unstructured_responses = df[(df['node_start'] == node) & (df['node_end'] != node) & (df['description'] == '')]
    unstructured_responses = unstructured_responses[['message']]
    unstructured_responses = unstructured_responses[unstructured_responses['message'] != '']
    csv_path = path + f'/Outputs/analisis_resultados_encuesta/Whatsapp/text_answers/not_structured/{node}_by_dept_group.csv'
    unstructured_responses.to_csv(csv_path, index=False)
    print(f"Saved unstructured responses for {node} at {csv_path}")