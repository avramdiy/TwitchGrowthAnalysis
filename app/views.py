import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, jsonify, send_file
import os

app = Flask(__name__)

# Paths to your Views.csv files
VIEWS_FILES = [
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_24_25\Views.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_25_25\Views.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_26_25\Views.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_27_25\Views.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_28_25\Views.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_29_25\Views.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_30_25\Views.csv"
]

# Views types we expect
VIEWS_TYPES = [
    "Followers", "Other Channel Pages", "Searches", "Browse Page"
]

def compile_views_data():
    views_data = []  # List to store DataFrames

    for file_path in VIEWS_FILES:
        try:
            # Read the Views.csv file
            df = pd.read_csv(file_path)
            print(f"Processing file: {file_path}")

            # Clean the data by ensuring the columns are stripped of any extra spaces
            df.columns = df.columns.str.strip()

            # Extract the values from the 'Views' column and clean them
            views_values = pd.to_numeric(df['Views'], errors='coerce').fillna(0)

            # Create a dictionary to store the views data by type
            views_dict = dict(zip(VIEWS_TYPES, views_values))

            # Extract Date from the folder name (last folder part of the path)
            folder_name = os.path.basename(os.path.dirname(file_path))  # Get the folder name (e.g., DTM_1_10_25)
            date_part = folder_name.split('_')[1:]  # Get the '1_10_25' part
            date_str = '_'.join(date_part)  # Convert it to '1_10_25'

            # Add the Date column
            views_dict['Date'] = date_str

            # Convert to DataFrame and append
            views_data.append(pd.DataFrame([views_dict]))

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Combine all DataFrames
    if views_data:
        combined_df = pd.concat(views_data, ignore_index=True)
        combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%m_%d_%y', errors='coerce')
        combined_df.dropna(subset=['Date'], inplace=True)  # Remove rows with invalid dates
        return combined_df
    else:
        print("No valid views data found.")
        return pd.DataFrame()

def create_bar_chart(views_df):
    # Group data for the bar chart
    grouped = views_df.groupby(['Date']).sum().reset_index()
    grouped.set_index('Date', inplace=True)

    # Create a stacked bar chart
    ax = grouped.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='viridis')

    # Chart customization
    plt.title("Daily Views by Type")
    plt.xlabel("Date")
    plt.ylabel("Views Count")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart
    chart_path = r'C:\Users\Ev\Desktop\Twitch Growth Analysis\views_chart.png'
    plt.savefig(chart_path)
    plt.close()
    return chart_path

@app.route('/views', methods=['GET'])
def get_views_chart():
    views_df = compile_views_data()
    if views_df.empty:
        return jsonify({"error": "No Views data found."}), 404

    chart_path = create_bar_chart(views_df)
    return send_file(chart_path, mimetype='image/png')

@app.route('/views_range', methods=['GET'])
def get_views_range_chart():
    views_df = compile_views_data()
    if views_df.empty:
        return jsonify({"error": "No Views data found."}), 404

    # Filter the data for a specific date range (example: 1/11 to 1/16)
    filtered_df = views_df[(views_df['Date'] >= '2025-01-11') & (views_df['Date'] <= '2025-01-16')]

    # Create the chart for the filtered data
    if filtered_df.empty:
        return jsonify({"error": "No data found in the specified date range."}), 404

    chart_path = create_bar_chart(filtered_df)
    return send_file(chart_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
