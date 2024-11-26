import pyreadstat
import pandas as pd
import os
import matplotlib.pyplot as plt

# Paths
completed_responses = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Qualtrics/Encuesta icfes educación superior_November 25, 2024_12.53.sav'
partial_responses = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Qualtrics/Encuesta icfes educación superior_November 25, 2024_12.54.sav'
output_dir = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/qualtrics/plots/'
os.makedirs(output_dir, exist_ok=True)


######## Import Files

# Read SPSS files
df_completed, meta_completed = pyreadstat.read_sav(completed_responses)
df_partial, meta_partial = pyreadstat.read_sav(partial_responses)

# Combine completed and partial responses
df_combined = pd.concat([df_completed, df_partial], ignore_index=True)

df_combined.to_csv('/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/qualtrics/qualtrics_responses_clean.csv', index=False)

######## Make graphs for every question

# Loop through each question (column) and create frequency plots
for question in df_combined.columns:
    # Drop NaN values and exclude empty strings
    valid_responses = df_combined[question].dropna()
    valid_responses = valid_responses[valid_responses != ""]  # Exclude empty strings
    valid_responses = valid_responses[valid_responses != 0]  # Exclude 0 as an answer
    
    # Skip the question if all responses are NaN or empty
    if valid_responses.empty:
        continue

    # Count frequency of responses
    freq = valid_responses.value_counts().head(20)  # Top 20 responses
    relative_freq = freq / freq.sum() * 100  # Calculate relative frequencies
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    bars = plt.bar(freq.index, freq.values, tick_label=freq.index)
    for bar, rel_freq in zip(bars, relative_freq):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{rel_freq:.1f}%",
            ha='center',
            va='bottom',
            fontsize=10
        )
    
    plt.title(f"Top 20 Responses for {question}", fontsize=14)
    plt.xlabel("Responses", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()
    
    # Save the plot
    plot_path = os.path.join(output_dir, f"{question}_frequency.png")
    plt.savefig(plot_path)
    plt.close()  # Close the plot to free memory

print(f"Plots saved to {output_dir}")