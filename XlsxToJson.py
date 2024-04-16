import pandas as pd
import os
import json

def convert_excel_to_json(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(directory, filename)
            data = pd.read_excel(file_path)

            # Convert DataFrame to list of dictionaries for JSON
            json_data = data.to_dict(orient='records')

            # Modify the IDs to match the provided format, if necessary
            for item in json_data:
                # Convert ID to string, remove characters after the dot, and then convert to integer
                item['ID'] = int(str(item['ID']).split('.')[0])

            # Define JSON output path
            json_file_path = os.path.join(directory, filename.replace('.xlsx', '.json'))

            # Write JSON data to file
            with open(json_file_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)

            print(f"Converted {filename} to JSON.")

# Specify the directory containing the Excel files
directory = 'C:\\Users\\lszos\\Downloads\\CCPR_GC1-37'
convert_excel_to_json(directory)
