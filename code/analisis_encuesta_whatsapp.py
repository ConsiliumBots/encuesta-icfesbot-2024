import pandas as pd

# Load the dataset
file_path = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Whatsapp/interacciones_chatbot_Encuesta_IcfesBot_2024-11-25_14-41-51.csv'
data = pd.read_csv(file_path)


############ Clean dataset

# Clean the phone numbers
data['user'] = data['user'].str.replace('whatsapp:', '', regex=False)

# Convert timestamp column to datetime with inferred format
data['timestamp'] = pd.to_datetime(data['timestamp'], format='ISO8601', errors='coerce')

# Check for any failed conversions (resulting in NaT)
if data['timestamp'].isna().any():
    print("Some timestamps could not be converted. Investigating the issue.")
    print(data[data['timestamp'].isna()]['timestamp'])

# Drop rows with invalid timestamps or handle them
data = data.dropna(subset=['timestamp'])

# Sort data by user and timestamp for logical sequence analysis
data['timestamp'] = pd.to_datetime(data['timestamp'])
data.sort_values(by=['user', 'timestamp'], inplace=True)

# Identify bot questions and user responses based on sender
data['is_bot_message'] = data['sender'] == 'bot'
data['is_user_response'] = data['sender'] == 'user'

# Assign question IDs based on node transitions (e.g., "node_start" -> "node_end")
data['question_id'] = data['node_end'].where(data['is_bot_message'])

# Forward fill question IDs to associate responses
data['question_id'] = data['question_id'].fillna(method='ffill')

# Filter out irrelevant messages (e.g., null UUIDs, non-conversational data)
data = data.dropna(subset=['uuid'])

# Extract relevant columns for question-response pairing
responses = data[data['is_user_response']][['user', 'question_id', 'message']]

# Pivot table to organize responses per user and question
responses_pivot = responses.pivot_table(
    index='user',
    columns='question_id',
    values='message',
    aggfunc='first'  # If multiple responses exist, take the first
).reset_index()

# Rename columns for clarity
responses_pivot.columns.name = None  # Remove pivot table name
responses_pivot.rename(columns={'user': 'phone'}, inplace=True)

# Save the clean responses to a CSV file
output_file = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/Whatsapp/cleaned_whatsapp_responses.csv'
responses_pivot.to_csv(output_file, index=False)



############ Analize dataset

# Make a frequency plot for every question
# Save every plot to '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/Whatsapp/plots'

import os
import matplotlib.pyplot as plt

# Define the output directory
output_dir = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/Whatsapp/plots/'
os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

# Generate frequency plots for the top 20 responses for each question
for question_id in responses['question_id'].unique():
    # Filter data for the specific question
    question_data = responses[responses['question_id'] == question_id]['message']
    
    # Count frequencies and calculate relative frequencies
    freq = question_data.value_counts().head(20)
    total_responses = question_data.count()
    rel_freq = (freq / total_responses) * 100  # Calculate relative frequency as percentage
    
    # Plot frequencies
    plt.figure(figsize=(12, 8))
    bars = plt.bar(freq.index, freq.values, color='skyblue')
    plt.title(f'Top 20 Responses for Question {question_id}', fontsize=16)
    plt.xlabel('Responses', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10, wrap=True)  # Ensure all text is visible

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
    
    # Adjust layout to prevent text overlap
    plt.tight_layout()
    
    # Save plot
    plot_path = os.path.join(output_dir, f'question_{question_id}_top20_frequency.png')
    plt.savefig(plot_path, dpi=300)  # Save with high resolution
    plt.close()  # Close the plot to avoid overlap in subsequent iterations

print(f"Top 20 response plots saved to {output_dir}")