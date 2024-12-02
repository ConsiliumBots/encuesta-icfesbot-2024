import pandas as pd
import os
from pandasgui import show
import matplotlib.pyplot as plt
import numpy as np

####### Import data

# Paths
completed_responses = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Qualtrics/Encuesta icfes educación superior_November 29, 2024_13.14.csv'
partial_responses = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Qualtrics/Encuesta icfes educación superior_November 29, 2024_13.14-2.csv'
output_dir = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/qualtrics/'
os.makedirs(output_dir, exist_ok=True)

# Import CSV files
df_completed = pd.read_csv(completed_responses)
df_partial = pd.read_csv(partial_responses)


####### Clean users

# 1) Drop druplicated IPAddress in df_completed. Keep the most recent one
# 2) Drop druplicated IPAddress in df_partial. Keep the most recent one
# 3) Check for common IPAddress within df_completed and df_partial. If in both, keep the one in df_completed

# Clean column names
df_completed.rename(columns=lambda x: x.strip(), inplace=True)
df_partial.rename(columns=lambda x: x.strip(), inplace=True)

# Check and parse dates
df_completed['StartDate'] = pd.to_datetime(df_completed['StartDate'], errors='coerce')
df_partial['StartDate'] = pd.to_datetime(df_partial['StartDate'], errors='coerce')

# Drop rows with invalid StartDate
df_completed = df_completed.dropna(subset=['StartDate'])
df_partial = df_partial.dropna(subset=['StartDate'])

# Remove duplicate IPAddresses, keeping the most recent response
df_completed = df_completed.sort_values(by='StartDate', ascending=False).drop_duplicates(subset='IPAddress', keep='first')
df_partial = df_partial.sort_values(by='StartDate', ascending=False).drop_duplicates(subset='IPAddress', keep='first')

# Remove IPs in df_partial that already exist in df_completed
common_ips = set(df_completed['IPAddress']).intersection(set(df_partial['IPAddress']))
df_partial = df_partial[~df_partial['IPAddress'].isin(common_ips)]

# Combine cleaned datasets
df_combined = pd.concat([df_completed, df_partial], ignore_index=True)

# Save the combined dataset
output_path = os.path.join(output_dir, 'cleaned_combined_responses.csv')
df_combined.to_csv(output_path, index=False)
print(f"Cleaned combined dataset saved to {output_path}")

# Display summary
print(f"Number of completed responses: {len(df_completed)}")
print(f"Number of partial responses after deduplication: {len(df_partial)}")
print(f"Total combined responses: {len(df_combined)}")

show(df_combined)

####### Impute sex from whatsapp responses

whatsapp = pd.read_csv('/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/Whatsapp/cleaned_whatsapp_responses.csv')
crosswalk = pd.read_stata('/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/envio/listado_de_conctactos_qualtrics_para_subir.dta')

# Ensure 'phone' column is converted to string before applying string operations
whatsapp['phone'] = whatsapp['phone'].astype(str).str.extract(r'(\d+)')  # Extract numeric values
whatsapp = whatsapp.dropna(subset=['phone'])  # Drop rows where phone is NaN

# Remove '.0' suffix from 'number' and ensure it's a clean string
crosswalk['phone'] = crosswalk['phone'].astype(str).str.replace(r'\.0$', '', regex=True)

# Step 3: Merge whatsapp['phone'] with crosswalk['number']
merged_df = pd.merge(whatsapp, crosswalk, left_on='phone', right_on='phone', how='inner')

# Convert columns to string
df_combined['ExternalReference'] = df_combined['ExternalReference'].astype(str)
merged_df['externaldatareference'] = merged_df['externaldatareference'].astype(str).str.replace(r'\.0$', '', regex=True)

# Step 4: Merge merged_df['link'] with df_combined['Responseld']
# Assuming `df_combined` is already loaded:
df_combined = pd.merge(df_combined, merged_df, left_on='ExternalReference', right_on='externaldatareference', how='left')

# Save the merged DataFrame if needed
output_path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/Qualtrics/whatsapp_qualtrics_merged_responses.csv'  # Replace with your desired output path
df_combined.to_csv(output_path, index=False)
print(f"Merged data saved to {output_path}")

####### Retention analysis

# Filter columns that start with "Q"
q_columns = [col for col in df_combined.columns if col.startswith("Q")]

# Subset the DataFrame to include only those columns
df_q_columns = df_combined[q_columns]

# Count non-NaN responses for each question
response_counts = df_q_columns.notna().sum()

# Calculate percentages relative to the first question
percentages = (response_counts / response_counts.iloc[0]) * 100

# Create the bar plot
plt.figure(figsize=(14, 6))
bars = plt.bar(response_counts.index, response_counts, color='skyblue', edgecolor='black')

# Add percentage labels above each bar
for bar, percent in zip(bars, percentages):
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 5,
        f'{percent:.1f}%',
        ha='center',
        fontsize=10
    )

# Customize the plot
plt.title('Number of Responses for Each Question', fontsize=16)
plt.xlabel('Questions', fontsize=14)
plt.ylabel('Number of Responses', fontsize=14)
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
plt.tight_layout()

# Save and show the plot
output_file = output_dir + 'responses_by_q_question_percentage.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Bar chart saved to {output_file}")


####### Clean responses: Q10 - Estado postulación
# Prepare the data for Q10
df_combined['Q10'] = df_combined['Q10'].fillna('Desconocido')  # Replace NaN values with 'Desconocido'
value_counts = df_combined['Q10'].value_counts()  # Count the frequency of each category
percentages = value_counts / value_counts.sum() * 100  # Calculate percentages

# Plot the bar chart
plt.figure(figsize=(12, 6))
bars = plt.bar(value_counts.index, value_counts, color='skyblue', edgecolor='black')

# Add percentage labels above each bar
for bar, percent in zip(bars, percentages):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{percent:.1f}%', ha='center', fontsize=10)

# Customize the chart
plt.title('Distribución del Estado de Postulación (Q10)', fontsize=16)
plt.xlabel('Estado de Postulación', fontsize=14)
plt.ylabel('Frecuencia', fontsize=14)
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

# Save and show the plot
plt.tight_layout()
output_file = output_dir + 'bar_chart_q10_labeled.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Bar chart saved to {output_file}")





######### Gráfico: Q10.1 - Numero de carreras postuladas
df_combined['Q10.1'] = pd.to_numeric(df_combined['Q10.1'], errors='coerce')

# Calculate the mean
mean_value = df_combined['Q10.1'].mean()
print(f"Mean of Q10.1: {mean_value:.2f}")

# Prepare the data for the histogram
data = df_combined['Q10.1'].dropna()
bins = np.arange(data.min(), data.max() + 2)  # Ensure all integers in range are shown
hist, bin_edges = np.histogram(data, bins=bins)
percentages = hist / hist.sum() * 100

# Plot the histogram
plt.figure(figsize=(12, 6))
bars = plt.bar(bin_edges[:-1], hist, width=0.9, color='skyblue', edgecolor='black', align='center')

# Add percentage labels above each bar
for bar, percent in zip(bars, percentages):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{percent:.1f}%', ha='center', fontsize=10)

# Customize x-axis to show every integer
plt.xticks(np.arange(data.min(), data.max() + 1, 1))

# Add titles and labels
plt.title('Distribución del Número de Carreras Postuladas (Q10.1)', fontsize=16)
plt.xlabel('Número de Carreras Postuladas', fontsize=14)
plt.ylabel('Frecuencia', fontsize=14)

# Highlight the mean value on the histogram
plt.axvline(mean_value, color='red', linestyle='dashed', linewidth=1.5, label=f'Media: {mean_value:.2f}')
plt.legend()

# Save and show the plot
plt.tight_layout()
plt.savefig(output_dir + 'histograma_q10_1_labeled.png', format='png', dpi=300)
plt.show()

print(f"Histogram saved to {output_dir + 'histograma_q10_1_labeled.png'}")







######### Gráfico: Carrera más preferida

# Q16_1 - Carrera en primera preferencia
# Q16_2 - Carrera en segunda preferencia
# Q16_3 - Carrera en tercera preferencia

# Filter Q16_1 to keep only entries containing "/"
df_combined['Q16_1'] = df_combined['Q16_1'].fillna('')  # Replace NaN with an empty string
df_filtered = df_combined[df_combined['Q16_1'].str.contains('/')]

# Filter Q16_1 to keep only entries containing "/"
df_combined['Q18_1'] = df_combined['Q18_1'].fillna('')  # Replace NaN with an empty string
df_filtered = df_combined[df_combined['Q18_1'].str.contains('/')]

# Filter Q16_1 to keep only entries containing "/"
df_combined['Q19_1.1'] = df_combined['Q19_1.1'].fillna('')  # Replace NaN with an empty string
df_filtered = df_combined[df_combined['Q19_1.1'].str.contains('/')]

# Count rows containing "/" in Q16_1
count_with_slash = df_combined['Q16_1'].str.contains('/').sum()

# Count rows not containing "/" in Q16_1
count_without_slash = len(df_combined) - count_with_slash

# Output the counts
print(f"Rows with '/': {count_with_slash}")
print(f"Rows without '/': {count_without_slash}")


# Tabulate rows without "/"
rows_without_slash = df_combined[(~df_combined['Q16_1'].str.contains('/')) & (df_combined['Q16_1'] != '')]

# Count unique values and their frequencies
tabulated_without_slash = rows_without_slash['Q16_1'].value_counts()

# Display the tabulated values
print(tabulated_without_slash)

# Define the function for imputing based on conditions
def impute_values(df, column, conditions):
    """
    Impute values in a column based on specified conditions.

    Args:
        df (pd.DataFrame): The DataFrame to modify.
        column (str): The column to clean.
        conditions (list): A list of dictionaries, where each dictionary contains:
            - "contains": List of strings to search for in the column.
            - "impute": The value to impute if all strings in "contains" are found.

    Returns:
        pd.DataFrame: DataFrame with the cleaned column.
    """
    # Apply the logic only to rows without '/' and not empty
    target_rows = (~df[column].str.contains('/')) & (df[column] != '')
    
    for condition in conditions:
        contains = condition['contains']
        impute = condition['impute']
        # Check if all substrings in "contains" are present in the column (case-insensitive)
        mask = df[target_rows][column].apply(
            lambda x: all(sub.lower() in x.lower() for sub in contains)
        )
        # Impute the value where the condition is met
        df.loc[mask.index[mask], column] = impute
    return df

conditions = [
    # Nacional
    {"contains": ["vet", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/MEDICINA VETERINARIA"},
    {"contains": ["medicina", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/MEDICINA"},
    {"contains": ["psic", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/PSICOLOGIA"},
    {"contains": ["derecho", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/DERECHO"},
    {"contains": ["mecanica", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/INGENIERIA MECANICA"},
    {"contains": ["cont", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/CONTADURIA PUBLICA"},
    {"contains": ["compu", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/INGENIERIA DE SISTEMAS Y COMPUTACION"},
    {"contains": ["arqui", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/ARQUITECTURA"},
    {"contains": ["admi", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/ADMINISTRACION DE EMPRESAS"},
    {"contains": ["economía", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/ECONOMÍA"},
    {"contains": ["química", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/QUÍMICA"},
    {"contains": ["civil", "nacional"], "impute": "UNIVERSIDAD NACIONAL DE COLOMBIA/INGENIERÍA CIVIL"},

    # Andes
    {"contains": ["psicología", "andes"], "impute": "UNIVERSIDAD DE LOS ANDES/PSICOLOGÍA"},
    {"contains": ["derecho", "andes"], "impute": "UNIVERSIDAD DE LOS ANDES/DERECHO"},
    {"contains": ["ing", "andes"], "impute": "UNIVERSIDAD DE LOS ANDES/INGENIERÍA INDUSTRIAL"},
    {"contains": ["admi", "andes"], "impute": "UNIVERSIDAD DE LOS ANDES/ADMINISTRACIÓN"},
    {"contains": ["eco", "andes"], "impute": "UNIVERSIDAD DE LOS ANDES/ECONOMÍA"},

    # Javeriana
    {"contains": ["ingeniería", "javeriana"], "impute": "UNIVERSIDAD JAVERIANA/INGENIERÍA DE SISTEMAS"},
    {"contains": ["medicina", "javeriana"], "impute": "UNIVERSIDAD JAVERIANA/MEDICINA"},
    {"contains": ["derecho", "javeriana"], "impute": "UNIVERSIDAD JAVERIANA/DERECHO"},
    {"contains": ["psico", "javeriana"], "impute": "UNIVERSIDAD JAVERIANA/PSICOLOGÍA"},
    {"contains": ["admi", "javeriana"], "impute": "UNIVERSIDAD JAVERIANA/ADMINISTRACIÓN DE EMPRESAS"},

    # Valle
    {"contains": ["medicina", "valle"], "impute": "UNIVERSIDAD DEL VALLE/MEDICINA"},
    {"contains": ["ing", "valle"], "impute": "UNIVERSIDAD DEL VALLE/INGENIERÍA INDUSTRIAL"},
    {"contains": ["arqui", "valle"], "impute": "UNIVERSIDAD DEL VALLE/ARQUITECTURA"},
    {"contains": ["derecho", "valle"], "impute": "UNIVERSIDAD DEL VALLE/DERECHO"},

    # Antioquia
    {"contains": ["medicina", "antioquia"], "impute": "UNIVERSIDAD DE ANTIOQUIA/MEDICINA"},
    {"contains": ["derecho", "antioquia"], "impute": "UNIVERSIDAD DE ANTIOQUIA/DERECHO"},
    {"contains": ["psicología", "antioquia"], "impute": "UNIVERSIDAD DE ANTIOQUIA/PSICOLOGÍA"},
    {"contains": ["eco", "antioquia"], "impute": "UNIVERSIDAD DE ANTIOQUIA/ECONOMÍA"},
    {"contains": ["ing", "antioquia"], "impute": "UNIVERSIDAD DE ANTIOQUIA/INGENIERÍA QUÍMICA"},

    # Atlántico
    {"contains": ["medicina", "atlántico"], "impute": "UNIVERSIDAD DEL ATLÁNTICO/MEDICINA"},
    {"contains": ["derecho", "atlántico"], "impute": "UNIVERSIDAD DEL ATLÁNTICO/DERECHO"},
    {"contains": ["ing", "atlántico"], "impute": "UNIVERSIDAD DEL ATLÁNTICO/INGENIERÍA INDUSTRIAL"},
]

# Apply the function to clean rows without "/"
df_combined_new = impute_values(df_combined, "Q16_1", conditions)
df_combined_new = impute_values(df_combined, "Q18_1", conditions)
df_combined_new = impute_values(df_combined, "Q19_1.1", conditions)

# Rows with "/" and not null
df_combined_new = df_combined_new[(df_combined_new['Q16_1'].str.contains('/')) & (df_combined_new['Q16_1'] != '')]
df_combined_new = df_combined_new[(df_combined_new['Q18_1'].str.contains('/')) & (df_combined_new['Q18_1'] != '')]
df_combined_new = df_combined_new[(df_combined_new['Q19_1.1'].str.contains('/')) & (df_combined_new['Q19_1.1'] != '')]

# Verify the results for rows without "/"
rows_without_slash_after = df_combined_new[(~df_combined_new['Q16_1'].str.contains('/')) & (df_combined_new['Q16_1'] != '')]
print("Cleaned Rows Without '/':")
print(rows_without_slash_after['Q16_1'].value_counts().head(100))

tabulated_without_slash = rows_without_slash_after['Q16_1'].value_counts()
print(tabulated_without_slash)

# Count the occurrences of each unique entry in Q16_1 and keep only the top 10
value_counts = df_combined_new['Q16_1'].value_counts().nlargest(10)

# Plot a horizontal bar chart
plt.figure(figsize=(10, 8))
bars = plt.barh(value_counts.index, value_counts, color='skyblue', edgecolor='black')

# Add percentage labels at the end of each bar
percentages = value_counts / value_counts.sum() * 100
for bar, percent in zip(bars, percentages):
    plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2, f'{percent:.1f}%', va='center', fontsize=10)

# Customize the chart
plt.title('Top 10 Carreras en Primera Preferencia (Q16_1)', fontsize=16)
plt.xlabel('Frecuencia', fontsize=14)
plt.ylabel('Carrera (Primera Preferencia)', fontsize=14)
plt.tight_layout()

# Save and show the plot
output_file = output_dir + 'horizontal_bar_q16_1_top10.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Horizontal bar chart saved to {output_file}")




######### Gráfico: Carrera más preferida según sexo (P13)

# Filter the DataFrame to include only "Femenino" and "Masculino"
df_combined_new = df_combined_new[df_combined_new['P13'].isin(['Femenino', 'Masculino'])]

# Count the occurrences of each unique entry in Q16_1 grouped by gender
grouped_counts = df_combined_new.groupby(['Q16_1', 'P13']).size().unstack(fill_value=0)

# Keep only the top 10 most popular careers overall
top_careers = grouped_counts.sum(axis=1).nlargest(10).index
grouped_counts = grouped_counts.loc[top_careers]

# Ensure correct color order: Masculino (blue) first, Femenino (pink) second
grouped_counts = grouped_counts[['Masculino', 'Femenino']]

# Plot the horizontal grouped bar chart
fig, ax = plt.subplots(figsize=(10, 8))
grouped_counts.plot(kind='barh', stacked=False, ax=ax, color=['skyblue', 'pink'], edgecolor='black')

# Add labels and legend
ax.set_title('Top 10 Carreras en Primera Preferencia por Género (Q16_1)', fontsize=16)
ax.set_xlabel('Frecuencia', fontsize=14)
ax.set_ylabel('Carrera (Primera Preferencia)', fontsize=14)
ax.legend(title='Género', loc='lower right')

# Add value annotations on the bars
for i, (gender, counts) in enumerate(grouped_counts.items()):
    for j, count in enumerate(counts):
        if count > 0:
            ax.text(count + 0.5, j + i * 0.25 - 0.125, str(count), va='center', fontsize=10)

# Customize layout and save the plot
plt.tight_layout()
output_file = output_dir + 'horizontal_grouped_bar_q16_1_top10_by_gender.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Horizontal grouped bar chart saved to {output_file}")














######### Gráfico: Categoría de carrera más preferida

def categorize_careers(df, column, conditions):
    """
    Categorize values in a column based on specified conditions.

    Args:
        df (pd.DataFrame): The DataFrame to modify.
        column (str): The column to categorize.
        conditions (list): A list of dictionaries, where each dictionary contains:
            - "contains": List of strings to search for in the column.
            - "impute": The category to assign if all strings in "contains" are found.

    Returns:
        pd.DataFrame: DataFrame with the categorized column.
    """
    # Create a temporary column to preserve the original values
    temp_column = f"{column}_original"
    df[temp_column] = df[column]

    for condition in conditions:
        contains = condition['contains']
        impute = condition['impute']
        # Apply the categorization based on the original values
        mask = df[temp_column].apply(lambda x: all(sub.lower() in str(x).lower() for sub in contains))
        df.loc[mask, column] = impute

    # Drop the temporary column after categorization (optional, for cleanliness)
    df.drop(columns=[temp_column], inplace=True)
    
    return df
    
conditions = [
    # Medical-related fields
    {"contains": ["vet"], "impute": "MEDICINA VETERINARIA"},
    {"contains": ["med"], "impute": "MEDICINA"},
    {"contains": ["enfer"], "impute": "ENFERMERÍA"},
    {"contains": ["nutri"], "impute": "NUTRICIÓN"},
    {"contains": ["fisi"], "impute": "FISIOTERAPIA"},
    {"contains": ["odont"], "impute": "ODONTOLOGÍA"},

    # Social sciences and psychology
    {"contains": ["psic"], "impute": "PSICOLOGÍA"},
    {"contains": ["soci"], "impute": "SOCIOLOGÍA"},
    {"contains": ["antrop"], "impute": "ANTROPOLOGÍA"},

    # Legal and administrative fields
    {"contains": ["derecho"], "impute": "DERECHO"},
    {"contains": ["admi"], "impute": "ADMINISTRACIÓN DE EMPRESAS"},
    {"contains": ["conta"], "impute": "CONTADURÍA"},

    # Engineering and technology
    {"contains": ["ingeniería"], "impute": "INGENIERÍA"},
    {"contains": ["sistemas"], "impute": "INGENIERÍA DE SISTEMAS"},
    {"contains": ["computación"], "impute": "INGENIERÍA DE SISTEMAS"},
    {"contains": ["industrial"], "impute": "INGENIERÍA INDUSTRIAL"},
    {"contains": ["civil"], "impute": "INGENIERÍA CIVIL"},
    {"contains": ["eléctrica"], "impute": "INGENIERÍA ELÉCTRICA"},
    {"contains": ["electrónica"], "impute": "INGENIERÍA ELECTRÓNICA"},
    {"contains": ["química"], "impute": "INGENIERÍA QUÍMICA"},
    {"contains": ["mecánica"], "impute": "INGENIERÍA MECÁNICA"},
    {"contains": ["ambiental"], "impute": "INGENIERÍA AMBIENTAL"},

    # Arts and architecture
    {"contains": ["arqu"], "impute": "ARQUITECTURA"},
    {"contains": ["diseño"], "impute": "DISEÑO GRÁFICO"},
    {"contains": ["arte"], "impute": "ARTES PLÁSTICAS"},

    # Science and math
    {"contains": ["biología"], "impute": "BIOLOGÍA"},
    {"contains": ["bio"], "impute": "BIOLOGÍA"},
    {"contains": ["química"], "impute": "QUÍMICA"},
    {"contains": ["fis"], "impute": "FÍSICA"},
    {"contains": ["mat"], "impute": "MATEMÁTICAS"},
    {"contains": ["estad"], "impute": "ESTADÍSTICA"},

    # Economics and business
    {"contains": ["eco"], "impute": "ECONOMÍA"},
    {"contains": ["fin"], "impute": "FINANZAS"},
    {"contains": ["merc"], "impute": "MERCADOTECNIA"},
    {"contains": ["negocios"], "impute": "NEGOCIOS INTERNACIONALES"},

    # Education
    {"contains": ["pedag"], "impute": "PEDAGOGÍA"},
    {"contains": ["educación"], "impute": "EDUCACIÓN"},

    # Law enforcement and public safety
    {"contains": ["crimin"], "impute": "CRIMINOLOGÍA"},
    {"contains": ["seguridad"], "impute": "SEGURIDAD PÚBLICA"},

    # Generic cases
    {"contains": ["tecnología"], "impute": "TECNOLOGÍA"},
    {"contains": ["tecnólogo"], "impute": "TECNOLOGÍA"},
    {"contains": ["ing"], "impute": "INGENIERÍA"},  # Shortened engineering
]

df_combined = df_combined[df_combined['Q16_1'] != '']

# Categorize careers based on conditions
df_combined = categorize_careers(df_combined, "Q16_1", conditions)

# Count the occurrences of each unique entry in Q16_1 and keep only the top 10
value_counts = df_combined['Q16_1'].value_counts().nlargest(10)

# Plot a horizontal bar chart
plt.figure(figsize=(10, 8))
bars = plt.barh(value_counts.index, value_counts, color='skyblue', edgecolor='black')

# Add percentage labels at the end of each bar
percentages = value_counts / value_counts.sum() * 100
for bar, percent in zip(bars, percentages):
    plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2, f'{percent:.1f}%', va='center', fontsize=10)

# Customize the chart
plt.title('Top 10 Categorías de Carrera (Q16_1)', fontsize=16)
plt.xlabel('Frecuencia', fontsize=14)
plt.ylabel('Categoría carrera', fontsize=14)
plt.tight_layout()

# Save and show the plot
output_file = output_dir + 'categorized_carrers_q16_1_top10.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Horizontal bar chart saved to {output_file}")



######### Gráfico: Categoría de carrera más preferida según género

# Filter the DataFrame to include only "Femenino" and "Masculino"
df_combined = df_combined[df_combined['P13'].isin(['Femenino', 'Masculino'])]

# Categorize careers based on conditions
df_combined = categorize_careers(df_combined, "Q16_1", conditions)

# Count occurrences of each career category grouped by gender
grouped_counts = df_combined.groupby(['Q16_1', 'P13']).size().unstack(fill_value=0)

# Keep only the top 10 most popular career categories overall
top_categories = grouped_counts.sum(axis=1).nlargest(10).index
grouped_counts = grouped_counts.loc[top_categories]

# Ensure correct color order: Masculino (blue) first, Femenino (pink) second
grouped_counts = grouped_counts[['Masculino', 'Femenino']]

# Plot the horizontal grouped bar chart
fig, ax = plt.subplots(figsize=(10, 8))
grouped_counts.plot(kind='barh', stacked=False, ax=ax, color=['skyblue', 'pink'], edgecolor='black')

# Add labels and legend
ax.set_title('Top 10 Categorías de Carrera por Género (Q16_1)', fontsize=16)
ax.set_xlabel('Frecuencia', fontsize=14)
ax.set_ylabel('Categoría de Carrera', fontsize=14)
ax.legend(title='Género', loc='lower right')

# Add value annotations on the bars
for i, (gender, counts) in enumerate(grouped_counts.items()):
    for j, count in enumerate(counts):
        if count > 0:
            ax.text(count + 0.5, j + i * 0.25 - 0.125, str(count), va='center', fontsize=10)

# Customize layout and save the plot
plt.tight_layout()
output_file = output_dir + 'horizontal_grouped_bar_categorized_careers_q16_1_by_gender.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Horizontal grouped bar chart saved to {output_file}")




######## Carrea en que queda aceptado
# i need to make a similar graph but for the carrer they got accepted to
#Q20
# if equal to ${q://QID16/ChoiceTextEntryValue/3} => 3ra preferencia
# if equal to ${q://QID16/ChoiceTextEntryValue/2} => 2da preferencia
# if equal to ${q://QID16/ChoiceTextEntryValue/1} => 1ra preferencia

# Ensure Q16 columns are not NaN
df_combined['Q16_1'] = df_combined['Q16_1'].fillna('')
df_combined['Q16_2'] = df_combined['Q16_2'].fillna('')
df_combined['Q16_3'] = df_combined['Q16_3'].fillna('')

# Function to determine preference level
def determine_preference(row):
    if row['Q20'] == '${q://QID16/ChoiceTextEntryValue/1}':
        return '1ra preferencia'
    elif row['Q20'] == '${q://QID16/ChoiceTextEntryValue/2}':
        return '2da preferencia'
    elif row['Q20'] == '${q://QID16/ChoiceTextEntryValue/3}':
        return '3ra preferencia'
    elif row['Q20'] == 'Otra':
        return 'Otra opción'        

# Apply the function to create the `Preference_Level` column
df_combined['Preference_Level'] = df_combined.apply(determine_preference, axis=1)

# Count occurrences of each preference level
preference_counts = df_combined['Preference_Level'].value_counts()

# Calculate percentages
percentages = preference_counts / preference_counts.sum() * 100

# Plot a bar chart
plt.figure(figsize=(10, 6))
bars = plt.bar(preference_counts.index, preference_counts, color='skyblue', edgecolor='black')

# Add percentage labels above each bar
for bar, percent in zip(bars, percentages):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{percent:.1f}%', ha='center', fontsize=10)

# Customize the chart
plt.title('Distribución de Preferencias por Carrera Aceptada (Q20)', fontsize=16)
plt.xlabel('Nivel de Preferencia', fontsize=14)
plt.ylabel('Frecuencia', fontsize=14)
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

# Save and show the plot
output_file = os.path.join(output_dir, 'bar_chart_preference_q20.png')
plt.tight_layout()
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Bar chart saved to {output_file}")





######## Costo de carrera en primera preferencia
# Make a similar graph with the costo semestral de la carrera (pesos colombianos)
# Q14
# Only keep numbers (delete any other string contained)
# Drop if equal to 0 
# Drop if the number consists only of one number (e.g 11111 or 999999999)

import re
import seaborn as sns

# Clean Q14: Keep only numeric values
def clean_cost(value):
    # Extract numeric characters
    numeric_value = re.sub(r'[^\d]', '', str(value))
    # Return as integer if valid, otherwise NaN
    return int(numeric_value) if numeric_value.isdigit() else np.nan

df_combined['Q14'] = df_combined['Q14'].apply(clean_cost)

# Drop rows where Q14 is close to 0
df_combined = df_combined[df_combined['Q14'] > 10000]
# Drop outliers
df_combined = df_combined[df_combined['Q14'] < 44911800]

# Drop rows where Q14 consists of a single repeated digit
df_combined = df_combined[~df_combined['Q14'].astype(str).str.fullmatch(r'(\d)\1*')]

# Calculate statistics
mean_cost = df_combined['Q14'].mean()
median_cost = df_combined['Q14'].median()
print(f"Mean Costo Semestral: {mean_cost:,.0f} COP")
print(f"Median Costo Semestral: {median_cost:,.0f} COP")

# KDE Plot
plt.figure(figsize=(12, 6))
sns.kdeplot(data=df_combined['Q14'], fill=True, color='skyblue', alpha=0.5, linewidth=2, label='Densidad de Costo Semestral')

# Add mean and median lines
plt.axvline(mean_cost, color='red', linestyle='dashed', linewidth=1.5, label=f'Media: {mean_cost:,.0f} COP')
plt.axvline(median_cost, color='green', linestyle='dashed', linewidth=1.5, label=f'Mediana: {median_cost:,.0f} COP')

# Customize the chart
plt.title('Distribución del Costo Semestral de la Carrera (Q14)', fontsize=16)
plt.xlabel('Costo Semestral (COP)', fontsize=14)
plt.ylabel('Densidad', fontsize=14)
plt.legend()

# Save and show the plot
output_file = os.path.join(output_dir, 'kde_costo_semestral_q14.png')
plt.tight_layout()
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"KDE plot saved to {output_file}")




######## Carrera ideal: 1) Si no dependiera de las pruebas de admisión, 2) ni del financiemiento

import matplotlib.pyplot as plt

# Prepare data for Q18_1 vs Q16_1
fraction_q18_q16 = (df_combined_new['Q18_1'] == df_combined_new['Q16_1']).mean()
data_q18 = [fraction_q18_q16, 1 - fraction_q18_q16]
labels_q18 = ['Igual', 'Distinta']

# Prepare data for Q19_1.1 vs Q16_1
fraction_q19_q16 = (df_combined_new['Q19_1.1'] == df_combined_new['Q16_1']).mean()
data_q19 = [fraction_q19_q16, 1 - fraction_q19_q16]
labels_q19 = ['Igual', 'Distinta']

# Create the figure and two pie charts
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# Pie chart for Q18_1 vs Q16_1
axes[0].pie(data_q18, labels=labels_q18, autopct='%1.1f%%', startangle=90, colors=['skyblue', 'lightcoral'])
axes[0].set_title('Ideal (sin pruebas) = Primera preferencia', fontsize=14)

# Pie chart for Q19_1.1 vs Q16_1
axes[1].pie(data_q19, labels=labels_q19, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'salmon'])
axes[1].set_title('Ideal (sin pruebas + financiada) = Primera preferencia', fontsize=14)

# Add an overall title
fig.suptitle('Comparación de Preferencias de Carreras Ideales', fontsize=16)

# Adjust layout
plt.tight_layout()

# Save and display the chart
output_file = './two_pie_charts_q18_q19_vs_q16_updated.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Pie charts saved to {output_file}")



####### Carrera ideal por género

# Filter the DataFrame to include only "Femenino" and "Masculino"
df_combined_new = df_combined_new[df_combined_new['P13'].isin(['Femenino', 'Masculino'])]

# Calculate fractions for Q18_1 == Q16_1 (Ideal without admission tests) by gender
gender_q18 = df_combined_new.groupby('P13').apply(
    lambda group: [(group['Q18_1'] == group['Q16_1']).mean(), 1 - (group['Q18_1'] == group['Q16_1']).mean()]
)

# Calculate fractions for Q19_1.1 == Q16_1 (Ideal without admission tests and financed) by gender
gender_q19 = df_combined_new.groupby('P13').apply(
    lambda group: [(group['Q19_1.1'] == group['Q16_1']).mean(), 1 - (group['Q19_1.1'] == group['Q16_1']).mean()]
)

# Convert the results into a DataFrame for grouped bar plots
df_q18 = pd.DataFrame(gender_q18.tolist(), index=gender_q18.index, columns=['Igual', 'Distinta'])
df_q19 = pd.DataFrame(gender_q19.tolist(), index=gender_q19.index, columns=['Igual', 'Distinta'])

# Plot grouped bar charts
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# Bar chart for Q18_1 vs Q16_1
df_q18.plot(kind='bar', ax=axes[0], color=['skyblue', 'lightcoral'], edgecolor='black', width=0.8)
axes[0].set_title('Ideal (sin pruebas) = Primera preferencia', fontsize=14)
axes[0].set_xlabel('Género', fontsize=12)
axes[0].set_ylabel('Proporción', fontsize=12)
axes[0].set_xticklabels(df_q18.index, rotation=0)
axes[0].legend(title='Comparación', loc='upper right')

# Bar chart for Q19_1.1 vs Q16_1
df_q19.plot(kind='bar', ax=axes[1], color=['lightgreen', 'salmon'], edgecolor='black', width=0.8)
axes[1].set_title('Ideal (sin pruebas + financiada) = Primera preferencia', fontsize=14)
axes[1].set_xlabel('Género', fontsize=12)
axes[1].set_ylabel('Proporción', fontsize=12)
axes[1].set_xticklabels(df_q19.index, rotation=0)
axes[1].legend(title='Comparación', loc='upper right')

# Add an overall title
fig.suptitle('Comparación de Preferencias de Carreras Ideales por Género', fontsize=16)

# Adjust layout and save the plot
plt.tight_layout()
output_file = './grouped_bar_comparison_q18_q19_by_gender.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Grouped bar chart saved to {output_file}")




######## Razón de no postular a carrera ideal
#Q23

# Define the full text of each option and their corresponding shorter labels
q23_options = [
    {"full": "Sí, postulé a mi carrera ideal y es mi primera preferencia", "short": "Carrera ideal en 1ra preferencia"},
    {"full": "La probabilidad de que quede seleccionado en esa carrera es muy baja", "short": "Probabilidad baja de selección"},
    {"full": "La carrera me parece demasiado difícil y no creo que vaya a terminarla en caso de matricularme", "short": "Carrera difícil/no terminarla"},
    {"full": "No tengo los recursos económicos para pagar el costo de la carrera", "short": "Falta de recursos económicos"},
    {"full": "No me alcanzó el tiempo para postular a esa opción", "short": "Falta de tiempo para postular"},
    {"full": "La institución no me permitió postular", "short": "La institución no me permitió postular"},
    {"full": "La decisión de dónde postular no dependió completamente de mí, y fue influenciada por otras personas (familia, amigos u otros)", "short": "La decisión no dependió completamente de mí"},
    {"full": "Pensé que postular a esta carrera habría reducido mis posibilidades de admisión en las demás carreras", "short": "Reducción de opciones de admisión en otras carreras"},
    {"full": "Dado que mi probabilidad de admisión es muy baja, prefiero no postular y quedar seleccionado en una carrera más preferida", "short": "Prefiero no postular y quedar seleccionado en una más preferida"},
]

# Initialize a DataFrame to store the counts of each option
option_counts = pd.DataFrame({'Option': [opt['short'] for opt in q23_options], 'Count': 0})

# Count occurrences of each option
for i, option in enumerate(q23_options):
    option_counts.loc[i, 'Count'] = df_combined_new['Q23'].str.contains(option['full'], na=False).sum()

# Calculate percentages
option_counts['Percentage'] = (option_counts['Count'] / option_counts['Count'].sum()) * 100

# Sort the options by count (descending)
option_counts = option_counts.sort_values(by='Count', ascending=False)

# Plot the bar chart
plt.figure(figsize=(12, 8))
bars = plt.bar(option_counts['Option'], option_counts['Count'], color='skyblue', edgecolor='black')

# Add percentage labels above each bar
for bar, percentage in zip(bars, option_counts['Percentage']):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{percentage:.1f}%', ha='center', fontsize=10)

# Customize the chart
plt.title('Razones de No Postular a Carrera Ideal (Q23)', fontsize=16)
plt.xlabel('Razón', fontsize=14)
plt.ylabel('Frecuencia', fontsize=14)
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

# Save and show the plot
plt.tight_layout()
output_file = output_dir + 'bar_chart_q23_selected_sorted.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Bar chart saved to {output_file}")

# Display the counts and percentages for verification
print(option_counts)



######## Razón de no postular a carrera ideal según género

import matplotlib.pyplot as plt
import pandas as pd

# Filter the DataFrame to include only "Femenino" and "Masculino"
df_combined_new = df_combined_new[df_combined_new['P13'].isin(['Femenino', 'Masculino'])]

# Define the full text of each option and their corresponding shorter labels
q23_options = [
    {"full": "Sí, postulé a mi carrera ideal y es mi primera preferencia", "short": "Carrera ideal en 1ra preferencia"},
    {"full": "La probabilidad de que quede seleccionado en esa carrera es muy baja", "short": "Probabilidad baja de selección"},
    {"full": "La carrera me parece demasiado difícil y no creo que vaya a terminarla en caso de matricularme", "short": "Carrera difícil/no terminarla"},
    {"full": "No tengo los recursos económicos para pagar el costo de la carrera", "short": "Falta de recursos económicos"},
    {"full": "No me alcanzó el tiempo para postular a esa opción", "short": "Falta de tiempo para postular"},
    {"full": "La institución no me permitió postular", "short": "La institución no me permitió postular"},
    {"full": "La decisión de dónde postular no dependió completamente de mí, y fue influenciada por otras personas (familia, amigos u otros)", "short": "La decisión no dependió completamente de mí"},
    {"full": "Pensé que postular a esta carrera habría reducido mis posibilidades de admisión en las demás carreras", "short": "Reducción de opciones de admisión en otras carreras"},
    {"full": "Dado que mi probabilidad de admisión es muy baja, prefiero no postular y quedar seleccionado en una carrera más preferida", "short": "Prefiero no postular y quedar seleccionado en una más preferida"},
]

# Initialize a DataFrame to store the counts for each gender
gender_counts = pd.DataFrame()

# Count occurrences of each option grouped by gender
for gender in ['Femenino', 'Masculino']:
    counts = []
    for option in q23_options:
        count = df_combined_new[df_combined_new['P13'] == gender]['Q23'].str.contains(option['full'], na=False).sum()
        counts.append(count)
    gender_counts[gender] = counts

# Add the option labels to the DataFrame
gender_counts['Option'] = [opt['short'] for opt in q23_options]

# Calculate the total counts across both genders for sorting
gender_counts['Total'] = gender_counts['Femenino'] + gender_counts['Masculino']

# Sort by total count in descending order
gender_counts.sort_values(by='Total', ascending=False, inplace=True)

# Drop the 'Total' column (optional, if not needed)
gender_counts.drop(columns=['Total'], inplace=True)

# Set the index to 'Option' for easier plotting
gender_counts.set_index('Option', inplace=True)

# Plot the grouped bar chart
fig, ax = plt.subplots(figsize=(12, 8))
gender_counts.plot(kind='bar', ax=ax, color=['pink', 'skyblue'], edgecolor='black', width=0.8)

# Add labels and legend
ax.set_title('Razones de No Postular a Carrera Ideal por Género (Q23)', fontsize=16)
ax.set_xlabel('Razón', fontsize=14)
ax.set_ylabel('Frecuencia', fontsize=14)
ax.legend(title='Género', loc='upper right')
ax.set_xticklabels(gender_counts.index, rotation=45, ha='right')

# Add value annotations directly over the bars
for gender, color in zip(['Femenino', 'Masculino'], ['pink', 'skyblue']):
    for i, value in enumerate(gender_counts[gender]):
        if value > 0:
            ax.text(i - 0.15 if gender == 'Femenino' else i + 0.15,  # Adjust position slightly for overlap
                    value + 1,  # Position above the bar
                    str(value), 
                    ha='center', 
                    fontsize=10, 
                    color='black')

# Adjust layout and save the plot
plt.tight_layout()
output_file = output_dir + 'grouped_bar_chart_q23_by_gender_sorted.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Grouped bar chart saved to {output_file}")

# Display the counts for verification
print(gender_counts)





######## Razón de no postular a educación superior
#Q20.1
#Simple bar graph with every option as previous ones.

import pandas as pd
import matplotlib.pyplot as plt

# Clean the column by replacing NaN with an empty string
df_combined_new['Q20.1'] = df_combined_new['Q20.1'].fillna('')

# Define the possible options for Q20.1 with simplified labels
options_q20_1 = {
    "No aprobé las pruebas de admisión de las carreras que quería estudiar": "No aprobé pruebas de admisión",
    "No puedo financiar la carrera que quiero estudiar": "No puedo financiar",
    "No tengo información de las carreras disponibles": "Falta de información",
    "Estoy trabajando o buscando trabajo": "Trabajando o buscando trabajo",
    "No está en mis planes": "No está en mis planes"
}

# Initialize a dictionary to store counts for each option
option_counts = {short_text: 0 for short_text in options_q20_1.values()}

# Iterate through each response and count occurrences of each option
for response in df_combined_new['Q20.1']:
    for full_text, short_text in options_q20_1.items():
        if full_text.lower() in response.lower():
            option_counts[short_text] += 1

# Convert counts into a pandas Series and sort by value
option_counts_series = pd.Series(option_counts).sort_values(ascending=False)

# Plot the bar graph
plt.figure(figsize=(12, 6))
bars = plt.bar(option_counts_series.index, option_counts_series, color='skyblue', edgecolor='black')

# Add value labels above each bar
for bar in bars:
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f'{bar.get_height()}', ha='center', fontsize=10)

# Customize the graph
plt.title('Razón de No Postular a Educación Superior (Q20.1)', fontsize=16)
plt.xlabel('Razón', fontsize=14)
plt.ylabel('Frecuencia', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Save and show the plot
output_file = './bar_chart_q20_1_updated.png'
plt.savefig(output_file, format='png', dpi=300)
plt.show()

print(f"Bar chart saved to {output_file}")

######## Días gastados postulando (Q12) y Dinero gastado postulando (Q13)

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Clean and preprocess Q12 (Días gastados postulando)
df_combined_new['Q12'] = pd.to_numeric(df_combined_new['Q12'], errors='coerce')  # Convert to numeric, coerce errors
df_combined_new['Q12'] = df_combined_new['Q12'].fillna(0).astype(int)  # Replace NaN with 0 and convert to integer

# Filter invalid values for Q12 (e.g., values equal to 0 or consisting of only repeated digits)
df_q12_filtered = df_combined_new[
    (df_combined_new['Q12'] > 0) & 
    (df_combined_new['Q12'] < 30)  # Maximum reasonable days spent
]

# Clean and preprocess Q13 (Dinero gastado postulando)
df_combined_new['Q13'] = df_combined_new['Q13'].str.replace(r'\D', '', regex=True)  # Remove non-numeric characters
df_combined_new['Q13'] = pd.to_numeric(df_combined_new['Q13'], errors='coerce')  # Convert to numeric
df_combined_new['Q13'] = df_combined_new['Q13'].fillna(0).astype(int)  # Replace NaN with 0 and convert to integer

# Filter invalid values for Q13 (e.g., values equal to 0 or consisting of only repeated digits)
df_q13_filtered = df_combined_new[
    (df_combined_new['Q13'] > 10000) &  # Minimum threshold
    (df_combined_new['Q13'] < 44911800)  # Maximum threshold
]

# Plot kernel density estimation for Q12
plt.figure(figsize=(12, 6))
sns.kdeplot(df_q12_filtered['Q12'], fill=True, color="skyblue", alpha=0.7, bw_adjust=1)
plt.title('Distribución de Días Gastados Postulando (Q12)', fontsize=16)
plt.xlabel('Días Gastados Postulando', fontsize=14)
plt.ylabel('Densidad', fontsize=14)
plt.axvline(df_q12_filtered['Q12'].mean(), color='red', linestyle='dashed', linewidth=1.5, label=f'Media: {df_q12_filtered["Q12"].mean():.2f}')
plt.legend()
plt.tight_layout()
plt.savefig(output_dir + 'kde_q12_days_spent.png', format='png', dpi=300)
plt.show()

# Plot kernel density estimation for Q13
plt.figure(figsize=(12, 6))
sns.kdeplot(df_q13_filtered['Q13'], fill=True, color="green", alpha=0.7, bw_adjust=1)
plt.title('Distribución de Dinero Gastado Postulando (Q13)', fontsize=16)
plt.xlabel('Dinero Gastado Postulando (COP)', fontsize=14)
plt.ylabel('Densidad', fontsize=14)
plt.axvline(df_q13_filtered['Q13'].mean(), color='red', linestyle='dashed', linewidth=1.5, label=f'Media: {df_q13_filtered["Q13"].mean():,.0f} COP')
plt.legend()
plt.tight_layout()
plt.savefig(output_dir + 'kde_q13_money_spent.png', format='png', dpi=300)
plt.show()

print("Graphs saved successfully!")