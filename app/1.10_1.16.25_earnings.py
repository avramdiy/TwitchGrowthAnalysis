import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, jsonify, send_file
import os
import tkinter as tk

app = Flask(__name__)

# Specify the exact paths to your Earnings.csv files
EARNINGS_FILES = [
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_10_25\Earnings.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_11_25\Earnings.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_12_25\Earnings.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_13_25\Earnings.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_14_25\Earnings.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_15_25\Earnings.csv",
    r"C:\Users\Ev\Desktop\Twitch Growth Analysis\DTM_1_16_25\Earnings.csv"
]

# Earnings types we expect
EARNINGS_TYPES = [
    "Paid Subs", "Prime Subs", "Gifted Subs", "Multi-Month Gifted Subs", 
    "Ads", "Turbo", "Cheering", "Game Sales", "Extensions", "Bounties", "Other Bits Interactions"
]

def compile_earnings_data():
    earnings_data = []  # List to store DataFrames

    for file_path in EARNINGS_FILES:
        try:
            # Read the CSV file with one column 'Earnings'
            df = pd.read_csv(file_path, header=None, names=['Earnings'])
            print(f"Processing file: {file_path}")

            # Remove any leading/trailing spaces in the column name
            df.columns = df.columns.str.strip()

            # Extract values from the 'Earnings' column
            earnings_values = df['Earnings'].replace({'\$': '', ',': ''}, regex=True)  # Clean the numbers
            earnings_values = pd.to_numeric(earnings_values, errors='coerce').fillna(0)

            # Create a dictionary to store the earnings data by type
            earnings_dict = dict(zip(EARNINGS_TYPES, earnings_values))

            # Extract Date from the folder name (last folder part of the path)
            folder_name = os.path.basename(os.path.dirname(file_path))  # Get the folder name (e.g., DTM_1_10_25)
            date_part = folder_name.split('_')[1:]  # Get the '1_10_25' part
            date_str = '_'.join(date_part)  # Convert it to '1_10_25'

            # Add the Date column
            earnings_dict['Date'] = date_str

            # Convert to DataFrame and append
            earnings_data.append(pd.DataFrame([earnings_dict]))

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Combine all DataFrames
    if earnings_data:
        combined_df = pd.concat(earnings_data, ignore_index=True)
        combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%m_%d_%y', errors='coerce')
        combined_df.dropna(subset=['Date'], inplace=True)  # Remove rows with invalid dates
        return combined_df
    else:
        print("No valid earnings data found.")
        return pd.DataFrame()

def create_bar_chart(earnings_df):
    # Group data for the bar chart
    grouped = earnings_df.groupby(['Date']).sum().reset_index()
    grouped.set_index('Date', inplace=True)

    # Create a stacked bar chart
    ax = grouped.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='viridis')

    # Chart customization
    plt.title("Daily Earnings by Type")
    plt.xlabel("Date")
    plt.ylabel("Earnings Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart
    chart_path = r'C:\Users\Ev\Desktop\Twitch Growth Analysis\earnings_chart.png'
    plt.savefig(chart_path)
    plt.close()
    return chart_path

@app.route('/earnings', methods=['GET'])
def get_earnings_chart():
    earnings_df = compile_earnings_data()
    if earnings_df.empty:
        return jsonify({"error": "No Earnings data found."}), 404

    chart_path = create_bar_chart(earnings_df)
    return send_file(chart_path, mimetype='image/png')

@app.route('/earnings_range', methods=['GET'])
def get_earnings_range_chart():
    earnings_df = compile_earnings_data()
    if earnings_df.empty:
        return jsonify({"error": "No Earnings data found."}), 404

    # Filter the data for the date range from 1/11 to 1/16
    filtered_df = earnings_df[(earnings_df['Date'] >= '2025-01-11') & (earnings_df['Date'] <= '2025-01-16')]

    # Create the chart for the filtered data
    if filtered_df.empty:
        return jsonify({"error": "No data found in the specified date range."}), 404

    chart_path = create_bar_chart(filtered_df)
    return send_file(chart_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
