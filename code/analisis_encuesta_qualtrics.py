import pyreadstat
import pandas as pd
import os
import matplotlib.pyplot as plt

# Paths
completed_responses = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Qualtrics/Encuesta icfes educación superior_November 25, 2024_12.53.sav'
partial_responses = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Qualtrics/Encuesta icfes educación superior_November 25, 2024_12.54.sav'
output_dir = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/qualtrics/plots/'
os.makedirs(output_dir, exist_ok=True)

# Read SPSS files
df_completed, meta_completed = pyreadstat.read_sav(completed_responses)
df_partial, meta_partial = pyreadstat.read_sav(partial_responses)

# Combine completed and partial responses
df_combined = pd.concat([df_completed, df_partial], ignore_index=True)

# Debug column labels to inspect their structure
print("Column Labels Metadata:")
print(meta_completed.column_labels)  # Add this line to inspect

# Check if column labels are provided and map them
if isinstance(meta_completed.column_labels, dict):
    # If column_labels is a dictionary, map it directly
    df_combined.columns = [meta_completed.column_labels.get(col, col) for col in df_combined.columns]
elif isinstance(meta_completed.column_labels, list):
    # If it's a list, use it directly assuming the order matches
    df_combined.columns = meta_completed.column_labels
else:
    print("Column labels are not in a recognized format. Using default column names.")

# Drop unnecessary metadata columns
columns_to_exclude = ['StartDate', 'EndDate', 'IPAddress', 'RecordedDate', 'ResponseId', 'RecipientLastName', 
                      'RecipientFirstName', 'RecipientEmail', 'ExternalReference', 'LocationLatitude', 
                      'LocationLongitude', 'DistributionChannel', 'UserLanguage']
df_cleaned = df_combined.drop(columns=columns_to_exclude, errors='ignore')

# Generate frequency plots for the most frequent responses for each question
for column in df_cleaned.columns:
    # Skip metadata and numerical progress columns
    if column in ['Progress', 'Duration__in_seconds_', 'Finished'] or df_cleaned[column].dtype in ['float64', 'int64']:
        continue
    
    # Count response frequencies
    freq = df_cleaned[column].value_counts().head(20)  # Top 20 responses
    
    if freq.empty:
        continue  # Skip empty columns
    
    total_responses = df_cleaned[column].count()
    rel_freq = (freq / total_responses) * 100  # Calculate relative frequency as a percentage
    
    # Plot frequencies
    plt.figure(figsize=(12, 8))
    bars = plt.bar(freq.index.astype(str), freq.values, color='skyblue')
    plt.title(f'Top 20 Responses for {column}', fontsize=16)
    plt.xlabel('Responses', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10, wrap=True)

    # Add relative frequency above each bar
    for bar, value, percentage in zip(bars, freq.values, rel_freq.values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f'{percentage:.1f}%',
            ha='center',
            va='bottom',
            fontsize=10,
            color='black'
        )
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Save the plot
    plot_filename = f'{column.replace("/", "_").replace(" ", "_")}_top20_frequency.png'
    plot_path = os.path.join(output_dir, plot_filename)
    plt.savefig(plot_path, dpi=300)
    plt.close()

print(f"Plots saved in: {output_dir}")