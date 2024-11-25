import pyreadstat
import pandas as pd
import os
import matplotlib.pyplot as plt

# Paths
completed_responses = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Qualtrics/Encuesta icfes educación superior_November 21, 2024_12.15.sav'
partial_responses = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/Encuesta/Qualtrics/Encuesta icfes educación superior_November 21, 2024_12.19.sav'
output_qualtrics = '/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Outputs/analisis_resultados_encuesta/qualtrics'

# Read SPSS files
df_completed, meta_completed = pyreadstat.read_sav(completed_responses)
df_partial, meta_partial = pyreadstat.read_sav(partial_responses)

# Combine completed and partial responses
df_combined = pd.concat([df_completed, df_partial], ignore_index=True)

# Add a column to identify response type
df_combined['ResponseType'] = ['Completed'] * len(df_completed) + ['Partial'] * len(df_partial)

# Get column-to-label mappings
question_labels = meta_completed.column_names_to_labels
response_labels = meta_completed.value_labels

# Analyze each question
for question_id in df_combined.columns:
	if question_id not in question_labels:
		continue

	question_label = question_labels.get(question_id, question_id)

	# Analyze responses
	if df_combined[question_id].dtype == 'O':  # Text responses
		response_counts = df_combined[question_id].value_counts()

	elif pd.api.types.is_numeric_dtype(df_combined[question_id]):  # Numeric responses
		response_counts = df_combined[question_id].dropna().value_counts()

	else:
		continue

	# Map responses to labels if available
	if question_id in response_labels:
		response_counts.index = response_counts.index.map(response_labels[question_id])

	# Save response table
	table_path = os.path.join(output_qualtrics, f"{question_id}_responses.csv")
	response_counts.to_csv(table_path, header=["Count"], index_label="Response")
	print(f"Saved response table for {question_label} to {table_path}")

	# Generate and save graphs
	plt.figure(figsize=(10, 6))
	response_counts.plot(kind='bar')
	plt.title(f"Responses to: {question_label}")
	plt.ylabel("Count")
	plt.xticks(rotation=45, ha="right")
	plt.tight_layout()
	graph_path = os.path.join(output_qualtrics, f"{question_id}_responses.png")
	plt.savefig(graph_path)
	plt.close()
	print(f"Saved graph for {question_label} to {graph_path}")

# Save combined data
combined_data_path = os.path.join(output_qualtrics, "combined_responses.csv")
df_combined.to_csv(combined_data_path, index=False)
print(f"Saved combined dataset to {combined_data_path}")