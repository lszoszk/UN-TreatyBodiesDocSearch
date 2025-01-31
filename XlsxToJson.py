import os
import pandas as pd
import json

def convert_xlsx_to_json_folder(input_folder, output_folder):
    """
    Convert all XLSX files in a folder to JSON format with the desired structure:
       [
         {"ID": <int>, "Text": "<string>", "Labels": []},
         ...
       ]
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        # Skip non-XLSX files and temp files
        if not file_name.endswith('.xlsx') or file_name.startswith('~$'):
            continue

        print(f"Processing file: {file_name}")
        file_path = os.path.join(input_folder, file_name)

        # Read the Excel file
        df = pd.read_excel(file_path)

        # Strip column names to remove trailing spaces
        df.columns = df.columns.str.strip()
        print("Columns:", df.columns.tolist())

        # Check if required columns exist
        if "ID" not in df.columns or "Text" not in df.columns:
            print(f"Skipping file {file_name}: Missing required columns ('ID' or 'Text')")
            continue

        print(f"Sample data from {file_name}:")
        print(df.head())

        # Build JSON data
        json_data = []
        for _, row in df.iterrows():
            raw_id = row["ID"]
            if pd.isna(raw_id):
                continue  # skip if ID is missing

            # handle numeric/floating IDs
            id_val = int(float(str(raw_id).strip().rstrip('.')))

            text_str = row["Text"]  # after stripping columns, "Text " becomes "Text"

            json_data.append({
                "ID": id_val,
                "Text": str(text_str),
                "Labels": []
            })

        # Write output JSON
        output_file = os.path.join(output_folder, file_name.replace('.xlsx', '.json'))
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

        print(f"Converted {file_name} -> {output_file}")


# Example usage:
if __name__ == "__main__":
    input_folder = # Add the path to the folder containing XLSX files
    output_folder = # Add the path to the folder where JSON files will be saved
    convert_xlsx_to_json_folder(input_folder, output_folder)
