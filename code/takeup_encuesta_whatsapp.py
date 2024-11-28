import pandas as pd
import pyreadstat
import matplotlib.pyplot as plt

# File path
file_path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Whatsapp/logs_icfes.sav'

# Load the file
data, meta = pyreadstat.read_sav(file_path)

# Define the mapping of questions to search terms and dummy column names
questions = {
    "Hola": "p0",
    "Para comenzar": "p1",
    "Recibiste alguna orientación": "p2",
    "medio prefieres": "p3",
    "hubiese gustado recibir": "p4",
    "difícil de encontrar": "p5",
    "lugar de residencia": "p6",
    "Política de Gratuidad": "p7",
    "Saber 11": "p8",
    "identidad de género": "p9",
    "orientación sexual": "p10",
    "experiencia con nosotros": "p11",
}

# Create dummy variables for each question
for key, dummy in questions.items():
    data[dummy] = data['Body'].str.contains(key, na=False).astype(int)

# Add a "question" column to represent the specific question matched by each row
data['question'] = None
for key, dummy in questions.items():
    data.loc[data[dummy] == 1, 'question'] = dummy

# Ensure the timestamp column is in datetime format
data['Date_Sent'] = pd.to_datetime(data['Date_Sent'])

# Filter rows where Date_Sent is after 2024-11-13 and before 2024-11-25
filtered_data = data[
    (data['Date_Sent'] > pd.Timestamp('2024-11-13')) & 
    (data['Date_Sent'] < pd.Timestamp('2024-11-25'))
]

#Sacar a Mauro e Ignacio
filtered_data = filtered_data[~filtered_data['To'].isin(['whatsapp:+56975815720', 'whatsapp:+56985051369'])]

# Filter out rows without a matched question
filtered_data = filtered_data[filtered_data['question'].notna()]

# Sort the data by number (To), question, and Date Sent
filtered_data = filtered_data.sort_values(by=['To', 'question', 'Date_Sent'], ascending=[True, True, False])

# Keep only the most recent row for each number (To) and question
unique_data = filtered_data.drop_duplicates(subset=['To', 'question'], keep='first')

# Reset index
unique_data.reset_index(drop=True, inplace=True)


# Export filtered log data
# File path to save the .sav file
sav_file_path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Whatsapp/logs_icfes_filtered.sav'

# Export DataFrame to .sav file
pyreadstat.write_sav(unique_data, sav_file_path)

# Analisis on filtered data

data = unique_data

# Prepare a dataset with cumulative counts of status for each question
status_summary = []
for dummy in questions.values():
    status_counts = data.groupby([dummy, 'Status']).size().unstack(fill_value=0)
    if 1 in status_counts.index:  # Ensure only rows where the dummy equals 1
        status_counts = status_counts.loc[1]
    else:  # If no rows match, create an empty row for consistency
        status_counts = pd.Series(index=status_counts.columns, data=0)
    status_summary.append(status_counts)

# Combine the cumulative counts into a single DataFrame
status_df = pd.concat(status_summary, axis=1)
status_df.columns = [f"P{num}" for num in range(len(questions))]  # Use question numbers as columns

# Add a totals row
status_df.loc['Total'] = status_df.sum()

# Rename the status to Spanish
status_df.rename(index={
    'delivered': 'Recepcionado',
    'failed': 'Fallado',
    'read': 'Leído',
    'sent': 'Enviado',
    'undelivered': 'No recepcionado'
}, inplace=True)

# Calculate percentages for each cell
percentage_df = status_df.div(status_df.loc['Total'], axis=1) * 100

# Combine counts and percentages into a single cell
final_df = status_df.copy()
for col in final_df.columns:
    for row in final_df.index:
        count = status_df.at[row, col]
        percent = percentage_df.at[row, col]
        final_df.at[row, col] = f"{int(count)} ({percent:.1f}%)"

# Export the table to Excel
excel_path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/status_cumulative_with_percentages.xlsx'
final_df.to_excel(excel_path, sheet_name='Cumulative Status Counts')

# Plot cumulative bar chart
status_df.drop('Total').T.plot(kind='bar', stacked=True, figsize=(12, 8))
plt.title('Estado acumulativo para cada pregunta')
plt.xlabel('Preguntas (P0-P11)')
plt.ylabel('Frecuencia')
plt.legend(title='Estado', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Save the plot
plot_path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/status_cumulative_bar_chart.png'
plt.savefig(plot_path)
plt.show()

print("Cumulative Status Counts with Percentages:")
print(final_df)

print(f"Table with percentages saved to {excel_path}")
print(f"Plot saved to {plot_path}")