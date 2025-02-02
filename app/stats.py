import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, jsonify, send_file
import os

app = Flask(__name__)

# Specify the exact paths to your Stats.csv files
STATS_FILES = [
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_24_25\Stats.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_25_25\Stats.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_26_25\Stats.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_27_25\Stats.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_28_25\Stats.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_29_25\Stats.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_30_25\Stats.csv"
]

def compile_stats_data():
    stats_data = []  # List to store DataFrames

    for file_path in STATS_FILES:
        try:
            # Read the Stats.csv file
            df = pd.read_csv(file_path)
            print(f"Processing file: {file_path}")

            # Clean the data by ensuring the columns are stripped of any extra spaces
            df.columns = df.columns.str.strip()

            # Ensure 'Minutes Watched' is numeric
            df['Minutes Watched'] = pd.to_numeric(df['Minutes Watched'], errors='coerce').fillna(0)

            # Extract Date from the folder name (last folder part of the path)
            folder_name = os.path.basename(os.path.dirname(file_path))  # Get the folder name (e.g., DTM_1_10_25)
            date_part = folder_name.split('_')[1:]  # Get the '1_10_25' part
            date_str = '_'.join(date_part)  # Convert it to '1_10_25'

            # Add the Date column
            df['Date'] = date_str

            # Append the dataframe to the list
            stats_data.append(df)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Combine all DataFrames
    if stats_data:
        combined_df = pd.concat(stats_data, ignore_index=True)
        combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%m_%d_%y', errors='coerce')
        combined_df.dropna(subset=['Date'], inplace=True)  # Remove rows with invalid dates
        return combined_df
    else:
        print("No valid stats data found.")
        return pd.DataFrame()


def create_minutes_watched_bar_chart(stats_df):
    # Set the Date column as the index
    stats_df.set_index('Date', inplace=True)

    # Plotting the 'Minutes Watched' as a bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    stats_df['Minutes Watched'].plot(kind='bar', ax=ax, color='skyblue', label='Minutes Watched', width=0.8)

    # Customization of the chart
    ax.set_title("Minutes Watched Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Minutes Watched")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart
    chart_path = r'C:\Users\Ev\Desktop\Twitch Growth Analysis\minutes_watched_chart.png'
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def create_line_chart(stats_df):
    # Set the Date column as the index
    stats_df.set_index('Date', inplace=True)

    # Plotting the other columns as line charts
    fig, ax = plt.subplots(figsize=(12, 6))
    stats_df['Followers Gained'].plot(ax=ax, color='green', label='Followers Gained', marker='o')
    stats_df['Followers Lost'].plot(ax=ax, color='red', label='Followers Lost', marker='x')
    stats_df['Max_Viewers'].plot(ax=ax, color='purple', label='Max_Viewers', marker='^')
    stats_df['Avg_Viewers'].plot(ax=ax, color='orange', label='Avg_Viewers', marker='s')

    # Customization of the chart
    ax.set_title("Twitch Stats Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart
    chart_path = r'C:\Users\Ev\Desktop\Twitch Growth Analysis\line_chart_stats.png'
    plt.savefig(chart_path)
    plt.close()
    return chart_path

@app.route('/minutes_watched', methods=['GET'])
def get_minutes_watched_chart():
    stats_df = compile_stats_data()
    if stats_df.empty:
        return jsonify({"error": "No Stats data found."}), 404

    chart_path = create_minutes_watched_bar_chart(stats_df)
    return send_file(chart_path, mimetype='image/png')

@app.route('/line_chart', methods=['GET'])
def get_line_chart():
    stats_df = compile_stats_data()
    if stats_df.empty:
        return jsonify({"error": "No Stats data found."}), 404

    chart_path = create_line_chart(stats_df)
    return send_file(chart_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
